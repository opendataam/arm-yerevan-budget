# Translation glossary (hy → en / ru)

Conventions used in `data/translations/*.csv`. Keep new translations consistent with them.
The functional and economic classification of the community budgets is the same as that of the state
budget, so the terms follow the dictionaries of the sister project
[arm-budget](https://github.com/opendataam/arm-budget) (part of the names were taken from there).

## File format

* UTF-8 CSV with the columns `hy,en,ru`; standard CSV quoting (`"` doubled inside quoted fields).
* `hy` is the key: the Armenian text as in the source, **without list numbering** (`1.1`, `ա)`, `Ա.`, `-` at the
  start are split off by the build and put back in front of the translation). The build compares the key by
  letters and digits only, so punctuation, spacing and case differences do not matter.
* `en` and `ru` must both be filled.
* The Armenian text is authoritative; translations are machine-assisted (LLM) and reviewed for consistency.

## Contexts

| file | contents |
|---|---|
| `revenue.csv` | revenue lines of the forms: taxes, local duties and fees, grants, other revenues |
| `functional.csv` | functional classification: sections, groups, classes |
| `economic.csv` | economic classification of expenditures (articles 4xxx–6xxx), lines of the economic statement |
| `financing.csv` | surplus / deficit and its financing (lines 7000–8xxx, articles 9xxx) |
| `program.csv` | programmes, measures and other rows of the detailed tables (appendices 6–7, execution measures, programme budget) |
| `labels.csv` | document titles, headings of the institutions pages, other labels |

## Style

* Translate the meaning; do not transliterate common words. Proper names of people and places are
  transliterated (Yerevan / Ереван, Kentron / Кентрон, Nor Nork / Нор-Норк, Malatia-Sebastia / Малатия-Себастия).
* Use sentence case, even when the Armenian source is in capitals (`ԿՐԹՈՒԹՅՈՒՆ` → `Education` / `Образование`).
* Drop the formulas and the words "including" (`(տող 1110 + տող 1120)`, `այդ թվում`) – the build removes them
  from the key anyway.
* Keep numbers, years, codes, Latin abbreviations (KfW, EIB, ADB) and quoted names; quotes in English `"…"`,
  in Russian `«…»`.
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
