-- Data quality checks, materialised as qc_* tables by the build.
-- Each check writes a row to qc_summary (check, status, number of issues, description).
-- Tolerance for sums: 1 thousand AMD (the documents round to 0.1).

CREATE TABLE qc_summary (check_name VARCHAR, status VARCHAR, n_issues BIGINT, details VARCHAR);
COMMENT ON TABLE qc_summary IS 'Result of all data quality checks (OK / WARN / INFO).';

-- 1. Revenue total = taxes + grants + other revenues (lines 1000 = 1100 + 1200 + 1300)
CREATE TABLE qc_revenue_total AS
WITH x AS (
    SELECT doc_id, file_id, doc_type, fiscal_year, report_period, scenario, value_year, value_period, budget_part,
           max(amount_kamd) FILTER (WHERE line_code = '1000') AS total,
           sum(amount_kamd) FILTER (WHERE line_code IN ('1100', '1200', '1300')) AS parts
    FROM fact_budget_line WHERE statement = 'revenue' AND row_type = 'line'
    GROUP BY ALL)
SELECT *, round(total - parts, 1) AS diff FROM x WHERE abs(coalesce(total, 0) - coalesce(parts, 0)) > 1;
COMMENT ON TABLE qc_revenue_total IS 'Tables where the revenue total (line 1000) differs from lines 1100 + 1200 + 1300 by more than 1 thousand AMD.';
INSERT INTO qc_summary SELECT 'revenue_total_equals_parts', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'amount columns where line 1000 <> 1100 + 1200 + 1300 (qc_revenue_total)' FROM qc_revenue_total;

-- 2. Expenditure total = sum of the functional sections (line 2000 = lines of sections XX.0.0)
CREATE TABLE qc_functional_total AS
WITH x AS (
    SELECT doc_id, file_id, doc_type, fiscal_year, report_period, scenario, value_year, value_period, budget_part,
           max(amount_kamd) FILTER (WHERE line_code = '2000') AS total,
           sum(amount_kamd) FILTER (WHERE func_code LIKE '%.0.0' AND line_code <> '2000') AS sections
    FROM fact_budget_line WHERE statement = 'expenditure_functional' AND row_type = 'line'
    GROUP BY ALL)
SELECT *, round(total - sections, 1) AS diff FROM x
WHERE total IS NOT NULL AND abs(total - coalesce(sections, 0)) > 1;
COMMENT ON TABLE qc_functional_total IS 'Tables where the expenditure total (line 2000) differs from the sum of the functional sections.';
INSERT INTO qc_summary SELECT 'functional_total_equals_sections', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'amount columns where line 2000 <> sum of the sections (qc_functional_total)' FROM qc_functional_total;

-- 3. Functional and economic classifications give the same expenditure total (line 2000 vs 4000)
CREATE TABLE qc_functional_vs_economic AS
WITH x AS (
    SELECT doc_id, fiscal_year, report_period, scenario, value_year, value_period, budget_part,
           max(amount_kamd) FILTER (WHERE statement = 'expenditure_functional' AND line_code = '2000') AS functional,
           max(amount_kamd) FILTER (WHERE statement = 'expenditure_economic' AND line_code = '4000') AS economic
    FROM fact_budget_line WHERE row_type = 'line' GROUP BY ALL)
SELECT *, round(functional - economic, 1) AS diff FROM x
WHERE functional IS NOT NULL AND economic IS NOT NULL AND abs(functional - economic) > 1;
COMMENT ON TABLE qc_functional_vs_economic IS 'Documents where total expenditures by functional classification (line 2000) and by economic classification (line 4000) differ.';
INSERT INTO qc_summary SELECT 'functional_equals_economic', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'amount columns where line 2000 <> line 4000 (qc_functional_vs_economic)' FROM qc_functional_vs_economic;

-- 4. Total = administrative part + fund part
CREATE TABLE qc_parts AS
WITH x AS (
    SELECT doc_id, file_id, seq, doc_type, fiscal_year, report_period, statement, line_code, label_hy, scenario, value_year, value_period,
           max(amount_kamd) FILTER (WHERE budget_part = 'total') AS total,
           max(amount_kamd) FILTER (WHERE budget_part = 'admin') AS admin,
           max(amount_kamd) FILTER (WHERE budget_part = 'fund') AS fund
    FROM fact_budget_line GROUP BY ALL)
SELECT *, round(total - coalesce(admin, 0) - coalesce(fund, 0), 1) AS diff FROM x
WHERE total IS NOT NULL AND (admin IS NOT NULL OR fund IS NOT NULL)
  AND abs(total - coalesce(admin, 0) - coalesce(fund, 0)) > 1;
COMMENT ON TABLE qc_parts IS 'Rows where total <> administrative part + fund part. Expected for some lines: the transfer from the reserve fund of the administrative part to the fund part (lines 1390–1393, 4050, 4770–4772) is counted in both parts.';
INSERT INTO qc_summary SELECT 'total_equals_admin_plus_fund', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'INFO' END, count(*),
       'rows where total <> admin + fund (qc_parts; expected for the internal transfer lines)' FROM qc_parts;

-- 5. Detailed tables: the city total (appendix 6) equals the sum of the Municipality and the districts (appendix 7)
CREATE TABLE qc_program_districts AS
WITH t AS (
    SELECT doc_id, fiscal_year, budget_part, appendix, district_code, amount_kamd
    FROM fact_budget_line WHERE doc_type = 'budget' AND statement = 'expenditure_program' AND row_type = 'total'),
x AS (
    SELECT doc_id, fiscal_year, budget_part,
           max(amount_kamd) FILTER (WHERE appendix = 6) AS city,
           sum(amount_kamd) FILTER (WHERE appendix = 7) AS units,
           count(*) FILTER (WHERE appendix = 7) AS n_units
    FROM t GROUP BY ALL)
SELECT *, round(city - units, 1) AS diff FROM x WHERE city IS NULL OR units IS NULL OR abs(city - units) > 1;
COMMENT ON TABLE qc_program_districts IS 'Budgets where total expenditures of appendix 6 (city) differ from the sum of the tables of appendix 7 (Municipality + districts).';
INSERT INTO qc_summary SELECT 'program_city_equals_units', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'budgets where appendix 6 total <> sum of appendix 7 tables (qc_program_districts)' FROM qc_program_districts;

-- 6. Coverage: which document types gave facts for which years
CREATE TABLE qc_coverage AS
SELECT m.doc_type, m.fiscal_year, string_agg(DISTINCT coalesce(m.period, ''), ',' ORDER BY coalesce(m.period, '')) AS periods,
       count(DISTINCT m.doc_id) AS n_documents,
       count(DISTINCT m.doc_id) FILTER (WHERE f.doc_id IS NOT NULL) AS n_with_facts,
       coalesce(sum(f.n), 0) AS n_facts
FROM meta_document m
LEFT JOIN (SELECT doc_id, count(*) AS n FROM fact_budget_line GROUP BY doc_id) f USING (doc_id)
WHERE m.doc_group = 'core'
GROUP BY ALL ORDER BY m.doc_type, m.fiscal_year;
COMMENT ON TABLE qc_coverage IS 'Core documents by type and year and how many of them gave facts.';
INSERT INTO qc_summary
SELECT 'documents_with_facts', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'documents of a type with tables (budget, execution report, MTEF, measures) without any facts: '
       || coalesce(string_agg(doc_id || ' ' || doc_type || ' ' || fiscal_year || coalesce(' ' || period, ''), '; '), '')
FROM meta_document m
WHERE doc_group = 'core' AND doc_type IN ('budget', 'execution_report', 'mtef', 'execution_measures')
  AND doc_id NOT IN (SELECT doc_id FROM fact_budget_line) AND duplicate_of IS NULL
  -- documents whose files are all identical to files of another document
  AND doc_id IN (SELECT doc_id FROM meta_file WHERE kind IS NOT NULL AND duplicate_of_file IS NULL);

-- 7. Files that could not be read or have tables with an unknown layout
INSERT INTO qc_summary SELECT 'files_extracted', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'files with an extraction error (meta_file.extract_error)' FROM meta_file WHERE extract_error IS NOT NULL;
INSERT INTO qc_summary SELECT 'tables_with_unknown_layout', 'INFO', coalesce(sum(n_unmapped_tables), 0),
       'tables with numbers but without a row of column numbers (cells only in raw_table_cell; meta_file.n_unmapped_tables)'
FROM meta_file;

-- 8. Names without a translation (into any of the languages: the name columns <name>_<lang>)
CREATE TEMP MACRO any_null(names) AS list_count(names) < len(names);
CREATE TABLE qc_missing_translation AS
SELECT DISTINCT l.context, l.label_hy AS hy
FROM dim_label l
JOIN (SELECT DISTINCT label_hy FROM v_budget_line WHERE any_null([*COLUMNS('^label_[a-z]{2}$')])
      UNION SELECT DISTINCT program_hy FROM v_budget_line
            WHERE program_hy IS NOT NULL AND any_null([*COLUMNS('^program_[a-z]{2}$')])) u
  USING (label_hy)
WHERE any_null([*COLUMNS('^label_[a-z]{2}$')])
UNION SELECT 'program', name_hy FROM dim_program WHERE name_hy IS NOT NULL AND any_null([*COLUMNS('^name_[a-z]{2}$')])
UNION SELECT 'program', name_hy FROM dim_measure WHERE name_hy IS NOT NULL AND any_null([*COLUMNS('^name_[a-z]{2}$')])
UNION SELECT CASE WHEN statement = 'revenue' THEN 'revenue' WHEN statement = 'expenditure_functional' THEN 'functional'
                  WHEN statement = 'expenditure_economic' THEN 'economic' ELSE 'financing' END, name_hy
      FROM dim_line WHERE name_hy IS NOT NULL AND any_null([*COLUMNS('^name_[a-z]{2}$')])
UNION SELECT 'functional', name_hy FROM dim_functional WHERE name_hy IS NOT NULL AND any_null([*COLUMNS('^name_[a-z]{2}$')])
UNION SELECT 'economic', name_hy FROM dim_economic WHERE name_hy IS NOT NULL AND any_null([*COLUMNS('^name_[a-z]{2}$')])
UNION SELECT 'labels', title_hy FROM meta_document WHERE any_null([*COLUMNS('^title_[a-z]{2}$')])
UNION SELECT 'labels', institution_group_hy FROM meta_document
      WHERE institution_group_hy IS NOT NULL AND any_null([*COLUMNS('^institution_group_[a-z]{2}$')])
UNION SELECT 'reference', name_hy FROM (
      SELECT COLUMNS('^name_[a-z]{2}$') FROM dim_doc_type
      UNION ALL BY NAME SELECT COLUMNS('^name_[a-z]{2}$') FROM dim_period
      UNION ALL BY NAME SELECT COLUMNS('^name_[a-z]{2}$') FROM dim_statement
      UNION ALL BY NAME SELECT COLUMNS('^name_[a-z]{2}$') FROM dim_scenario
      UNION ALL BY NAME SELECT COLUMNS('^name_[a-z]{2}$') FROM dim_budget_part
      UNION ALL BY NAME SELECT COLUMNS('^name_[a-z]{2}$') FROM dim_district)
      WHERE any_null([*COLUMNS('^name_[a-z]{2}$')]);
COMMENT ON TABLE qc_missing_translation IS 'Armenian names without a translation into one of the languages ({langs}): names of codes (dimensions), document titles, and row names of the primary documents that have no code to fall back on (fill them with `python -m yerevan_budget translations`).';
INSERT INTO qc_summary SELECT 'translations_complete', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'WARN' END, count(*),
       'names without a translation (qc_missing_translation)' FROM qc_missing_translation;

-- 9. Approved plan in the annual report vs the budget decision (they differ when the budget was amended
--    before the report's "approved" column was filled; informational)
CREATE TABLE qc_report_vs_budget AS
SELECT r.fiscal_year, r.statement, r.line_code, r.label_hy, r.approved_total_kamd AS report_approved_kamd,
       b.total_kamd AS budget_kamd, round(r.approved_total_kamd - b.total_kamd, 1) AS diff
FROM v_execution_annual r
JOIN v_budget_approved b USING (fiscal_year, statement, line_code)
WHERE r.line_code IN ('1000', '1100', '1200', '1300', '4000')
  AND abs(coalesce(r.approved_total_kamd, 0) - coalesce(b.total_kamd, 0)) > 1;
COMMENT ON TABLE qc_report_vs_budget IS 'Main lines where the "approved plan" of the annual execution report differs from the budget decision.';
INSERT INTO qc_summary SELECT 'report_approved_equals_budget', CASE WHEN count(*) = 0 THEN 'OK' ELSE 'INFO' END, count(*),
       'main lines where the approved plan of the annual report differs from the budget decision (qc_report_vs_budget)'
FROM qc_report_vs_budget;
