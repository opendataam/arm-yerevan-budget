"""Meaning of the rows and amount columns of the budget tables.

* :func:`table_kind` – which statement a row belongs to (revenues, expenditures by
  functional / economic classification, balance, financing of the deficit, or
  the detailed "functional class × programme × economic article" tables);
* :func:`amount_semantics` – for every amount column: scenario (approved plan,
  revised plan, actual, forecast, ...), the year and period it refers to and the
  part of the budget (total / administrative / fund).

The forms number their lines the same way in all documents (Տողի NN):
1000–1399 revenues, 2000–3999 expenditures by functional classification,
4000–6999 expenditures by economic classification, 7000 surplus / deficit,
8000–8999 financing of the deficit. In the appendices of the budget decision
the surplus / deficit line is numbered 8000 and the financing total 8010.
"""

from __future__ import annotations

import re

KINDS = {
    # kind -> (English, Russian, Armenian)
    "revenue": ("Revenues", "Доходы", "Եկամուտներ"),
    "expenditure_functional": ("Expenditures by functional classification",
                               "Расходы по функциональной классификации",
                               "Ծախսերն ըստ գործառական դասակարգման"),
    "expenditure_economic": ("Expenditures by economic classification",
                             "Расходы по экономической классификации",
                             "Ծախսերն ըստ տնտեսագիտական դասակարգման"),
    "balance": ("Surplus or deficit", "Профицит или дефицит", "Հավելուրդ կամ դեֆիցիտ"),
    "financing": ("Financing of the deficit (use of the surplus)",
                  "Источники финансирования дефицита (направления использования профицита)",
                  "Դեֆիցիտի ֆինանսավորման աղբյուրները (հավելուրդի օգտագործման ուղղությունները)"),
    "expenditure_program": ("Expenditures by functional class, programme and economic article",
                            "Расходы по функциональным классам, программам и экономическим статьям",
                            "Ծախսերն ըստ գործառական դասերի, ծրագրերի և տնտեսագիտական հոդվածների"),
}

SCENARIOS = {
    "approved": ("Approved annual plan", "Утверждённый годовой план", "Տարեկան հաստատված պլան"),
    "revised": ("Revised annual plan", "Уточнённый годовой план", "Տարեկան ճշտված պլան"),
    "actual": ("Actual (executed)", "Фактическое исполнение", "Փաստացի"),
    "draft": ("Draft budget", "Проект бюджета", "Բյուջեի նախագիծ"),
    "forecast": ("Medium-term forecast", "Среднесрочный прогноз", "Միջնաժամկետ կանխատեսում"),
    "plan_period": ("Plan for the period (cumulative from the start of the year)",
                    "План на период (нарастающим итогом с начала года)",
                    "Պլան՝ ժամանակահատվածի համար (տարեսկզբից աճողական)"),
    "change": ("Change of the plan (amendment)", "Изменение плана (поправка)", "Պլանի փոփոխություն"),
    "unknown": ("Not identified", "Не определено", "Չի որոշված"),
}

PARTS = {
    "total": ("Total", "Всего", "Ընդամենը"),
    "admin": ("Administrative part", "Административная часть", "Վարչական մաս"),
    "fund": ("Fund (capital) part", "Фондовая часть", "Ֆոնդային մաս"),
}


def line_kind(line_code: str | None, label: str | None) -> str | None:
    """Statement of a row from its line code (None if the code does not tell)."""
    if not line_code or not line_code.isdigit():
        return None
    n = int(line_code)
    if len(line_code) == 5:  # 11301.., 13501..: sub-lines of local duties and fees
        n = int(line_code[:4])
    lab = (label or "").upper()
    if 1000 <= n < 2000:
        return "revenue"
    if 2000 <= n < 4000:
        return "expenditure_functional"
    if 4000 <= n < 7000:
        return "expenditure_economic"
    if n == 7000:
        return "balance"
    if n == 8000 and ("ՀԱՎԵԼՈՒՐԴ" in lab or "ԴԵՖԻՑԻՏ" in lab or "ՊԱԿԱՍՈՒՐԴ" in lab):
        return "balance"
    if 8000 <= n < 9000:
        return "financing"
    return None


def table_kind(kinds: set[str], line_code: str | None, label: str | None, prev: str | None) -> str | None:
    """Statement of a row: the layout decides for the detailed tables, otherwise the line code."""
    if "func" in kinds and "class" in kinds:
        return "expenditure_program"
    if "func" in kinds:
        return "expenditure_functional"
    return line_kind(line_code, label) or prev


def row_type(kind: str, line_code, func, class_code, label) -> str:
    """Type of a row inside a statement: total / functional / program / economic / line."""
    if kind == "expenditure_program":
        if class_code and class_code.isdigit():
            return "economic"
        if any(func):
            return "functional"
        if label and re.match(r"^\s*ԸՆԴԱՄԵՆԸ", label):
            return "total"
        return "program"
    return "line"


# matched on the header text with all whitespace removed (PDF extraction splits words: 'տ արի')
_PART = [("admin", re.compile(r"վարչական")), ("fund", re.compile(r"ֆոնդային")),
         ("total", re.compile(r"[Ըը]նդամենը"))]
_SCEN = [("approved", re.compile(r"հաստատված")), ("revised", re.compile(r"ճշտված")),
         ("actual", re.compile(r"[Փփ]աստ"))]
_YEAR = re.compile(r"(20\d\d)թ")
_PERIOD = [("Q1", re.compile(r"1-?ինեռամսյակ|Iեռամսյակ|առաջինեռամսյակ")),
           ("H1", re.compile(r"կիսամյակ")),
           ("9M", re.compile(r"9ամիս|իննամիս")),
           ("FY", re.compile(r"տարի|տարեկան"))]


def amount_semantics(doc_type: str, headers: list[str], fiscal_year: int | None, period: str | None) -> list[dict]:
    """Meaning of each amount column of a table (``headers``: header text of the columns, left to right)."""
    n = len(headers)
    out = []
    scen = year = per = cur_part = None
    for i, h in enumerate(headers):
        h = re.sub(r"[\s\-\u00ad\u2010\u2011]+", "", h or "")  # 'վարչա - կան' -> 'վարչական'
        part = next((p for p, rx in _PART if rx.search(h)), None)
        if part is not None:
            cur_part = part
        elif cur_part is not None:
            part = cur_part
        elif n % 3 == 0:
            part = ("total", "admin", "fund")[i % 3]
        s = next((s for s, rx in _SCEN if rx.search(h)), None)
        y = _YEAR.search(h)
        p = next((p for p, rx in _PERIOD if rx.search(h)), None)
        if s:
            scen = s
        if y:
            year = int(y.group(1))
        if p:
            per = p
        out.append({"part": part or "total", "scenario": scen, "year": year, "period": per, "header": headers[i]})

    # every group of three columns of these forms is total / administrative / fund part
    if doc_type in ("execution_report", "mtef", "budget", "budget_draft", "budget_amendment") and n % 3 == 0:
        for g in range(0, n, 3):
            if [o["part"] for o in out[g:g + 3]] != ["total", "admin", "fund"]:
                for k, part in enumerate(("total", "admin", "fund")):
                    out[g + k]["part"] = part
    if doc_type == "execution_report":
        default = ["approved", "revised", "actual"]
        for i, o in enumerate(out):
            if o["scenario"] is None and n == 9:
                o["scenario"] = default[i // 3]
            o["year"] = fiscal_year
            o["period"] = period if o["scenario"] == "actual" else "FY"
    elif doc_type in ("budget", "budget_draft", "budget_amendment"):
        for o in out:
            o["scenario"] = {"budget_draft": "draft", "budget_amendment": "change"}.get(doc_type) or o["scenario"] or "approved"
            o["year"] = o["year"] or fiscal_year
            o["period"] = "FY"
    elif doc_type == "mtef":
        for i, o in enumerate(out):
            o["scenario"] = "forecast"
            if o["year"] is None and fiscal_year:
                o["year"] = fiscal_year + (i // 3 if n % 3 == 0 else i)
            o["period"] = "FY"
    elif doc_type == "execution_measures":
        for o in out:
            o["scenario"] = "plan_period" if o["period"] in ("Q1", "H1", "9M") else "approved"
            o["year"] = fiscal_year
            o["period"] = o["period"] or "FY"
    else:
        for o in out:
            o["scenario"] = o["scenario"] or "unknown"
            o["year"] = o["year"] or fiscal_year
            o["period"] = o["period"] or "FY"
    return out
