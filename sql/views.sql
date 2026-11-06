-- Views: ready-made selections in three languages. They use only the primary document
-- of each type / year / period (meta_document.is_primary).

-- All amounts with names in hy / en / ru
CREATE VIEW v_budget_line AS
SELECT f.fiscal_year, f.doc_type, f.report_period, f.statement, f.row_type, f.appendix,
       f.district_code, d.name_en AS district_en,
       f.line_code, f.func_code, f.class_code,
       f.label_hy,
       -- translation of the name as printed; otherwise the name of its code (functional class, article, line)
       coalesce(l.label_en, CASE WHEN f.row_type IN ('line', 'functional') THEN fu.name_en END,
                CASE WHEN f.statement <> 'revenue' THEN e.name_en END, dl.name_en) AS label_en,
       coalesce(l.label_ru, CASE WHEN f.row_type IN ('line', 'functional') THEN fu.name_ru END,
                CASE WHEN f.statement <> 'revenue' THEN e.name_ru END, dl.name_ru) AS label_ru,
       f.program_hy, p.label_en AS program_en, p.label_ru AS program_ru,
       f.scenario, f.value_year, f.value_period, f.budget_part, f.amount_kamd,
       f.doc_id, f.file_id, f.page, f.seq, f.col_no
FROM fact_budget_line f
JOIN meta_document m USING (doc_id)
LEFT JOIN dim_label l ON l.label_hy = f.label_hy
     AND l.context = CASE f.statement WHEN 'revenue' THEN 'revenue' WHEN 'expenditure_functional' THEN 'functional'
                     WHEN 'expenditure_economic' THEN 'economic' WHEN 'expenditure_program' THEN 'program'
                     ELSE 'financing' END
LEFT JOIN dim_label p ON p.label_hy = f.program_hy AND p.context = 'program'
LEFT JOIN dim_district d ON d.district_code = f.district_code
LEFT JOIN dim_functional fu ON fu.func_code = f.func_code AND f.statement IN ('expenditure_functional', 'expenditure_program')
LEFT JOIN dim_economic e ON e.econ_code = f.class_code
LEFT JOIN dim_line dl ON dl.statement = f.statement AND dl.line_code = f.line_code
WHERE m.is_primary;
COMMENT ON VIEW v_budget_line IS 'fact_budget_line of the primary documents with the row names in English and Russian.';

-- Execution reports (form Հ-9): one row per report line, plan and execution side by side
CREATE VIEW v_execution AS
SELECT fiscal_year, report_period, statement, line_code, func_code, class_code,
       any_value(label_hy) AS label_hy, any_value(label_en) AS label_en, any_value(label_ru) AS label_ru,
       max(amount_kamd) FILTER (WHERE scenario = 'approved' AND budget_part = 'total') AS approved_total_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'approved' AND budget_part = 'admin') AS approved_admin_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'approved' AND budget_part = 'fund') AS approved_fund_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'revised' AND budget_part = 'total') AS revised_total_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'revised' AND budget_part = 'admin') AS revised_admin_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'revised' AND budget_part = 'fund') AS revised_fund_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'actual' AND budget_part = 'total') AS actual_total_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'actual' AND budget_part = 'admin') AS actual_admin_kamd,
       max(amount_kamd) FILTER (WHERE scenario = 'actual' AND budget_part = 'fund') AS actual_fund_kamd,
       min(seq) AS seq, any_value(doc_id) AS doc_id
FROM v_budget_line
WHERE doc_type = 'execution_report'
GROUP BY fiscal_year, report_period, statement, file_id, seq, line_code, func_code, class_code;
COMMENT ON VIEW v_execution IS 'Budget execution reports (form Հ-9, quarterly and annual): approved plan, revised plan and actual execution (cumulative from 1 January) by part of the budget, thousand AMD.';

CREATE VIEW v_execution_annual AS
SELECT * EXCLUDE (report_period) FROM v_execution WHERE report_period = 'FY';
COMMENT ON VIEW v_execution_annual IS 'Annual execution reports: approved plan, revised plan, actual by line, thousand AMD.';

-- Approved budget (appendices 1–5 of the budget decision of the council)
CREATE VIEW v_budget_approved AS
SELECT fiscal_year, appendix, statement, line_code, func_code, class_code,
       any_value(label_hy) AS label_hy, any_value(label_en) AS label_en, any_value(label_ru) AS label_ru,
       max(amount_kamd) FILTER (WHERE budget_part = 'total') AS total_kamd,
       max(amount_kamd) FILTER (WHERE budget_part = 'admin') AS admin_kamd,
       max(amount_kamd) FILTER (WHERE budget_part = 'fund') AS fund_kamd,
       min(seq) AS seq, any_value(doc_id) AS doc_id
FROM v_budget_line
WHERE doc_type = 'budget' AND statement <> 'expenditure_program'
GROUP BY fiscal_year, appendix, statement, file_id, seq, line_code, func_code, class_code;
COMMENT ON VIEW v_budget_approved IS 'Budget of the city as approved by the council (revenues, expenditures by functional and economic classification, balance, financing), thousand AMD.';

-- Detailed allocation: functional class x programme x economic article, city total and by district
CREATE VIEW v_budget_program AS
SELECT b.fiscal_year, b.doc_type, b.appendix, b.district_code, b.district_en, b.row_type,
       b.func_code, fu.name_hy AS func_name_hy, fu.name_en AS func_name_en, fu.name_ru AS func_name_ru,
       b.program_hy, b.program_en, b.program_ru, b.class_code,
       b.label_hy, b.label_en, b.label_ru,
       b.scenario, b.value_year, b.value_period,
       max(b.amount_kamd) FILTER (WHERE b.budget_part = 'total') AS total_kamd,
       max(b.amount_kamd) FILTER (WHERE b.budget_part = 'admin') AS admin_kamd,
       max(b.amount_kamd) FILTER (WHERE b.budget_part = 'fund') AS fund_kamd,
       b.seq, b.doc_id
FROM v_budget_line b
LEFT JOIN dim_functional fu USING (func_code)
WHERE b.statement = 'expenditure_program'
GROUP BY ALL;
COMMENT ON VIEW v_budget_program IS 'Detailed tables: expenditures by functional class, programme and economic article (budget appendix 6 = city, appendix 7 = Municipality and each district; also the medium-term programme and the quarterly execution measures). row_type: functional / program / economic / total.';

-- Medium-term expenditure programmes: forecasts for three years
CREATE VIEW v_mtef AS
SELECT fiscal_year AS mtef_first_year, value_year, statement, line_code, func_code, class_code,
       any_value(label_hy) AS label_hy, any_value(label_en) AS label_en, any_value(label_ru) AS label_ru,
       max(amount_kamd) FILTER (WHERE budget_part = 'total') AS total_kamd,
       max(amount_kamd) FILTER (WHERE budget_part = 'admin') AS admin_kamd,
       max(amount_kamd) FILTER (WHERE budget_part = 'fund') AS fund_kamd,
       min(seq) AS seq, any_value(doc_id) AS doc_id
FROM v_budget_line
WHERE doc_type = 'mtef' AND statement <> 'expenditure_program'
GROUP BY fiscal_year, value_year, statement, file_id, seq, line_code, func_code, class_code;
COMMENT ON VIEW v_mtef IS 'Medium-term expenditure programmes (MTEF): forecasts of revenues, expenditures and financing for each of the three years, thousand AMD.';

-- Revenues and expenditures by year: approved, revised, actual (annual reports) and the approved budget
CREATE VIEW v_summary AS
WITH rep AS (
    SELECT fiscal_year,
           max(approved_total_kamd) FILTER (WHERE statement = 'revenue' AND line_code = '1000') AS revenue_approved_kamd,
           max(revised_total_kamd) FILTER (WHERE statement = 'revenue' AND line_code = '1000') AS revenue_revised_kamd,
           max(actual_total_kamd) FILTER (WHERE statement = 'revenue' AND line_code = '1000') AS revenue_actual_kamd,
           max(approved_total_kamd) FILTER (WHERE statement = 'expenditure_functional' AND line_code = '2000') AS expenditure_approved_kamd,
           max(revised_total_kamd) FILTER (WHERE statement = 'expenditure_functional' AND line_code = '2000') AS expenditure_revised_kamd,
           max(actual_total_kamd) FILTER (WHERE statement = 'expenditure_functional' AND line_code = '2000') AS expenditure_actual_kamd
    FROM v_execution_annual GROUP BY fiscal_year),
bud AS (
    SELECT fiscal_year,
           max(total_kamd) FILTER (WHERE statement = 'revenue' AND line_code = '1000') AS revenue_budget_kamd,
           max(total_kamd) FILTER (WHERE statement = 'expenditure_economic' AND line_code = '4000') AS expenditure_budget_kamd
    FROM v_budget_approved GROUP BY fiscal_year)
SELECT fiscal_year, b.revenue_budget_kamd, b.expenditure_budget_kamd, r.* EXCLUDE (fiscal_year)
FROM rep r FULL JOIN bud b USING (fiscal_year)
ORDER BY fiscal_year;
COMMENT ON VIEW v_summary IS 'Total revenues and expenditures by year: the approved budget (budget decision) and the approved / revised / actual figures of the annual execution report, thousand AMD.';

-- Documents with English / Russian titles and their type names
CREATE VIEW v_document AS
SELECT m.doc_id, m.doc_group, m.doc_type, t.name_en AS doc_type_en, t.name_ru AS doc_type_ru, m.fiscal_year, m.period,
       m.title_hy, m.title_en, m.title_ru, m.url, m.ext, m.size_bytes, m.is_primary, m.duplicate_of, m.pages
FROM meta_document m LEFT JOIN dim_doc_type t USING (doc_type);
COMMENT ON VIEW v_document IS 'Documents of the Finance section with type names and titles in three languages.';

-- Programme budget (tables ԾԲ): allocations with programme / measure / article names in three languages
CREATE VIEW v_program_budget AS
SELECT f.fiscal_year, f.doc_type, f.value_year, f.district_code, d.name_en AS district_en, d.name_ru AS district_ru,
       f.row_type, f.func_code, fu.name_en AS func_name_en,
       f.program_code, p.name_hy AS program_hy, p.name_en AS program_en, p.name_ru AS program_ru,
       f.measure_code, m.name_hy AS measure_hy, m.name_en AS measure_en, m.name_ru AS measure_ru,
       f.econ_code, e.name_hy AS econ_hy, e.name_en AS econ_en, e.name_ru AS econ_ru,
       f.label_hy, f.amount_kamd, f.doc_id, f.file_id, f.seq
FROM fact_program_budget f
JOIN meta_document md USING (doc_id)
LEFT JOIN dim_district d USING (district_code)
LEFT JOIN dim_functional fu USING (func_code)
LEFT JOIN dim_program p USING (program_code)
LEFT JOIN dim_measure m USING (program_code, measure_code)
LEFT JOIN dim_economic e ON e.econ_code = f.econ_code
WHERE md.is_primary OR md.doc_type IN ('budget_message');
COMMENT ON VIEW v_program_budget IS 'Programme budget (budget message tables for 2025+ and medium-term programmes): amounts by unit, functional class, programme, measure and economic article, with names in hy / en / ru, thousand AMD. Totals by measure: row_type = ''measure''; by article: row_type = ''economic''.';
