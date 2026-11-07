/* Interface strings shared by every page: English (the fallback of every language). {name} = placeholder. */
YB.strings("en", {
  "brand.title": "Yerevan Budget",
  "brand.subtitle": "visualization mockups",
  "nav.index": "Tools & mockups",
  "nav.overview": "At a glance",
  "nav.treemap": "Where money goes",
  "nav.flow": "Money flow",
  "nav.execution": "Plan vs actual",
  "nav.districts": "Districts",
  "nav.receipt": "Tax receipt",
  "ui.pages": "Mockups",
  "ui.language": "Language",
  "ui.show_table": "Show table",
  "ui.hide_table": "Hide table",
  "foot.data": "Data: Yerevan Municipality, Finance section (budget decisions and form Հ-9 execution reports), collected into DuckDB by opendataam/arm-yerevan-budget. Amounts are nominal AMD.",
  "foot.mockup": "Mockup, not an official publication. Data snapshot {date}.",
  "foot.translation": "The budget is published in Armenian only; names and interface are machine-assisted translations.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "n/a",
  "fmt.amd_bn": "AMD {n} bn",
  "fmt.amd_m": "AMD {n} m",
  "fmt.amd_k": "AMD {n} k",
  "fmt.bn": "{n} bn",
  "fmt.m": "{n} m",
  "fmt.k": "{n} k",
  "fmt.pct": "{n}%",

  /* execution status */
  "status.good": "On plan",
  "status.warning": "Behind",
  "status.serious": "Lagging",
  "status.critical": "Far behind",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "General public services",
  "section.02": "Defence",
  "section.03": "Public order & safety",
  "section.04": "Economic affairs",
  "section.05": "Environmental protection",
  "section.06": "Housing & community amenities",
  "section.07": "Health",
  "section.08": "Recreation, culture & religion",
  "section.09": "Education",
  "section.10": "Social protection",
  "section.11": "Reserve funds",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "Compensation of employees",
  "econ.goods": "Goods and services",
  "econ.subsidies": "Subsidies to municipal organisations",
  "econ.other_current": "Grants, social benefits and other current",
  "econ.capital": "Capital investment (fixed assets)",
  "econ.asset_sales": "Sale of land and property (offset)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "Real estate tax",
  "rev.vehicle_tax": "Vehicle property tax",
  "rev.local_duties": "Local duties (permits)",
  "rev.local_fees": "Local fees (waste, parking, etc.)",
  "rev.delegated": "State funds for delegated powers",
  "rev.grants": "State budget grants",
  "rev.state_duties": "State duties",
  "rev.other": "Service payments, rent, fines, other",

  /* labels of data.js nodes */
  "data.not_itemised": "Not itemised by programme",
});
