# Names in three languages

**English** | [Հայերեն](../hy/translations.md) | [Русский](../ru/translations.md)

The documents are published only in Armenian. The database keeps the Armenian names as printed and adds English
and Russian names from translation dictionaries versioned in git.

## Dictionaries

`data/translations/<context>.csv`, UTF-8 CSV with the columns `hy,en,ru`:

| context | contents |
|---|---|
| `revenue` | revenue lines: taxes, local duties and fees, state duties, grants, other revenues |
| `functional` | functional classification: sections, groups, classes |
| `economic` | economic classification of expenditures, lines of the economic statement |
| `financing` | surplus / deficit and its financing |
| `program` | programmes, measures and other rows of the detailed tables and of the programme budget |
| `labels` | document titles, headings of the pages of the institutions, other labels |

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
`dim_program`, `dim_measure`, `meta_document.title_en / title_ru` and in the `*_en`, `*_ru` columns of the views.

## Method

* Names of the functional and economic classification shared with the state budget were taken from the
  dictionaries of the sister project [arm-budget](https://github.com/opendataam/arm-budget).
* The other names were translated with an LLM (Claude) following the glossary, in batches by context, and checked
  for consistency of terms; the Armenian text stays authoritative.
* Long descriptions (goals and results of programmes, descriptions of measures, performance indicators) are kept in
  Armenian only.

## Translating new names

After a new document is published:

```bash
python -m yerevan_budget build          # names without a translation -> qc_missing_translation
python -m yerevan_budget translations   # -> data/translations/pending/<context>.csv (hy filled, en/ru empty)
# fill en and ru (by hand or with a machine translation, then review)
python -m yerevan_budget translations --merge
python -m yerevan_budget build
```

`SELECT * FROM qc_summary WHERE check_name = 'translations_complete'` shows how many names are left.
