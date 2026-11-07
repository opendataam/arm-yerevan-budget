# Yerevan city budget: documents of the Municipality in DuckDB

**English** | [Հայերեն](README.hy.md) | [Русский](README.ru.md)

Collection, normalisation and documentation of the data on the planning and execution of the **budget of the city
of Yerevan** published by the Yerevan Municipality in the section "Finance" («Ֆինանսներ») of its website:
<https://www.yerevan.am/hy/finance/>.

The section is available only in Armenian and consists of files (PDF, RAR/ZIP archives, XLS, DOC) linked from
the main page and the archive pages of 2018–2025. The pipeline collects **all of them**:

* **budgets of the city** 2018–2026 (decisions of the Council of Elders with appendices: revenues, expenditures by
  functional and economic classification, deficit and its financing, detailed allocation by programme and economic
  article for the city and each of the 12 districts), drafts and amendments;
* **execution reports** 2017–2026 (form Հ-9, quarterly and annual: approved plan, revised plan, actual);
* **measures ensuring the execution of the budget** 2018–2026 (quarterly breakdown of the plan);
* **medium-term expenditure programmes** 2023–2025 … 2027–2029 (three-year forecasts);
* **budget messages of the Mayor** with the **programme budget** tables (programmes, measures, performance
  indicators) for 2025–2026; citizens' budget brochures, staff lists and other documents;
* a catalogue of the **financial documents of municipal institutions and companies** (422 archives, ≈10.6 GB;
  downloaded on request, not parsed).

The result is the DuckDB database `data/yerevan_budget.duckdb`: ≈530 000 amounts in a long fact table with the
meaning of every column (scenario, year, period, part of the budget), the programme budget, classifiers with
**names in Armenian and eight translations** (English, Russian, French, Spanish, Portuguese, German, Arabic,
Persian), the full text of every page and every table cell of the source, data quality checks and documentation in
three languages.

## Ready-made data: releases

The database and the raw data are not stored in git. Each collection run is published as a repository **release**
([Releases](https://github.com/opendataam/arm-yerevan-budget/releases)) tagged `data-YYYY-MM-DD` — the collection
date; the tag points to the code commit the database was built with.

| release asset | contents |
|---|---|
| `yerevan_budget.duckdb.xz` | DuckDB database |
| `yerevan_budget-parquet.zip` | all tables and views as Parquet + data dictionary |
| `yerevan_budget-raw.tar.xz` | raw data: site pages, documents, unpacked archives (`raw/`), extracted text and tables (`interim/`), manifests (`catalog/`) |
| `SHA256SUMS` | checksums |

```bash
make install
make download            # latest release: database -> data/yerevan_budget.duckdb (SHA256 verified)
```

Other options: `make download-parquet`, `make download-raw` (then `make build` rebuilds the database without
touching the website), a specific snapshot — `make download TAG=data-2026-11-06`.

## Quick start: build everything yourself

```bash
make install   # creates .venv and installs the package (via uv if available; Python ≥ 3.10)
make all       # catalog → fetch → extract → build → docs  (≈10 minutes, mostly downloading)
```

Needs `unrar` (RAR archives) and `7zz`/`7z` or `bsdtar` (ZIP); `.doc` files are read with `textutil` (macOS) or
`soffice`. Step by step (in the activated environment: `source .venv/bin/activate`):

```bash
python -m yerevan_budget catalog   # Finance pages -> data/catalog/{pages,documents}.json
python -m yerevan_budget fetch     # documents -> data/raw/files, archives unpacked -> data/raw/extracted
python -m yerevan_budget extract   # text and tables of every file -> data/interim (cache)
python -m yerevan_budget build     # -> data/yerevan_budget.duckdb
python -m yerevan_budget docs      # -> docs/data_dictionary.md, docs/{en,hy,ru}/inventory.md
python -m yerevan_budget fetch --institutions   # optional: the ≈10 GB of institutional archives
```

Example query:

```bash
duckdb -readonly data/yerevan_budget.duckdb -c "
  SELECT fiscal_year, round(revenue_actual_kamd / 1e6, 1) AS revenue_bn_amd,
         round(expenditure_actual_kamd / 1e6, 1) AS expenditure_bn_amd
  FROM v_summary ORDER BY fiscal_year"
```

## Repository layout

```
├── README.md                  this file (English); README.hy.md — Armenian, README.ru.md — Russian
├── Makefile                   pipeline commands
├── pyproject.toml             yerevan_budget package (CLI: yerevan-budget)
├── src/yerevan_budget/
│   ├── config.py              paths, pages of the section, HTTP settings
│   ├── http.py                HTTP client: pauses, retries, streamed downloads
│   ├── catalog.py             step 1: crawl the pages, list the documents
│   ├── classify.py            type / year / period of a document from its title
│   ├── fetch.py               step 2: download, unpack archives
│   ├── extract.py             step 3: text and tables of PDF / XLS / XLSX / DOC / DOCX (legacy fonts, glyph maps)
│   ├── build.py               step 4: DuckDB build
│   ├── translations.py        hy -> en / ru / fr / es / pt / de / ar / fa dictionaries (data/translations)
│   ├── reference.py           districts of Yerevan
│   ├── docs.py, release.py    generated documentation; data snapshots in GitHub releases
│   ├── cli.py, __main__.py    command line
│   └── parsers/               page links, legacy Armenian fonts, budget tables, their semantics, programme budget
├── sql/
│   ├── schema.sql             tables + COMMENT ON (descriptions are stored in the database itself)
│   ├── dims.sql               dimensions derived from the facts
│   ├── views.sql              views
│   └── qc.sql                 data quality checks
├── data/
│   ├── catalog/               manifests (in git): pages.json, documents.json
│   ├── translations/          translation dictionaries hy -> 8 languages (in git) and GLOSSARY.md
│   ├── raw/                   downloaded pages, documents, unpacked archives (not in git; in releases)
│   ├── interim/               extracted text and tables (not in git; in releases)
│   └── yerevan_budget.duckdb  result (not in git; in releases)
├── docs/
│   ├── en/, hy/, ru/          documentation in English, Armenian and Russian
│   └── data_dictionary.md     all tables and columns (generated)
├── scripts/                   notebook runner and JupyterLab settings
└── tests/                     tests of the parsers, the documentation and the built database
```

## Documentation

The documentation is available in English ([docs/en](docs/en)), Armenian ([docs/hy](docs/hy)) and Russian
([docs/ru](docs/ru)).

| document | contents |
|---|---|
| [sources.md](docs/en/sources.md) | the website section, kinds of documents, formats and their quirks, the budget forms |
| [documents.md](docs/en/documents.md) | contents of each kind of document and how tables are recognised |
| [database.md](docs/en/database.md) | database design: principles, schema (ER), tables, views, example queries |
| [data_dictionary.md](docs/data_dictionary.md) | all tables and columns (generated) |
| [translations.md](docs/en/translations.md) | names in nine languages: languages, dictionaries, method, how to translate new names |
| [data_quality.md](docs/en/data_quality.md) | data quality checks and known issues |
| [inventory.md](docs/en/inventory.md) | list of documents (generated) |
| [maintenance.md](docs/en/maintenance.md) | updates, new documents, changes on the site, code layout |
| [examples.ipynb](docs/examples.ipynb) | Jupyter notebook with example queries and charts (`make lab`, `make notebook`; text in Russian) |

## Main tables

| table / view | contents |
|---|---|
| `v_execution`, `v_execution_annual` | execution reports: approved / revised plan and actual by line, part of the budget and period |
| `v_budget_approved` | the budget approved by the council: revenues, expenditures, deficit, financing |
| `v_budget_program` | detailed allocation: functional class × programme × economic article, city and districts |
| `v_program_budget` | programme budget (programmes and measures with codes) |
| `v_mtef` | medium-term forecasts |
| `v_summary` | totals by year |
| `fact_budget_line` | all amounts of the standard forms (long form) |
| `fact_program_budget`, `fact_program_indicator` | programme budget allocations and performance indicators |
| `dim_functional`, `dim_economic`, `dim_line`, `dim_program`, `dim_measure`, `dim_district`, `dim_label` | classifiers and names in hy and every translation language (`*_en` … `*_fa`) |
| `meta_document`, `meta_file` | documents and files with provenance |
| `raw_page_text`, `raw_table_cell`, `stg_table_row` | lossless source text, cells and table rows |

## Caveats

* Amounts are in thousand AMD, as in the documents (`*_kamd`). Execution data are cumulative from 1 January.
* Totals and subtotals are stored together with detail rows — select one level before summing.
* Several documents may cover the same year and period; the views use the primary one (`meta_document.is_primary`).
* The administrative and fund parts include the internal transfer from the reserve fund, so total ≠ admin + fund
  for a few lines (see [data_quality.md](docs/en/data_quality.md)).

## Source

Data: Yerevan Municipality, <https://www.yerevan.am/hy/finance/>. A licence for the repository code has not been
chosen yet.
