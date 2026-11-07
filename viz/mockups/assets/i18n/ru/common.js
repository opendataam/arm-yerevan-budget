/* Interface strings shared by every page: Russian. {name} = placeholder. */
YB.strings("ru", {
  "brand.title": "Бюджет Еревана",
  "brand.subtitle": "макеты визуализаций",
  "nav.index": "Инструменты и макеты",
  "nav.overview": "Обзор",
  "nav.treemap": "Куда идут деньги",
  "nav.flow": "Денежные потоки",
  "nav.execution": "План и факт",
  "nav.districts": "Районы",
  "nav.receipt": "Налоговый чек",
  "ui.pages": "Макеты",
  "ui.language": "Язык",
  "ui.show_table": "Показать таблицу",
  "ui.hide_table": "Скрыть таблицу",
  "foot.data": "Данные: мэрия Еревана, раздел «Финансы» (решения о бюджете и отчёты об исполнении по форме Հ-9), собраны в DuckDB проектом opendataam/arm-yerevan-budget. Суммы в номинальных драмах.",
  "foot.mockup": "Макет, а не официальная публикация. Данные на {date}.",
  "foot.translation": "Бюджет публикуется только на армянском языке; названия и интерфейс переведены с помощью машинного перевода.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "н/д",
  "fmt.amd_bn": "{n} млрд драмов",
  "fmt.amd_m": "{n} млн драмов",
  "fmt.amd_k": "{n} тыс. драмов",
  "fmt.bn": "{n} млрд",
  "fmt.m": "{n} млн",
  "fmt.k": "{n} тыс.",
  "fmt.pct": "{n} %",

  /* execution status */
  "status.good": "По плану",
  "status.warning": "Небольшое отставание",
  "status.serious": "Отставание",
  "status.critical": "Сильное отставание",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "Общегосударственные услуги",
  "section.02": "Оборона",
  "section.03": "Общественный порядок и безопасность",
  "section.04": "Экономические отношения",
  "section.05": "Охрана окружающей среды",
  "section.06": "Жильё и коммунальные услуги",
  "section.07": "Здравоохранение",
  "section.08": "Отдых, культура и религия",
  "section.09": "Образование",
  "section.10": "Социальная защита",
  "section.11": "Резервные фонды",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "Оплата труда",
  "econ.goods": "Товары и услуги",
  "econ.subsidies": "Субсидии муниципальным организациям",
  "econ.other_current": "Гранты, социальные пособия и прочие текущие расходы",
  "econ.capital": "Капитальные вложения (основные средства)",
  "econ.asset_sales": "Продажа земли и имущества (вычитается)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "Налог на недвижимое имущество",
  "rev.vehicle_tax": "Налог на имущество за транспортные средства",
  "rev.local_duties": "Местные пошлины (разрешения)",
  "rev.local_fees": "Местные сборы (вывоз мусора, парковка и др.)",
  "rev.delegated": "Средства государства на делегированные полномочия",
  "rev.grants": "Гранты из государственного бюджета",
  "rev.state_duties": "Государственные пошлины",
  "rev.other": "Плата за услуги, аренда, штрафы, прочее",

  /* labels of data.js nodes */
  "data.not_itemised": "Без разбивки по программам",
});
