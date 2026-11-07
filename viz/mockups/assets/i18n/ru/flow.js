/* Interface strings of flow.html: Russian. {name} = placeholder; values with <b> are HTML. */
YB.strings("ru", {
  "flow.title": "Денежные потоки бюджета Еревана",
  "flow.h1": "От доходов к расходам",
  "flow.lede": "Проследите путь денег: откуда берётся городской бюджет и какие функции и услуги он оплачивает. Ширина полос пропорциональна суммам.",
  "flow.pattern": "<b>Приём:</b> диаграмма потоков (Санкея) на главном экране, как в Open Budget Oakland / Sacramento, Civio Presupuesto и USAspending Data Lab",
  "flow.f_year": "Год",
  "flow.year_actual": "{year}, факт",
  "flow.year_approved": "{year}, утверждено",
  "flow.revenue_actual": "Доходы, факт",
  "flow.revenue_approved": "Доходы, утверждённый бюджет",
  "flow.spending_actual": "Расходы, факт",
  "flow.spending_approved": "Расходы, утверждённый бюджет",
  "flow.surplus": "Профицит",
  "flow.deficit": "Дефицит",
  "flow.col_sources": "Источники",
  "flow.col_budget": "Бюджет",
  "flow.col_functions": "Функции",
  "flow.col_services": "Основные услуги",
  "flow.chart_aria": "Диаграмма Санкея: от источников доходов через городской бюджет к функциям и услугам",

  /* names of the nodes of the diagram */
  "flow.hub": "Бюджет города {year}",
  "flow.asset_sales": "Продажа земли и имущества",
  "flow.deficit_financing": "Финансирование дефицита",
  /* {name} = the function, {lname} = the same name in lower case */
  "flow.other_in_section": "Прочее ({lname})",
  "flow.other_functions": "Прочие функции",
  "flow.unspent": "Не израсходовано (профицит)",

  /* short names of some sub-functions (functional classification codes 01.1.1 etc.) */
  "flow.short_01_1_1": "Исполнительные органы и управление",
  "flow.short_04_1_1": "Общие экономические отношения",
  "flow.short_04_5_5": "Метро, лифты и прочий транспорт",
  "flow.short_04_9_1": "Экономические отношения (прочие)",
  "flow.short_05_6_1": "Охрана окружающей среды (прочее)",
  "flow.short_09_6_1": "Вспомогательные услуги в образовании",
  "flow.short_06_6_1": "Жильё и коммунальные услуги (прочее)",

  "flow.tip_edge": "{from} → {to}",
  "flow.tip_share": "{pct} всех средств",
  "flow.col_from": "Откуда",
  "flow.col_to": "Куда",
  "flow.col_amd": "Сумма, драм",
  /* {source} = flow.source_report or flow.source_decision */
  "flow.read_note": "<b>Как читать:</b> {source} Продажа земли и имущества ({asset}) в исходных документах отражена как отрицательные расходы; здесь она показана как источник, поэтому «Экономические отношения» даны в валовом выражении. «Средства государства на делегированные полномочия» оплачивают задачи, которые государство передаёт городу, например метро и школы.",
  "flow.source_report": "Годовой отчёт об исполнении бюджета за {year} год.",
  "flow.source_decision": "Решение Совета старейшин о бюджете на {year} год.",
  "flow.other_note": "<b>Прочие функции</b> объединяют здравоохранение, оборону, общественный порядок и резервные фонды.",
});
