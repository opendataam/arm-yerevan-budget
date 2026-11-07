/* Interface strings of flow.html: English. {name} = placeholder; values with <b> are HTML. */
YB.strings("en", {
  "flow.title": "Yerevan Budget Money Flow",
  "flow.h1": "From revenue to spending",
  "flow.lede": "Follow the money: where the city budget comes from, and which functions and services it pays for. Band widths are proportional to amounts.",
  "flow.pattern": "<b>Pattern:</b> flow (Sankey) landing view, as in Open Budget Oakland / Sacramento, Civio Presupuesto and the USAspending Data Lab",
  "flow.f_year": "Year",
  "flow.year_actual": "{year} actual",
  "flow.year_approved": "{year} approved",
  "flow.revenue_actual": "Revenue, actual",
  "flow.revenue_approved": "Revenue, approved budget",
  "flow.spending_actual": "Spending, actual",
  "flow.spending_approved": "Spending, approved budget",
  "flow.surplus": "Surplus",
  "flow.deficit": "Deficit",
  "flow.col_sources": "Sources",
  "flow.col_budget": "Budget",
  "flow.col_functions": "Functions",
  "flow.col_services": "Main services",
  "flow.chart_aria": "Sankey diagram from revenue sources through the city budget to functions and services",

  /* names of the nodes of the diagram */
  "flow.hub": "City budget {year}",
  "flow.asset_sales": "Sale of land and property",
  "flow.deficit_financing": "Deficit financing",
  /* {name} = the function, {lname} = the same name in lower case */
  "flow.other_in_section": "Other {lname}",
  "flow.other_functions": "Other functions",
  "flow.unspent": "Unspent (surplus)",

  /* short names of some sub-functions (functional classification codes 01.1.1 etc.) */
  "flow.short_01_1_1": "Executive bodies and administration",
  "flow.short_04_1_1": "General economic affairs",
  "flow.short_04_5_5": "Metro, lifts and other transport",
  "flow.short_04_9_1": "Economic affairs n.e.c.",
  "flow.short_05_6_1": "Environmental protection n.e.c.",
  "flow.short_09_6_1": "Support services to education",
  "flow.short_06_6_1": "Housing and amenities n.e.c.",

  "flow.tip_edge": "{from} → {to}",
  "flow.tip_share": "{pct} of all money",
  "flow.col_from": "From",
  "flow.col_to": "To",
  "flow.col_amd": "AMD",
  /* {source} = flow.source_report or flow.source_decision */
  "flow.read_note": "<b>How to read:</b> {source} Land and property sales ({asset}) appear in the source documents as negative spending; here they are shown as a source, so “Economic affairs” is gross. “State funds for delegated powers” pay for tasks the state hands to the city, such as the metro and schools.",
  "flow.source_report": "Annual execution report for {year}.",
  "flow.source_decision": "Budget decision of the Council for {year}.",
  "flow.other_note": "<b>Other functions</b> joins health, defence, public order and reserve funds.",
});
