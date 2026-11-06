"""Generic parser of the budget tables: forms with a row of column numbers.

All tables of the budget documents (the execution report form Հ-9, the
appendices of the budget decision, the medium-term expenditure programme, the
measures ensuring the execution of the budget) follow the standard layout of
the Armenian community budget forms:

    header rows            | Տողի NN | Եկամտատեսակները | Հոդվածի NN | Տարեկան հաստատված պլան ... |
    row of column numbers  |    1    |        2        |     3      |   4   |  5  |  6  | ...     |
    data rows              |  1000   | ԸՆԴԱՄԵՆԸ ...     |            | 159,399,554.2 | ...       |

The row of column numbers ("1, 2, 3, ...") is the anchor: it tells which
physical columns of an extracted table belong to which logical column (PDF
tables often split a logical column into several physical ones, and a code like
``2100`` may be split into ``2`` and ``100``). Tables on continuation pages
without that row reuse the layout of the previous table with the same number of
physical columns.

The output is a list of :class:`Row` – one per logical row of the source, with
its line code (``Տողի NN``), functional classification codes, the classification
article code, the label, and the amount cells – plus the header text of every
amount column. Label lines continued on the following physical rows are merged.
Semantics (which amount column is which scenario / year / budget part) are
assigned by :mod:`.semantics`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..reference import district_of
from .common import clean, code_str, is_amount, is_marker, parse_amount

_ARM = re.compile(r"[Ա-և]")
_LINE_CODE = re.compile(r"^\d{4,5}$")
_SHORT_CODE = re.compile(r"^\d{1,3}$")
_CLASS_CODE = re.compile(r"^(\d{4}|x|X|х|Х)$")
_APPENDIX = re.compile(r"(?:Հավելված|ՀԱՎԵԼՎԱԾ)\s*(?:N|№|Ն)?\s*(\d{1,2})")
_SECTION = re.compile(r"(?:ՀԱՏՎԱԾ|Հատված)\s*(?:N|№)?\s*(\d{1,2})")
_TABLE_NO = re.compile(r"(?:Աղյուսակ|ԱՂՅՈՒՍԱԿ)\s*(?:N|№)?\s*(\d{1,2})")


@dataclass
class Layout:
    """Physical -> logical column mapping of one table and the header text of each logical column."""

    n_physical: int
    logical_of: list[int]                 # physical column -> logical column (1-based)
    n_logical: int
    headers: dict[int, str] = field(default_factory=dict)  # logical column -> header text (top to bottom)


@dataclass
class Row:
    """One logical row of a budget table."""

    page: int | None
    seq: int                              # order of the row in the file
    context: dict                         # appendix / section / table number and title in force
    cells: dict[int, str]                 # logical column -> text
    layout: Layout
    line_code: str | None = None
    func: tuple[str | None, str | None, str | None] = (None, None, None)
    class_code: str | None = None
    label: str | None = None
    amounts: list[tuple[str | None, float | None, str | None]] = field(default_factory=list)  # (raw, value, flag)
    amount_cols: list[int] = field(default_factory=list)  # logical columns of the amounts
    kinds: frozenset = frozenset()       # roles of the columns of the layout (line, func, label, class, amount)


def numbering_row(row: list) -> list[int] | None:
    """Physical positions of the column numbers if ``row`` is a row of column numbers.

    Accepted: small integers starting with 1, strictly increasing (usually 1, 2, 3, ...;
    some forms skip the numbers of hidden columns: 1, 2, 3, 10, 11, 12, ...), at least 4 of them.
    A number split over two adjacent cells by the PDF extraction ('1' '2' for 12) is joined.
    """
    toks = []
    for i, c in enumerate(row):
        t = clean(c)
        if not t:
            continue
        toks.append((i, t.removesuffix(".0")))
    # one cell of the row may be garbage instead of its number (an Excel formula left in the source:
    # '1, 2, 3, 4, =SUM(R[2]C,R[62]C), 6, ...'): accept it when its neighbours are n-1 and n+1
    bad = [k for k, (_, t) in enumerate(toks) if not t.isdigit()]
    if len(bad) > 1:
        return None
    if bad:
        k = bad[0]
        if 0 < k < len(toks) - 1 and toks[k - 1][1].isdigit() and toks[k + 1][1].isdigit() \
                and int(toks[k + 1][1]) == int(toks[k - 1][1]) + 2:
            toks[k] = (toks[k][0], str(int(toks[k - 1][1]) + 1))
        else:
            return None
    pos: list[int] = []
    nums: list[int] = []
    j = 0
    while j < len(toks):
        i, t = toks[j]
        n = int(t)
        nxt = nums[-1] + 1 if nums else 1
        # join a fragment with the next cell if that gives the expected number ('1' + '2' -> 12)
        if j + 1 < len(toks) and n != nxt and int(t + toks[j + 1][1]) == nxt:
            n = nxt
            j += 1
        if nums and n <= nums[-1] or n > 60:
            return None
        pos.append(i)
        nums.append(n)
        j += 1
    if len(nums) >= 4 and nums[0] == 1 and nums[:3] == [1, 2, 3]:
        return pos
    return None


def _layout(rows: list[list], idx: int, n_physical: int) -> Layout:
    pos = numbering_row(rows[idx])
    logical_of = []
    cur = 1
    for j in range(n_physical):
        if j in pos:
            cur = pos.index(j) + 1
        logical_of.append(cur)
    headers: dict[int, list[str]] = {}
    for r in rows[:idx]:
        last = None
        for j, c in enumerate(r[:n_physical]):
            t = clean(c)
            if t:
                lg = logical_of[j]
                if lg != last:
                    headers.setdefault(lg, []).append(t)
                else:
                    headers[lg][-1] += " " + t
                last = lg
    return Layout(n_physical, logical_of, len(pos), {k: " | ".join(v) for k, v in headers.items()})


def _logical(row: list, layout: Layout) -> dict[int, str]:
    out: dict[int, list[str]] = {}
    for j, c in enumerate(row[: layout.n_physical]):
        t = clean(c)
        if t:
            out.setdefault(layout.logical_of[j], []).append(t)
    return {k: " ".join(v) for k, v in out.items()}


def page_context(text: str, prev: dict) -> dict:
    """Appendix / section / table numbers and the title stated at the top of a page (inherited otherwise)."""
    ctx = dict(prev)
    head = "\n".join(text.splitlines()[:40])
    for key, rx in (("appendix", _APPENDIX), ("section", _SECTION), ("table_no", _TABLE_NO)):
        m = rx.search(head)
        if m:
            if key == "appendix" and ctx.get("appendix") != int(m.group(1)):
                for k in ("table_no", "section", "district"):
                    ctx.pop(k, None)
            ctx[key] = int(m.group(1))
            if key == "table_no":
                # the unit (district / Municipality) of a detailed table is named in its title
                ctx["district"] = district_of(head[m.end():m.end() + 700])
    titles = [ln.strip() for ln in head.splitlines()
              if len(ln.strip()) > 25 and _ARM.search(ln) and ln.strip().upper() == ln.strip()]
    if titles:
        ctx["title"] = " ".join(titles)[:500]
    return ctx


class TableReader:
    """Turns the extracted tables of one file into logical rows."""

    def __init__(self) -> None:
        self.layouts: dict[int, Layout] = {}   # n_physical -> last layout with that width
        self.last: Layout | None = None
        self.rows: list[Row] = []
        self.unmapped_tables = 0
        self.seq = 0

    def add_table(self, rows: list[list], page: int | None, context: dict) -> None:
        if not rows:
            return
        n_physical = max(len(r) for r in rows)
        rows = [list(r) + [None] * (n_physical - len(r)) for r in rows]
        idx = next((i for i, r in enumerate(rows) if numbering_row(r)), None)
        if idx is not None:
            layout = _layout(rows, idx, n_physical)
            self.layouts[n_physical] = layout
            self.last = layout
            data = rows[idx + 1:]
        else:
            layout = self.layouts.get(n_physical)
            if layout is None and self.last is not None and n_physical == self.last.n_logical:
                layout = Layout(n_physical, list(range(1, n_physical + 1)), n_physical, self.last.headers)
            if layout is None:
                if any(is_amount(c) and clean(c) not in ("-",) for r in rows for c in r):
                    self.unmapped_tables += 1
                return
            data = rows
        for r in data:
            cells = _logical(r, layout)
            if cells:
                self.seq += 1
                self.rows.append(Row(page=page, seq=self.seq, context=dict(context), cells=cells, layout=layout))


def _compact(v: str | None) -> str:
    """'7 1 0 0' -> '7100', '2 100' -> '2100' (codes split by the PDF text layer); other text unchanged."""
    t = code_str(v) or ""
    return t.replace(" ", "") if re.fullmatch(r"[\d ]+", t) else t


def _kinds(rows: list[Row], layout: Layout) -> dict[int, str]:
    """Role of every logical column of a layout from the content of its rows:
    ``line`` (line code), ``func`` (functional code parts), ``label``, ``class`` (article code), ``amount``."""
    stats: dict[int, dict[str, int]] = {}
    for r in rows:
        for k, v in r.cells.items():
            s = stats.setdefault(k, {"n": 0, "line": 0, "short": 0, "class": 0, "amount": 0, "arm": 0, "dec": 0})
            s["n"] += 1
            t = _compact(v)
            s["line"] += bool(_LINE_CODE.match(t))
            s["short"] += bool(_SHORT_CODE.match(t))
            s["class"] += bool(_CLASS_CODE.match(t))
            s["amount"] += is_amount(v)
            s["dec"] += bool(re.search(r"\d[.,]\d", v)) or t in ("X", "x", "-")
            s["arm"] += len(_ARM.findall(v))
    if not stats:
        return {}
    label = max(stats, key=lambda k: stats[k]["arm"])
    if stats[label]["arm"] == 0:
        # no text at all in the table (labels drawn as images): the label column is the first column
        # after the codes that is empty or holds neither codes nor amounts
        label = next((k for k in range(2, layout.n_logical + 1)
                      if k not in stats or (stats[k]["line"] + stats[k]["short"] + stats[k]["amount"]) == 0), 2)
    kinds: dict[int, str] = {label: "label"}
    left = sorted(k for k in stats if k < label)
    right = sorted(k for k in stats if k > label)
    # left of the label: line code first, then the parts of the functional code (section, group, class)
    for k in left:
        s = stats[k]
        if s["line"] >= max(1, 0.5 * s["n"]) and "line" not in kinds.values():
            kinds[k] = "line"
        elif s["short"] >= 0.5 * s["n"]:
            kinds[k] = "func"
        elif s["line"] > 0 and "line" not in kinds.values():
            kinds[k] = "line"
    # right of the label: an optional article code column, then the amounts
    for k in right:
        s = stats[k]
        if s["n"] and s["class"] >= 0.6 * s["n"] and s["dec"] < 0.5 * s["n"] and "amount" not in kinds.values():
            kinds[k] = "class"
        else:
            kinds[k] = "amount"
    # columns that never had content keep their place as amounts if they are right of the label
    for k in range(label + 1, layout.n_logical + 1):
        kinds.setdefault(k, "amount" if k > max([c for c, v in kinds.items() if v == "class"], default=label) else "class")
    return kinds


def assemble(reader: TableReader) -> list[Row]:
    """Interpret the cells of the logical rows and merge label continuation rows."""
    by_layout: dict[int, list[Row]] = {}
    for r in reader.rows:
        by_layout.setdefault(id(r.layout), []).append(r)
    kinds_of: dict[int, dict[int, str]] = {}
    for lid, rows in by_layout.items():
        kinds_of[lid] = _kinds(rows, rows[0].layout)

    detailed: set[int] = set()
    for lid, rows in by_layout.items():
        kinds = kinds_of[lid]
        if "func" in kinds.values() and "class" not in kinds.values():
            func_cols = [k for k, v in kinds.items() if v == "func"]
            line_cols = [k for k, v in kinds.items() if v == "line"]
            uncoded = sum(1 for r in rows if not any(r.cells.get(k) for k in func_cols + line_cols)
                          and any(is_amount(r.cells.get(k)) for k, v in kinds.items() if v == "amount"))
            if uncoded > 0.2 * len(rows):
                detailed.add(lid)
    out: list[Row] = []
    carry: str | None = None
    for r in reader.rows:
        kinds = kinds_of[id(r.layout)]
        r.kinds = frozenset(kinds.values()) | ({"class"} if id(r.layout) in detailed else set())
        pending, carry = carry, None
        func = []
        label_parts = []
        amounts = []
        amount_cols = []
        for k in range(1, r.layout.n_logical + 1):
            kind = kinds.get(k)
            v = r.cells.get(k)
            if kind == "line":
                c = _compact(v) or None
                if c and not _LINE_CODE.match(c):
                    # '1370 1371': two codes in one cell (two rows merged by the extraction):
                    # the first belongs to this row, the second to the next row without a code
                    parts = [p for p in (v or "").split() if _LINE_CODE.match(p)]
                    if len(parts) >= 2:
                        c = parts[0]
                        carry = parts[1]
                r.line_code = c
            elif kind == "func":
                func.append(_compact(v) or None)
            elif kind == "label":
                if v:
                    label_parts.append(v)
            elif kind == "class":
                r.class_code = _compact(v) or None
            elif kind == "amount":
                val, flag = parse_amount(v)
                amounts.append((v, val, flag))
                amount_cols.append(k)
        while len(func) < 3:
            func.append(None)
        label = " ".join(label_parts) if label_parts else None
        if label and "line" not in kinds.values():
            m = re.match(r"^(\d{4,5})\s+(?=.*[\u0531-\u0587])", label)  # line code printed in the label column
            if m:
                r.line_code, label = m.group(1), label[m.end():]
        if label and func[0] and func[1] and not func[2]:
            m = re.match(r"^(\d)\s+(?=\D)", label)  # class digit of the functional code in the label column
            if m:
                func[2], label = m.group(1), label[m.end():]
        if label and "func" in kinds.values():
            # stray digits of neighbouring code / number columns glued to the name ('0 Այլ ...', '... 10')
            label = re.sub(r"^\d{1,2}\s+(?=[\u0531-\u0587])", "", label)
            label = re.sub(r"(?<=[\u0531-\u0587)])\s+\d{1,2}$", "", label)
        if r.class_code and not _CLASS_CODE.match(r.class_code):
            label = f"{label or ''} {r.class_code}".strip() if not label else label
            r.class_code = None
        if label and not r.class_code and "func" in kinds.values() and not any(func) and not r.line_code:
            m = re.search(r"\s(\d{4})$", label)  # economic article printed at the end of the name
            if m:
                r.class_code, label = m.group(1), label[:m.start()].strip()
        r.func = tuple(func[:3])
        r.label = label
        r.amounts, r.amount_cols = amounts, amount_cols
        if r.line_code is None and pending and any(v is not None for _, v, _ in amounts):
            r.line_code = pending
        elif pending and not carry and r.line_code is None:
            carry = pending  # a label continuation row: keep the code for the next data row
        has_values = any(v is not None or f in ("na", "dash") for _, v, f in amounts)
        has_code = bool(r.line_code and _LINE_CODE.match(r.line_code)) or bool(r.class_code and r.class_code.isdigit())
        if not has_values and not has_code:
            # a continuation of the previous label, a structural word or the repeated column numbers
            if (r.label and not is_marker(r.label) and out and out[-1].page == r.page
                    and not numbering_row(list(r.cells.values()))):
                out[-1].label = f"{out[-1].label or ''} {r.label}".strip()
            continue
        out.append(r)
    return out
