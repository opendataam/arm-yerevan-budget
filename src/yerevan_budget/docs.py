"""Generate docs/data_dictionary.md (from the comments stored in the DuckDB catalog) and docs/<lang>/inventory.md."""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from . import config

log = logging.getLogger(__name__)

PREFIX_TITLES = [
    ("meta_", "Metadata / provenance"),
    ("dim_", "Dimensions"),
    ("fact_", "Facts"),
    ("stg_", "Staging"),
    ("raw_", "Raw data"),
    ("qc_", "Data quality"),
    ("v_", "Views"),
]


def _md(s) -> str:
    return "" if s is None else str(s).replace("|", "\\|").replace("\n", " ")


def _row(cells) -> str:
    return "| " + " | ".join(cells) + " |"


INVENTORY_TEXT = {
    "en": {
        "title": "Source inventory",
        "intro": "Generated automatically (`python -m yerevan_budget docs`) from the tables `meta_document`, `meta_file`, "
                 "`fact_budget_line` — do not edit by hand.",
        "core": "Documents of the city budget",
        "core_cols": ["year", "type", "period", "document", "file", "files", "pages", "amounts", "primary"],
        "inst": "Documents of municipal institutions (catalogued, not parsed)",
        "inst_cols": ["group of institutions", "years", "documents", "size stated on the site, MB"],
        "yes": "yes", "no": "",
    },
    "hy": {
        "title": "Աղբյուրների ցանկ",
        "intro": "Ստեղծվում է ավտոմատ (`python -m yerevan_budget docs`) `meta_document`, `meta_file`, `fact_budget_line` "
                 "աղյուսակներից․ ձեռքով մի խմբագրեք։",
        "core": "Քաղաքի բյուջեի փաստաթղթեր",
        "core_cols": ["տարի", "տեսակ", "ժամանակահատված", "փաստաթուղթ", "ֆայլ", "ֆայլեր", "էջեր", "գումարներ", "հիմնական"],
        "inst": "Համայնքային կազմակերպությունների փաստաթղթեր (ցուցակագրված, չեն մշակվում)",
        "inst_cols": ["կազմակերպությունների խումբ", "տարիներ", "փաստաթղթեր", "կայքում նշված չափը, ՄԲ"],
        "yes": "այո", "no": "",
    },
    "ru": {
        "title": "Перечень источников",
        "intro": "Генерируется автоматически (`python -m yerevan_budget docs`) из таблиц `meta_document`, `meta_file`, "
                 "`fact_budget_line` — не редактировать вручную.",
        "core": "Документы бюджета города",
        "core_cols": ["год", "тип", "период", "документ", "файл", "файлов", "страниц", "сумм", "основной"],
        "inst": "Документы муниципальных учреждений (в каталоге, не разбираются)",
        "inst_cols": ["группа учреждений", "годы", "документов", "размер по данным сайта, МБ"],
        "yes": "да", "no": "",
    },
}


def write_inventory(con, docs_dir: Path) -> None:
    """docs/<lang>/inventory.md: every core document and a summary of the institutional ones, in each language."""
    core = con.execute("""
        SELECT m.fiscal_year, m.doc_type, t.name_en, t.name_ru, t.name_hy, m.period, m.title_hy, m.title_en, m.title_ru,
               m.url, m.ext, m.n_files,
               (SELECT sum(n_pages) FROM meta_file f WHERE f.doc_id = m.doc_id),
               (SELECT count(*) FROM fact_budget_line b WHERE b.doc_id = m.doc_id)
               + (SELECT count(*) FROM fact_program_budget b WHERE b.doc_id = m.doc_id),
               m.is_primary, m.doc_id
        FROM meta_document m JOIN dim_doc_type t USING (doc_type)
        WHERE m.doc_group = 'core'
        ORDER BY m.fiscal_year, m.doc_type, m.period, m.doc_id""").fetchall()
    inst = con.execute("""
        SELECT institution_group_hy, institution_group_en, institution_group_ru,
               min(fiscal_year) || '–' || max(fiscal_year), count(*), round(sum(size_mb_stated))
        FROM meta_document WHERE doc_group = 'institutions'
        GROUP BY ALL ORDER BY 1""").fetchall()
    for lang, tx in INVENTORY_TEXT.items():
        li = {"en": 0, "ru": 1, "hy": 2}[lang]
        lines = [f"# {tx['title']}", "", tx["intro"], "", f"## {tx['core']}", "",
                 _row(tx["core_cols"]), "|" + "---|" * len(tx["core_cols"])]
        for (year, _dt, *rest) in core:
            type_names, period, titles, url, ext, n_files, n_pages, n_amounts, primary, doc_id = (
                rest[0:3], rest[3], rest[4:7], rest[7], rest[8], rest[9], rest[10], rest[11], rest[12], rest[13])
            title = {"hy": titles[0], "en": titles[1], "ru": titles[2]}[lang] or titles[0]
            lines.append(_row([str(year or ""), _md(type_names[li]), period or "", _md(title),
                               f"[{doc_id}.{ext}]({url})", str(n_files or ""), str(int(n_pages or 0) or ""),
                               f"{n_amounts:,}" if n_amounts else "", tx["yes"] if primary else tx["no"]]))
        lines += ["", f"## {tx['inst']}", "", _row(tx["inst_cols"]), "|" + "---|" * len(tx["inst_cols"])]
        for g_hy, g_en, g_ru, years, n, mb in inst:
            g = {"hy": g_hy, "en": g_en or g_hy, "ru": g_ru or g_hy}[lang]
            lines.append(_row([_md(g), years, str(n), f"{mb:,.0f}" if mb else ""]))
        out = docs_dir / lang / "inventory.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_data_dictionary(con, out: Path) -> None:
    objects = con.execute("""
        SELECT table_name, 'table' AS kind, comment FROM duckdb_tables() WHERE schema_name = 'main'
        UNION ALL
        SELECT view_name, 'view', comment FROM duckdb_views() WHERE schema_name = 'main' AND NOT internal
        ORDER BY 1
    """).fetchall()
    cols = con.execute("""
        SELECT table_name, column_name, data_type, comment
        FROM duckdb_columns() WHERE schema_name = 'main' ORDER BY table_name, column_index
    """).fetchall()
    by_table: dict[str, list] = {}
    for t, c, typ, com in cols:
        by_table.setdefault(t, []).append((c, typ, com))
    lines = [
        "# Data dictionary",
        "",
        "Generated automatically from the DuckDB catalog by `python -m yerevan_budget docs` — do not edit by hand.",
        ("The descriptions of tables and columns are also stored in the database itself (`duckdb_tables()`, "
         "`duckdb_columns()`) and are defined in `sql/schema.sql`, `sql/views.sql`, `sql/qc.sql` (`COMMENT ON`). "
         "Schema overview: [database.md](en/database.md) ([hy](hy/database.md), [ru](ru/database.md))."),
        "",
    ]
    for prefix, title in PREFIX_TITLES:
        group = [o for o in objects if o[0].startswith(prefix)]
        if not group:
            continue
        lines += [f"## {title}", ""]
        for name, kind, comment in group:
            rows = con.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
            lines += [f"### `{name}` ({kind}, {rows:,} rows)", "", _md(comment) or "_no description_", "",
                      "| column | type | description |", "|---|---|---|"]
            for c, typ, com in by_table.get(name, []):
                lines.append(f"| `{c}` | {typ} | {_md(com)} |")
            lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_all(db_path=None) -> None:
    con = duckdb.connect(str(db_path or config.DUCKDB_PATH), read_only=True)
    docs_dir = config.ROOT / "docs"
    write_data_dictionary(con, docs_dir / "data_dictionary.md")
    write_inventory(con, docs_dir)
    con.close()
    log.info("written docs/data_dictionary.md and docs/*/inventory.md")
