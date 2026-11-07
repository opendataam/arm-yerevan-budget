"""Unit tests of the parsers: legacy fonts, values, column layouts, page links, classification."""

from yerevan_budget import classify, reference
from yerevan_budget.parsers import armscii, semantics
from yerevan_budget.parsers import budget_tables as bt
from yerevan_budget.parsers.common import code_str, parse_amount
from yerevan_budget.parsers.pages import normalize_url, size_hint
from yerevan_budget.translations import split_enum, strip_formula


def test_armscii_to_unicode():
    assert armscii.fix("Ð³í»Éí³Í") == "Հավելված"
    assert armscii.fix("ºñ¨³Ý") == "Երևան"
    assert armscii.fix("(Ñ³½³ñ ¹ñ³ÙÝ»ñáí)") == "(հազար դրամներով)"


def test_armscii_leaves_unicode_alone():
    for s in ("«Երևան» 2026", "Yerevan «city»", "1,234.5", "X", None):
        assert armscii.fix(s) == s


def test_parse_amount():
    assert parse_amount("159,399,554.2") == (159399554.2, None)
    assert parse_amount("(87,805.5)") == (-87805.5, None)
    assert parse_amount("-30,319.1") == (-30319.1, None)
    assert parse_amount("1 4 , 4 27,068.9") == (14427068.9, None)
    assert parse_amount("X") == (None, "na")
    assert parse_amount("-") == (0.0, "dash")
    assert parse_amount("") == (None, None)
    assert parse_amount("տող") == (None, "text")


def test_code_str():
    assert code_str("1112.0") == "1112"
    assert code_str(" 7100 ") == "7100"
    assert code_str("") is None


def test_numbering_row():
    assert bt.numbering_row(["1", "2", "3", "4", "5"]) == [0, 1, 2, 3, 4]
    assert bt.numbering_row(["1", "", "2", "3", "4", "5", "", "", "6"]) == [0, 2, 3, 4, 5, 8]
    assert bt.numbering_row(["1.0", "2.0", "3.0", "4.0"]) == [0, 1, 2, 3]
    # hidden columns of the form, numbers split by the PDF extraction
    assert bt.numbering_row(["1", "2", "3", "10", "11", "12"]) == [0, 1, 2, 3, 4, 5]
    assert bt.numbering_row(["1", "2", "3", "10", "11", "1", "2"]) == [0, 1, 2, 3, 4, 5]
    assert bt.numbering_row(["1", "2", "3", "4", "=SUM(R[2]C,R[62]C)", "6", "7"]) == [0, 1, 2, 3, 4, 5, 6]
    assert bt.numbering_row(["1000", "ԸՆԴԱՄԵՆԸ", "1", "2"]) is None
    assert bt.numbering_row(["1", "2", "3"]) is None


def _rows(table):
    reader = bt.TableReader()
    reader.add_table(table, 1, {})
    return bt.assemble(reader)


def test_table_reader_h9_revenue():
    rows = _rows([
        ["Տողի NN", "Եկամտատեսակները", "Հոդվածի NN", "Տարեկան հաստատված պլան", "", ""],
        ["", "", "", "Ընդամենը", "վարչական մաս", "ֆոնդային մաս"],
        ["1", "2", "3", "4", "5", "6"],
        ["1000", "ԸՆԴԱՄԵՆԸ ԵԿԱՄՈՒՏՆԵՐ (տող 1100 + տող 1200)", "", "100.0", "90.0", "10.0"],
        ["", "այդ թվում`", "", "", "", ""],
        ["1100", "1. ՀԱՐԿԵՐ ԵՎ ՏՈՒՐՔԵՐ", "7100", "60.0", "60.0", "X"],
        ["", "շարունակություն", "", "", "", ""],
    ])
    assert [r.line_code for r in rows] == ["1000", "1100"]
    assert rows[1].class_code == "7100"
    assert rows[1].label == "1. ՀԱՐԿԵՐ ԵՎ ՏՈՒՐՔԵՐ շարունակություն"
    assert [a[1] for a in rows[0].amounts] == [100.0, 90.0, 10.0]
    assert rows[1].amounts[2][2] == "na"


def test_table_reader_split_line_code_and_func():
    rows = _rows([
        ["1", "", "2", "3", "4", "5", "6", "7", "8"],
        ["2", "100", "01", "0", "0", "ԸՆԴՀԱՆՈՒՐ ԲՆՈՒՅԹԻ ՀԱՆՐԱՅԻՆ ԾԱՌԱՅՈՒԹՅՈՒՆՆԵՐ", "14,617,191.7", "12,377,749.8", "2,239,441.9"],
    ])
    assert rows[0].line_code == "2100"
    assert rows[0].func == ("01", "0", "0")


def test_semantics_h9():
    headers = ["Տարեկան հաստատված պլան | Ընդամենը", "այդ թվում` | վարչական մաս", "ֆոնդային մաս",
               "Տարեկան ճշտված պլան | Ընդամենը", "վարչական մաս", "ֆոնդային մաս",
               "Փաստացի | Ընդամենը", "վարչական մաս", "ֆոնդային մաս"]
    sem = semantics.amount_semantics("execution_report", headers, 2025, "H1")
    assert [(s["scenario"], s["part"]) for s in sem[:4]] == [
        ("approved", "total"), ("approved", "admin"), ("approved", "fund"), ("revised", "total")]
    assert sem[6]["period"] == "H1" and sem[0]["period"] == "FY"


def test_semantics_measures_and_mtef():
    h = ["Ընդամենը", "վարչական բյուջե | տարի", "1-ին եռամսյակ", "1-ին կիսամյակ", "9 ամիս",
         "ֆոնդային բյուջե | տ արի", "1-ին եռամսյակ", "1-ին կիսամյակ", "9 ամիս"]
    sem = semantics.amount_semantics("execution_measures", h, 2026, None)
    assert [(s["part"], s["period"]) for s in sem] == [
        ("total", "FY"), ("admin", "FY"), ("admin", "Q1"), ("admin", "H1"), ("admin", "9M"),
        ("fund", "FY"), ("fund", "Q1"), ("fund", "H1"), ("fund", "9M")]
    h = ["2027 թվական | Ընդամենը", "վարչական", "ֆոնդային", "2028 թվական | Ընդամենը", "վարչական", "ֆոնդային",
         "2029 թվական | Ընդամենը", "վարչական", "ֆոնդային"]
    assert [s["year"] for s in semantics.amount_semantics("mtef", h, 2027, None)][::3] == [2027, 2028, 2029]


def test_line_kind():
    assert semantics.line_kind("11301", None) == "revenue"
    assert semantics.line_kind("2911", None) == "expenditure_functional"
    assert semantics.line_kind("5113", None) == "expenditure_economic"
    assert semantics.line_kind("8000", "ԸՆԴԱՄԵՆԸ ՀԱՎԵԼՈՒՐԴԸ ԿԱՄ ԴԵՖԻՑԻՏԸ") == "balance"
    assert semantics.line_kind("8000", "ԸՆԴԱՄԵՆԸ`") == "financing"


def test_classify_titles():
    c = classify.classify("2019թ. 9 ամիսների հաշվետվություն")
    assert (c["doc_type"], c["fiscal_year"], c["period"]) == ("execution_report", 2019, "9M")
    c = classify.classify("Հաշվետվություն համայնքի բյուջեի կատարման վերաբերյալ՝ 01.01 2026թ.-30.06.2026թ. ժամանակահատվածի համար")
    assert (c["doc_type"], c["fiscal_year"], c["period"]) == ("execution_report", 2026, "H1")
    c = classify.classify("Երևան քաղաքի 2027-2029 թվականների միջնաժամկետ ծախսերի ծրագիրը հաստատելու մասին")
    assert (c["doc_type"], c["fiscal_year"]) == ("mtef", 2027)
    assert classify.classify("Երևան քաղաքի 2026 թվականի բյուջեի հավելվածներ")["doc_type"] == "budget"
    assert classify.classify("Երևանի քաղաքապետի 2026 թվականի բյուջետային ուղերձ")["doc_type"] == "budget_message"
    c = classify.classify("Ճշտված նախահաշիվներ", group="institutions", heading_year=2015)
    assert (c["doc_type"], c["fiscal_year"]) == ("institution_revised_estimate", 2015)


def test_pages_helpers():
    assert size_hint("Նախահաշիվներ / ներբեռնել՝ 31 Mb/") == ("Նախահաշիվներ", 31.0)
    assert size_hint("Հաստիքացուցակ / ներբեռնել՝ 512 կբ/") == ("Հաստիքացուցակ", 0.5)
    assert normalize_url("/edfiles/Financedocs/a b.rar") == "https://www.yerevan.am/edfiles/Financedocs/a%20b.rar"
    assert normalize_url("http://budget.yerevan.am/") == "http://budget.yerevan.am/"


def test_districts():
    assert reference.district_of("ԵՐԵՎԱՆԻ 2025 ԹՎԱԿԱՆԻ ԲՅՈՒՋԵԻ ... ԱՋԱՓՆՅԱԿ ՎԱՐՉԱԿԱՆ ՇՐՋԱՆԻ ՄԱՍՈՎ") == "ajapnyak"
    assert reference.district_of("ՆՈՐՔ-ՄԱՐԱՇ ՎԱՐՉԱԿԱՆ ՇՐՋԱՆԻ") == "nork_marash"
    assert reference.district_of("ՆՈՐ ՆՈՐՔ ՎԱՐՉԱԿԱՆ ՇՐՋԱՆԻ") == "nor_nork"
    assert reference.district_of("Ավան") == "avan"
    assert reference.district_of("ԵՐԵՎԱՆ ՔԱՂԱՔԻ ԱՎԱԳԱՆԻ") is None


def test_translation_keys():
    assert split_enum("1.1 Գույքային հարկեր") == ("1.1", "Գույքային հարկեր")
    assert split_enum("ա) Քաղաքացիական") == ("ա)", "Քաղաքացիական")
    assert split_enum("- Այլ ծախսեր") == ("-", "Այլ ծախսեր")
    assert strip_formula("1. ՀԱՐԿԵՐ ԵՎ ՏՈՒՐՔԵՐ (տող 1110 + տող 1120), այդ թվում`") == "1. ՀԱՐԿԵՐ ԵՎ ՏՈՒՐՔԵՐ"


def test_render_sql_repeats_language_lines():
    from yerevan_budget import config
    from yerevan_budget.build import render_sql

    sql = render_sql("SELECT a,\n       x.name_{lang} AS name_{lang},\n  -- name_{lang} stays\nFROM t; -- {langs}")
    lines = sql.splitlines()
    assert lines[1:1 + len(config.LANGS)] == [f"       x.name_{lang} AS name_{lang}," for lang in config.LANGS]
    assert "  -- name_{lang} stays" in lines
    assert lines[-1] == "FROM t; -- " + " / ".join(config.LANGS)
    assert "[a-z]{2}" in render_sql("WHERE c ~ '[a-z]{2}'")


def test_merge_pending_partial(tmp_path, monkeypatch):
    from yerevan_budget import translations as tr

    monkeypatch.setattr(tr.config, "TRANSLATIONS_DIR", tmp_path)
    monkeypatch.setattr(tr, "PENDING_DIR", tmp_path / "pending")
    empty = {lang: "" for lang in tr.LANGS}
    tr.write_csv(tr.path("labels"), [{"hy": "Ավան", **empty, "en": "Avan", "ru": "Аван"}])
    full = {lang: f"Avan-{lang}" for lang in tr.LANGS}
    tr.write_csv(tr.PENDING_DIR / "labels.csv", [
        {"hy": "Ավան", **empty, "fr": "Avan"},          # fills one language of a known name
        {"hy": "Կենտրոն", **full},                     # new, complete
        {"hy": "Էրեբունի", **empty},                    # nothing filled: stays pending
    ])
    tr.merge_pending()
    rows = {r["hy"]: r for r in tr.read_csv(tr.path("labels"))}
    assert rows["Ավան"]["en"] == "Avan" and rows["Ավան"]["fr"] == "Avan" and rows["Ավան"]["de"] == ""
    assert rows["Կենտրոն"] == {"hy": "Կենտրոն", **full}
    left = [r["hy"] for r in tr.read_csv(tr.PENDING_DIR / "labels.csv")]
    assert left == ["Ավան", "Էրեբունի"]
