/* Interface strings of flow.html: Arabic (Modern Standard Arabic). {name} = placeholder; values with <b> are HTML. */
YB.strings("ar", {
  "flow.title": "تدفق أموال موازنة يريفان",
  "flow.h1": "من الإيرادات إلى النفقات",
  "flow.lede": "تتبّع الأموال: من أين تأتي موازنة المدينة، وأي وظائف وخدمات تموّلها. عرض الأشرطة يتناسب مع المبالغ.",
  "flow.pattern": "<b>النمط:</b> واجهة رئيسية للتدفق (مخطط سانكي)، كما في Open Budget Oakland / Sacramento وCivio Presupuesto وUSAspending Data Lab",
  "flow.f_year": "السنة",
  "flow.year_actual": "{year} (فعلي)",
  "flow.year_approved": "{year} (معتمد)",
  "flow.revenue_actual": "الإيرادات، الفعلية",
  "flow.revenue_approved": "الإيرادات، الموازنة المعتمدة",
  "flow.spending_actual": "النفقات، الفعلية",
  "flow.spending_approved": "النفقات، الموازنة المعتمدة",
  "flow.surplus": "الفائض",
  "flow.deficit": "العجز",
  "flow.col_sources": "المصادر",
  "flow.col_budget": "الموازنة",
  "flow.col_functions": "الوظائف",
  "flow.col_services": "الخدمات الرئيسية",
  "flow.chart_aria": "مخطط سانكي من مصادر الإيرادات عبر موازنة المدينة إلى الوظائف والخدمات",

  /* names of the nodes of the diagram */
  "flow.hub": "موازنة المدينة {year}",
  "flow.asset_sales": "بيع الأراضي والممتلكات",
  "flow.deficit_financing": "تمويل العجز",
  /* {name} = the function, {lname} = the same name in lower case */
  "flow.other_in_section": "بنود أخرى في {lname}",
  "flow.other_functions": "وظائف أخرى",
  "flow.unspent": "غير مُنفَق (فائض)",

  /* short names of some sub-functions (functional classification codes 01.1.1 etc.) */
  "flow.short_01_1_1": "الهيئات التنفيذية والإدارة",
  "flow.short_04_1_1": "الشؤون الاقتصادية العامة",
  "flow.short_04_5_5": "المترو والمصاعد ووسائل نقل أخرى",
  "flow.short_04_9_1": "الشؤون الاقتصادية (أخرى)",
  "flow.short_05_6_1": "حماية البيئة (أخرى)",
  "flow.short_09_6_1": "الخدمات المساعدة للتعليم",
  "flow.short_06_6_1": "الإسكان والمرافق (أخرى)",

  "flow.tip_edge": "{from} ← {to}",
  "flow.tip_share": "{pct} من مجموع الأموال",
  "flow.col_from": "من",
  "flow.col_to": "إلى",
  "flow.col_amd": "درام",
  /* {source} = flow.source_report or flow.source_decision */
  "flow.read_note": "<b>طريقة القراءة:</b> {source} تظهر مبيعات الأراضي والممتلكات ({asset}) في الوثائق المصدرية كنفقات سالبة؛ وهنا تُعرض كمصدر، لذا فإن «الشؤون الاقتصادية» إجمالية. «أموال الدولة للصلاحيات المفوضة» تموّل مهامّ تُسندها الدولة إلى المدينة، مثل المترو والمدارس.",
  "flow.source_report": "تقرير التنفيذ السنوي لعام {year}.",
  "flow.source_decision": "قرار المجلس بشأن موازنة {year}.",
  "flow.other_note": "<b>وظائف أخرى</b> تجمع الصحة والدفاع والنظام العام والصناديق الاحتياطية.",
});
