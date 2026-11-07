# Names in nine languages

**English** | [Հայերեն](../hy/translations.md) | [Русский](../ru/translations.md)

The documents are published only in Armenian. The database keeps the Armenian names as printed and adds their
translations from dictionaries versioned in git.

## Languages

| code | language | why |
|---|---|---|
| `hy` | Armenian | the source; authoritative |
| `en` | English | international language of the data |
| `ru` | Russian | widely used in Armenia; the largest community of the diaspora (Russia) |
| `fr` | French | France, Belgium, Quebec, Lebanon |
| `es` | Spanish | Argentina, Uruguay |
| `pt` | Portuguese (Brazil) | Brazil |
| `de` | German | Germany |
| `ar` | Arabic (Modern Standard) | Lebanon, Syria, Egypt, Iraq, the Gulf |
| `fa` | Persian | Iran |

The list is `LANGS` in `src/yerevan_budget/config.py`. Every name column of Armenian text `<name>_hy` has a column
`<name>_<lang>` for each language: `label_en` … `label_fa`, `name_en` … `name_fa`, `title_en` … `title_fa`.

## Dictionaries

`data/translations/<context>.csv`, UTF-8 CSV with the columns `hy,en,ru,fr,es,pt,de,ar,fa`:

| context | contents |
|---|---|
| `revenue` | revenue lines: taxes, local duties and fees, state duties, grants, other revenues |
| `functional` | functional classification: sections, groups, classes |
| `economic` | economic classification of expenditures, lines of the economic statement |
| `financing` | surplus / deficit and its financing |
| `program` | programmes, measures and other rows of the detailed tables and of the programme budget |
| `labels` | document titles, headings of the pages of the institutions, other labels |
| `reference` | names of the reference lists defined in the code (document types, periods, statements, scenarios, parts of the budget, districts): English and Russian come from the code, the other languages from this file |

Conventions (terms, style, transliteration of proper names) are in
[GLOSSARY.md](../../data/translations/GLOSSARY.md).

## How names are matched

* The key of a name is its Armenian text reduced to letters and digits (`norm_key`): differences in spacing,
  punctuation, case, `եւ` / `և` do not matter.
* List numbering at the start (`1.1`, `ա)`, `Ա.`, `-`) is split off before the lookup and put back in front of the
  translation; formulas (`(տող 1110 + տող 1120)`) and the words "including" (`այդ թվում`, `որից`) are removed
  from the names stored in the facts.
* A name is looked up in its context first, then in any context.
* If a name has no translation, the views fall back to the name of its code: the functional class
  (`dim_functional`), the article (`dim_economic`) or the line of the form (`dim_line`).

The result is in `dim_label` (every distinct row name), `dim_functional`, `dim_economic`, `dim_line`,
`dim_program`, `dim_measure`, `dim_district` and the other reference lists, `meta_document.title_<lang>` and in the
`*_<lang>` columns of the views.

## Method

* Names of the functional and economic classification shared with the state budget were taken from the
  dictionaries of the sister project [arm-budget](https://github.com/opendataam/arm-budget).
* The other English and Russian names were translated with an LLM (Claude) following the glossary, in batches by
  context, and checked for consistency of terms; the Armenian text stays authoritative.
* French, Spanish, Portuguese, German, Arabic and Persian were translated with an LLM (Claude) from the English and
  Russian names together (two independent translations of the same Armenian original), with a glossary of key terms
  fixed per language first. They have not been reviewed by native speakers yet: corrections are welcome.
* Long descriptions (goals and results of programmes, descriptions of measures, performance indicators) are kept in
  Armenian only.

## Translating new names

After a new document is published:

```bash
python -m yerevan_budget build          # names without a translation -> qc_missing_translation
python -m yerevan_budget translations   # -> data/translations/pending/<context>.csv (known languages filled, the missing ones empty)
# fill the empty columns (by hand or with a machine translation, then review)
python -m yerevan_budget translations --merge
python -m yerevan_budget build
```

`--merge` takes every filled cell; rows with an empty language stay in `pending/`.
`SELECT * FROM qc_summary WHERE check_name = 'translations_complete'` shows how many names are left.

## Adding a language

1. Add its code to `LANGS` and its name to `LANG_NAMES` in `src/yerevan_budget/config.py`: the build creates the
   columns `*_<code>` in every table and view (`sql/*.sql` repeat the lines with `{lang}` for every language).
2. Add the column to `data/translations/*.csv` and fill it (`python -m yerevan_budget translations` writes the
   names into `pending/`, every name is missing the new language).
3. Add the terms of the language to [GLOSSARY.md](../../data/translations/GLOSSARY.md), rebuild and check
   `translations_complete`.
