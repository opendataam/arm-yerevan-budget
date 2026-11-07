"""Step 4: build the DuckDB database from the catalog, the extraction cache and the dictionaries.

The database is rebuilt from scratch on every run (into a temporary file that
replaces ``data/yerevan_budget.duckdb`` at the end), so the build is
deterministic and depends only on ``data/catalog``, ``data/interim`` (made by
``extract`` from ``data/raw``) and ``data/translations``.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import pandas as pd

from . import classify, config, reference
from .extract import PARSED_EXT, files_of, read_cache
from .parsers import budget_tables as bt
from .parsers import program_tables, semantics
from .parsers.common import clean, code_str
from .translations import Dictionary, strip_formula
from .utils import read_json

log = logging.getLogger(__name__)

# document types whose budget tables are interpreted into fact_budget_line,
# with the number of amount columns their forms have
FACT_LAYOUTS: dict[str, tuple[int, ...]] = {
    "execution_report": (9,),          # approved / revised / actual x total / admin / fund
    "budget": (3,),                    # total / admin / fund
    "budget_draft": (3,),
    "budget_amendment": (3,),
    "mtef": (9, 3),                    # three years x total / admin / fund
    "execution_measures": (9,),        # total, admin (year, Q1, H1, 9M), fund (year, Q1, H1, 9M)
}


def insert(con: duckdb.DuckDBPyConnection, table: str, records: list[dict] | pd.DataFrame) -> int:
    df = records if isinstance(records, pd.DataFrame) else pd.DataFrame.from_records(records)
    if df.empty:
        log.warning("table %s: nothing to insert", table)
        return 0
    cols = [r[0] for r in con.execute(f"DESCRIBE {table}").fetchall()]
    df = df[[c for c in df.columns if c in cols]]
    con.register("_df", df)
    con.execute(f"INSERT INTO {table} BY NAME SELECT * FROM _df")
    con.unregister("_df")
    log.info("table %-22s +%d rows", table, len(df))
    return len(df)


def render_sql(text: str) -> str:
    """Expand the language placeholders of the SQL files.

    A line containing ``{lang}`` is repeated for every translation language (:data:`config.LANGS`), with
    ``{language}`` replaced by its English name; ``{langs}`` anywhere becomes ``en / ru / ...``.
    Comment lines (``--``) are left as they are.
    """
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("--"):
            out.append(line)
            continue
        line = line.replace("{langs}", " / ".join(config.LANGS))
        if "{lang}" in line:
            out += [line.replace("{lang}", lang).replace("{language}", config.LANG_NAMES[lang])
                    for lang in config.LANGS]
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def run_sql_file(con, path: Path) -> None:
    con.execute(render_sql(path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# tables of a file
# ---------------------------------------------------------------------------

def sheet_rows(sheet: dict) -> list[list]:
    grid: dict[int, dict[int, str]] = {}
    for r, c, text, _num in sheet["cells"]:
        grid.setdefault(r, {})[c] = text
    return [[grid.get(r, {}).get(c) for c in range(sheet["n_cols"])] for r in range(sheet["n_rows"])]


def read_tables(cache: dict) -> bt.TableReader:
    reader = bt.TableReader()
    ctx: dict = {}
    if cache["kind"] == "pdf":
        for p in cache["pages"]:
            ctx = bt.page_context(p["text"], ctx)
            for t in p["tables"]:
                reader.add_table(t["rows"], p["page"], ctx)
    elif cache["kind"] == "sheet":
        for sh in cache["sheets"]:
            rows = sheet_rows(sh)
            head = "\n".join(" ".join(clean(c) for c in r if c) for r in rows[:12])
            ctx = bt.page_context(head, {})
            ctx["sheet"] = sh["name"]
            ctx["district"] = reference.district_of(sh["name"]) or ctx.get("district")
            reader.add_table(rows, None, ctx)
    elif cache["kind"] == "text":
        for t in cache.get("tables", []):
            reader.add_table(t["rows"], None, ctx)
    return reader


def func_code(func: tuple) -> str | None:
    s, g, c = (code_str(x) for x in func)
    if not s or not s.isdigit():
        return None
    g = g if g and g.isdigit() else "0"
    c = c if c and c.isdigit() else "0"
    return f"{int(s):02d}.{int(g)}.{int(c)}"


def interpret(rows: list[bt.Row], doc: dict, file_id: str) -> tuple[list[dict], list[dict]]:
    """stg_table_row records and fact_budget_line records of the rows of one file."""
    stg, facts = [], []
    doc_type = doc["doc_type"]
    allowed = FACT_LAYOUTS.get(doc_type)
    sem_cache: dict[tuple[int, int], list[dict]] = {}
    statement = None
    cur_func = cur_program = None
    last_ctx_key = None
    for r in rows:
        headers = [r.layout.headers.get(k, "") for k in r.amount_cols]
        stg.append({
            "file_id": file_id, "seq": r.seq, "page": r.page, "sheet": r.context.get("sheet"),
            "appendix": r.context.get("appendix"), "section_no": r.context.get("section"),
            "table_no": r.context.get("table_no"), "table_title": r.context.get("title"),
            "line_code": r.line_code, "func_section": r.func[0], "func_group": r.func[1], "func_class": r.func[2],
            "class_code": r.class_code, "label_raw": r.label,
            "amount_text": [a[0] for a in r.amounts], "headers": headers,
        })
        ctx_key = (r.context.get("appendix"), r.context.get("table_no"), r.context.get("sheet"))
        if ctx_key != last_ctx_key:
            cur_func = cur_program = None
            last_ctx_key = ctx_key
        n_amounts = len(r.amounts)
        while n_amounts and r.amounts[n_amounts - 1][0] is None:
            n_amounts -= 1  # trailing empty columns of the layout
        statement = semantics.table_kind(set(r.kinds), r.line_code, r.label, statement)
        if not allowed or n_amounts not in allowed or statement is None:
            continue
        lid = id(r.layout)
        if (lid, n_amounts) not in sem_cache:
            sem_cache[(lid, n_amounts)] = semantics.amount_semantics(doc_type, headers[:n_amounts], doc["fiscal_year"],
                                                                     doc.get("period"))
        sem = sem_cache[(lid, n_amounts)]
        label = strip_formula(r.label) or None
        fc = func_code(r.func)
        rtype = semantics.row_type(statement, r.line_code, r.func, r.class_code, label)
        if statement == "expenditure_program":
            if rtype == "functional":
                cur_func, cur_program = fc, None
            elif rtype == "program":
                cur_program = label
            elif rtype == "total":
                cur_func = cur_program = None
        class_code = r.class_code if r.class_code and r.class_code.isdigit() else None
        district = r.context.get("district") if statement == "expenditure_program" else None
        for i, (raw, val, flag) in enumerate(r.amounts[:n_amounts]):
            if raw is None or flag == "text":
                continue  # empty cells and text in an amount column (notes) stay only in stg_table_row
            s = sem[i] if i < len(sem) else {}
            facts.append({
                "doc_id": doc["doc_id"], "file_id": file_id, "seq": r.seq, "col_no": i + 1, "page": r.page,
                "doc_type": doc_type, "fiscal_year": doc["fiscal_year"], "report_period": doc.get("period"),
                "statement": statement, "row_type": rtype, "appendix": r.context.get("appendix"),
                "district_code": district,
                "line_code": r.line_code if r.line_code and r.line_code.isdigit() else None,
                "func_code": fc if rtype in ("functional", "line") else cur_func,
                "class_code": class_code,
                "program_hy": cur_program if rtype == "economic" else None,
                "label_hy": label,
                "scenario": s.get("scenario"), "value_year": s.get("year"), "value_period": s.get("period"),
                "budget_part": s.get("part"), "amount_kamd": val, "amount_text": raw,
            })
    return stg, facts


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def _title_translations(docs: list[dict], d: Dictionary) -> None:
    for rec in docs:
        g = rec.get("institution_group_hy")
        for lang in config.LANGS:
            rec[f"title_{lang}"] = d.get("labels", rec["title_hy"], lang)
            rec[f"institution_group_{lang}"] = d.get("labels", g, lang) if g else None


def _reference_dims(con, d: Dictionary) -> None:
    """Reference dimensions defined in the code with their names in en, ru and hy; the other languages come from
    the dictionary ``reference`` (looked up by the Armenian name)."""
    def names(hy: str, en: str, ru: str) -> dict:
        return {"name_hy": hy, **{f"name_{lang}": {"en": en, "ru": ru}.get(lang) or d.get("reference", hy, lang)
                                  for lang in config.LANGS}}

    insert(con, "dim_doc_type", [{"doc_type": k, **names(hy, en, ru)} for k, (en, ru, hy) in classify.DOC_TYPES.items()])
    insert(con, "dim_period", [{"period": k, "months": months, **names(hy, en, ru)}
                               for k, (months, en, ru, hy) in classify.PERIODS.items()])
    for table, key, items in (("dim_statement", "statement", semantics.KINDS),
                              ("dim_scenario", "scenario", semantics.SCENARIOS),
                              ("dim_budget_part", "budget_part", semantics.PARTS)):
        insert(con, table, [{key: k, **names(hy, en, ru)} for k, (en, ru, hy) in items.items()])
    insert(con, "dim_district", [{"district_code": code, "sort_order": i, **names(hy, en, ru)}
                                 for i, (code, (hy, en, ru, _rx)) in enumerate(reference.DISTRICTS.items())])


def build(db_path: str | None = None) -> Path:
    out = Path(db_path) if db_path else config.DUCKDB_PATH
    tmp = out.with_name(out.stem + ".building.duckdb")
    tmp.unlink(missing_ok=True)
    con = duckdb.connect(str(tmp))
    run_sql_file(con, config.SQL_DIR / "schema.sql")

    pages = read_json(config.CATALOG_DIR / "pages.json", [])
    docs = read_json(config.CATALOG_DIR / "documents.json", [])
    if not docs:
        raise SystemExit("data/catalog/documents.json is empty: run catalog and fetch first")
    dictionary = Dictionary()

    # reference dimensions
    _reference_dims(con, dictionary)
    insert(con, "dim_translation", pd.DataFrame(
        dictionary.records(), columns=["context", "key", "hy", *config.LANGS]).drop_duplicates(["context", "key"]))

    # pages and documents
    insert(con, "meta_page", [{**p, "page_group": p["group"]} for p in pages])
    _title_translations(docs, dictionary)
    insert(con, "meta_document", [{
        **{k: v for k, v in rec.items() if k not in ("links", "members", "size")},
        "doc_group": rec["group"], "size_bytes": rec.get("size"),
        "n_files": len(rec["members"]) if rec.get("members") else (1 if rec.get("sha256") else 0),
        "pages": [ln["page"] for ln in rec["links"]],
    } for rec in docs])

    # files: raw text and cells, budget tables
    meta_files, page_text, stg_all, facts_all = [], [], [], []
    prog_facts, prog_ind, programs, measures = [], [], [], []
    seen_sha: dict[str, str] = {}
    cell_frames = []
    for rec in docs:
        if rec["group"] != "core" or not rec.get("sha256"):
            continue
        for f in files_of(rec):
            mf = {"file_id": f["file_id"], "doc_id": rec["doc_id"], "member": f["member"], "ext": f["ext"],
                  "size_bytes": f.get("size"), "sha256": f.get("sha256")}
            meta_files.append(mf)
            if f["ext"] not in PARSED_EXT or not f.get("sha256"):
                continue
            cache = read_cache(f["sha256"])
            if cache is None:
                mf["extract_error"] = "not extracted (run `python -m yerevan_budget extract`)"
                continue
            mf.update({"kind": cache.get("kind"), "extract_error": cache.get("error"),
                       "legacy_font_conversions": cache.get("legacy_font_conversions"),
                       "glyph_mapped_spans": cache.get("glyph_mapped_spans")})
            if f["sha256"] in seen_sha:
                mf["duplicate_of_file"] = seen_sha[f["sha256"]]
                continue
            seen_sha[f["sha256"]] = f["file_id"]
            kind = cache.get("kind")
            cells = []
            if kind == "pdf":
                mf["n_pages"] = cache["n_pages"]
                mf["n_tables"] = sum(len(p["tables"]) for p in cache["pages"])
                for p in cache["pages"]:
                    page_text.append({"file_id": f["file_id"], "page": p["page"], "text": p["text"],
                                      "n_images": p["n_images"]})
                    for ti, t in enumerate(p["tables"]):
                        for ri, row in enumerate(t["rows"]):
                            for ci, v in enumerate(row):
                                if v is not None and str(v).strip():
                                    cells.append((f["file_id"], p["page"], None, ti, ri, ci, v, None))
            elif kind == "sheet":
                mf["n_sheets"] = mf["n_tables"] = len(cache["sheets"])
                for sh in cache["sheets"]:
                    for r, c, text, num in sh["cells"]:
                        cells.append((f["file_id"], None, sh["name"], sh["index"], r, c, text, num))
            elif kind == "text":
                page_text.append({"file_id": f["file_id"], "page": 1, "text": cache["text"], "n_images": None})
                mf["n_tables"] = len(cache.get("tables", []))
                for ti, t in enumerate(cache.get("tables", [])):
                    for ri, row in enumerate(t["rows"]):
                        for ci, v in enumerate(row):
                            if v and v.strip():
                                cells.append((f["file_id"], None, None, ti, ri, ci, v, None))
            if cells:
                cell_frames.append(pd.DataFrame(cells, columns=["file_id", "page", "sheet", "table_no", "row_no", "col_no",
                                                                "value_text", "value_num"]))
            if kind in ("pdf", "sheet", "text"):
                reader = read_tables(cache)
                rows = bt.assemble(reader)
                stg, facts = interpret(rows, rec, f["file_id"])
                mf["n_rows_parsed"] = len(stg)
                mf["n_unmapped_tables"] = reader.unmapped_tables
                stg_all.extend(stg)
                facts_all.extend(facts)
            if kind in ("pdf", "sheet") and rec["doc_type"] in PROGRAM_DOC_TYPES:
                parsed = program_tables.parse(cache, f["file_id"], rec["fiscal_year"],
                                              n_years=3 if rec["doc_type"] == "mtef" else 1)
                if parsed:
                    base = {"doc_id": rec["doc_id"], "doc_type": rec["doc_type"], "fiscal_year": rec["fiscal_year"]}
                    prog_facts += [{**base, **a} for a in parsed.allocations]
                    prog_ind += [{**base, **i} for i in parsed.indicators]
                    programs += [{**vars(p), "year": rec["fiscal_year"]} for p in parsed.programs.values()]
                    measures += [{**vars(m), "year": rec["fiscal_year"]} for m in parsed.measures.values()]
                    mf["n_rows_parsed"] = (mf.get("n_rows_parsed") or 0) + len(parsed.allocations) + len(parsed.indicators)
                    mf["n_unmapped_tables"] = 0

    insert(con, "meta_file", meta_files)
    insert(con, "raw_page_text", page_text)
    if cell_frames:
        insert(con, "raw_table_cell", pd.concat(cell_frames, ignore_index=True))
    insert(con, "stg_table_row", stg_all)
    insert(con, "fact_budget_line", facts_all)
    insert(con, "fact_program_budget", prog_facts)
    insert(con, "fact_program_indicator", prog_ind)
    _program_dims(con, programs, measures, dictionary)

    # derived dimensions, translations of the facts, views, quality checks
    run_sql_file(con, config.SQL_DIR / "dims.sql")
    _translate_dims(con, dictionary)
    run_sql_file(con, config.SQL_DIR / "views.sql")
    run_sql_file(con, config.SQL_DIR / "qc.sql")
    for row in con.execute("SELECT check_name, status, n_issues FROM qc_summary ORDER BY check_name").fetchall():
        log.info("qc %-40s %-4s %s", *row)
    con.execute("CHECKPOINT")
    con.close()
    tmp.replace(out)
    log.info("database written to %s", out)
    return out


PROGRAM_DOC_TYPES = ("budget_message", "mtef", "budget")


def _program_dims(con, programs: list[dict], measures: list[dict], d: Dictionary) -> None:
    """dim_program / dim_measure: the most recent non-empty name, goal, result, description of every code."""
    def latest(items: list[dict], key, fields) -> list[dict]:
        out: dict = {}
        for it in sorted(items, key=lambda x: x["year"] or 0):
            k = key(it)
            if k is None or None in (k if isinstance(k, tuple) else (k,)):
                continue
            rec = out.setdefault(k, {"first_year": it["year"], "last_year": it["year"]})
            rec["last_year"] = it["year"]
            for f_src, f_dst in fields:
                if it.get(f_src):
                    rec[f_dst] = clean(it[f_src])
        return [{"key": k, **v} for k, v in out.items()]

    progs = latest(programs, lambda p: p["code"], [("name", "name_hy"), ("goal", "goal_hy"), ("result", "result_hy")])
    for p in progs:
        p["program_code"] = p["key"]
        for lang in config.LANGS:
            p[f"name_{lang}"] = d.get("program", p.get("name_hy"), lang)
    insert(con, "dim_program", progs)
    meas = latest(measures, lambda m: (m["program_code"], m["code"]),
                  [("name", "name_hy"), ("description", "description_hy"), ("measure_type", "measure_type_hy")])
    for m in meas:
        m["program_code"], m["measure_code"] = m["key"]
        for lang in config.LANGS:
            m[f"name_{lang}"] = d.get("program", m.get("name_hy"), lang)
    insert(con, "dim_measure", meas)


CONTEXT_OF_STATEMENT = {
    "revenue": "revenue",
    "expenditure_functional": "functional",
    "expenditure_economic": "economic",
    "balance": "financing",
    "financing": "financing",
    "expenditure_program": "program",
}


def _translate_dims(con, d: Dictionary) -> None:
    """Fill the name_<lang> columns of the dimensions and the label translations of the facts."""
    for table, key_cols, ctx_sql in (
            ("dim_functional", ["func_code"], "'functional'"),
            ("dim_economic", ["econ_code"], "'economic'"),
            ("dim_line", ["statement", "line_code"], "statement")):
        rows = con.execute(f"SELECT {', '.join(key_cols)}, {ctx_sql}, name_hy FROM {table}").fetchall()
        upd = []
        for *keys, ctx, name in rows:
            ctx = CONTEXT_OF_STATEMENT.get(ctx, ctx)
            upd.append((*(d.get(ctx, name, lang) for lang in config.LANGS), *keys))
        where = " AND ".join(f"{k} = ?" for k in key_cols)
        sets = ", ".join(f"name_{lang} = ?" for lang in config.LANGS)
        con.executemany(f"UPDATE {table} SET {sets} WHERE {where}", upd)
    # every distinct label of the facts in every language
    labels = con.execute("""
        SELECT DISTINCT statement, label_hy FROM fact_budget_line WHERE label_hy IS NOT NULL
        UNION SELECT DISTINCT 'expenditure_program', program_hy FROM fact_budget_line WHERE program_hy IS NOT NULL
        UNION SELECT DISTINCT CASE WHEN row_type = 'economic' THEN 'expenditure_economic'
                                   WHEN row_type IN ('section', 'group', 'class') THEN 'expenditure_functional'
                                   ELSE 'expenditure_program' END, label_hy
              FROM fact_program_budget WHERE label_hy IS NOT NULL AND row_type NOT IN ('program', 'measure')
    """).fetchall()
    recs = []
    for statement, label in labels:
        ctx = CONTEXT_OF_STATEMENT.get(statement, "labels")
        recs.append({"context": ctx, "label_hy": label,
                     **{f"label_{lang}": d.get(ctx, label, lang) for lang in config.LANGS}})
    label_cols = "".join(f"label_{lang} VARCHAR, " for lang in config.LANGS)
    con.execute(f"CREATE TABLE dim_label (context VARCHAR, label_hy VARCHAR, {label_cols}PRIMARY KEY (context, label_hy))")
    insert(con, "dim_label", pd.DataFrame(recs).drop_duplicates(["context", "label_hy"]))
    con.execute("COMMENT ON TABLE dim_label IS 'Every distinct row name of fact_budget_line (label_hy, program_hy) "
                f"with its translations into {' / '.join(config.LANGS)} (from dim_translation; numbering kept).'")
    con.execute("COMMENT ON COLUMN dim_label.context IS 'Translation context: revenue | functional | economic | "
                "financing | program'")
