"""Integration tests of the built database (skipped if it has not been built)."""

import duckdb
import pytest

from yerevan_budget import config

pytestmark = pytest.mark.skipif(not config.DUCKDB_PATH.exists(), reason="database not built (make build)")


@pytest.fixture(scope="module")
def con():
    c = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    yield c
    c.close()


def one(con, sql):
    return con.execute(sql).fetchone()[0]


def test_core_tables_not_empty(con):
    for t in ("meta_document", "meta_file", "raw_page_text", "raw_table_cell", "stg_table_row", "fact_budget_line",
              "fact_program_budget", "fact_program_indicator", "dim_functional", "dim_economic", "dim_line",
              "dim_program", "dim_measure", "dim_label"):
        assert one(con, f"SELECT count(*) FROM {t}") > 0, t


def test_documents_catalogued(con):
    assert one(con, "SELECT count(*) FROM meta_document WHERE doc_group = 'core'") >= 80
    assert one(con, "SELECT count(*) FROM meta_document WHERE doc_group = 'institutions'") >= 400
    assert one(con, "SELECT count(*) FROM meta_document WHERE doc_group = 'core' AND sha256 IS NULL") == 0
    assert one(con, "SELECT count(*) FROM meta_file WHERE extract_error IS NOT NULL") == 0


def test_every_year_has_budget_and_report(con):
    years = {r[0] for r in con.execute(
        "SELECT DISTINCT fiscal_year FROM fact_budget_line WHERE doc_type = 'budget'").fetchall()}
    assert set(range(2018, 2027)) <= years
    years = {r[0] for r in con.execute(
        "SELECT DISTINCT fiscal_year FROM v_execution WHERE statement = 'revenue' AND line_code = '1000'").fetchall()}
    assert set(range(2017, 2027)) - {2020} <= years


def test_one_primary_document_per_type_year_period(con):
    assert one(con, """
        SELECT count(*) FROM (
            SELECT doc_type, fiscal_year, period FROM meta_document WHERE is_primary
            GROUP BY ALL HAVING count(*) > 1)""") == 0


def test_known_totals(con):
    # 2025 annual report: total revenues, approved plan and actual (thousand AMD, from the PDF)
    row = con.execute("""
        SELECT approved_total_kamd, actual_total_kamd FROM v_execution_annual
        WHERE fiscal_year = 2025 AND statement = 'revenue' AND line_code = '1000'""").fetchone()
    assert row == (159399554.2, 148517551.6)
    # 2025 budget, appendix 6 = sum of appendix 7 (city = Municipality + districts)
    assert one(con, "SELECT count(*) FROM qc_program_districts") == 0


def test_amount_semantics_complete(con):
    assert one(con, "SELECT count(*) FROM fact_budget_line WHERE scenario IS NULL OR budget_part IS NULL") == 0
    assert one(con, "SELECT count(*) FROM fact_budget_line WHERE value_year IS NULL") == 0


def test_names_in_three_languages(con):
    assert one(con, "SELECT count(*) FROM qc_missing_translation") == 0
    assert one(con, "SELECT avg((label_en IS NOT NULL)::INT) FROM v_budget_line") > 0.99
    assert one(con, "SELECT count(*) FROM dim_functional WHERE name_en IS NULL OR name_ru IS NULL") == 0
    assert one(con, "SELECT count(*) FROM meta_document WHERE title_en IS NULL OR title_ru IS NULL") == 0


def test_districts(con):
    n = one(con, """SELECT count(DISTINCT district_code) FROM fact_budget_line
                    WHERE doc_type = 'budget' AND fiscal_year = 2025 AND appendix = 7""")
    assert n == 13  # the Municipality and the 12 districts


def test_comments_on_every_table(con):
    assert one(con, "SELECT count(*) FROM duckdb_tables() WHERE schema_name = 'main' AND comment IS NULL") == 0
