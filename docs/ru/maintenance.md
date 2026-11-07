# Сопровождение

[English](../en/maintenance.md) | [Հայերեն](../hy/maintenance.md) | **Русский**

## Регулярное обновление

На новой машине сначала восстановите сырые данные последнего снимка, чтобы ничего не скачивать и не извлекать
заново:

```bash
make install download-raw
```

Затем:

```bash
make catalog fetch extract build docs test
git add -A && git commit -m "data: update to $(date +%F)" && git push
make release            # новый релиз data-<дата сбора> с базой, Parquet и сырыми данными
```

* `catalog` заново обходит страницы раздела «Финансы». Новые документы подхватываются автоматически и
  классифицируются по заголовкам; изменения `data/catalog/documents.json` видны в `git diff` — удобный способ
  увидеть, что опубликовано.
* `fetch` скачивает только недостающие документы (`--force` — все заново) и распаковывает архивы в
  `data/raw/extracted/<doc_id>/`; размеры и SHA-256 файлов и членов архивов сохраняются в каталоге.
* `extract` читает новые файлы (текст и таблицы PDF, электронные таблицы, Word) в кэш `data/interim/` (одинаковые
  файлы читаются один раз; около 3 минут на всё).
* `build` пересоздаёт всю базу (около минуты). Проверьте `SELECT * FROM qc_summary`
  (см. [data_quality.md](data_quality.md)).
* Новые названия → [translations.md](translations.md) (`make translations`, заполнить, `make translations-merge`,
  `make build`).
* `release` требует чистого рабочего дерева, отправленного `HEAD` и `gh` с правом записи в
  `opendataam/arm-yerevan-budget`; тег — `data-<дата обхода>`.

Квартальные отчёты публикуются примерно через 1–2 месяца после квартала, бюджет следующего года — в декабре,
среднесрочная программа — в сентябре; достаточно ежемесячного обновления.

## Что делать, если…

**Документу присвоен неверный тип, год или период.** Правила — в
[`classify.py`](../../src/yerevan_budget/classify.py); добавьте правило или запись в `OVERRIDES` (ключ — `doc_id`)
и добавьте заголовок в `tests/test_parsers.py`.

**Новая разметка таблицы не распознаётся** (`tables_with_unknown_layout`, документ без фактов в `qc_coverage`).
Посмотрите строки файла в `raw_table_cell` / `stg_table_row`. Бюджетные таблицы опознаются по строке номеров
столбцов ([`parsers/budget_tables.py`](../../src/yerevan_budget/parsers/budget_tables.py)); смысл столбцов сумм
определяется текстом заголовка и типом документа
([`parsers/semantics.py`](../../src/yerevan_budget/parsers/semantics.py), `FACT_LAYOUTS` в `build.py`).

**Текст выходит как `Ð³í»Éí³Í` или номера глифов.** Старые шрифты конвертирует
[`parsers/armscii.py`](../../src/yerevan_budget/parsers/armscii.py); шрифты без таблицы Unicode восстанавливаются
по встроенному шрифту в `extract.py` (`_glyph_maps`). После изменения извлечения увеличьте `extract.VERSION` и
выполните `make extract build`.

**Не сходится контрольная сумма.** Найдите документ и столбец в таблице `qc_*`, затем строки в `stg_table_row`
(`file_id`, `seq`) и страницу в `raw_page_text`. Типичные причины: строка, обрезанная на разрыве страницы, две
строки в одной ячейке, новый код строки.

**Сайт изменил страницы.** Список страниц — `config.PAGES`; ссылки читаются из блока содержимого страницы
модулем [`parsers/pages.py`](../../src/yerevan_budget/parsers/pages.py).

## Структура кода

| модуль | роль |
|---|---|
| `config.py` | пути, страницы раздела, настройки HTTP |
| `http.py` | HTTP-клиент: паузы, повторы, потоковое скачивание |
| `catalog.py` | шаг 1: обход страниц → `data/catalog/pages.json`, `documents.json` |
| `classify.py` | тип / год / период документа по заголовку |
| `fetch.py` | шаг 2: скачивание, распаковка архивов, хеши |
| `extract.py` | шаг 3: текст и таблицы каждого файла → `data/interim` |
| `build.py` | шаг 4: сборка DuckDB (`sql/schema.sql`, `sql/dims.sql`, `sql/views.sql`, `sql/qc.sql`) |
| `parsers/armscii.py` | старые армянские шрифты → Unicode |
| `parsers/pages.py` | ссылки и заголовки страниц |
| `parsers/budget_tables.py` | таблицы со строкой номеров столбцов → логические строки |
| `parsers/semantics.py` | разделы, типы строк, смысл столбцов сумм |
| `parsers/program_tables.py` | таблицы программного бюджета (ԾԲ) |
| `parsers/common.py` | значения, коды, названия |
| `translations.py` | словари hy → en / ru / fr / es / pt / de / ar / fa |
| `reference.py` | районы Еревана |
| `docs.py`, `release.py` | генерируемая документация, снимки данных в релизах GitHub |
| `cli.py`, `__main__.py` | командная строка |
