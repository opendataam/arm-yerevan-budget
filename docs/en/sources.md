# Sources

**English** | [Հայերեն](../hy/sources.md) | [Русский](../ru/sources.md)

## The website

The Yerevan Municipality publishes the documents of the city budget in the section "Finance"
(«Ֆինանսներ») of its website: <https://www.yerevan.am/hy/finance/>. The section exists only in Armenian: the
English and Russian versions of the page (`/en/finance/`, `/ru/finance/`) say "The content is available only in
Armenian version".

The section consists of the main page and sub pages linked from it:

| page (`https://www.yerevan.am/hy/<slug>/`) | contents | group |
|---|---|---|
| `finance` | documents of the current year (2026) | core |
| `archive-documents-of-2018` … `archive-documents-of-2022`, `finance-archive-documents-of-2023` … `-2025` | archive of earlier years (the same document may be linked from two pages) | core |
| `byowje-bolori-hamar` | "Budget for everyone" – a citizens' budget brochure | core |
| `finance-docs` | annual financial documents of state and community non-commercial organisations subordinate to the Municipality (schools, kindergartens, music, art and sports schools, …): budget estimates, revised estimates, actual execution, staff lists, 2014–2026 | institutions |
| `finance-other-docs` | the same for community closed joint-stock companies by sector (health, utilities, sport and culture, transport, IT, urban development), 2025–2026 | institutions |
| `interactive-budget` | a link to the "interactive budget" <http://budget.yerevan.am/> (was not reachable at the time of collection) | link |

Every document is a plain link (`<a href>`) to a file: PDF, RAR / ZIP archives (with PDF, DOC/DOCX, XLS/XLSX
inside), XLS. There are no document identifiers or metadata on the site except the link text; the pipeline
classifies the documents by their titles (see [documents.md](documents.md)).

* **Core documents** – 88 distinct documents (≈176 MB, 214 files after unpacking the archives), 2017–2027.
  They are downloaded, unpacked and parsed into the database.
* **Documents of municipal institutions** – 422 RAR archives of ≈10.6 GB. They are listed in the catalog and
  in `meta_document` (group heading, year, title, size stated on the site), and can be downloaded with
  `python -m yerevan_budget fetch --institutions` (`make fetch-institutions`); they are not parsed: they contain
  scanned and Excel estimates of hundreds of individual institutions in different layouts.

## Kinds of documents

| type (`doc_type`) | what it is | years | format |
|---|---|---|---|
| `budget` | Decision of the Council of Elders on the budget of the year with its appendices 1–7 | 2018–2026 | PDF (one file for 2018–2019; separate files per appendix since 2020) |
| `budget_draft` | Draft budget submitted to public discussion | 2019, 2020 | PDF |
| `budget_amendment` | Decisions amending the budget | 2018, 2019 | PDF |
| `budget_message` | Budget message of the Mayor; since 2025 with the programme-budget tables (ԾԲ) in Excel | 2018–2026 | PDF, DOCX, XLSX |
| `execution_measures` | Decision of the Mayor on the measures ensuring the execution of the budget: quarterly breakdown of revenues and expenditures, by district | 2018–2026 | PDF |
| `execution_report` | Reports on the execution of the budget: quarterly (Q1, January–June, January–September) and annual, in the standard form Հ-9 of the Ministry of Finance; annual explanatory notes ("Տեղեկանք-հիմնավորում") | 2017–2026 | XLS (2018–2020), PDF |
| `report_approval` | Council decision approving the annual report | 2017 | PDF |
| `mtef` | Medium-term expenditure programme for three years (forecasts by the same forms; programme-budget tables) | 2023–2027 | PDF, XLS (Excel 2003 XML), DOCX |
| `citizens_budget` | "Budget for everyone" brochure, summary booklet | 2018, 2026 | PDF |
| `staff_list` | Staff lists of the Municipality | 2019 | PDF |
| `other` | Information on kindergartens, sports, music and art schools | 2019 | PDF |

## Formats and their quirks

* **Legacy Armenian fonts.** Most of the appendices and many reports were typed in the 8-bit fonts
  "Arial Armenian" / "Times Armenian" (ArmSCII-8 layout): the text layer of the PDF and the cells of the XLS
  files contain Latin-1 characters (`Ð³í»Éí³Í` instead of `Հավելված`). The extraction converts every such
  piece to Unicode ([`parsers/armscii.py`](../../src/yerevan_budget/parsers/armscii.py)); `0xA8` is `և` in these fonts.
  Unicode and legacy fonts are mixed even within one page, so the decision is made per text piece / cell.
* **Fonts without a Unicode map.** The report for January–September 2021 is typed in GHEA Grapalat embedded as a
  CID font without a ToUnicode table: text extraction returns glyph numbers. The extraction rebuilds the map from
  the `cmap` of the embedded font program (fontTools).
* **Bold faked by double printing** (every character printed twice) – removed with pdfplumber `dedupe_chars`.
* **Text drawn as images.** In the appendices of the 2025–2027 medium-term programme the names of the lines are
  images; only codes and numbers are text. The rows are parsed, the names are taken from the line codes.
* **Excel 2003 XML** saved with the `.xls` extension (MTEF 2024–2026) – read as SpreadsheetML.
* **Duplicates.** The same file is sometimes published under two URLs (`meta_document.duplicate_of`), and the same
  report appears in two documents (e.g. a report and a re-published "annual report"); identical files are parsed
  once and the views use one primary document per type / year / period (`meta_document.is_primary`).
* **Units.** All amounts are in thousand AMD (as in the documents). Negative amounts are printed with a minus or in
  parentheses; `X` means "not applicable" (stored as NULL), `-` means zero.
* **Periods.** Quarterly reports are cumulative from 1 January: `Q1` January–March, `H1` January–June, `9M`
  January–September, `FY` the year.

## The budget forms

All tables follow the standard forms of the community budgets (order of the Minister of Finance, form Հ-9):

* **revenues** (lines `1000`–`1393`, with 5-digit sub-lines `11301`…, `13501`… for local duties and fees) and the
  revenue article codes (`7100` taxes and duties, `7131` property taxes on real estate, …);
* **expenditures by functional classification** (lines `2000`–`3xxx`; section / group / class codes, e.g.
  `09 1 1` – pre-school education);
* **expenditures by economic classification** (lines `4000`–`6xxx`; article codes `4111` wages, `5113` capital
  repair of buildings, …);
* **surplus / deficit** (line `7000` in the reports, `8000` in the budget decision) and **its financing**
  (lines `8000`/`8010`–`8xxx`, articles `9xxx`);
* columns for the **administrative part** (current budget) and the **fund part** (capital budget) and their total.

The detailed tables (appendix 6 of the budget: functional class × programme × economic article; appendix 7: the
same for the Municipality and each of the 12 administrative districts) and the programme-budget tables (since 2025,
with codes of programmes and measures and performance indicators) give the allocation below the classification.

See [documents.md](documents.md) for the contents of each document and [database.md](database.md) for how they are
stored.
