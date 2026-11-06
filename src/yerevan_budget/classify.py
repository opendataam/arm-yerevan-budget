"""Classification of the documents by their link text: type, fiscal year, reporting period.

The site gives every document only as a link with an Armenian title. The rules
below turn the title into

* ``doc_type`` – see :data:`DOC_TYPES`;
* ``fiscal_year`` – the budget year the document is about (for medium-term
  programmes: the first year of the three);
* ``period`` – for execution reports: ``Q1`` (January–March), ``H1``
  (January–June), ``9M`` (January–September), ``FY`` (the year).

The rules are checked by ``tests/test_classify.py`` against all titles of the
catalog; exceptions can be listed in :data:`OVERRIDES` (key: ``doc_id``).
"""

from __future__ import annotations

import re

# doc_type -> (English, Russian, Armenian) names
DOC_TYPES: dict[str, tuple[str, str, str]] = {
    "budget": ("Budget of the city (council decision with appendices)",
               "Бюджет города (решение Совета старейшин с приложениями)",
               "Երևան քաղաքի բյուջե (ավագանու որոշում՝ հավելվածներով)"),
    "budget_draft": ("Draft budget submitted to public discussion",
                     "Проект бюджета, представленный на общественное обсуждение",
                     "Հանրային քննարկման ներկայացված բյուջեի նախագիծ"),
    "budget_amendment": ("Amendment of the budget (council decision)",
                         "Изменение бюджета (решение Совета старейшин)",
                         "Բյուջեում փոփոխություններ (ավագանու որոշում)"),
    "budget_message": ("Budget message of the Mayor",
                       "Бюджетное послание мэра",
                       "Քաղաքապետի բյուջետային ուղերձ"),
    "execution_measures": ("Measures ensuring the execution of the budget (Mayor's decision)",
                           "Меры по обеспечению исполнения бюджета (решение мэра)",
                           "Բյուջեի կատարումն ապահովող միջոցառումներ (քաղաքապետի որոշում)"),
    "execution_report": ("Budget execution report",
                         "Отчёт об исполнении бюджета",
                         "Բյուջեի կատարման հաշվետվություն"),
    "report_approval": ("Council decision approving the execution report",
                        "Решение Совета старейшин об утверждении отчёта об исполнении",
                        "Կատարման հաշվետվությունը հաստատելու մասին ավագանու որոշում"),
    "mtef": ("Medium-term expenditure programme",
             "Среднесрочная программа расходов",
             "Միջնաժամկետ ծախսերի ծրագիր"),
    "citizens_budget": ("Citizens' budget (summary for the public)",
                        "Гражданский бюджет (краткое изложение для граждан)",
                        "Բյուջե՝ բոլորի համար (ամփոփ տեղեկագիր)"),
    "staff_list": ("Staff list of the Municipality",
                   "Штатное расписание мэрии",
                   "Քաղաքապետարանի հաստիքացուցակ"),
    "other": ("Other document", "Прочий документ", "Այլ փաստաթուղթ"),
    "institution_estimate": ("Budget estimates of municipal institutions",
                             "Сметы муниципальных учреждений", "Նախահաշիվներ"),
    "institution_revised_estimate": ("Revised budget estimates of municipal institutions",
                                     "Уточнённые сметы муниципальных учреждений", "Ճշտված նախահաշիվներ"),
    "institution_execution": ("Actual execution of municipal institutions",
                              "Фактическое исполнение смет муниципальных учреждений", "Փաստացի կատարողական"),
    "institution_staff_list": ("Staff lists of municipal institutions",
                               "Штатные расписания муниципальных учреждений", "Հաստիքացուցակներ"),
    "institution_report": ("Financial reports of municipal institutions",
                           "Финансовые отчёты муниципальных учреждений", "Ֆինանսական հաշվետվություններ"),
    "institution_other": ("Other documents of municipal institutions",
                          "Прочие документы муниципальных учреждений", "Այլ փաստաթղթեր"),
}

PERIODS: dict[str, tuple[int, str, str, str]] = {
    # code -> (months, English, Russian, Armenian)
    "Q1": (3, "January–March", "январь–март", "հունվար–մարտ"),
    "H1": (6, "January–June", "январь–июнь", "հունվար–հունիս"),
    "9M": (9, "January–September", "январь–сентябрь", "հունվար–սեպտեմբեր"),
    "FY": (12, "Year", "год", "տարի"),
}

# doc_id -> fields that override the rules (titles that do not follow the patterns)
OVERRIDES: dict[str, dict] = {}

_YEAR = r"(20\d\d)"


def _has(t: str, *words: str) -> bool:
    return any(w in t for w in words)


def period_of(title: str) -> str | None:
    t = title.lower()
    if _has(t, "առաջին եռամսյակ", "3 ամսվա", "31.03", "-31.03"):
        return "Q1"
    if _has(t, "կիսամյակ", "երկրորդ եռամսյակ", "30.06"):
        return "H1"
    if _has(t, "9 ամի", "9 ամս", "ինն ամս", "30.09"):
        return "9M"
    if _has(t, "տարեկան", "31.12", "կատարման հաշվետվություն", "կատարման վերաբերյալ հաշվետվություն"):
        return "FY"
    return None


def year_of(title: str, doc_type: str) -> int | None:
    t = title
    pats = [
        rf"{_YEAR}\s*[-–]\s*20\d\d\s*թ",               # 2027-2029 թվականների (MTEF: first year)
        rf"քաղաքի\s+{_YEAR}\s*թ",                       # Երևան քաղաքի 2026 թվականի ...
        rf"քաղաքապետի\s+{_YEAR}\s*թ",                   # Երևանի քաղաքապետի 2026 թվականի ուղերձ
        rf"Բյուջե\s+{_YEAR}",                            # Երևանի Բյուջե 2018
        rf"համար\s+{_YEAR}",                             # Բյուջե՝ բոլորի համար 2026
        rf"\d\d\.\d\d\.{_YEAR}\s*թ?\.?\s*[-–]",          # 01.01.2026 - ...
        rf"\d\d\.\d\d\.{_YEAR}",                         # 31.12.2025
        rf"^{_YEAR}\s*թ",                                # 2025թ. տարեկան հաշվետվություն
        rf"{_YEAR}\s*թվականի\s+(?:առաջին|3|9|ինն|երկրորդ)",
        rf"{_YEAR}\s*թ",
    ]
    if doc_type == "report_approval":
        pats.insert(0, rf"«Երևան քաղաքի\s+{_YEAR}")
    for p in pats:
        m = re.search(p, t)
        if m:
            return int(m.group(1))
    return None


def classify(title: str, page_year: int | None = None, group: str = "core", heading_year: int | None = None,
             group_heading: str | None = None) -> dict:
    """``doc_type``, ``fiscal_year`` and ``period`` of a document from its link text."""
    t = title.strip()
    tl = t.lower()
    if group == "institutions":
        if "ճշտված" in tl:
            dt = "institution_revised_estimate"
        elif "նախահաշիվ" in tl:
            dt = "institution_estimate"
        elif "կատարողական" in tl:
            dt = "institution_execution"
        elif "հաստիք" in tl:
            dt = "institution_staff_list"
        elif "հաշվետվություն" in tl:
            dt = "institution_report"
        else:
            dt = "institution_other"
        m = re.search(_YEAR, t)
        return {"doc_type": dt, "fiscal_year": heading_year or (int(m.group(1)) if m else None),
                "period": period_of(t) if dt == "institution_report" else None}

    if _has(tl, "բյուջետային ուղերձ"):
        dt = "budget_message"
    elif _has(tl, "կատարումն ապահովող"):
        dt = "execution_measures"
    elif _has(tl, "միջնաժամկետ"):
        dt = "mtef"
    elif _has(tl, "հաշվետվությունը հաստատելու"):
        dt = "report_approval"
    elif _has(tl, "փոփոխություններ կատարելու"):
        dt = "budget_amendment"
    elif _has(tl, "հաստիք"):
        dt = "staff_list"
    elif _has(tl, "բոլորի համար", "ամփոփ տեղեկագիր"):
        dt = "citizens_budget"
    elif _has(tl, "հաշվետվություն"):
        dt = "execution_report"
    elif _has(tl, "նախագիծ") and _has(tl, "բյուջե"):
        dt = "budget_draft"
    elif re.search(r"բյուջե(?:ն|ի հավելվածներ)?\b|բյուջեն հաստատելու|բյուջեի մասին", tl) or tl.endswith("բյուջե"):
        dt = "budget"
    else:
        dt = "other"
    year = year_of(t, dt)
    if dt == "budget_amendment" and page_year:
        year = page_year  # amendments of the budget of the year of the archive page
    if year is None:
        year = page_year
    period = period_of(t) if dt == "execution_report" else None
    if dt == "execution_report" and period is None:
        period = "FY"
    return {"doc_type": dt, "fiscal_year": year, "period": period}
