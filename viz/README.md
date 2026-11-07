# Visualization mockups

Interactive mockups of ways to present the Yerevan city budget, built on the data of this repository
(labels in English). Open `mockups/index.html`: it links the six mockups and reviews the open-source tools
for budget visualization.

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

Notes on the figures:

* land and property sales are booked in the budget as negative spending (functional class 04.9.1, economic
  line 6000); composition views show gross allocations and treat these sales as a source;
* internal transfers from the administrative to the fund part of the budget are excluded from programmes;
* per-resident figures use the 2022 census population of the districts (1,086,677 in total).
