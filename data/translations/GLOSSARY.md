# Translation glossary (hy → en / ru / fr / es / pt / de / ar / fa)

Conventions used in `data/translations/*.csv`. Keep new translations consistent with them.
The functional and economic classification of the community budgets is the same as that of the state
budget, so the terms follow the dictionaries of the sister project
[arm-budget](https://github.com/opendataam/arm-budget) (part of the names were taken from there).

## File format

* UTF-8 CSV with the columns `hy,en,ru,fr,es,pt,de,ar,fa` (English, Russian, French, Spanish, Brazilian Portuguese,
  German, Modern Standard Arabic, Persian); standard CSV quoting (`"` doubled inside quoted fields).
* `hy` is the key: the Armenian text as in the source, **without list numbering** (`1.1`, `ա)`, `Ա.`, `-` at the
  start are split off by the build and put back in front of the translation). The build compares the key by
  letters and digits only, so punctuation, spacing and case differences do not matter.
* Every language column must be filled (`qc_summary.translations_complete`).
* The Armenian text is authoritative; translations are machine-assisted (LLM) and reviewed for consistency.
  `fr`, `es`, `pt`, `de`, `ar`, `fa` were translated from `en` and `ru` together and have not been reviewed by
  native speakers yet.

## Contexts

| file | contents |
|---|---|
| `revenue.csv` | revenue lines of the forms: taxes, local duties and fees, grants, other revenues |
| `functional.csv` | functional classification: sections, groups, classes |
| `economic.csv` | economic classification of expenditures (articles 4xxx–6xxx), lines of the economic statement |
| `financing.csv` | surplus / deficit and its financing (lines 7000–8xxx, articles 9xxx) |
| `program.csv` | programmes, measures and other rows of the detailed tables (appendices 6–7, execution measures, programme budget) |
| `labels.csv` | document titles, headings of the institutions pages, other labels |
| `reference.csv` | names of the reference lists defined in the code (document types, periods, statements, scenarios, parts of the budget, districts); `en` and `ru` repeat the code |

## Style

* Translate the meaning; do not transliterate common words. Proper names of people and places are
  transliterated (Yerevan / Ереван, Kentron / Кентрон, Nor Nork / Нор-Норк, Malatia-Sebastia / Малатия-Себастия).
* Use sentence case, even when the Armenian source is in capitals (`ԿՐԹՈՒԹՅՈՒՆ` → `Education` / `Образование`);
  German nouns keep their capitals.
* Drop the formulas and the words "including" (`(տող 1110 + տող 1120)`, `այդ թվում`) – the build removes them
  from the key anyway.
* Keep numbers, years, codes, Latin abbreviations (KfW, EIB, ADB) and quoted names; digits 0–9 also in Arabic
  and Persian. Quotes: en `"…"`, ru `«…»`, fr `«…»`, es `«…»`, pt `"…"`, de `„…“`, ar `«…»`, fa `«…»`.
* Proper names are transliterated by the usual conventions of each language, based on the English form; Yerevan =
  Ереван, Erevan (fr, pt), Ereván (es), Jerewan (de), يريفان (ar), ایروان (fa).
* Variants: fr — France, es — neutral international Spanish, pt — Brazilian Portuguese, de — Germany,
  ar — Modern Standard Arabic, fa — Iranian Persian.
* Typos and encoding artefacts of the source are translated by their evident meaning; a truncated name stays
  truncated (`…`).
* Programme / measure names are noun phrases describing an activity: translate as a noun phrase
  (`… պահպանում` → `Maintenance of …` / `Содержание …`; `… կառուցում` → `Construction of …` / `Строительство …`;
  `… հիմնանորոգում` → `Major repair of …` / `Капитальный ремонт …`).

## Terms of the city budget

| hy | en | ru |
|---|---|---|
| Երևան քաղաքի ավագանի | Council of Elders of Yerevan (city council) | Совет старейшин Еревана |
| Երևանի քաղաքապետ / քաղաքապետարան | Mayor of Yerevan / Yerevan Municipality | мэр Еревана / мэрия Еревана |
| քաղաքապետարանի աշխատակազմ | staff (office) of the Municipality | аппарат мэрии |
| վարչական շրջան | administrative district | административный район |
| համայնք / համայնքային | community / community (municipal) | община / общинный |
| համայնքի բյուջե | community budget | бюджет общины |
| վարչական մաս (բյուջե) | administrative part (current budget) | административная часть (бюджета) |
| ֆոնդային մաս (բյուջե) | fund part (capital budget) | фондовая часть (бюджета) |
| տարեկան հաստատված / ճշտված պլան | approved / revised annual plan | утверждённый / уточнённый годовой план |
| փաստացի (կատարողական) | actual (execution) | фактическое исполнение |
| միջնաժամկետ ծախսերի ծրագիր | medium-term expenditure programme | среднесрочная программа расходов |
| բյուջետային ուղերձ | budget message | бюджетное послание |
| բյուջեի կատարումն ապահովող միջոցառումներ | measures ensuring the execution of the budget | меры по обеспечению исполнения бюджета |
| նախահաշիվ / ճշտված նախահաշիվ | budget estimate / revised estimate | смета / уточнённая смета |
| հաստիքացուցակ | staff list | штатное расписание |
| ՀՈԱԿ (համայնքային ոչ առևտրային կազմակերպություն) | CNCO (community non-commercial organisation) | ОНКО (общинная некоммерческая организация) |
| ՊՈԱԿ | SNCO (state non-commercial organisation) | ГНКО (государственная некоммерческая организация) |
| ՓԲԸ / ԲԲԸ / ՍՊԸ | CJSC / OJSC / LLC | ЗАО / ОАО / ООО |
| ծրագիր / միջոցառում | programme / measure | программа / мероприятие |
| տեղական տուրք / տեղական վճար | local duty / local fee | местная пошлина / местный сбор |
| պետական տուրք | state duty | государственная пошлина |
| գույքահարկ / հողի հարկ | property tax / land tax | налог на имущество / земельный налог |
| անշարժ գույքի հարկ | real estate tax | налог на недвижимое имущество |
| թույլտվություն | permit | разрешение |
| դոտացիա / նպատակային հատկացում | subsidy (dotation) / targeted allocation | дотация / целевое ассигнование |
| պատվիրակված լիազորություններ | delegated powers | делегированные полномочия |
| դրամաշնորհ (պաշտոնական / ոչ պաշտոնական) | grant (official / unofficial) | грант (официальный / неофициальный) |
| պահուստային ֆոնդ | reserve fund | резервный фонд |
| տարեսկզբի ազատ մնացորդ | free balance at the beginning of the year | свободный остаток на начало года |
| հիմնական միջոցներ | fixed assets | основные средства |
| ոչ ֆինանսական ակտիվներ | non-financial assets | нефинансовые активы |
| կապիտալ վերանորոգում / հիմնանորոգում | capital repair / major repair | капитальный ремонт |
| ընթացիկ նորոգում և պահպանում | current repair and maintenance | текущий ремонт и содержание |
| բարեկարգում | improvement (landscaping) | благоустройство |
| մանկապարտեզ / նախադպրոցական ուսումնական հաստատություն | kindergarten / preschool educational institution | детский сад / дошкольное образовательное учреждение |
| արտադպրոցական դաստիարակություն | out-of-school education | внешкольное воспитание |
| Եվրոպական ներդրումային բանկ / Ասիական զարգացման բանկ | European Investment Bank (EIB) / Asian Development Bank (ADB) | Европейский инвестиционный банк (ЕИБ) / Азиатский банк развития (АБР) |

## Functional classification (COFOG)

| hy | en | ru |
|---|---|---|
| ԸՆԴՀԱՆՈՒՐ ԲՆՈՒՅԹԻ ՀԱՆՐԱՅԻՆ ԾԱՌԱՅՈՒԹՅՈՒՆՆԵՐ | General public services | Общегосударственные услуги |
| ՊԱՇՏՊԱՆՈՒԹՅՈՒՆ | Defence | Оборона |
| ՀԱՍԱՐԱԿԱԿԱՆ ԿԱՐԳ, ԱՆՎՏԱՆԳՈՒԹՅՈՒՆ ԵՎ ԴԱՏԱԿԱՆ ԳՈՐԾՈՒՆԵՈՒԹՅՈՒՆ | Public order, safety and judicial activity | Общественный порядок, безопасность и судебная деятельность |
| ՏՆՏԵՍԱԿԱՆ ՀԱՐԱԲԵՐՈՒԹՅՈՒՆՆԵՐ | Economic affairs | Экономические отношения |
| ՇՐՋԱԿԱ ՄԻՋԱՎԱՅՐԻ ՊԱՇՏՊԱՆՈՒԹՅՈՒՆ | Environmental protection | Охрана окружающей среды |
| ԲՆԱԿԱՐԱՆԱՅԻՆ ՇԻՆԱՐԱՐՈՒԹՅՈՒՆ ԵՎ ԿՈՄՈՒՆԱԼ ԾԱՌԱՅՈՒԹՅՈՒՆՆԵՐ | Housing construction and community amenities | Жилищное строительство и коммунальные услуги |
| ԱՌՈՂՋԱՊԱՀՈՒԹՅՈՒՆ | Health | Здравоохранение |
| ՀԱՆԳԻՍՏ, ՄՇԱԿՈՒՅԹ ԵՎ ԿՐՈՆ | Recreation, culture and religion | Отдых, культура и религия |
| ԿՐԹՈՒԹՅՈՒՆ | Education | Образование |
| ՍՈՑԻԱԼԱԿԱՆ ՊԱՇՏՊԱՆՈՒԹՅՈՒՆ | Social protection | Социальная защита |
| ՀԻՄՆԱԿԱՆ ԲԱԺԻՆՆԵՐԻՆ ՉԴԱՍՎՈՂ ՊԱՀՈՒՍՏԱՅԻՆ ՖՈՆԴԵՐ | Reserve funds not classified under the main sections | Резервные фонды, не отнесенные к основным разделам |
| (այլ դասերին չպատկանող) | (not elsewhere classified) | (не отнесенные к другим категориям) |

## Terms in the other languages

The terms of the two tables above in French, Spanish, Portuguese (Brazil), German, Arabic and Persian. They were
fixed first and used for every dictionary of the language.

| en | fr | es | pt | de | ar | fa |
|---|---|---|---|---|---|---|
| Council of Elders of Yerevan (city council) | Conseil des anciens d'Erevan (conseil municipal) | Consejo de Ancianos de Ereván (concejo municipal) | Conselho de Anciãos de Erevan (câmara municipal) | Ältestenrat von Jerewan (Stadtrat) | مجلس حكماء يريفان (مجلس المدينة) | شورای ریش‌سفیدان ایروان (شورای شهر) |
| Mayor of Yerevan / Yerevan Municipality | Maire d'Erevan / Mairie d'Erevan | Alcalde de Ereván / Alcaldía de Ereván | Prefeito de Erevan / Prefeitura de Erevan | Bürgermeister von Jerewan / Stadtverwaltung Jerewan | عمدة يريفان / بلدية يريفان | شهردار ایروان / شهرداری ایروان |
| staff (office) of the Municipality | Services administratifs (cabinet) de la mairie | aparato administrativo (oficina) de la Alcaldía | gabinete (aparato administrativo) da Prefeitura | Verwaltungsapparat der Stadtverwaltung | جهاز البلدية | دستگاه اداری شهرداری |
| administrative district | district administratif | distrito administrativo | distrito administrativo | Verwaltungsbezirk | المنطقة الإدارية | منطقه اداری |
| community / community (municipal) | communauté / communal, de la communauté (municipal) | comunidad / comunitario (municipal) | comunidade / comunitário (municipal) | Gemeinde / Gemeinde- (kommunal) | المجتمع المحلي / التابع للمجتمع المحلي (البلدي) | جامعه محلی / جامعه محلی (شهری) |
| community budget | budget de la communauté | presupuesto de la comunidad | orçamento da comunidade | Gemeindehaushalt | موازنة المجتمع المحلي | بودجه جامعه محلی |
| administrative part (current budget) | section administrative (budget de fonctionnement) | parte administrativa (presupuesto corriente) | parte administrativa (orçamento corrente) | Verwaltungsteil (laufender Haushalt) | الجزء الإداري (الموازنة الجارية) | بخش اداری (بودجه جاری) |
| fund part (capital budget) | section des fonds (budget d'investissement) | parte de fondos (presupuesto de capital) | parte de fundos (orçamento de capital) | Fondsteil (Vermögenshaushalt) | جزء الصندوق (الموازنة الرأسمالية) | بخش صندوقی (بودجه سرمایه‌ای) |
| approved / revised annual plan | plan annuel approuvé / révisé | plan anual aprobado / revisado | plano anual aprovado / revisado | genehmigter / geänderter Jahresplan | الخطة السنوية المعتمدة / المعدلة | برنامه سالانه مصوب / اصلاح‌شده |
| actual (execution) | exécution effective | ejecución real | execução efetiva (realizado) | Ist (Vollzug) | التنفيذ الفعلي | عملکرد (اجرای واقعی) |
| medium-term expenditure programme | programme de dépenses à moyen terme | programa de gastos a mediano plazo | programa de despesas de médio prazo | mittelfristiges Ausgabenprogramm | برنامج الإنفاق متوسط الأجل | برنامه هزینه‌های میان‌مدت |
| budget message | message budgétaire | mensaje presupuestario | mensagem orçamentária | Haushaltsbotschaft | رسالة الموازنة | پیام بودجه |
| measures ensuring the execution of the budget | mesures assurant l'exécution du budget | medidas para garantizar la ejecución del presupuesto | medidas para assegurar a execução do orçamento | Maßnahmen zur Sicherstellung des Haushaltsvollzugs | تدابير ضمان تنفيذ الموازنة | اقدامات تضمین اجرای بودجه |
| budget estimate / revised estimate | état prévisionnel des dépenses / état prévisionnel révisé | estimación presupuestaria / estimación revisada | estimativa orçamentária / estimativa revisada | Haushaltsvoranschlag / geänderter Haushaltsvoranschlag | تقديرات الموازنة / التقديرات المعدلة | برآورد هزینه / برآورد هزینه اصلاح‌شده |
| staff list | tableau des effectifs | plantilla de personal | quadro de pessoal | Stellenplan | جدول الملاك الوظيفي | جدول تشکیلات |
| CNCO (community non-commercial organisation) | organisation non commerciale communale (CNCO) | organización comunitaria no comercial (CNCO) | CNCO (organização comunitária sem fins lucrativos) | kommunale nichtkommerzielle Organisation (CNCO) | المنظمة المجتمعية غير التجارية (CNCO) | سازمان غیرتجاری جامعه محلی (CNCO) |
| SNCO (state non-commercial organisation) | organisation non commerciale d'État (SNCO) | organización estatal no comercial (SNCO) | SNCO (organização estatal sem fins lucrativos) | staatliche nichtkommerzielle Organisation (SNCO) | المنظمة الحكومية غير التجارية (SNCO) | سازمان غیرتجاری دولتی (SNCO) |
| CJSC / OJSC / LLC | société anonyme fermée (CJSC) / société anonyme ouverte (OJSC) / société à responsabilité limitée (SARL) | sociedad anónima cerrada (CJSC) / sociedad anónima abierta (OJSC) / sociedad de responsabilidad limitada (SRL) | CJSC (sociedade anônima de capital fechado) / OJSC (sociedade anônima de capital aberto) / LLC (sociedade limitada) | geschlossene Aktiengesellschaft (CJSC) / offene Aktiengesellschaft (OJSC) / GmbH | شركة مساهمة مغلقة (CJSC) / شركة مساهمة مفتوحة (OJSC) / شركة ذات مسؤولية محدودة (LLC) | شرکت سهامی خاص / شرکت سهامی عام / شرکت با مسئولیت محدود |
| programme / measure | programme / mesure | programa / medida | programa / medida | Programm / Maßnahme | البرنامج / الإجراء | برنامه / اقدام |
| local duty / local fee | droit local / redevance locale | tasa local / cargo local | taxa local / tarifa local | örtliche Abgabe / örtliche Gebühr | الرسم المحلي / رسم الخدمة المحلي | عوارض محلی / کارمزد محلی |
| state duty | droit d'État | tasa estatal | taxa estatal | Staatsgebühr | رسم الدولة | عوارض دولتی |
| property tax / land tax | impôt sur les biens / impôt foncier | impuesto sobre la propiedad / impuesto sobre la tierra | imposto sobre a propriedade / imposto territorial | Vermögensteuer / Grundsteuer | ضريبة الممتلكات / ضريبة الأراضي | مالیات بر دارایی / مالیات بر زمین |
| real estate tax | impôt sur les biens immobiliers | impuesto sobre bienes inmuebles | imposto sobre bens imóveis | Immobiliensteuer | ضريبة العقارات | مالیات بر املاک |
| permit | autorisation | permiso | autorização | Genehmigung | التصريح | مجوز |
| subsidy (dotation) / targeted allocation | dotation / allocation ciblée | subsidio (dotación) / asignación específica | subsídio (dotação) / alocação vinculada | Dotation (Finanzzuweisung) / Zweckzuweisung | الإعانة / الاعتماد المحدد الغرض | کمک تعادلی (دوتاسیون) / تخصیص هدفمند |
| delegated powers | compétences déléguées | competencias delegadas | competências delegadas | übertragene Befugnisse | الصلاحيات المفوضة | اختیارات تفویض‌شده |
| grant (official / unofficial) | don (officiel / non officiel) | donación (oficial / no oficial) | doação (oficial / não oficial) | Zuschuss (offiziell / inoffiziell) | المنحة (الرسمية / غير الرسمية) | کمک بلاعوض (رسمی / غیررسمی) |
| reserve fund | fonds de réserve | fondo de reserva | fundo de reserva | Reservefonds | الصندوق الاحتياطي | صندوق ذخیره |
| free balance at the beginning of the year | solde disponible en début d'année | saldo libre al inicio del año | saldo livre no início do ano | freier Mittelbestand zu Jahresbeginn | الرصيد الحر في بداية السنة | مانده آزاد در ابتدای سال |
| fixed assets | actifs fixes | activos fijos | ativos fixos | Anlagegüter | الأصول الثابتة | دارایی‌های ثابت |
| non-financial assets | actifs non financiers | activos no financieros | ativos não financeiros | nichtfinanzielle Vermögenswerte | الأصول غير المالية | دارایی‌های غیرمالی |
| capital repair / major repair | grosses réparations | reparación capital / reparación mayor | reforma geral / reparo de grande porte | Grundinstandsetzung | الإصلاح الرأسمالي | تعمیرات اساسی |
| current repair and maintenance | réparations courantes et entretien | reparación corriente y mantenimiento | reparos correntes e manutenção | laufende Reparatur und Instandhaltung | الإصلاح الجاري والصيانة | تعمیرات جاری و نگهداری |
| improvement (landscaping) | aménagement urbain (embellissement) | mejoramiento urbano (paisajismo) | urbanização (paisagismo) | Gestaltung (Landschaftsbau) | التهيئة العمرانية (تنسيق المواقع) | بهسازی (محوطه‌سازی) |
| kindergarten / preschool educational institution | jardin d'enfants / établissement d'enseignement préscolaire | jardín de infancia / institución de educación preescolar | jardim de infância / instituição de educação infantil | Kindergarten / vorschulische Bildungseinrichtung | روضة الأطفال / مؤسسة التعليم ما قبل المدرسي | مهدکودک / مؤسسه آموزشی پیش‌دبستانی |
| out-of-school education | éducation extrascolaire | educación extraescolar | educação extraescolar | außerschulische Bildung | التعليم خارج المدرسة | آموزش فوق‌برنامه (خارج از مدرسه) |
| European Investment Bank (EIB) / Asian Development Bank (ADB) | Banque européenne d'investissement (EIB) / Banque asiatique de développement (ADB) | Banco Europeo de Inversiones (EIB) / Banco Asiático de Desarrollo (ADB) | Banco Europeu de Investimento (EIB) / Banco Asiático de Desenvolvimento (ADB) | Europäische Investitionsbank (EIB) / Asiatische Entwicklungsbank (ADB) | بنك الاستثمار الأوروبي (EIB) / بنك التنمية الآسيوي (ADB) | بانک سرمایه‌گذاری اروپا (EIB) / بانک توسعه آسیایی (ADB) |
| General public services | Services généraux des administrations publiques | Servicios públicos generales | Serviços públicos gerais | Allgemeine öffentliche Verwaltung | الخدمات العمومية العامة | خدمات عمومی همگانی |
| Defence | Défense | Defensa | Defesa | Verteidigung | الدفاع | دفاع |
| Public order, safety and judicial activity | Ordre public, sécurité et activités judiciaires | Orden público, seguridad y actividad judicial | Ordem pública, segurança e atividades judiciárias | Öffentliche Ordnung, Sicherheit und Justiz | النظام العام والسلامة والنشاط القضائي | نظم عمومی، امنیت و فعالیت قضایی |
| Economic affairs | Affaires économiques | Asuntos económicos | Assuntos econômicos | Wirtschaftliche Angelegenheiten | الشؤون الاقتصادية | امور اقتصادی |
| Environmental protection | Protection de l'environnement | Protección del medio ambiente | Proteção do meio ambiente | Umweltschutz | حماية البيئة | حفاظت از محیط زیست |
| Housing construction and community amenities | Construction de logements et équipements collectifs | Construcción de viviendas y servicios comunitarios | Construção habitacional e serviços comunitários | Wohnungsbau und kommunale Einrichtungen | بناء المساكن والمرافق المجتمعية | ساخت مسکن و خدمات شهری |
| Health | Santé | Salud | Saúde | Gesundheitswesen | الصحة | بهداشت و درمان |
| Recreation, culture and religion | Loisirs, culture et culte | Actividades recreativas, cultura y religión | Lazer, cultura e religião | Freizeitgestaltung, Kultur und Religion | الترفيه والثقافة والدين | تفریح، فرهنگ و مذهب |
| Education | Enseignement | Educación | Educação | Bildungswesen | التعليم | آموزش |
| Social protection | Protection sociale | Protección social | Proteção social | Soziale Sicherung | الحماية الاجتماعية | حمایت اجتماعی |
| Reserve funds not classified under the main sections | Fonds de réserve non classés dans les sections principales | Fondos de reserva no clasificados en las secciones principales | Fundos de reserva não classificados nas seções principais | Nicht den Hauptabschnitten zugeordnete Reservefonds | الصناديق الاحتياطية غير المصنفة ضمن الأبواب الرئيسية | صندوق‌های ذخیره طبقه‌بندی‌نشده در بخش‌های اصلی |
| (not elsewhere classified) | (non classés ailleurs) | (no clasificados en otra parte) | (não classificados em outra parte) | (anderweitig nicht genannt) | (غير المصنفة في موضع آخر) | (طبقه‌بندی‌نشده در جای دیگر) |
