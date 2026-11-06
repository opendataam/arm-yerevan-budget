-- DuckDB schema of the Yerevan city budget database.
-- Table prefixes:
--   meta_  provenance: site pages, documents, files (archive members)
--   dim_   reference dimensions with names in Armenian (hy), English (en) and Russian (ru)
--   fact_  normalised facts parsed from the budget tables
--   stg_   staging: every logical row of every recognised budget table (before interpretation)
--   raw_   lossless dump: text of every page, every table cell and spreadsheet cell
--   qc_    data quality checks (created by the build, sql/qc.sql)
-- Amounts are in thousand AMD (as in the source documents): columns *_kamd.
-- Comments on every table and column are stored in the database catalog
-- (duckdb_tables() / duckdb_columns()) and rendered into docs/data_dictionary.md.

------------------------------------------------------------------------------
-- metadata / provenance
------------------------------------------------------------------------------
CREATE TABLE meta_page (
    slug         VARCHAR PRIMARY KEY,
    url          VARCHAR,
    page_group   VARCHAR,
    year         INTEGER,
    title_hy     VARCHAR,
    title_en     VARCHAR,
    fetched_at   TIMESTAMP,
    sha256       VARCHAR,
    n_documents  INTEGER
);
COMMENT ON TABLE meta_page IS 'Pages of the "Finance" section of yerevan.am (https://www.yerevan.am/hy/finance/) that were crawled.';
COMMENT ON COLUMN meta_page.slug IS 'Page path segment: https://www.yerevan.am/hy/<slug>/';
COMMENT ON COLUMN meta_page.page_group IS 'core (city budget documents) | institutions (documents of municipal institutions and companies) | link';
COMMENT ON COLUMN meta_page.year IS 'Year of an archive page (archive-documents-of-<year>)';
COMMENT ON COLUMN meta_page.sha256 IS 'Hash of the downloaded HTML';

CREATE TABLE meta_document (
    doc_id                VARCHAR PRIMARY KEY,
    doc_group             VARCHAR,
    url                   VARCHAR,
    file_name             VARCHAR,
    ext                   VARCHAR,
    title_hy              VARCHAR,
    title_en              VARCHAR,
    title_ru              VARCHAR,
    doc_type              VARCHAR,
    fiscal_year           INTEGER,
    period                VARCHAR,
    institution_group_hy  VARCHAR,
    institution_group_en  VARCHAR,
    institution_group_ru  VARCHAR,
    size_mb_stated        DOUBLE,
    size_bytes            BIGINT,
    sha256                VARCHAR,
    downloaded_at         TIMESTAMP,
    duplicate_of          VARCHAR,
    is_primary            BOOLEAN,
    n_files               INTEGER,
    pages                 VARCHAR[]
);
COMMENT ON TABLE meta_document IS 'Every document linked from the Finance pages (one row per distinct URL). Core documents are downloaded and parsed; documents of municipal institutions are catalogued (downloaded only with fetch --institutions, not parsed).';
COMMENT ON COLUMN meta_document.doc_id IS 'Stable id: first 10 hex digits of SHA-1 of the URL';
COMMENT ON COLUMN meta_document.doc_group IS 'core | institutions';
COMMENT ON COLUMN meta_document.title_hy IS 'Link text on the site (Armenian, numbering removed)';
COMMENT ON COLUMN meta_document.doc_type IS 'Type of the document, see dim_doc_type';
COMMENT ON COLUMN meta_document.fiscal_year IS 'Budget year the document is about (MTEF: the first of its three years; institutions: the year heading on the page)';
COMMENT ON COLUMN meta_document.period IS 'Execution reports: Q1 | H1 | 9M | FY (see dim_period)';
COMMENT ON COLUMN meta_document.institution_group_hy IS 'Institutions: group heading on the page (schools, kindergartens, sector of community companies, ...)';
COMMENT ON COLUMN meta_document.size_mb_stated IS 'Size stated in the link text on the site, MB (institutions)';
COMMENT ON COLUMN meta_document.size_bytes IS 'Size of the downloaded file';
COMMENT ON COLUMN meta_document.duplicate_of IS 'doc_id of a document with byte-identical content published under another URL';
COMMENT ON COLUMN meta_document.is_primary IS 'TRUE for the document whose facts are used by the v_* views when several documents cover the same type / year / period (duplicates and re-publications)';
COMMENT ON COLUMN meta_document.pages IS 'Slugs of the pages that link the document';

CREATE TABLE meta_file (
    file_id                  VARCHAR PRIMARY KEY,
    doc_id                   VARCHAR NOT NULL,
    member                   VARCHAR,
    ext                      VARCHAR,
    size_bytes               BIGINT,
    sha256                   VARCHAR,
    kind                     VARCHAR,
    n_pages                  INTEGER,
    n_sheets                 INTEGER,
    n_tables                 INTEGER,
    legacy_font_conversions  INTEGER,
    glyph_mapped_spans       INTEGER,
    extract_error            VARCHAR,
    duplicate_of_file        VARCHAR,
    n_rows_parsed            INTEGER,
    n_unmapped_tables        INTEGER
);
COMMENT ON TABLE meta_file IS 'Files of the core documents: the downloaded file itself or every member of a downloaded rar / zip archive.';
COMMENT ON COLUMN meta_file.file_id IS '<doc_id> for a plain file, <doc_id>/<path in the archive> for an archive member';
COMMENT ON COLUMN meta_file.kind IS 'pdf | sheet (xls, xlsx, Excel 2003 XML) | text (doc, docx) | NULL (not parsed: images, unknown formats)';
COMMENT ON COLUMN meta_file.n_tables IS 'PDF: tables detected on all pages; spreadsheets: sheets';
COMMENT ON COLUMN meta_file.legacy_font_conversions IS 'Text pieces converted from the legacy Armenian 8-bit font encoding (ArmSCII-8 / Arial Armenian) to Unicode';
COMMENT ON COLUMN meta_file.glyph_mapped_spans IS 'PDF text pieces recovered from glyph ids through the cmap of the embedded font (fonts without a ToUnicode table)';
COMMENT ON COLUMN meta_file.duplicate_of_file IS 'file_id of an identical file (same sha256) parsed earlier; its rows are not parsed again';
COMMENT ON COLUMN meta_file.n_rows_parsed IS 'Logical rows of budget tables found in the file (stg_table_row)';
COMMENT ON COLUMN meta_file.n_unmapped_tables IS 'Tables with numbers whose column layout could not be determined (not in stg_table_row; their cells are in raw_table_cell)';

------------------------------------------------------------------------------
-- dimensions
------------------------------------------------------------------------------
CREATE TABLE dim_doc_type (doc_type VARCHAR PRIMARY KEY, name_en VARCHAR, name_ru VARCHAR, name_hy VARCHAR);
COMMENT ON TABLE dim_doc_type IS 'Types of documents (meta_document.doc_type).';

CREATE TABLE dim_period (period VARCHAR PRIMARY KEY, months INTEGER, name_en VARCHAR, name_ru VARCHAR, name_hy VARCHAR);
COMMENT ON TABLE dim_period IS 'Reporting periods; values are cumulative from 1 January.';

CREATE TABLE dim_statement (statement VARCHAR PRIMARY KEY, name_en VARCHAR, name_ru VARCHAR, name_hy VARCHAR);
COMMENT ON TABLE dim_statement IS 'Statements (parts) of the budget forms: revenues, expenditures by functional / economic classification, balance, financing, detailed programme tables.';

CREATE TABLE dim_scenario (scenario VARCHAR PRIMARY KEY, name_en VARCHAR, name_ru VARCHAR, name_hy VARCHAR);
COMMENT ON TABLE dim_scenario IS 'Meaning of an amount column: approved plan, revised plan, actual, draft, forecast, plan for the period.';

CREATE TABLE dim_budget_part (budget_part VARCHAR PRIMARY KEY, name_en VARCHAR, name_ru VARCHAR, name_hy VARCHAR);
COMMENT ON TABLE dim_budget_part IS 'Parts of a community budget: administrative (current) part, fund (capital) part, total.';

CREATE TABLE dim_district (
    district_code VARCHAR PRIMARY KEY, name_hy VARCHAR, name_en VARCHAR, name_ru VARCHAR, sort_order INTEGER
);
COMMENT ON TABLE dim_district IS 'Administrative districts of Yerevan and the Municipality itself: units of the detailed tables of the budget (appendix 7 of the budget decision, programme budget tables).';

CREATE TABLE dim_functional (
    func_code     VARCHAR PRIMARY KEY,
    func_section  VARCHAR,
    func_group    VARCHAR,
    func_class    VARCHAR,
    level         VARCHAR,
    name_hy       VARCHAR,
    name_en       VARCHAR,
    name_ru       VARCHAR,
    first_year    INTEGER,
    last_year     INTEGER
);
COMMENT ON TABLE dim_functional IS 'Functional classification of budget expenditures (section.group.class) as used in the documents; names from the most recent document.';
COMMENT ON COLUMN dim_functional.func_code IS 'SS.G.C, e.g. 09.1.1 (section 09 Education, group 1, class 1); 09.0.0 = the section, 09.1.0 = the group';
COMMENT ON COLUMN dim_functional.level IS 'section | group | class';

CREATE TABLE dim_economic (
    econ_code   VARCHAR PRIMARY KEY,
    kind        VARCHAR,
    name_hy     VARCHAR,
    name_en     VARCHAR,
    name_ru     VARCHAR,
    first_year  INTEGER,
    last_year   INTEGER
);
COMMENT ON TABLE dim_economic IS 'Article codes printed next to the lines: economic classification of expenditures (4xxx–6xxx: 4111 wages, 5113 capital repair, ...), revenue articles (7xxx) and financing articles (8xxx–9xxx); names from the most recent document.';
COMMENT ON COLUMN dim_economic.kind IS 'revenue | expenditure | financing (statement the code is used in)';

CREATE TABLE dim_line (
    statement    VARCHAR NOT NULL,
    line_code    VARCHAR NOT NULL,
    class_code   VARCHAR,
    func_code    VARCHAR,
    name_hy      VARCHAR,
    name_en      VARCHAR,
    name_ru      VARCHAR,
    first_year   INTEGER,
    last_year    INTEGER,
    n_names      INTEGER,
    PRIMARY KEY (statement, line_code)
);
COMMENT ON TABLE dim_line IS 'Lines (Տողի NN) of the standard community budget forms by statement; names (without the formulas) from the most recent document.';
COMMENT ON COLUMN dim_line.class_code IS 'Revenue article / economic article code printed next to the line (most recent)';
COMMENT ON COLUMN dim_line.n_names IS 'Number of different Armenian names the line had over the years';

CREATE TABLE dim_translation (
    context  VARCHAR,
    key      VARCHAR,
    hy       VARCHAR,
    en       VARCHAR,
    ru       VARCHAR,
    PRIMARY KEY (context, key)
);
COMMENT ON TABLE dim_translation IS 'Translation dictionaries hy -> en / ru (data/translations/<context>.csv); key = Armenian text reduced to letters and digits.';

------------------------------------------------------------------------------
-- staging and facts
------------------------------------------------------------------------------
CREATE TABLE stg_table_row (
    file_id        VARCHAR NOT NULL,
    seq            INTEGER NOT NULL,
    page           INTEGER,
    sheet          VARCHAR,
    appendix       INTEGER,
    section_no     INTEGER,
    table_no       INTEGER,
    table_title    VARCHAR,
    line_code      VARCHAR,
    func_section   VARCHAR,
    func_group     VARCHAR,
    func_class     VARCHAR,
    class_code     VARCHAR,
    label_raw      VARCHAR,
    amount_text    VARCHAR[],
    headers        VARCHAR[],
    PRIMARY KEY (file_id, seq)
);
COMMENT ON TABLE stg_table_row IS 'Every logical row of every budget table recognised in the files (tables anchored by a row of column numbers), before interpretation. Label lines continued on following rows are merged.';
COMMENT ON COLUMN stg_table_row.seq IS 'Order of the row in the file';
COMMENT ON COLUMN stg_table_row.appendix IS 'Appendix number (Հավելված N) in force on the page';
COMMENT ON COLUMN stg_table_row.section_no IS 'Section number (Հատված N) of the execution report form';
COMMENT ON COLUMN stg_table_row.table_no IS 'Table number (Աղյուսակ N) in force on the page';
COMMENT ON COLUMN stg_table_row.table_title IS 'Upper-case title lines at the top of the page';
COMMENT ON COLUMN stg_table_row.amount_text IS 'Text of the amount cells, left to right';
COMMENT ON COLUMN stg_table_row.headers IS 'Header text of the amount columns, left to right';

CREATE TABLE fact_budget_line (
    doc_id         VARCHAR NOT NULL,
    file_id        VARCHAR NOT NULL,
    seq            INTEGER NOT NULL,
    col_no         INTEGER NOT NULL,
    page           INTEGER,
    doc_type       VARCHAR,
    fiscal_year    INTEGER,
    report_period  VARCHAR,
    statement      VARCHAR,
    row_type       VARCHAR,
    appendix       INTEGER,
    district_code  VARCHAR,
    line_code      VARCHAR,
    func_code      VARCHAR,
    class_code     VARCHAR,
    program_hy     VARCHAR,
    label_hy       VARCHAR,
    scenario       VARCHAR,
    value_year     INTEGER,
    value_period   VARCHAR,
    budget_part    VARCHAR,
    amount_kamd    DOUBLE,
    amount_text    VARCHAR,
    PRIMARY KEY (file_id, seq, col_no)
);
COMMENT ON TABLE fact_budget_line IS 'All amounts of the budget tables in long form: one row per table row x amount column. Use the v_* views for ready-made selections (they keep only the primary document of each type / year / period).';
COMMENT ON COLUMN fact_budget_line.seq IS 'Row of the table (stg_table_row.seq)';
COMMENT ON COLUMN fact_budget_line.col_no IS 'Amount column, 1-based, left to right';
COMMENT ON COLUMN fact_budget_line.report_period IS 'Period of the document (execution reports)';
COMMENT ON COLUMN fact_budget_line.statement IS 'See dim_statement';
COMMENT ON COLUMN fact_budget_line.row_type IS 'line (a line of a standard statement); in expenditure_program tables: total | functional | program | economic';
COMMENT ON COLUMN fact_budget_line.appendix IS 'Appendix number of the document the row comes from';
COMMENT ON COLUMN fact_budget_line.district_code IS 'Detailed tables by district (appendix 7 of the budget, programme tables): see dim_district; NULL = the city total';
COMMENT ON COLUMN fact_budget_line.line_code IS 'Line number of the form (Տողի NN), see dim_line';
COMMENT ON COLUMN fact_budget_line.func_code IS 'Functional classification code SS.G.C (expenditure rows), see dim_functional; for program / economic rows of the detailed tables: the class they belong to';
COMMENT ON COLUMN fact_budget_line.class_code IS 'Article code printed in the row: revenue article (71xx–74xx), economic article (4xxx–6xxx), financing article (9xxx); see dim_economic';
COMMENT ON COLUMN fact_budget_line.program_hy IS 'Detailed tables: the programme / measure the economic row belongs to';
COMMENT ON COLUMN fact_budget_line.label_hy IS 'Name of the row in Armenian without the formulas (տող ... + տող ...) and the words "including"';
COMMENT ON COLUMN fact_budget_line.scenario IS 'See dim_scenario';
COMMENT ON COLUMN fact_budget_line.value_year IS 'Year the amount refers to (differs from fiscal_year in medium-term programmes)';
COMMENT ON COLUMN fact_budget_line.value_period IS 'Period the amount refers to: FY, or Q1 / H1 / 9M (actual values of quarterly reports, quarterly plans)';
COMMENT ON COLUMN fact_budget_line.budget_part IS 'total | admin | fund (see dim_budget_part)';
COMMENT ON COLUMN fact_budget_line.amount_kamd IS 'Amount, thousand AMD; NULL for "X" (not applicable) and empty cells, 0 for "-"';
COMMENT ON COLUMN fact_budget_line.amount_text IS 'Cell as printed in the source';

------------------------------------------------------------------------------
-- raw (lossless) data
------------------------------------------------------------------------------
CREATE TABLE raw_page_text (
    file_id   VARCHAR NOT NULL,
    page      INTEGER NOT NULL,
    text      VARCHAR,
    n_images  INTEGER,
    PRIMARY KEY (file_id, page)
);
COMMENT ON TABLE raw_page_text IS 'Text of every page of every PDF (Unicode, legacy fonts converted) and the full text of doc/docx files (page 1). Use for full-text search.';

CREATE TABLE raw_table_cell (
    file_id    VARCHAR NOT NULL,
    page       INTEGER,
    sheet      VARCHAR,
    table_no   INTEGER NOT NULL,
    row_no     INTEGER NOT NULL,
    col_no     INTEGER NOT NULL,
    value_text VARCHAR,
    value_num  DOUBLE
);
COMMENT ON TABLE raw_table_cell IS 'Every non-empty cell of every table detected in the PDFs (pdfplumber), of every docx table and of every spreadsheet sheet (0-based row / column numbers).';
COMMENT ON COLUMN raw_table_cell.table_no IS 'PDF: number of the table on the page (0-based); spreadsheet: sheet index; docx: table index';
COMMENT ON COLUMN raw_table_cell.value_num IS 'Numeric value of spreadsheet cells';

------------------------------------------------------------------------------
-- programme budgeting (tables "ԾԲ" of the budget message and of the MTEF)
------------------------------------------------------------------------------
CREATE TABLE dim_program (
    program_code  VARCHAR PRIMARY KEY,
    name_hy       VARCHAR,
    name_en       VARCHAR,
    name_ru       VARCHAR,
    goal_hy       VARCHAR,
    result_hy     VARCHAR,
    first_year    INTEGER,
    last_year     INTEGER
);
COMMENT ON TABLE dim_program IS 'Budget programmes of the programme budgeting tables (4-digit codes); names, goals and final results from the most recent document. Goals and results are in Armenian only.';

CREATE TABLE dim_measure (
    program_code    VARCHAR NOT NULL,
    measure_code    VARCHAR NOT NULL,
    name_hy         VARCHAR,
    name_en         VARCHAR,
    name_ru         VARCHAR,
    description_hy  VARCHAR,
    measure_type_hy VARCHAR,
    first_year      INTEGER,
    last_year       INTEGER,
    PRIMARY KEY (program_code, measure_code)
);
COMMENT ON TABLE dim_measure IS 'Measures (5-digit codes, unique within a programme) of the programme budgeting tables; descriptions and types in Armenian only.';

CREATE TABLE fact_program_budget (
    doc_id         VARCHAR NOT NULL,
    file_id        VARCHAR NOT NULL,
    seq            INTEGER NOT NULL,
    col_no         INTEGER NOT NULL,
    page           INTEGER,
    doc_type       VARCHAR,
    fiscal_year    INTEGER,
    district_code  VARCHAR,
    row_type       VARCHAR,
    func_code      VARCHAR,
    program_code   VARCHAR,
    measure_code   VARCHAR,
    econ_code      VARCHAR,
    label_hy       VARCHAR,
    value_year     INTEGER,
    amount_kamd    DOUBLE,
    amount_text    VARCHAR,
    PRIMARY KEY (file_id, seq, col_no)
);
COMMENT ON TABLE fact_program_budget IS 'Programme budget, table 1: expenditures by functional class x programme x measure x economic article, for the city (district_code NULL), the Municipality and every district; one row per table row x year column, thousand AMD.';
COMMENT ON COLUMN fact_program_budget.row_type IS 'total | section | group | class (functional rows) | program | measure | economic | other';
COMMENT ON COLUMN fact_program_budget.func_code IS 'Functional class SS.G.C the row belongs to';
COMMENT ON COLUMN fact_program_budget.program_code IS 'Programme (dim_program) the row belongs to';
COMMENT ON COLUMN fact_program_budget.measure_code IS 'Measure (dim_measure) of measure and economic rows';
COMMENT ON COLUMN fact_program_budget.econ_code IS 'Economic article of economic rows (dim_economic)';
COMMENT ON COLUMN fact_program_budget.value_year IS 'Year of the amount column (the budget year; three years in an MTEF)';

CREATE TABLE fact_program_indicator (
    doc_id        VARCHAR NOT NULL,
    file_id       VARCHAR NOT NULL,
    seq           INTEGER NOT NULL,
    page          INTEGER,
    doc_type      VARCHAR,
    fiscal_year   INTEGER,
    program_code  VARCHAR,
    measure_code  VARCHAR,
    indicator_hy  VARCHAR,
    value_text    VARCHAR,
    value_num     DOUBLE,
    PRIMARY KEY (file_id, seq)
);
COMMENT ON TABLE fact_program_indicator IS 'Programme budget, table 2: performance indicators of the measures and their target values (as printed; value_num when numeric).';
