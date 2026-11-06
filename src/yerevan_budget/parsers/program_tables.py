"""Programme budget tables ("ԾԲ" – ծրագրային բյուջետավորում, programme budgeting).

Since 2025 the budget message of the Mayor and the medium-term expenditure
programmes come with two tables in the programme-budgeting format:

* **Table 1** (allocations), one sheet / table per unit (city total, the
  Municipality, every district)::

      Բաժինը | Խումբը | Դասը | Ծրագիր | Միջոցառում | name                          | Հոդվածի NN | 2026թ. | ...
        01   |        |      |        |            | ԸՆԴՀԱՆՈՒՐ ԲՆՈՒՅԹԻ ...         |            | 14 689 328.2
             |        |      |  5001  |            | Երևանի քաղաքապետարանի ...     |            | ...
             |        |      |        |   50001    | Աշխատակազմի գործունեության ... |            | ...
             |        |      |        |            | - Աշխատողների աշխատավարձեր    |    4111    | ...

  with description rows ("Ծրագրի նպատակը՝" – goal of the programme,
  "Վերջնական արդյունքի նկարագրությունը՝" – final result, "Միջոցառման
  նկարագրությունը՝" – description of the measure, "Միջոցառման տեսակը՝" – type).

* **Table 2** (performance): programme code, name and final result; measure code,
  name, performance indicators and their target values.

The functional codes of these tables use two digits for the group and the class
(``01 / 01 / 01``); they are converted to the ``SS.G.C`` form of the other tables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..reference import district_of
from .common import clean, code_str, parse_amount

_ARM = re.compile(r"[Ա-և]")
_DESC = {
    "goal": re.compile(r"^Ծրագրի\s+նպատակ"),
    "result": re.compile(r"^Վերջնական\s+արդյունք"),
    "measure_description": re.compile(r"^Միջոցառման\s+նկարագրություն"),
    "measure_type": re.compile(r"^Միջոցառման\s+տեսակ"),
    "program_name": re.compile(r"^Ծրագրի\s+անվանում"),
    "measure_name": re.compile(r"^Միջոցառման\s+անվանում"),
}
_YEAR = re.compile(r"(20\d\d)\s*թ")


def is_table1(text: str) -> bool:
    t = text.replace("\n", " ")
    return ("Ծրագրային դասիչ" in t or "Ծրագիր" in t and "Միջոցառում" in t and "Բաժին" in t)


def is_table2(text: str) -> bool:
    t = text.replace("\n", " ")
    return "Ծրագրի դասիչ" in t and ("Արդյունքային" in t or "վերջնական արդյունք" in t)


@dataclass
class Program:
    code: str
    name: str | None = None
    goal: str | None = None
    result: str | None = None


@dataclass
class Measure:
    code: str
    program_code: str | None
    name: str | None = None
    description: str | None = None
    measure_type: str | None = None


@dataclass
class Parsed:
    allocations: list[dict] = field(default_factory=list)
    indicators: list[dict] = field(default_factory=list)
    programs: dict[str, Program] = field(default_factory=dict)
    measures: dict[tuple, Measure] = field(default_factory=dict)  # (programme code, measure code) -> measure


def _codes(cells: list[str]) -> list[tuple[int, str]]:
    return [(i, code_str(c).replace(" ", "")) for i, c in enumerate(cells)
            if code_str(c) and re.fullmatch(r"[\d ]+", code_str(c))]


def _label_col(rows: list[list[str]]) -> int:
    score: dict[int, int] = {}
    for r in rows:
        for i, c in enumerate(r):
            score[i] = score.get(i, 0) + len(_ARM.findall(c or ""))
    return max(score, key=score.get) if score else 5


class Table1Reader:
    """Allocations: functional code x programme x measure x economic article, by unit."""

    def __init__(self, parsed: Parsed, years: list[int]) -> None:
        self.p = parsed
        self.years = years
        self.seq = 0
        self.unit: str | None = "?"
        self.reset()

    def reset(self) -> None:
        self.func: list[str | None] = [None, None, None]
        self.program: str | None = None
        self.measure: str | None = None
        self.pending_desc: str | None = None

    def read(self, rows: list[list], unit: str | None, page: int | None, file_id: str) -> None:
        """Read one table; the position in the hierarchy carries over to the next table of the same unit."""
        rows = [[clean(c) for c in r] for r in rows]
        if not rows:
            return
        if unit != self.unit:
            self.unit = unit
            self.reset()
        lab = _label_col(rows)
        func = self.func
        program, measure, pending_desc = self.program, self.measure, self.pending_desc
        for r in rows:
            label = r[lab] if lab < len(r) else ""
            left = r[:lab]
            right = r[lab + 1:]
            if any(c in ("Բաժինը", "Խումբը", "Դասը", "Ծրագիր", "Միջոցառում") for c in r):
                continue
            yr = [int(m.group(1)) for c in right for m in [_YEAR.search(c)] if m]
            if yr and not any(parse_amount(c)[0] is not None for c in right if not _YEAR.search(c)):
                self.years = yr
                continue
            # description rows: a heading row, then the text on the next row(s)
            kind = next((k for k, rx in _DESC.items() if rx.match(label)), None)
            if kind:
                pending_desc = kind
                rest = label.split("՝", 1)[1].strip() if "՝" in label else ""
                if rest:
                    self._describe(kind, rest, program, measure)
                    pending_desc = None
                continue
            codes = _codes(left)
            if re.fullmatch(r"[\d ]+", label or ""):
                # a code printed in the name column (PDF tables with shifted columns)
                codes.append((len(left), label.replace(" ", "")))
                label = ""
            econ = next((code_str(c) for c in right[:1] if code_str(c) and re.fullmatch(r"\d{4}", code_str(c))), None)
            amount_cells = right[1:] if right and (econ or not right[0] or re.fullmatch(r"\d{4}", right[0] or "")) else right
            amounts = [parse_amount(c) for c in amount_cells]
            has_amount = any(v is not None or f == "dash" for v, f in amounts)
            if not has_amount and not codes and not econ:
                if pending_desc and label:
                    self._describe(pending_desc, label, program, measure)
                continue
            pending_desc = None
            row_type = "economic" if econ else None
            for i, c in codes:
                if len(c) == 5:
                    measure = c
                    row_type = "measure"
                elif len(c) == 4:
                    program, measure = c, None
                    row_type = "program"
                elif len(c) <= 2:
                    # section / group / class by the column the code is printed in
                    pos = min(i, 2)
                    func[pos] = c
                    for j in range(pos + 1, 3):
                        func[j] = None
                    program = measure = None
                    row_type = ("section", "group", "class")[pos]
            if row_type is None:
                row_type = "total" if label.upper().startswith("ԸՆԴԱՄԵՆԸ") else "other"
            has_name = bool(_ARM.search(label or ""))
            if row_type == "program" and program and has_name:
                pr = self.p.programs.setdefault(program, Program(program))
                pr.name = pr.name or label
            if row_type == "measure" and measure and has_name:
                m = self.p.measures.setdefault((program, measure), Measure(measure, program))
                m.name = m.name or label
            fc = None
            if func[0]:
                fc = f"{int(func[0]):02d}.{int(func[1] or 0)}.{int(func[2] or 0)}"
            self.seq += 1
            for k, (v, flag) in enumerate(amounts):
                raw = amount_cells[k]
                if not raw:
                    continue
                self.p.allocations.append({
                    "file_id": file_id, "seq": self.seq, "col_no": k + 1, "page": page, "district_code": unit,
                    "row_type": row_type, "func_code": fc, "program_code": program,
                    "measure_code": measure if row_type in ("measure", "economic") else None,
                    "econ_code": econ, "label_hy": re.sub(r"^[-–]\s*", "", label) or None,
                    "value_year": self.years[k] if k < len(self.years) else None,
                    "amount_kamd": v, "amount_text": raw,
                })
        self.program, self.measure, self.pending_desc = program, measure, pending_desc

    def _describe(self, kind: str, text: str, program: str | None, measure: str | None) -> None:
        def add(old, new):
            # every unit (sheet) repeats the descriptions of its programmes: keep each text once
            if old and new in old:
                return old
            return f"{old} {new}".strip() if old else new
        if kind in ("goal", "result") and program:
            pr = self.p.programs.setdefault(program, Program(program))
            setattr(pr, kind, add(getattr(pr, kind), text))
        elif kind in ("measure_description", "measure_type") and measure:
            m = self.p.measures.setdefault((program, measure), Measure(measure, program))
            attr = "description" if kind == "measure_description" else "measure_type"
            setattr(m, attr, add(getattr(m, attr), text))


def read_table2(rows: list[list], parsed: Parsed, file_id: str, page: int | None, state: dict) -> None:
    """Performance indicators: programme / measure codes, indicator names and target values."""
    for r in rows:
        r = [clean(c) for c in r] + ["", "", "", ""]
        c0, c1, c2, c3 = r[0], r[1], r[2], r[3]
        if c0.startswith(("Ծրագրի դասիչ", "Միջոցառման դասիչ", "Ծրագրի միջոցառումներ", "Աղյուսակ")):
            continue
        code = code_str(c0)
        if code and re.fullmatch(r"\d{4}", code):
            state["program"], state["measure"] = code, None
            pr = parsed.programs.setdefault(code, Program(code))
            pr.name = pr.name or (c1 if _ARM.search(c1) else None)
            pr.result = pr.result or c2 or None
            continue
        if code and re.fullmatch(r"\d{5}", code):
            state["measure"] = code
            m = parsed.measures.setdefault((state.get("program"), code), Measure(code, state.get("program")))
            m.name = m.name or (c1 if _ARM.search(c1) else None)
        if state.get("measure") and c2 and not c2.endswith("՝"):
            state["n"] = state.get("n", 0) + 1
            v, _flag = parse_amount(c3)
            parsed.indicators.append({
                "file_id": file_id, "seq": state["n"], "page": page, "program_code": state.get("program"),
                "measure_code": state["measure"], "indicator_hy": c2, "value_text": c3 or None, "value_num": v,
            })


def parse(cache: dict, file_id: str, fiscal_year: int | None, n_years: int = 1) -> Parsed | None:
    """Programme tables of one extracted file (None if the file has none)."""
    parsed = Parsed()
    years = [fiscal_year + i for i in range(n_years)] if fiscal_year else []
    t1 = Table1Reader(parsed, years)
    found = False
    t2state: dict = {"n": 0}
    if cache["kind"] == "sheet":
        for sh in cache["sheets"]:
            grid: dict[int, dict[int, str]] = {}
            for r, c, text, _ in sh["cells"]:
                grid.setdefault(r, {})[c] = text
            rows = [[grid.get(r, {}).get(c) for c in range(sh["n_cols"])] for r in range(sh["n_rows"])]
            head = " ".join(clean(c) for r in rows[:10] for c in r if c)
            unit = district_of(sh["name"]) or district_of(" ".join(clean(c) for r in rows[1:5] for c in r if c))
            if is_table1(head):
                t1.unit = "?"  # every sheet starts a new hierarchy
                found = True
                t1.read(rows, unit, None, file_id)
            elif is_table2(head):
                found = True
                t2state.update(program=None, measure=None)
                read_table2(rows, parsed, file_id, None, t2state)
    elif cache["kind"] == "pdf":
        mode = None
        unit = None
        state: dict = {}
        for p in cache["pages"]:
            head = "\n".join(p["text"].splitlines()[:30])
            first_rows = " ".join(clean(c) for t in p["tables"][:1] for r in t["rows"][:6] for c in r if c)
            if is_table1(head + " " + first_rows):
                mode = "t1"
            elif is_table2(head + " " + first_rows):
                mode = "t2"
            m = re.search(r"Աղյուսակ\s*N?\s*(\d+(?:\.\d+)?)", head)
            if m:
                unit = district_of(head[m.end():m.end() + 400]) if "." in m.group(1) else None
            if mode is None:
                continue
            found = True
            for t in p["tables"]:
                if mode == "t1":
                    t1.read(t["rows"], unit, p["page"], file_id)
                else:
                    read_table2(t["rows"], parsed, file_id, p["page"], state)
    return parsed if found else None
