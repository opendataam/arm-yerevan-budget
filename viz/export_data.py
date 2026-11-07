"""Export the aggregates used by the visualization mockups (viz/mockups) from the DuckDB database.

Writes viz/mockups/data.js, which sets ``window.BUDGET``: a plain script (not JSON) so that the
mockups also open straight from disk (file://) without a web server.

Usage:
    python viz/export_data.py [--db data/yerevan_budget.duckdb] [--out viz/mockups/data.js]

All amounts are converted from thousand AMD (as in the source documents) to million AMD.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent

# Functional sections (first level of the functional classification) with short English names.
SECTIONS = {
    "01": "General public services",
    "02": "Defence",
    "03": "Public order & safety",
    "04": "Economic affairs",
    "05": "Environmental protection",
    "06": "Housing & community amenities",
    "07": "Health",
    "08": "Recreation, culture & religion",
    "09": "Education",
    "10": "Social protection",
    "11": "Reserve funds",
}

# Revenue groups for the flow diagram: (key, label, line codes added, line codes subtracted)
REVENUE_GROUPS = [
    ("real_estate_tax", "Real estate tax", ["1110"]),
    ("vehicle_tax", "Vehicle property tax", ["1120"]),
    ("local_duties", "Local duties (permits)", ["1130"]),
    ("local_fees", "Local fees (waste, parking, etc.)", ["1350"]),
    ("delegated", "State funds for delegated powers", ["1342"]),
    ("grants", "State budget grants", ["1200"]),
    ("state_duties", "State duties", ["1140"]),
]

# Economic classification groups. "other_current" is the remainder of current expenditures (4050),
# because the 2026 budget decision does not itemise grants, social benefits and other expenses.
ECON_GROUPS = [
    ("wages", "Compensation of employees", "4100"),
    ("goods", "Goods and services", "4200"),
    ("subsidies", "Subsidies to municipal organisations", "4400"),
    ("other_current", "Grants, social benefits and other current", None),
    ("capital", "Capital investment (fixed assets)", "5000"),
    ("asset_sales", "Sale of land and property (offset)", "6000"),
]

# Resident population by district, 2022 census (Statistical Committee of the RA; the twelve figures
# add up to the city total of 1,086,677). Used only for per-resident figures.
POPULATION_2022 = {
    "ajapnyak": 111508, "arabkir": 118870, "avan": 55094, "davtashen": 43704, "erebuni": 124957,
    "kanaker_zeytun": 73834, "kentron": 119841, "malatia_sebastia": 140784, "nork_marash": 11098,
    "nor_nork": 134668, "nubarashen": 11794, "shengavit": 140525,
}

M = 1000.0  # thousand AMD -> million AMD


def mln(v):
    return None if v is None else round(v / M, 1)


def q(con, sql, params=None):
    cur = con.execute(sql, params or [])
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def summary(con):
    rows = q(con, "SELECT * FROM v_summary ORDER BY fiscal_year")
    out = []
    for r in rows:
        out.append({
            "year": r["fiscal_year"],
            "revenue_budget": mln(r["revenue_budget_kamd"]),
            "expenditure_budget": mln(r["expenditure_budget_kamd"]),
            "revenue_approved": mln(r["revenue_approved_kamd"]),
            "revenue_revised": mln(r["revenue_revised_kamd"]),
            "revenue_actual": mln(r["revenue_actual_kamd"]),
            "expenditure_approved": mln(r["expenditure_approved_kamd"]),
            "expenditure_revised": mln(r["expenditure_revised_kamd"]),
            "expenditure_actual": mln(r["expenditure_actual_kamd"]),
        })
    return out


def periods(con):
    """Cumulative execution by reporting period (Q1, H1, 9M, FY): actual vs revised annual plan."""
    rows = q(con, """
        SELECT fiscal_year, report_period, statement,
               max(approved_total_kamd) AS approved, max(revised_total_kamd) AS revised,
               max(actual_total_kamd) AS actual
        FROM v_execution
        WHERE (statement = 'revenue' AND line_code = '1000')
           OR (statement = 'expenditure_functional' AND line_code = '2000')
        GROUP BY ALL ORDER BY 1, 2""")
    return [{
        "year": r["fiscal_year"], "period": r["report_period"],
        "statement": "revenue" if r["statement"] == "revenue" else "expenditure",
        "approved": mln(r["approved"]), "revised": mln(r["revised"]), "actual": mln(r["actual"]),
    } for r in rows]


def functions_by_year(con):
    """Expenditure by functional section: annual reports (approved / revised / actual) + latest budget."""
    rows = q(con, """
        SELECT fiscal_year, left(func_code, 2) AS sec,
               max(approved_total_kamd) AS approved, max(revised_total_kamd) AS revised,
               max(actual_total_kamd) AS actual
        FROM v_execution_annual
        WHERE statement = 'expenditure_functional' AND func_code LIKE '%.0.0'
        GROUP BY ALL ORDER BY 1, 2""")
    out = [{"year": r["fiscal_year"], "section": r["sec"], "source": "report",
            "approved": mln(r["approved"]), "revised": mln(r["revised"]), "actual": mln(r["actual"])}
           for r in rows]
    report_years = {r["fiscal_year"] for r in rows}
    bud = q(con, """
        SELECT fiscal_year, left(func_code, 2) AS sec, max(total_kamd) AS total
        FROM v_budget_approved
        WHERE statement = 'expenditure_functional' AND func_code LIKE '%.0.0'
        GROUP BY ALL ORDER BY 1, 2""")
    for r in bud:
        if r["fiscal_year"] not in report_years:
            out.append({"year": r["fiscal_year"], "section": r["sec"], "source": "budget",
                        "approved": mln(r["total"]), "revised": None, "actual": None})
    return out


def functions_by_period(con):
    """Expenditure by functional section for every reporting period (for the execution tracker)."""
    rows = q(con, """
        SELECT fiscal_year, report_period, left(func_code, 2) AS sec,
               max(approved_total_kamd) AS approved, max(revised_total_kamd) AS revised,
               max(actual_total_kamd) AS actual
        FROM v_execution
        WHERE statement = 'expenditure_functional' AND func_code LIKE '%.0.0' AND fiscal_year >= 2021
        GROUP BY ALL ORDER BY 1, 2, 3""")
    return [{"year": r["fiscal_year"], "period": r["report_period"], "section": r["sec"],
             "approved": mln(r["approved"]), "revised": mln(r["revised"]), "actual": mln(r["actual"])}
            for r in rows]


def classes_by_period(con):
    """Expenditure by functional class for every reporting period since 2021 (execution drill-down)."""
    rows = q(con, """
        SELECT fiscal_year, report_period, func_code,
               max(approved_total_kamd) AS approved, max(revised_total_kamd) AS revised,
               max(actual_total_kamd) AS actual
        FROM v_execution
        WHERE statement = 'expenditure_functional' AND func_code NOT LIKE '%.0' AND fiscal_year >= 2021
        GROUP BY ALL ORDER BY 1, 2, 3""")
    return [{"year": r["fiscal_year"], "period": r["report_period"], "code": r["func_code"],
             "approved": mln(r["approved"]), "revised": mln(r["revised"]), "actual": mln(r["actual"])}
            for r in rows
            if any(r[k] for k in ("approved", "revised", "actual"))]


def hierarchy(con, years):
    """Approved budget: functional section -> class -> programme (budget appendix 6, city total)."""
    out = {}
    for year in years:
        classes = q(con, """
            SELECT func_code, any_value(label_en) AS label, max(total_kamd) AS total
            FROM v_budget_program
            WHERE fiscal_year = ? AND doc_type = 'budget' AND appendix = 6 AND row_type = 'functional'
              AND func_code NOT LIKE '%.0' GROUP BY func_code ORDER BY func_code""", [year])
        progs = q(con, """
            SELECT func_code, label_en, label_hy, total_kamd AS total, seq
            FROM v_budget_program
            WHERE fiscal_year = ? AND doc_type = 'budget' AND appendix = 6 AND row_type = 'program'
            ORDER BY seq""", [year])
        names = {r["func_code"]: r["name_en"] for r in q(con, "SELECT func_code, name_en FROM dim_functional")}
        tree = {}
        for c in classes:
            sec = c["func_code"][:2]
            tree.setdefault(sec, {"code": sec, "name": SECTIONS.get(sec, sec), "children": []})
            tree[sec]["children"].append({
                "code": c["func_code"], "name": names.get(c["func_code"]) or c["label"],
                "total": mln(c["total"]), "children": []})
        by_class = {c["code"]: c for s in tree.values() for c in s["children"]}
        for p in progs:
            cls = by_class.get(p["func_code"])
            if cls is None or p["total"] is None:
                continue
            label = (p["label_en"] or p["label_hy"] or "").strip()
            # programme names are numbered within their class ("15. Passenger transportation ...")
            if ". " in label[:5]:
                label = label.split(". ", 1)[1]
            label = label.lstrip("- ").strip()
            # internal transfer between the administrative and the fund parts: not spending
            if "reserve fund" in label.lower() and "fund" in label.lower().replace("reserve fund", ""):
                continue
            cls["children"].append({"name": label, "total": mln(p["total"])})
        for cls in by_class.values():
            rest = (cls["total"] or 0) - sum(p["total"] for p in cls["children"])
            if rest > 1:  # class amount not broken down into programmes
                cls["children"].append({"name": "Not itemised by programme", "total": round(rest, 1)})
        out[str(year)] = sorted(tree.values(), key=lambda s: s["code"])
    return out


def revenue_groups(con):
    """Revenue by source group: annual report actuals and approved budgets."""
    rep = q(con, """
        SELECT fiscal_year, line_code, max(actual_total_kamd) AS actual, max(approved_total_kamd) AS approved
        FROM v_execution_annual WHERE statement = 'revenue' AND fiscal_year >= 2024
        GROUP BY ALL""")
    bud = q(con, """
        SELECT fiscal_year, line_code, max(total_kamd) AS total
        FROM v_budget_approved WHERE statement = 'revenue' AND fiscal_year >= 2024
        GROUP BY ALL""")
    data = {}
    for r in rep:
        data.setdefault((r["fiscal_year"], "actual"), {})[r["line_code"]] = r["actual"]
    for r in bud:
        data.setdefault((r["fiscal_year"], "approved"), {})[r["line_code"]] = r["total"]
    out = []
    for (year, kind), lines in sorted(data.items()):
        total = lines.get("1000")
        if total is None:
            continue
        groups, used = [], 0.0
        for key, label, codes in REVENUE_GROUPS:
            v = sum(lines.get(c) or 0 for c in codes)
            used += v
            groups.append({"key": key, "label": label, "value": mln(v)})
        groups.append({"key": "other", "label": "Service payments, rent, fines, other", "value": mln(total - used)})
        out.append({"year": year, "kind": kind, "total": mln(total), "groups": groups})
    return out


def economic_by_year(con):
    rep = q(con, """
        SELECT fiscal_year, line_code, max(actual_total_kamd) AS v
        FROM v_execution_annual WHERE statement = 'expenditure_economic'
          AND line_code IN ('4000', '4050', '4100', '4200', '4400', '5000', '6000')
        GROUP BY ALL""")
    bud = q(con, """
        SELECT fiscal_year, line_code, max(total_kamd) AS v
        FROM v_budget_approved WHERE statement = 'expenditure_economic'
          AND line_code IN ('4000', '4050', '4100', '4200', '4400', '5000', '6000')
        GROUP BY ALL""")
    lines = {}
    for r in rep:
        lines.setdefault((r["fiscal_year"], "actual"), {})[r["line_code"]] = r["v"]
    report_years = {y for (y, _) in lines}
    for r in bud:
        if r["fiscal_year"] not in report_years:
            lines.setdefault((r["fiscal_year"], "approved"), {})[r["line_code"]] = r["v"]
    out = []
    for (year, kind), ln in sorted(lines.items()):
        if any(ln.get(c) is None for c in ("4000", "4050", "4100", "4200", "4400", "5000")):
            continue  # incomplete table (2020 report)
        rec = {"year": year, "kind": kind, "total": mln(ln["4000"])}
        for key, _label, code in ECON_GROUPS:
            if key == "other_current":
                v = ln["4050"] - ln["4100"] - ln["4200"] - ln["4400"]
            else:
                v = ln.get(code) or 0
            rec[key] = mln(v)
        out.append(rec)
    return out


def districts(con, years):
    """Approved budget by administrative district (budget appendix 7): sections and classes."""
    rows = q(con, """
        SELECT b.fiscal_year, b.district_code, b.func_code, max(b.total_kamd) AS total
        FROM v_budget_program b
        WHERE b.doc_type = 'budget' AND b.appendix = 7 AND b.row_type = 'functional'
          AND b.fiscal_year IN (SELECT unnest(?::INTEGER[]))
        GROUP BY ALL ORDER BY 1, 2, 3""", [list(years)])
    out = {}
    for r in rows:
        d = out.setdefault(str(r["fiscal_year"]), {}).setdefault(r["district_code"], {"sections": {}, "classes": {}})
        fc = r["func_code"]
        if fc.endswith(".0.0"):
            d["sections"][fc[:2]] = mln(r["total"])
        elif not fc.endswith(".0"):
            d["classes"][fc] = mln(r["total"])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=str(ROOT / "data" / "yerevan_budget.duckdb"))
    ap.add_argument("--out", default=str(ROOT / "viz" / "mockups" / "data.js"))
    args = ap.parse_args()

    con = duckdb.connect(args.db, read_only=True)
    years = [2024, 2025, 2026]
    names = q(con, "SELECT func_code, name_en FROM dim_functional WHERE level = 'class'")
    dist = q(con, "SELECT district_code, name_en, name_hy, sort_order FROM dim_district ORDER BY sort_order")
    data = {
        "generated": dt.date.today().isoformat(),
        "unit": "million AMD",
        "source": "Yerevan Municipality, Finance section (yerevan.am/hy/finance); opendataam/arm-yerevan-budget",
        "sections": SECTIONS,
        "class_names": {r["func_code"]: r["name_en"] for r in names},
        "district_names": [{"code": r["district_code"], "name": r["name_en"], "name_hy": r["name_hy"]} for r in dist],
        "econ_groups": [{"key": k, "label": label} for k, label, _ in ECON_GROUPS],
        "summary": summary(con),
        "periods": periods(con),
        "functions_by_year": functions_by_year(con),
        "functions_by_period": functions_by_period(con),
        "classes_by_period": classes_by_period(con),
        "population_2022": POPULATION_2022,
        "hierarchy": hierarchy(con, years),
        "revenue": revenue_groups(con),
        "economic": economic_by_year(con),
        "districts": districts(con, years),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    out.write_text("/* generated by viz/export_data.py, do not edit */\nwindow.BUDGET = " + body + ";\n",
                   encoding="utf-8")
    print(f"{out}: {out.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
