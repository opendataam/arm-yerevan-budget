# Maintenance

**English** | [Հայերեն](../hy/maintenance.md) | [Русский](../ru/maintenance.md)

## Regular update

On a new machine, first restore the raw data of the latest snapshot so that nothing is downloaded or extracted
again:

```bash
make install download-raw
```

Then:

```bash
make catalog fetch extract build docs test
git add -A && git commit -m "data: update to $(date +%F)" && git push
make release            # a new data-<collection date> release with the database, Parquet and raw data
```

* `catalog` crawls the Finance pages again. New documents are picked up automatically and classified by their
  titles; the changes of `data/catalog/documents.json` show up in `git diff` – a convenient way to see what was
  published.
* `fetch` downloads only missing documents (`--force` downloads all again) and unpacks the archives into
  `data/raw/extracted/<doc_id>/`; sizes and SHA-256 of files and archive members are stored in the catalog.
* `extract` reads the new files (PDF text and tables, spreadsheets, Word) into the cache `data/interim/`
  (identical files are read once; about 3 minutes for everything).
* `build` recreates the whole database (about 1 minute). Check `SELECT * FROM qc_summary` (see
  [data_quality.md](data_quality.md)).
* New names → [translations.md](translations.md) (`make translations`, fill, `make translations-merge`, `make build`).
* `release` requires a clean working tree, a pushed `HEAD` and `gh` with write access to
  `opendataam/arm-yerevan-budget`; the tag is `data-<date of the crawl>`.

The site publishes the quarterly reports about 1–2 months after the quarter, the budget of the next year in
December, the medium-term programme in September; a monthly update is enough.

## What to do if…

**A document gets the wrong type, year or period.** The rules are in
[`classify.py`](../../src/yerevan_budget/classify.py); add a rule or an entry to `OVERRIDES` (key: `doc_id`) and
add the title to `tests/test_parsers.py`.

**A new layout of a table is not recognised** (`tables_with_unknown_layout`, a document without facts in
`qc_coverage`). Look at the rows in `raw_table_cell` / `stg_table_row` of the file. Budget tables are anchored by the
row of column numbers ([`parsers/budget_tables.py`](../../src/yerevan_budget/parsers/budget_tables.py)); the meaning
of the amount columns comes from the header text and the document type
([`parsers/semantics.py`](../../src/yerevan_budget/parsers/semantics.py), `FACT_LAYOUTS` in `build.py`).

**Text comes out as `Ð³í»Éí³Í` or as glyph numbers.** Legacy fonts are converted by
[`parsers/armscii.py`](../../src/yerevan_budget/parsers/armscii.py); fonts without a Unicode map are recovered from
the embedded font in `extract.py` (`_glyph_maps`). After changing the extraction, increase `extract.VERSION` and run
`make extract build`.

**A sum check fails.** Find the document and column in the `qc_*` table, then the rows in `stg_table_row`
(`file_id`, `seq`) and the page in `raw_page_text`. Typical causes: a row cut at a page break, two rows merged into
one cell, a new line code.

**The site changes its pages.** The list of pages is `config.PAGES`; the links are read from the content block of a
page by [`parsers/pages.py`](../../src/yerevan_budget/parsers/pages.py).

## Code layout

| module | role |
|---|---|
| `config.py` | paths, pages of the section, HTTP settings |
| `http.py` | HTTP client: pauses, retries, streamed downloads |
| `catalog.py` | step 1: crawl the pages → `data/catalog/pages.json`, `documents.json` |
| `classify.py` | type / year / period of a document from its title |
| `fetch.py` | step 2: download, unpack archives, hashes |
| `extract.py` | step 3: text and tables of every file → `data/interim` |
| `build.py` | step 4: DuckDB build (`sql/schema.sql`, `sql/dims.sql`, `sql/views.sql`, `sql/qc.sql`) |
| `parsers/armscii.py` | legacy Armenian fonts → Unicode |
| `parsers/pages.py` | links and headings of the pages |
| `parsers/budget_tables.py` | tables with a row of column numbers → logical rows |
| `parsers/semantics.py` | statements, row types, meaning of amount columns |
| `parsers/program_tables.py` | programme-budget tables (ԾԲ) |
| `parsers/common.py` | values, codes, names |
| `translations.py` | dictionaries hy → en / ru |
| `reference.py` | districts of Yerevan |
| `docs.py`, `release.py` | generated documentation, data snapshots in GitHub releases |
| `cli.py`, `__main__.py` | command line |
