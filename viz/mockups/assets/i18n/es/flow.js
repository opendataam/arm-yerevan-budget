/* Interface strings of flow.html: Spanish. {name} = placeholder; values with <b> are HTML. */
YB.strings("es", {
  "flow.title": "Flujo del dinero del presupuesto de Ereván",
  "flow.h1": "De los ingresos al gasto",
  "flow.lede": "Sigue el dinero: de dónde procede el presupuesto de la ciudad y qué funciones y servicios financia. El ancho de las bandas es proporcional a los importes.",
  "flow.pattern": "<b>Patrón:</b> vista de inicio de flujo (Sankey), como en Open Budget Oakland / Sacramento, Civio Presupuesto y el Data Lab de USAspending",
  "flow.f_year": "Año",
  "flow.year_actual": "{year} (ejecución)",
  "flow.year_approved": "{year} (aprobado)",
  "flow.revenue_actual": "Ingresos, ejecución real",
  "flow.revenue_approved": "Ingresos, presupuesto aprobado",
  "flow.spending_actual": "Gastos, ejecución real",
  "flow.spending_approved": "Gastos, presupuesto aprobado",
  "flow.surplus": "Superávit",
  "flow.deficit": "Déficit",
  "flow.col_sources": "Fuentes",
  "flow.col_budget": "Presupuesto",
  "flow.col_functions": "Funciones",
  "flow.col_services": "Servicios principales",
  "flow.chart_aria": "Diagrama de Sankey desde las fuentes de ingresos, a través del presupuesto de la ciudad, hasta las funciones y los servicios",

  /* names of the nodes of the diagram */
  "flow.hub": "Presupuesto de la ciudad {year}",
  "flow.asset_sales": "Venta de terrenos y bienes",
  "flow.deficit_financing": "Financiación del déficit",
  /* {name} = the function, {lname} = the same name in lower case */
  "flow.other_in_section": "Otros ({lname})",
  "flow.other_functions": "Otras funciones",
  "flow.unspent": "No gastado (superávit)",

  /* short names of some sub-functions (functional classification codes 01.1.1 etc.) */
  "flow.short_01_1_1": "Órganos ejecutivos y administración",
  "flow.short_04_1_1": "Asuntos económicos generales",
  "flow.short_04_5_5": "Metro, ascensores y otros transportes",
  "flow.short_04_9_1": "Asuntos económicos n.c.o.p.",
  "flow.short_05_6_1": "Protección del medio ambiente n.c.o.p.",
  "flow.short_09_6_1": "Servicios auxiliares de la educación",
  "flow.short_06_6_1": "Vivienda y servicios comunitarios n.c.o.p.",

  "flow.tip_edge": "{from} → {to}",
  "flow.tip_share": "{pct} del total",
  "flow.col_from": "Origen",
  "flow.col_to": "Destino",
  "flow.col_amd": "AMD",
  /* {source} = flow.source_report or flow.source_decision */
  "flow.read_note": "<b>Cómo leerlo:</b> {source} Las ventas de terrenos y bienes ({asset}) figuran en los documentos fuente como gasto negativo; aquí se muestran como fuente, por lo que «Asuntos económicos» aparece en bruto. Los «Fondos estatales para competencias delegadas» pagan tareas que el Estado encomienda a la ciudad, como el metro y las escuelas.",
  "flow.source_report": "Informe anual de ejecución de {year}.",
  "flow.source_decision": "Decisión presupuestaria del Consejo de Ancianos para {year}.",
  "flow.other_note": "<b>Otras funciones</b> agrupa salud, defensa, orden público y fondos de reserva.",
});
