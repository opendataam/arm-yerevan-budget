"""Translation dictionaries Armenian -> English / Russian.

The dictionaries are CSV files ``data/translations/<context>.csv`` with the
columns ``hy,en,ru`` (UTF-8), versioned in git. The build loads them into
``dim_translation`` and looks names up by the Armenian text compared with
:func:`norm_key` (letters and digits only), so differences in punctuation,
spacing and case do not matter.

Contexts:

* ``revenue``    – revenue lines (types of taxes, duties, fees, grants, ...);
* ``functional`` – sections, groups and classes of the functional classification;
* ``economic``   – lines and articles of the economic classification;
* ``financing``  – lines of the surplus / deficit and its financing;
* ``program``    – programmes and measures (detailed tables of the budget);
* ``labels``     – everything else: document titles, table titles, districts.

List numbering at the start of a name (``1.1``, ``ա)``, ``Ա.``, ``-``) is not
part of the key: it is split off before the lookup and put back afterwards.

Workflow for new names (e.g. after a new budget year is published)::

    python -m yerevan_budget build          # names without a translation: qc_missing_translation
    python -m yerevan_budget translations   # -> data/translations/pending/<context>.csv
    # fill the en and ru columns (by hand or with a machine translation, then review)
    python -m yerevan_budget translations --merge
    python -m yerevan_budget build
"""

from __future__ import annotations

import csv
import logging
import re
from pathlib import Path

from . import config
from .parsers.common import clean, norm_key

log = logging.getLogger(__name__)

CONTEXTS = ("revenue", "functional", "economic", "financing", "program", "labels")
FIELDS = ["hy", "en", "ru"]
PENDING_DIR = config.TRANSLATIONS_DIR / "pending"

# list numbering at the start of a label: '1.', '1.1', '1.1.', '2.3.1.1', 'ա)', 'Ա.', '-', '1)'
_ENUM = re.compile(r"^\s*((?:\d{1,2}\.)+\d{0,2}\.?|\d{1,2}\)|[ա-ֆ]\)|[Ա-Ֆ]\.|[-–])\s*(?=\S)")
# formulas of the forms: '(տող 1110 + տող 1120)', '(ս.5+ս.6)'
_FORMULA = re.compile(r"\(\s*(?:տող|ս\.)[^()]*\)\s*,?")


def split_enum(label: str | None) -> tuple[str, str]:
    """('1.1', 'Գույքային հարկեր') from '1.1 Գույքային հարկեր'."""
    t = clean(label)
    m = _ENUM.match(t)
    if m:
        return m.group(1), t[m.end():].strip()
    return "", t


def strip_formula(label: str | None) -> str:
    t = _FORMULA.sub(" ", clean(label))
    t = re.sub(r"\s*[,]?\s*(այդ\s*թվում|որից)\s*[`՝':]?\s*$", "", clean(t))
    t = re.sub(r"^(այդ\s*թվում|որից)\s*[`՝':]\s*", "", t)
    return clean(t).rstrip(",")


def path(context: str) -> Path:
    return config.TRANSLATIONS_DIR / f"{context}.csv"


def read_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return [{k: (r.get(k) or "").strip() for k in FIELDS} for r in csv.DictReader(f)]


def write_csv(p: Path, rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(p)


class Dictionary:
    """All translations, looked up by context and normalised Armenian text."""

    def __init__(self) -> None:
        self.rows: dict[str, list[dict]] = {c: read_csv(path(c)) for c in CONTEXTS}
        self.index: dict[tuple[str, str], dict] = {}
        self.any: dict[str, dict] = {}
        for c, rows in self.rows.items():
            for r in rows:
                if r["hy"] and (r["en"] or r["ru"]):
                    k = norm_key(r["hy"])
                    self.index[(c, k)] = r
                    self.any.setdefault(k, r)

    def lookup(self, context: str, text: str | None) -> dict | None:
        k = norm_key(text)
        return self.index.get((context, k)) or self.any.get(k) if k else None

    def get(self, context: str, hy: str | None, lang: str) -> str | None:
        """Translation of a label, keeping its list numbering."""
        if not hy:
            return None
        enum, text = split_enum(hy)
        r = self.lookup(context, text)
        if not r or not r[lang]:
            return None
        return f"{enum} {r[lang]}".strip() if enum else r[lang]

    def records(self) -> list[tuple[str, str, str, str | None, str | None]]:
        return [(c, norm_key(r["hy"]), r["hy"], r["en"] or None, r["ru"] or None)
                for c, rows in self.rows.items() for r in rows if r["hy"]]


def write_pending(db_path: Path | None = None) -> None:
    """Names without a translation (from ``qc_missing_translation``) -> data/translations/pending/<context>.csv."""
    import duckdb

    con = duckdb.connect(str(db_path or config.DUCKDB_PATH), read_only=True)
    rows = con.execute("SELECT context, hy FROM qc_missing_translation ORDER BY context, hy").fetchall()
    con.close()
    by_ctx: dict[str, list[dict]] = {}
    for ctx, hy in rows:
        by_ctx.setdefault(ctx, []).append({"hy": hy, "en": "", "ru": ""})
    for ctx, items in by_ctx.items():
        write_csv(PENDING_DIR / f"{ctx}.csv", items)
        log.info("pending %s: %d names -> %s", ctx, len(items), PENDING_DIR / f"{ctx}.csv")
    if not by_ctx:
        log.info("every name has a translation")


def merge_pending() -> None:
    """Merge filled rows of data/translations/pending/*.csv into the dictionaries (rows without en/ru are kept pending)."""
    for p in sorted(PENDING_DIR.glob("*.csv")):
        ctx = p.stem.split("-")[0]
        if ctx not in CONTEXTS:
            log.warning("unknown context %s (%s)", ctx, p)
            continue
        new = read_csv(p)
        done = [r for r in new if r["hy"] and r["en"] and r["ru"]]
        left = [r for r in new if r not in done]
        rows = read_csv(path(ctx))
        known = {norm_key(r["hy"]): i for i, r in enumerate(rows)}
        for r in done:
            k = norm_key(r["hy"])
            if k in known:
                rows[known[k]] = r
            else:
                known[k] = len(rows)
                rows.append(r)
        write_csv(path(ctx), rows)
        if left:
            write_csv(p, left)
        else:
            p.unlink()
        log.info("%s: merged %d, %d left pending", ctx, len(done), len(left))
