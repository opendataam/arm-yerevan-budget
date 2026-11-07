/* Interface strings of flow.html: Portuguese (Brazil). {name} = placeholder; values with <b> are HTML. */
YB.strings("pt", {
  "flow.title": "Fluxo do dinheiro no orçamento de Erevan",
  "flow.h1": "Da receita à despesa",
  "flow.lede": "Siga o dinheiro: de onde vem o orçamento da cidade e quais funções e serviços ele financia. A largura das faixas é proporcional aos valores.",
  "flow.pattern": "<b>Padrão:</b> página inicial de fluxo (Sankey), como no Open Budget Oakland / Sacramento, no Civio Presupuesto e no USAspending Data Lab",
  "flow.f_year": "Ano",
  "flow.year_actual": "{year} realizado",
  "flow.year_approved": "{year} aprovado",
  "flow.revenue_actual": "Receita realizada",
  "flow.revenue_approved": "Receita, orçamento aprovado",
  "flow.spending_actual": "Despesa realizada",
  "flow.spending_approved": "Despesa, orçamento aprovado",
  "flow.surplus": "Superávit",
  "flow.deficit": "Déficit",
  "flow.col_sources": "Fontes",
  "flow.col_budget": "Orçamento",
  "flow.col_functions": "Funções",
  "flow.col_services": "Principais serviços",
  "flow.chart_aria": "Diagrama de Sankey das fontes de receita, passando pelo orçamento da cidade, até as funções e os serviços",

  /* names of the nodes of the diagram */
  "flow.hub": "Orçamento municipal {year}",
  "flow.asset_sales": "Venda de terrenos e imóveis",
  "flow.deficit_financing": "Financiamento do déficit",
  /* {name} = the function, {lname} = the same name in lower case */
  "flow.other_in_section": "Outras despesas com {lname}",
  "flow.other_functions": "Outras funções",
  "flow.unspent": "Não gasto (superávit)",

  /* short names of some sub-functions (functional classification codes 01.1.1 etc.) */
  "flow.short_01_1_1": "Órgãos executivos e administração",
  "flow.short_04_1_1": "Assuntos econômicos gerais",
  "flow.short_04_5_5": "Metrô, elevadores e outros transportes",
  "flow.short_04_9_1": "Assuntos econômicos n.e.",
  "flow.short_05_6_1": "Proteção do meio ambiente n.e.",
  "flow.short_09_6_1": "Serviços auxiliares da educação",
  "flow.short_06_6_1": "Habitação e serviços comunitários n.e.",

  "flow.tip_edge": "{from} → {to}",
  "flow.tip_share": "{pct} de todo o dinheiro",
  "flow.col_from": "De",
  "flow.col_to": "Para",
  "flow.col_amd": "AMD",
  /* {source} = flow.source_report or flow.source_decision */
  "flow.read_note": "<b>Como ler:</b> {source} As vendas de terrenos e imóveis ({asset}) aparecem nos documentos de origem como despesa negativa; aqui são mostradas como fonte, por isso “Assuntos econômicos” está em valores brutos. Os “Recursos do Estado para competências delegadas” pagam tarefas que o Estado transfere à cidade, como o metrô e as escolas.",
  "flow.source_report": "Relatório anual de execução de {year}.",
  "flow.source_decision": "Decisão orçamentária do Conselho de Anciãos para {year}.",
  "flow.other_note": "<b>Outras funções</b> reúne saúde, defesa, ordem pública e fundos de reserva.",
});
