# Contents of the documents

**English** | [Հայերեն](../hy/documents.md) | [Русский](../ru/documents.md)

What is inside each kind of document and how it ends up in the database. The full list of documents with links
is in [inventory.md](inventory.md).

## Budget of the city (`budget`)

Decision of the Council of Elders "On the budget of Yerevan for <year>" (2018–2026). Since 2020 the appendices are
separate PDF files in a RAR / ZIP archive (`1.pdf` … `7.pdf`), with the text of the decision as DOC / DOCX.

| appendix | contents | statement in the database |
|---|---|---|
| 1 | revenues of the administrative and fund parts by source | `revenue` |
| 2 | expenditures by functional classification (sections, groups, classes) | `expenditure_functional` |
| 3 | expenditures by economic classification | `expenditure_economic` |
| 4 | surplus / deficit (line 8000) | `balance` |
| 5 | directions of the use of the surplus / sources of financing of the deficit | `financing` |
| 6 | expenditures by functional class, programme and economic article (city total) | `expenditure_program`, `district_code` NULL |
| 7 | the allocation of appendix 6 by unit: table 1 – the Municipality (without the districts), tables 2–13 – the 12 administrative districts | `expenditure_program`, `district_code` = unit |

Columns: total, administrative part, fund part (`scenario = 'approved'`). Views: `v_budget_approved`
(appendices 1–5), `v_budget_program` (appendices 6–7).

## Execution reports (`execution_report`)

Reports "on the execution of the community budget" in the form Հ-9 (Q1, January–June, January–September, year),
2017–2026. For 2018–2020 the quarterly reports are XLS files with one sheet per section of the form; later they
are PDF. Sections of the form:

| section | contents | statement |
|---|---|---|
| 1 | revenues | `revenue` |
| 2 | expenditures by functional classification | `expenditure_functional` |
| 3 | expenditures by economic classification | `expenditure_economic` |
| 4 | surplus / deficit (line 7000) | `balance` |
| 5 | financing of the deficit | `financing` |
| 6 (some reports) | expenditures by functional class × programme × economic article | `expenditure_program` |

Columns: approved annual plan, revised annual plan, actual (cumulative from 1 January) – each as total,
administrative part, fund part (9 amount columns). View: `v_execution` (and `v_execution_annual`).

The annual "reports" of 2020–2025 published as "Տեղեկանք-հիմնավորում" (explanatory note) are narrative documents
with their own analytic tables; their text is in `raw_page_text` and their cells in `raw_table_cell`, and the
form Հ-9 of the year comes from the separate document "Report on the execution of the community budget …
31.12.<year>" where it exists. For 2020 only the explanatory note was published (it contains the expenditure
tables of the form, but not the revenues).

## Measures ensuring the execution of the budget (`execution_measures`)

Decision of the Mayor issued in January (2018–2026), appendices 1–11 with the quarterly (cumulative) proportions
of the annual plan – year, Q1, January–June, January–September:

| appendix | contents |
|---|---|
| 1 | revenues by source |
| 2 | revenues by source, tables by responsible unit |
| 3, 4 | expenditures by functional and by economic classification |
| 5, 6 | deficit and its financing |
| 7, 8 | detailed allocation (functional class × programme × economic article); appendix 8 – by unit (Municipality, districts) |
| 9 | revenues from the sale of property and land by responsible unit |
| 10 | grants and subsidies by programme and economic article |
| 11 | programmes co-financed by international organisations |

Columns: total; administrative part for the year and the three periods; fund part for the year and the three
periods (`scenario` `approved` for the year, `plan_period` for the periods).

The tables of appendices 2 and 10 have a broken row of column numbers in the PDF text layer and are partly parsed;
all their cells are in `raw_table_cell`.

## Medium-term expenditure programmes (`mtef`)

Decisions of the Council approving the programme for the next three years (2023–2025 … 2027–2029). Appendices
2–7 repeat the forms of the budget (revenues, functional and economic classification, financing, detailed
allocation) with three year columns (`scenario = 'forecast'`, `value_year` = the year); since 2026–2028 they also
include the programme-budget tables. View: `v_mtef`.

## Budget message of the Mayor (`budget_message`)

A narrative document (PDF / DOCX). For 2025 and 2026 it comes with two Excel tables in the programme-budgeting
format ("ԾԲ"):

* **table 1** – allocation by functional class, programme (4-digit code), measure (5-digit code) and economic
  article, one sheet per unit (city, Municipality, 12 districts), with the goal of each programme, its final
  result, the description and the type of each measure → `fact_program_budget`, `dim_program`, `dim_measure`;
* **table 2** – performance indicators of each measure and their target values → `fact_program_indicator`.

The same tables are attached to the medium-term programmes 2026–2028 and 2027–2029 (PDF).

## Other documents

Budget drafts and amendments (2018–2020) have the same forms as the budget and are parsed the same way
(`scenario` `draft` / `change`). Citizens' budget brochures, staff lists, information on schools and kindergartens,
council decisions and the text parts of all documents are kept as text (`raw_page_text`, full-text search) and
cells (`raw_table_cell`).

## How tables are recognised

1. Every page of every PDF is read with PyMuPDF (text) and pdfplumber (tables); every sheet of XLS / XLSX
   (and of Excel 2003 XML) cell by cell; DOCX paragraphs and tables, DOC as text. The result is cached in
   `data/interim/<sha256>.json.gz`.
2. A budget table is anchored by its **row of column numbers** (`1, 2, 3, …`). It tells which physical columns of
   the extracted table form a logical column (PDF tables often split a column or a code like `2100` into `2` and
   `100`). Tables on continuation pages reuse the layout of the previous table of the same width.
3. The role of each column is determined from its content: line code, parts of the functional code, name, article
   code, amounts. Name lines continued on the next physical rows are merged.
4. The statement of a row follows from its line code; the meaning of each amount column (scenario, year, period,
   part of the budget) from the header text and the document type ([`parsers/semantics.py`](../../src/yerevan_budget/parsers/semantics.py)).
5. The programme-budget tables have no column numbers and are read by a separate parser
   ([`parsers/program_tables.py`](../../src/yerevan_budget/parsers/program_tables.py)).

All logical rows are kept in `stg_table_row` (with the header text of the amount columns), so the interpretation
can be checked against the source.
