/* Interface strings shared by every page: Arabic (Modern Standard Arabic). {name} = placeholder. */
YB.strings("ar", {
  "brand.title": "موازنة يريفان",
  "brand.subtitle": "نماذج أولية للتمثيل البصري",
  "nav.index": "الأدوات والنماذج",
  "nav.overview": "نظرة عامة",
  "nav.treemap": "أين تذهب الأموال",
  "nav.flow": "تدفق الأموال",
  "nav.execution": "الخطة مقابل الفعلي",
  "nav.districts": "المناطق",
  "nav.receipt": "إيصال الضرائب",
  "ui.pages": "النماذج",
  "ui.language": "اللغة",
  "ui.show_table": "إظهار الجدول",
  "ui.hide_table": "إخفاء الجدول",
  "foot.data": "البيانات: بلدية يريفان، قسم المالية (قرارات الموازنة وتقارير التنفيذ بالنموذج Հ-9)، جمعها في DuckDB مشروع opendataam/arm-yerevan-budget. المبالغ بالدرام بالقيمة الاسمية.",
  "foot.mockup": "نموذج أولي، وليس منشورًا رسميًا. لقطة البيانات بتاريخ {date}.",
  "foot.translation": "تُنشر الموازنة باللغة الأرمنية فقط؛ الأسماء والواجهة مترجمة بمساعدة الترجمة الآلية.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "غير متوفر",
  "fmt.amd_bn": "{n} مليار درام",
  "fmt.amd_m": "{n} مليون درام",
  "fmt.amd_k": "{n} ألف درام",
  "fmt.bn": "{n} مليار",
  "fmt.m": "{n} مليون",
  "fmt.k": "{n} ألف",
  "fmt.pct": "{n}%",

  /* execution status */
  "status.good": "وفق الخطة",
  "status.warning": "متأخر قليلًا",
  "status.serious": "متأخر",
  "status.critical": "متأخر كثيرًا",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "الخدمات العمومية العامة",
  "section.02": "الدفاع",
  "section.03": "النظام العام والسلامة",
  "section.04": "الشؤون الاقتصادية",
  "section.05": "حماية البيئة",
  "section.06": "الإسكان والمرافق المجتمعية",
  "section.07": "الصحة",
  "section.08": "الترفيه والثقافة والدين",
  "section.09": "التعليم",
  "section.10": "الحماية الاجتماعية",
  "section.11": "الصناديق الاحتياطية",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "تعويضات العاملين",
  "econ.goods": "السلع والخدمات",
  "econ.subsidies": "الدعم للمنظمات البلدية",
  "econ.other_current": "المنح والاستحقاقات الاجتماعية ونفقات جارية أخرى",
  "econ.capital": "الاستثمار الرأسمالي (الأصول الثابتة)",
  "econ.asset_sales": "بيع الأراضي والممتلكات (مقاصة)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "ضريبة العقارات",
  "rev.vehicle_tax": "ضريبة الممتلكات على المركبات",
  "rev.local_duties": "الرسوم المحلية (التصاريح)",
  "rev.local_fees": "رسوم الخدمات المحلية (النفايات، المواقف، إلخ)",
  "rev.delegated": "أموال الدولة للصلاحيات المفوضة",
  "rev.grants": "منح من موازنة الدولة",
  "rev.state_duties": "رسوم الدولة",
  "rev.other": "مدفوعات الخدمات والإيجار والغرامات وغيرها",

  /* labels of data.js nodes */
  "data.not_itemised": "غير مفصّل حسب البرامج",
});
