-- Dimensions derived from the facts (run by the build after fact_budget_line is loaded).

-- Primary document of each type / year / period: the one with the most statements and rows.
-- The v_* views use only primary documents, so re-published documents are not counted twice.
UPDATE meta_document SET is_primary = doc_id IN (
    SELECT doc_id FROM (
        SELECT doc_id, row_number() OVER (
                   PARTITION BY doc_type, fiscal_year, coalesce(report_period, '')
                   ORDER BY count(DISTINCT statement) DESC, count(*) DESC, doc_id) AS rn
        FROM fact_budget_line GROUP BY doc_id, doc_type, fiscal_year, report_period)
    WHERE rn = 1);

-- name of a code: the label of its most recent row (execution reports first: their names are not cut)
CREATE TEMP TABLE _named AS
SELECT f.*, regexp_replace(f.label_hy, '^[-–]\s*', '') AS name,
       row_number() OVER (PARTITION BY f.statement, f.line_code ORDER BY f.fiscal_year DESC,
                          f.doc_type = 'execution_report' DESC, length(f.label_hy) DESC) AS rn_line,
       row_number() OVER (PARTITION BY f.func_code ORDER BY f.fiscal_year DESC,
                          f.doc_type = 'execution_report' DESC, length(f.label_hy) DESC) AS rn_func,
       row_number() OVER (PARTITION BY f.class_code ORDER BY f.fiscal_year DESC,
                          f.doc_type = 'execution_report' DESC, length(f.label_hy) DESC) AS rn_class
FROM fact_budget_line f
WHERE f.col_no = 1 AND f.label_hy IS NOT NULL;

INSERT INTO dim_functional
SELECT n.func_code, split_part(n.func_code, '.', 1), split_part(n.func_code, '.', 2), split_part(n.func_code, '.', 3),
       CASE WHEN n.func_code LIKE '%.0.0' THEN 'section' WHEN n.func_code LIKE '%.0' THEN 'group' ELSE 'class' END,
       n.name, NULL, NULL, y.first_year, y.last_year
FROM _named n
JOIN (SELECT func_code, min(fiscal_year) AS first_year, max(fiscal_year) AS last_year
      FROM fact_budget_line WHERE func_code IS NOT NULL AND row_type IN ('line', 'functional') GROUP BY func_code) y
  USING (func_code)
WHERE n.row_type IN ('line', 'functional') AND n.func_code IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY n.func_code ORDER BY n.rn_func) = 1;

INSERT INTO dim_economic
SELECT n.class_code,
       CASE WHEN n.class_code < '4' THEN 'other' WHEN n.class_code < '7' THEN 'expenditure'
            WHEN n.class_code < '8' THEN 'revenue' ELSE 'financing' END,
       n.name, NULL, NULL, y.first_year, y.last_year
FROM _named n
JOIN (SELECT class_code, min(fiscal_year) AS first_year, max(fiscal_year) AS last_year
      FROM fact_budget_line WHERE class_code IS NOT NULL GROUP BY class_code) y USING (class_code)
WHERE n.class_code IS NOT NULL AND (n.statement <> 'revenue' OR n.line_code IS NOT NULL)
QUALIFY row_number() OVER (PARTITION BY n.class_code
                           ORDER BY (n.statement IN ('expenditure_economic', 'expenditure_program', 'financing')) DESC,
                                    n.rn_class) = 1;

INSERT INTO dim_line
SELECT n.statement, n.line_code, n.class_code, n.func_code, n.name, NULL, NULL, y.first_year, y.last_year, y.n_names
FROM _named n
JOIN (SELECT statement, line_code, min(fiscal_year) AS first_year, max(fiscal_year) AS last_year,
             count(DISTINCT label_hy) AS n_names
      FROM fact_budget_line WHERE line_code IS NOT NULL AND statement <> 'expenditure_program'
      GROUP BY statement, line_code) y USING (statement, line_code)
WHERE n.line_code IS NOT NULL AND n.statement <> 'expenditure_program' AND n.rn_line = 1;

DROP TABLE _named;
