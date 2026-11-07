# Visualization mockups

Interactive mockups of ways to present the Yerevan city budget, built on the data of this repository.
Open `mockups/index.html`: it links the six mockups and reviews the open-source tools for budget visualization.

The mockups speak every language of the database: Armenian, English, Russian, French, Spanish, Portuguese,
German, Arabic and Persian (switcher in the top bar; `?lang=fr` in the URL; the choice is remembered in the
browser; the default follows the browser language, else English). Arabic and Persian pages run right-to-left
(the charts stay left-to-right).

Live: <https://opendataam.github.io/arm-yerevan-budget/> (published by `.github/workflows/pages.yml` on every
push to `main` that changes `viz/mockups`).

| page | pattern |
|---|---|
| `overview.html` | headline figures, revenue and spending 2017–2026 (approved / revised / actual), spending by function and economic type |
| `treemap.html` | drill-down treemap and sunburst: function → sub-function → programme, searchable programme table |
| `flow.html` | Sankey: revenue sources → budget → functions → main services |
| `execution.html` | plan vs actual by function and sub-function, quarterly pace across years |
| `districts.html` | tile map of the 12 districts, total and per resident, district × function heatmap |
| `receipt.html` | personal tax receipt calculator |

The pages are static: Apache ECharts and Google Fonts load from CDNs, the data from `mockups/data.js`.
Serve the folder over HTTP or open the files directly:

```bash
python3 -m http.server 8765 --directory viz/mockups
```

`mockups/data.js` is generated from the database (amounts converted to million AMD):

```bash
python viz/export_data.py --db data/yerevan_budget.duckdb
```

## Languages

* Names from the database (functional classes, districts, programmes) are exported by `export_data.py` in
  every language of the database (`data.js`: objects `{"hy": …, "en": …}`; programme names deduplicated in
  `names`) and picked by `assets/common.js` for the language of the page.
* Interface strings are in `mockups/assets/i18n/<lang>/common.js` (shared: navigation, units, short section
  names, revenue and economic groups) and `mockups/assets/i18n/<lang>/<page>.js`. English is the source and the
  fallback for a missing string. A page runs its code in `YB.ready("<page>", …)`; static elements carry
  `data-i18n` (text), `data-i18n-html` (text with markup) or `data-i18n-attr` (attributes); scripts use
  `YB.t(key, {placeholders})` and format numbers with `YB.num`, `YB.amd`, `YB.short`, `YB.pct` (conventions
  of the language, digits 0–9).
* To add a string: add the key to `i18n/en/<file>.js` and to every other language. To add a language: add it
  to the database (see [docs/en/translations.md](../docs/en/translations.md)), to `LANGS` / `LOCALE` in
  `assets/common.js` and a folder `i18n/<lang>/` with every file.
* The interface texts in languages other than English and the names in French, Spanish, Portuguese, German,
  Arabic and Persian are machine-assisted translations (LLM) that have not been reviewed by native speakers yet;
  the footer of every non-English page says so.

## Notes on the figures

* land and property sales are booked in the budget as negative spending (functional class 04.9.1, economic
  line 6000); composition views show gross allocations and treat these sales as a source;
* internal transfers from the administrative to the fund part of the budget are excluded from programmes;
* per-resident figures use the 2022 census population of the districts (1,086,677 in total).
