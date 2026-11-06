# Data dictionary

Generated automatically from the DuckDB catalog by `python -m yerevan_budget docs` — do not edit by hand.
The descriptions of tables and columns are also stored in the database itself (`duckdb_tables()`, `duckdb_columns()`) and are defined in `sql/schema.sql`, `sql/views.sql`, `sql/qc.sql` (`COMMENT ON`). Schema overview: [database.md](en/database.md) ([hy](hy/database.md), [ru](ru/database.md)).

## Metadata / provenance

### `meta_document` (table, 510 rows)

Every document linked from the Finance pages (one row per distinct URL). Core documents are downloaded and parsed; documents of municipal institutions are catalogued (downloaded only with fetch --institutions, not parsed).

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR | Stable id: first 10 hex digits of SHA-1 of the URL |
| `doc_group` | VARCHAR | core \| institutions |
| `url` | VARCHAR |  |
| `file_name` | VARCHAR |  |
| `ext` | VARCHAR |  |
| `title_hy` | VARCHAR | Link text on the site (Armenian, numbering removed) |
| `title_en` | VARCHAR |  |
| `title_ru` | VARCHAR |  |
| `doc_type` | VARCHAR | Type of the document, see dim_doc_type |
| `fiscal_year` | INTEGER | Budget year the document is about (MTEF: the first of its three years; institutions: the year heading on the page) |
| `period` | VARCHAR | Execution reports: Q1 \| H1 \| 9M \| FY (see dim_period) |
| `institution_group_hy` | VARCHAR | Institutions: group heading on the page (schools, kindergartens, sector of community companies, ...) |
| `institution_group_en` | VARCHAR |  |
| `institution_group_ru` | VARCHAR |  |
| `size_mb_stated` | DOUBLE | Size stated in the link text on the site, MB (institutions) |
| `size_bytes` | BIGINT | Size of the downloaded file |
| `sha256` | VARCHAR |  |
| `downloaded_at` | TIMESTAMP |  |
| `duplicate_of` | VARCHAR | doc_id of a document with byte-identical content published under another URL |
| `is_primary` | BOOLEAN | TRUE for the document whose facts are used by the v_* views when several documents cover the same type / year / period (duplicates and re-publications) |
| `n_files` | INTEGER |  |
| `pages` | VARCHAR[] | Slugs of the pages that link the document |

### `meta_file` (table, 277 rows)

Files of the core documents: the downloaded file itself or every member of a downloaded rar / zip archive.

| column | type | description |
|---|---|---|
| `file_id` | VARCHAR | <doc_id> for a plain file, <doc_id>/<path in the archive> for an archive member |
| `doc_id` | VARCHAR |  |
| `member` | VARCHAR |  |
| `ext` | VARCHAR |  |
| `size_bytes` | BIGINT |  |
| `sha256` | VARCHAR |  |
| `kind` | VARCHAR | pdf \| sheet (xls, xlsx, Excel 2003 XML) \| text (doc, docx) \| NULL (not parsed: images, unknown formats) |
| `n_pages` | INTEGER |  |
| `n_sheets` | INTEGER |  |
| `n_tables` | INTEGER | PDF: tables detected on all pages; spreadsheets: sheets |
| `legacy_font_conversions` | INTEGER | Text pieces converted from the legacy Armenian 8-bit font encoding (ArmSCII-8 / Arial Armenian) to Unicode |
| `glyph_mapped_spans` | INTEGER | PDF text pieces recovered from glyph ids through the cmap of the embedded font (fonts without a ToUnicode table) |
| `extract_error` | VARCHAR |  |
| `duplicate_of_file` | VARCHAR | file_id of an identical file (same sha256) parsed earlier; its rows are not parsed again |
| `n_rows_parsed` | INTEGER | Logical rows of budget tables found in the file (stg_table_row) |
| `n_unmapped_tables` | INTEGER | Tables with numbers whose column layout could not be determined (not in stg_table_row; their cells are in raw_table_cell) |

### `meta_page` (table, 13 rows)

Pages of the "Finance" section of yerevan.am (https://www.yerevan.am/hy/finance/) that were crawled.

| column | type | description |
|---|---|---|
| `slug` | VARCHAR | Page path segment: https://www.yerevan.am/hy/<slug>/ |
| `url` | VARCHAR |  |
| `page_group` | VARCHAR | core (city budget documents) \| institutions (documents of municipal institutions and companies) \| link |
| `year` | INTEGER | Year of an archive page (archive-documents-of-<year>) |
| `title_hy` | VARCHAR |  |
| `title_en` | VARCHAR |  |
| `fetched_at` | TIMESTAMP |  |
| `sha256` | VARCHAR | Hash of the downloaded HTML |
| `n_documents` | INTEGER |  |

## Dimensions

### `dim_budget_part` (table, 3 rows)

Parts of a community budget: administrative (current) part, fund (capital) part, total.

| column | type | description |
|---|---|---|
| `budget_part` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `name_hy` | VARCHAR |  |

### `dim_district` (table, 13 rows)

Administrative districts of Yerevan and the Municipality itself: units of the detailed tables of the budget (appendix 7 of the budget decision, programme budget tables).

| column | type | description |
|---|---|---|
| `district_code` | VARCHAR |  |
| `name_hy` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `sort_order` | INTEGER |  |

### `dim_doc_type` (table, 17 rows)

Types of documents (meta_document.doc_type).

| column | type | description |
|---|---|---|
| `doc_type` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `name_hy` | VARCHAR |  |

### `dim_economic` (table, 145 rows)

Article codes printed next to the lines: economic classification of expenditures (4xxx–6xxx: 4111 wages, 5113 capital repair, ...), revenue articles (7xxx) and financing articles (8xxx–9xxx); names from the most recent document.

| column | type | description |
|---|---|---|
| `econ_code` | VARCHAR |  |
| `kind` | VARCHAR | revenue \| expenditure \| financing (statement the code is used in) |
| `name_hy` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `first_year` | INTEGER |  |
| `last_year` | INTEGER |  |

### `dim_functional` (table, 213 rows)

Functional classification of budget expenditures (section.group.class) as used in the documents; names from the most recent document.

| column | type | description |
|---|---|---|
| `func_code` | VARCHAR | SS.G.C, e.g. 09.1.1 (section 09 Education, group 1, class 1); 09.0.0 = the section, 09.1.0 = the group |
| `func_section` | VARCHAR |  |
| `func_group` | VARCHAR |  |
| `func_class` | VARCHAR |  |
| `level` | VARCHAR | section \| group \| class |
| `name_hy` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `first_year` | INTEGER |  |
| `last_year` | INTEGER |  |

### `dim_label` (table, 2,185 rows)

Every distinct row name of fact_budget_line (label_hy, program_hy) with its English and Russian translation (from dim_translation; numbering kept).

| column | type | description |
|---|---|---|
| `context` | VARCHAR | Translation context: revenue \| functional \| economic \| financing \| program |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |

### `dim_line` (table, 622 rows)

Lines (Տողի NN) of the standard community budget forms by statement; names (without the formulas) from the most recent document.

| column | type | description |
|---|---|---|
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `class_code` | VARCHAR | Revenue article / economic article code printed next to the line (most recent) |
| `func_code` | VARCHAR |  |
| `name_hy` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `first_year` | INTEGER |  |
| `last_year` | INTEGER |  |
| `n_names` | INTEGER | Number of different Armenian names the line had over the years |

### `dim_measure` (table, 222 rows)

Measures (5-digit codes, unique within a programme) of the programme budgeting tables; descriptions and types in Armenian only.

| column | type | description |
|---|---|---|
| `program_code` | VARCHAR |  |
| `measure_code` | VARCHAR |  |
| `name_hy` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `description_hy` | VARCHAR |  |
| `measure_type_hy` | VARCHAR |  |
| `first_year` | INTEGER |  |
| `last_year` | INTEGER |  |

### `dim_period` (table, 4 rows)

Reporting periods; values are cumulative from 1 January.

| column | type | description |
|---|---|---|
| `period` | VARCHAR |  |
| `months` | INTEGER |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `name_hy` | VARCHAR |  |

### `dim_program` (table, 62 rows)

Budget programmes of the programme budgeting tables (4-digit codes); names, goals and final results from the most recent document. Goals and results are in Armenian only.

| column | type | description |
|---|---|---|
| `program_code` | VARCHAR |  |
| `name_hy` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `goal_hy` | VARCHAR |  |
| `result_hy` | VARCHAR |  |
| `first_year` | INTEGER |  |
| `last_year` | INTEGER |  |

### `dim_scenario` (table, 8 rows)

Meaning of an amount column: approved plan, revised plan, actual, draft, forecast, plan for the period.

| column | type | description |
|---|---|---|
| `scenario` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `name_hy` | VARCHAR |  |

### `dim_statement` (table, 6 rows)

Statements (parts) of the budget forms: revenues, expenditures by functional / economic classification, balance, financing, detailed programme tables.

| column | type | description |
|---|---|---|
| `statement` | VARCHAR |  |
| `name_en` | VARCHAR |  |
| `name_ru` | VARCHAR |  |
| `name_hy` | VARCHAR |  |

### `dim_translation` (table, 1,796 rows)

Translation dictionaries hy -> en / ru (data/translations/<context>.csv); key = Armenian text reduced to letters and digits.

| column | type | description |
|---|---|---|
| `context` | VARCHAR |  |
| `key` | VARCHAR |  |
| `hy` | VARCHAR |  |
| `en` | VARCHAR |  |
| `ru` | VARCHAR |  |

## Facts

### `fact_budget_line` (table, 532,596 rows)

All amounts of the budget tables in long form: one row per table row x amount column. Use the v_* views for ready-made selections (they keep only the primary document of each type / year / period).

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `seq` | INTEGER | Row of the table (stg_table_row.seq) |
| `col_no` | INTEGER | Amount column, 1-based, left to right |
| `page` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `report_period` | VARCHAR | Period of the document (execution reports) |
| `statement` | VARCHAR | See dim_statement |
| `row_type` | VARCHAR | line (a line of a standard statement); in expenditure_program tables: total \| functional \| program \| economic |
| `appendix` | INTEGER | Appendix number of the document the row comes from |
| `district_code` | VARCHAR | Detailed tables by district (appendix 7 of the budget, programme tables): see dim_district; NULL = the city total |
| `line_code` | VARCHAR | Line number of the form (Տողի NN), see dim_line |
| `func_code` | VARCHAR | Functional classification code SS.G.C (expenditure rows), see dim_functional; for program / economic rows of the detailed tables: the class they belong to |
| `class_code` | VARCHAR | Article code printed in the row: revenue article (71xx–74xx), economic article (4xxx–6xxx), financing article (9xxx); see dim_economic |
| `program_hy` | VARCHAR | Detailed tables: the programme / measure the economic row belongs to |
| `label_hy` | VARCHAR | Name of the row in Armenian without the formulas (տող ... + տող ...) and the words "including" |
| `scenario` | VARCHAR | See dim_scenario |
| `value_year` | INTEGER | Year the amount refers to (differs from fiscal_year in medium-term programmes) |
| `value_period` | VARCHAR | Period the amount refers to: FY, or Q1 / H1 / 9M (actual values of quarterly reports, quarterly plans) |
| `budget_part` | VARCHAR | total \| admin \| fund (see dim_budget_part) |
| `amount_kamd` | DOUBLE | Amount, thousand AMD; NULL for "X" (not applicable) and empty cells, 0 for "-" |
| `amount_text` | VARCHAR | Cell as printed in the source |

### `fact_program_budget` (table, 14,818 rows)

Programme budget, table 1: expenditures by functional class x programme x measure x economic article, for the city (district_code NULL), the Municipality and every district; one row per table row x year column, thousand AMD.

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `seq` | INTEGER |  |
| `col_no` | INTEGER |  |
| `page` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `district_code` | VARCHAR |  |
| `row_type` | VARCHAR | total \| section \| group \| class (functional rows) \| program \| measure \| economic \| other |
| `func_code` | VARCHAR | Functional class SS.G.C the row belongs to |
| `program_code` | VARCHAR | Programme (dim_program) the row belongs to |
| `measure_code` | VARCHAR | Measure (dim_measure) of measure and economic rows |
| `econ_code` | VARCHAR | Economic article of economic rows (dim_economic) |
| `label_hy` | VARCHAR |  |
| `value_year` | INTEGER | Year of the amount column (the budget year; three years in an MTEF) |
| `amount_kamd` | DOUBLE |  |
| `amount_text` | VARCHAR |  |

### `fact_program_indicator` (table, 8,858 rows)

Programme budget, table 2: performance indicators of the measures and their target values (as printed; value_num when numeric).

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `seq` | INTEGER |  |
| `page` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `program_code` | VARCHAR |  |
| `measure_code` | VARCHAR |  |
| `indicator_hy` | VARCHAR |  |
| `value_text` | VARCHAR |  |
| `value_num` | DOUBLE |  |

## Staging

### `stg_table_row` (table, 87,019 rows)

Every logical row of every budget table recognised in the files (tables anchored by a row of column numbers), before interpretation. Label lines continued on following rows are merged.

| column | type | description |
|---|---|---|
| `file_id` | VARCHAR |  |
| `seq` | INTEGER | Order of the row in the file |
| `page` | INTEGER |  |
| `sheet` | VARCHAR |  |
| `appendix` | INTEGER | Appendix number (Հավելված N) in force on the page |
| `section_no` | INTEGER | Section number (Հատված N) of the execution report form |
| `table_no` | INTEGER | Table number (Աղյուսակ N) in force on the page |
| `table_title` | VARCHAR | Upper-case title lines at the top of the page |
| `line_code` | VARCHAR |  |
| `func_section` | VARCHAR |  |
| `func_group` | VARCHAR |  |
| `func_class` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_raw` | VARCHAR |  |
| `amount_text` | VARCHAR[] | Text of the amount cells, left to right |
| `headers` | VARCHAR[] | Header text of the amount columns, left to right |

## Raw data

### `raw_page_text` (table, 6,264 rows)

Text of every page of every PDF (Unicode, legacy fonts converted) and the full text of doc/docx files (page 1). Use for full-text search.

| column | type | description |
|---|---|---|
| `file_id` | VARCHAR |  |
| `page` | INTEGER |  |
| `text` | VARCHAR |  |
| `n_images` | INTEGER |  |

### `raw_table_cell` (table, 1,170,654 rows)

Every non-empty cell of every table detected in the PDFs (pdfplumber), of every docx table and of every spreadsheet sheet (0-based row / column numbers).

| column | type | description |
|---|---|---|
| `file_id` | VARCHAR |  |
| `page` | INTEGER |  |
| `sheet` | VARCHAR |  |
| `table_no` | INTEGER | PDF: number of the table on the page (0-based); spreadsheet: sheet index; docx: table index |
| `row_no` | INTEGER |  |
| `col_no` | INTEGER |  |
| `value_text` | VARCHAR |  |
| `value_num` | DOUBLE | Numeric value of spreadsheet cells |

## Data quality

### `qc_coverage` (table, 51 rows)

Core documents by type and year and how many of them gave facts.

| column | type | description |
|---|---|---|
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `periods` | VARCHAR |  |
| `n_documents` | BIGINT |  |
| `n_with_facts` | BIGINT |  |
| `n_facts` | HUGEINT |  |

### `qc_functional_total` (table, 0 rows)

Tables where the expenditure total (line 2000) differs from the sum of the functional sections.

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `report_period` | VARCHAR |  |
| `scenario` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `value_period` | VARCHAR |  |
| `budget_part` | VARCHAR |  |
| `total` | DOUBLE |  |
| `sections` | DOUBLE |  |
| `diff` | DOUBLE |  |

### `qc_functional_vs_economic` (table, 0 rows)

Documents where total expenditures by functional classification (line 2000) and by economic classification (line 4000) differ.

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `report_period` | VARCHAR |  |
| `scenario` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `value_period` | VARCHAR |  |
| `budget_part` | VARCHAR |  |
| `functional` | DOUBLE |  |
| `economic` | DOUBLE |  |
| `diff` | DOUBLE |  |

### `qc_missing_translation` (table, 0 rows)

Armenian names without an English or Russian translation: names of codes (dimensions), document titles, and row names of the primary documents that have no code to fall back on (fill them with `python -m yerevan_budget translations`).

| column | type | description |
|---|---|---|
| `context` | VARCHAR |  |
| `hy` | VARCHAR |  |

### `qc_parts` (table, 1,552 rows)

Rows where total <> administrative part + fund part. Expected for some lines: the transfer from the reserve fund of the administrative part to the fund part (lines 1390–1393, 4050, 4770–4772) is counted in both parts.

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `seq` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `report_period` | VARCHAR |  |
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `scenario` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `value_period` | VARCHAR |  |
| `total` | DOUBLE |  |
| `admin` | DOUBLE |  |
| `fund` | DOUBLE |  |
| `diff` | DOUBLE |  |

### `qc_program_districts` (table, 0 rows)

Budgets where total expenditures of appendix 6 (city) differ from the sum of the tables of appendix 7 (Municipality + districts).

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `budget_part` | VARCHAR |  |
| `city` | DOUBLE |  |
| `units` | DOUBLE |  |
| `n_units` | BIGINT |  |
| `diff` | DOUBLE |  |

### `qc_report_vs_budget` (table, 0 rows)

Main lines where the "approved plan" of the annual execution report differs from the budget decision.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `report_approved_kamd` | DOUBLE |  |
| `budget_kamd` | DOUBLE |  |
| `diff` | DOUBLE |  |

### `qc_revenue_total` (table, 47 rows)

Tables where the revenue total (line 1000) differs from lines 1100 + 1200 + 1300 by more than 1 thousand AMD.

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `doc_type` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `report_period` | VARCHAR |  |
| `scenario` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `value_period` | VARCHAR |  |
| `budget_part` | VARCHAR |  |
| `total` | DOUBLE |  |
| `parts` | DOUBLE |  |
| `diff` | DOUBLE |  |

### `qc_summary` (table, 10 rows)

Result of all data quality checks (OK / WARN / INFO).

| column | type | description |
|---|---|---|
| `check_name` | VARCHAR |  |
| `status` | VARCHAR |  |
| `n_issues` | BIGINT |  |
| `details` | VARCHAR |  |

## Views

### `v_budget_approved` (view, 2,040 rows)

Budget of the city as approved by the council (revenues, expenditures by functional and economic classification, balance, financing), thousand AMD.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `appendix` | INTEGER |  |
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |
| `total_kamd` | DOUBLE |  |
| `admin_kamd` | DOUBLE |  |
| `fund_kamd` | DOUBLE |  |
| `seq` | INTEGER |  |
| `doc_id` | VARCHAR |  |

### `v_budget_line` (view, 519,665 rows)

fact_budget_line of the primary documents with the row names in English and Russian.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `report_period` | VARCHAR |  |
| `statement` | VARCHAR |  |
| `row_type` | VARCHAR |  |
| `appendix` | INTEGER |  |
| `district_code` | VARCHAR |  |
| `district_en` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |
| `program_hy` | VARCHAR |  |
| `program_en` | VARCHAR |  |
| `program_ru` | VARCHAR |  |
| `scenario` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `value_period` | VARCHAR |  |
| `budget_part` | VARCHAR |  |
| `amount_kamd` | DOUBLE |  |
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `page` | INTEGER |  |
| `seq` | INTEGER |  |
| `col_no` | INTEGER |  |

### `v_budget_program` (view, 131,376 rows)

Detailed tables: expenditures by functional class, programme and economic article (budget appendix 6 = city, appendix 7 = Municipality and each district; also the medium-term programme and the quarterly execution measures). row_type: functional / program / economic / total.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `appendix` | INTEGER |  |
| `district_code` | VARCHAR |  |
| `district_en` | VARCHAR |  |
| `row_type` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `func_name_hy` | VARCHAR |  |
| `func_name_en` | VARCHAR |  |
| `func_name_ru` | VARCHAR |  |
| `program_hy` | VARCHAR |  |
| `program_en` | VARCHAR |  |
| `program_ru` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |
| `scenario` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `value_period` | VARCHAR |  |
| `total_kamd` | DOUBLE |  |
| `admin_kamd` | DOUBLE |  |
| `fund_kamd` | DOUBLE |  |
| `seq` | INTEGER |  |
| `doc_id` | VARCHAR |  |

### `v_document` (view, 510 rows)

Documents of the Finance section with type names and titles in three languages.

| column | type | description |
|---|---|---|
| `doc_id` | VARCHAR |  |
| `doc_group` | VARCHAR |  |
| `doc_type` | VARCHAR |  |
| `doc_type_en` | VARCHAR |  |
| `doc_type_ru` | VARCHAR |  |
| `fiscal_year` | INTEGER |  |
| `period` | VARCHAR |  |
| `title_hy` | VARCHAR |  |
| `title_en` | VARCHAR |  |
| `title_ru` | VARCHAR |  |
| `url` | VARCHAR |  |
| `ext` | VARCHAR |  |
| `size_bytes` | BIGINT |  |
| `is_primary` | BOOLEAN |  |
| `duplicate_of` | VARCHAR |  |
| `pages` | VARCHAR[] |  |

### `v_execution` (view, 20,592 rows)

Budget execution reports (form Հ-9, quarterly and annual): approved plan, revised plan and actual execution (cumulative from 1 January) by part of the budget, thousand AMD.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `report_period` | VARCHAR |  |
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |
| `approved_total_kamd` | DOUBLE |  |
| `approved_admin_kamd` | DOUBLE |  |
| `approved_fund_kamd` | DOUBLE |  |
| `revised_total_kamd` | DOUBLE |  |
| `revised_admin_kamd` | DOUBLE |  |
| `revised_fund_kamd` | DOUBLE |  |
| `actual_total_kamd` | DOUBLE |  |
| `actual_admin_kamd` | DOUBLE |  |
| `actual_fund_kamd` | DOUBLE |  |
| `seq` | INTEGER |  |
| `doc_id` | VARCHAR |  |

### `v_execution_annual` (view, 4,668 rows)

Annual execution reports: approved plan, revised plan, actual by line, thousand AMD.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |
| `approved_total_kamd` | DOUBLE |  |
| `approved_admin_kamd` | DOUBLE |  |
| `approved_fund_kamd` | DOUBLE |  |
| `revised_total_kamd` | DOUBLE |  |
| `revised_admin_kamd` | DOUBLE |  |
| `revised_fund_kamd` | DOUBLE |  |
| `actual_total_kamd` | DOUBLE |  |
| `actual_admin_kamd` | DOUBLE |  |
| `actual_fund_kamd` | DOUBLE |  |
| `seq` | INTEGER |  |
| `doc_id` | VARCHAR |  |

### `v_mtef` (view, 2,191 rows)

Medium-term expenditure programmes (MTEF): forecasts of revenues, expenditures and financing for each of the three years, thousand AMD.

| column | type | description |
|---|---|---|
| `mtef_first_year` | INTEGER |  |
| `value_year` | INTEGER |  |
| `statement` | VARCHAR |  |
| `line_code` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `class_code` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `label_en` | VARCHAR |  |
| `label_ru` | VARCHAR |  |
| `total_kamd` | DOUBLE |  |
| `admin_kamd` | DOUBLE |  |
| `fund_kamd` | DOUBLE |  |
| `seq` | INTEGER |  |
| `doc_id` | VARCHAR |  |

### `v_program_budget` (view, 14,818 rows)

Programme budget (budget message tables for 2025+ and medium-term programmes): amounts by unit, functional class, programme, measure and economic article, with names in hy / en / ru, thousand AMD. Totals by measure: row_type = 'measure'; by article: row_type = 'economic'.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `doc_type` | VARCHAR |  |
| `value_year` | INTEGER |  |
| `district_code` | VARCHAR |  |
| `district_en` | VARCHAR |  |
| `district_ru` | VARCHAR |  |
| `row_type` | VARCHAR |  |
| `func_code` | VARCHAR |  |
| `func_name_en` | VARCHAR |  |
| `program_code` | VARCHAR |  |
| `program_hy` | VARCHAR |  |
| `program_en` | VARCHAR |  |
| `program_ru` | VARCHAR |  |
| `measure_code` | VARCHAR |  |
| `measure_hy` | VARCHAR |  |
| `measure_en` | VARCHAR |  |
| `measure_ru` | VARCHAR |  |
| `econ_code` | VARCHAR |  |
| `econ_hy` | VARCHAR |  |
| `econ_en` | VARCHAR |  |
| `econ_ru` | VARCHAR |  |
| `label_hy` | VARCHAR |  |
| `amount_kamd` | DOUBLE |  |
| `doc_id` | VARCHAR |  |
| `file_id` | VARCHAR |  |
| `seq` | INTEGER |  |

### `v_summary` (view, 10 rows)

Total revenues and expenditures by year: the approved budget (budget decision) and the approved / revised / actual figures of the annual execution report, thousand AMD.

| column | type | description |
|---|---|---|
| `fiscal_year` | INTEGER |  |
| `revenue_budget_kamd` | DOUBLE |  |
| `expenditure_budget_kamd` | DOUBLE |  |
| `revenue_approved_kamd` | DOUBLE |  |
| `revenue_revised_kamd` | DOUBLE |  |
| `revenue_actual_kamd` | DOUBLE |  |
| `expenditure_approved_kamd` | DOUBLE |  |
| `expenditure_revised_kamd` | DOUBLE |  |
| `expenditure_actual_kamd` | DOUBLE |  |

