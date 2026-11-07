# Data quality

**English** | [Հայերեն](../hy/data_quality.md) | [Русский](../ru/data_quality.md)

The build runs the checks of [`sql/qc.sql`](../../sql/qc.sql) and stores the results in `qc_summary` and the
`qc_*` tables:

```sql
SELECT * FROM qc_summary ORDER BY check_name;
```

| check | what it verifies | expected |
|---|---|---|
| `revenue_total_equals_parts` | revenue total (line 1000) = taxes (1100) + grants (1200) + other revenues (1300), for every amount column of every table | OK; failures point to rows lost by the extraction (`qc_revenue_total`) |
| `functional_total_equals_sections` | expenditure total (line 2000) = sum of the functional sections | OK (`qc_functional_total`) |
| `functional_equals_economic` | totals by functional (2000) and economic (4000) classification are equal | OK (`qc_functional_vs_economic`) |
| `total_equals_admin_plus_fund` | total = administrative part + fund part in every row | INFO: differs by design for the lines of the transfer from the reserve fund of the administrative part to the fund part (lines 1390–1393, 3110–3112, 4050, 4770–4772 and the totals that include them) – the transfer is counted in both parts (`qc_parts`) |
| `program_city_equals_units` | total of appendix 6 of the budget (city) = sum of the tables of appendix 7 (Municipality + 12 districts) | OK (`qc_program_districts`) |
| `report_approved_equals_budget` | the "approved plan" of the annual report = the budget decision for lines 1000, 1100, 1200, 1300, 4000 | OK (`qc_report_vs_budget`) |
| `documents_with_facts` | every budget, execution report, MTEF and execution-measures document gave facts | the annual explanatory notes 2023–2025 have no form tables (their form Հ-9 is a separate document) |
| `files_extracted` | every file could be read | OK |
| `tables_with_unknown_layout` | tables with numbers that have no row of column numbers | INFO: budget messages, explanatory notes, staff lists, parts of the execution measures – their cells are in `raw_table_cell` |
| `translations_complete` | every name has a translation into every language (en, ru, fr, es, pt, de, ar, fa) | see [translations.md](translations.md) |

`qc_coverage` lists the core documents by type and year and how many amounts each gave.

## Known issues of the sources and of the parsing

* **The interactive budget** <http://budget.yerevan.am/> linked from the section did not respond during the
  collection; it is not part of the data.
* **2020 annual report.** Only the explanatory note was published; it contains the expenditure tables of the form
  but not the revenues, so `v_summary` has no revenues for 2020.
* **2026** – the annual report is not yet published (the data end with January–September 2026).
* **Rows lost at page breaks.** In a few PDF reports a row that starts at the bottom of a page is cut by the table
  detection (e.g. line 1200 "official grants" in the reports for January–June and January–September 2026, line
  1300 in the report for January–June 2022). The QC tables show the affected columns; the values can be read from
  `raw_page_text`.
* **Names drawn as images** in the appendices of the 2025–2027 medium-term programme: the rows have codes and
  amounts but no names (`label_hy` NULL); the views show the name of the line code.
* **Execution measures, appendices 2 and 10**: the row of column numbers is broken in the text layer; most of these
  tables are not interpreted (only `raw_table_cell`).
* **2018 execution measures** (`f6053241d4`) is a scan with a poor text layer: only part of its tables are parsed.
* **Garbled names.** Names that wrap over several lines are sometimes cut or glued to the next row by the table
  detection in the older PDFs (2017–2019); the codes and amounts are not affected, and the views fall back to the
  name of the code when the garbled name has no translation.
* **Rounding.** The documents round to 0.1 thousand AMD; sums are compared with a tolerance of 1 thousand AMD.
* **Legacy fonts.** The conversion from the 8-bit Armenian fonts is exact for the letters; a few rare punctuation
  signs of these fonts may be mapped imprecisely.
* **Institutional documents** (≈10.6 GB) are catalogued only.
