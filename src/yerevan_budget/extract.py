"""Step 3: extract the text and the tables of every downloaded file.

Every file of a core document (a downloaded file or a member of a downloaded
archive) is converted into a lossless intermediate form, cached in
``data/interim/<sha256[:16]>.json.gz`` (identical files are extracted once):

* PDF – the text of every page (PyMuPDF) and the tables found on it (pdfplumber);
* XLS / XLSX – every non-empty cell of every sheet;
* DOCX – paragraphs and tables; DOC – plain text (``textutil`` on macOS or
  ``soffice``).

Text in legacy Armenian 8-bit fonts is converted to Unicode on the way
(:mod:`.parsers.armscii`); the number of converted pieces is recorded.
The build step reads only this cache, so the slow PDF table detection runs once
per file content. Bump :data:`VERSION` when the extraction changes.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from . import config
from .fetch import raw_path
from .parsers import armscii
from .utils import read_json

log = logging.getLogger(__name__)

VERSION = 2
PARSED_EXT = ("pdf", "xls", "xlsx", "doc", "docx")


def files_of(rec: dict) -> list[dict]:
    """The files of a catalog document: the document itself or the members of its archive."""
    if rec.get("members"):
        base = config.EXTRACTED_DIR / rec["doc_id"]
        out = []
        for m in rec["members"]:
            ext = m["path"].rsplit(".", 1)[-1].lower() if "." in m["path"] else ""
            out.append({"doc_id": rec["doc_id"], "file_id": f"{rec['doc_id']}/{m['path']}", "member": m["path"],
                        "ext": ext, "path": base / m["path"], "sha256": m.get("sha256"), "size": m.get("size")})
        return out
    return [{"doc_id": rec["doc_id"], "file_id": rec["doc_id"], "member": None, "ext": rec["ext"],
             "path": raw_path(rec), "sha256": rec.get("sha256"), "size": rec.get("size")}]


def cache_path(sha256: str) -> Path:
    return config.INTERIM_DIR / f"{sha256[:16]}.json.gz"


def read_cache(sha256: str) -> dict | None:
    p = cache_path(sha256)
    if not p.exists():
        return None
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return json.load(f)


def _write_cache(sha256: str, obj: dict) -> None:
    p = cache_path(sha256)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    tmp.replace(p)


class _Counter:
    def __init__(self) -> None:
        self.converted = 0
        self.glyph_mapped = 0

    def fix(self, s):
        if s is None:
            return None
        if isinstance(s, str) and armscii.looks_armscii(s):
            self.converted += 1
            return armscii.to_unicode(s)
        return s


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

_CID = re.compile(r"^\(cid:(\d+)\)$")
_SUBSET = re.compile(r"^[A-Z]{6}\+")


def _glyph_maps(doc) -> dict[str, dict[int, str]]:
    """Glyph id -> character maps of the embedded Identity-H fonts that lack a ToUnicode table.

    Some reports are typed in GHEA Grapalat embedded as a CID font without the
    glyph -> Unicode table, so text extraction returns glyph ids
    (``(cid:481)`` in pdfplumber, ``chr(481)`` in PyMuPDF). The font program
    itself still has a ``cmap`` (Unicode -> glyph), which is inverted here.
    """
    maps: dict[str, dict[int, str]] = {}
    seen = set()
    for page in doc:
        for xref, ext, ftype, basefont, _name, enc in page.get_fonts(full=False):
            if xref in seen or ftype != "Type0" or "Identity" not in (enc or ""):
                continue
            seen.add(xref)
            try:
                import io

                from fontTools.ttLib import TTFont

                buf = doc.extract_font(xref)[3]
                if not buf:
                    continue
                font = TTFont(io.BytesIO(buf))
                cmap = font.getBestCmap() or {}
                inv: dict[int, str] = {}
                for code, glyph in sorted(cmap.items(), reverse=True):  # prefer the lowest code point
                    inv[font.getGlyphID(glyph)] = chr(code)
                if inv:
                    maps[_SUBSET.sub("", basefont)] = inv
            except Exception as exc:  # noqa: BLE001 - no fontTools, CFF-only fonts, broken buffers
                log.debug("font %s: no glyph map (%s)", basefont, exc)
    return maps


def _needs_glyph_map(text: str) -> bool:
    return any(ord(c) < 32 and c not in "\t\n\r" or 0x17F < ord(c) < 0x530 for c in text)


def _pdf(path: Path, cnt: _Counter) -> dict:
    import pdfplumber
    import pymupdf

    pages = []
    doc = pymupdf.open(path)
    gmaps = _glyph_maps(doc)
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(doc):
            lines = []
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    parts = []
                    for s in line["spans"]:
                        t = s["text"]
                        gm = gmaps.get(_SUBSET.sub("", s["font"]))
                        if gm and _needs_glyph_map(t):
                            t = "".join(gm.get(ord(c), c) for c in t)
                            cnt.glyph_mapped += 1
                        parts.append(cnt.fix(t))
                    t = "".join(parts)
                    if t.strip():
                        lines.append(t.rstrip())
            n_images = len(page.get_images())
            tables = []
            try:
                pp = pdf.pages[i]
                if gmaps:
                    for ch in pp.chars:
                        m = _CID.match(ch["text"])
                        if m:
                            gm = gmaps.get(_SUBSET.sub("", ch.get("fontname") or ""))
                            if gm and int(m.group(1)) in gm:
                                ch["text"] = gm[int(m.group(1))]
                # bold text is sometimes faked by printing every character twice
                pp = pp.dedupe_chars()
                for t in pp.find_tables():
                    rows = [[cnt.fix(c) if c is not None else None for c in r] for r in t.extract()]
                    tables.append({"bbox": [round(x, 1) for x in t.bbox], "rows": rows})
            except Exception as exc:  # noqa: BLE001 - pdfminer occasionally fails on broken pages
                log.warning("%s page %d: table detection failed: %s", path.name, i + 1, exc)
            pages.append({"page": i + 1, "width": round(page.rect.width, 1), "height": round(page.rect.height, 1),
                          "text": "\n".join(lines), "n_images": n_images, "tables": tables})
    return {"kind": "pdf", "n_pages": len(pages), "pages": pages, "glyph_mapped_fonts": sorted(gmaps)}


# ---------------------------------------------------------------------------
# spreadsheets
# ---------------------------------------------------------------------------

def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


_SS = "{urn:schemas-microsoft-com:office:spreadsheet}"


def _spreadsheet_xml(path: Path, cnt: _Counter) -> dict:
    """Excel 2003 XML ("SpreadsheetML") saved with an .xls extension."""
    from lxml import etree

    root = etree.parse(str(path)).getroot()
    sheets = []
    for si, ws in enumerate(root.iter(f"{_SS}Worksheet")):
        cells = []
        n_rows = n_cols = 0
        r = -1
        for table in ws.iter(f"{_SS}Table"):
            for row in table.iter(f"{_SS}Row"):
                r = int(row.get(f"{_SS}Index")) - 1 if row.get(f"{_SS}Index") else r + 1
                c = -1
                for cell in row.iter(f"{_SS}Cell"):
                    c = int(cell.get(f"{_SS}Index")) - 1 if cell.get(f"{_SS}Index") else c + 1
                    data = cell.find(f"{_SS}Data")
                    if data is not None:
                        text = "".join(data.itertext())
                        if text.strip():
                            num = None
                            if data.get(f"{_SS}Type") == "Number":
                                try:
                                    num = float(text)
                                    text = str(int(num)) if num.is_integer() else text
                                except ValueError:
                                    num = None
                            cells.append([r, c, cnt.fix(text) if num is None else text, num])
                            n_rows, n_cols = max(n_rows, r + 1), max(n_cols, c + 1)
                    c += int(cell.get(f"{_SS}MergeAcross") or 0)
        sheets.append({"index": si, "name": cnt.fix(ws.get(f"{_SS}Name")), "visible": True,
                       "n_rows": n_rows, "n_cols": n_cols, "cells": cells})
    return {"kind": "sheet", "sheets": sheets}


def _xls(path: Path, cnt: _Counter) -> dict:
    import xlrd

    with open(path, "rb") as f:
        head = f.read(512).lstrip()
    if head.startswith(b"<?xml") or b"urn:schemas-microsoft-com:office:spreadsheet" in head:
        return _spreadsheet_xml(path, cnt)
    if head[:4] == b"PK\x03\x04":
        return _xlsx(path, cnt)
    wb = xlrd.open_workbook(path, on_demand=True)
    sheets = []
    for si in range(wb.nsheets):
        sh = wb.sheet_by_index(si)
        cells = []
        for r in range(sh.nrows):
            for c in range(sh.ncols):
                v = sh.cell_value(r, c)
                if v == "" or v is None:
                    continue
                text = v if isinstance(v, str) else (repr(v) if isinstance(v, float) else str(v))
                if isinstance(v, float) and v.is_integer():
                    text = str(int(v))
                cells.append([r, c, cnt.fix(text) if isinstance(v, str) else text, _num(v)])
        sheets.append({"index": si, "name": cnt.fix(sh.name), "visible": sh.visibility == 0,
                       "n_rows": sh.nrows, "n_cols": sh.ncols, "cells": cells})
        wb.unload_sheet(si)
    return {"kind": "sheet", "sheets": sheets}


def _xlsx(path: Path, cnt: _Counter) -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = []
    for si, ws in enumerate(wb.worksheets):
        cells = []
        n_rows = n_cols = 0
        for r, row in enumerate(ws.iter_rows(values_only=True)):
            for c, v in enumerate(row):
                if v is None or v == "":
                    continue
                n_rows, n_cols = max(n_rows, r + 1), max(n_cols, c + 1)
                if isinstance(v, float) and v.is_integer():
                    text = str(int(v))
                else:
                    text = str(v)
                cells.append([r, c, cnt.fix(text) if isinstance(v, str) else text, _num(v)])
        sheets.append({"index": si, "name": ws.title, "visible": ws.sheet_state == "visible",
                       "n_rows": n_rows, "n_cols": n_cols, "cells": cells})
    wb.close()
    return {"kind": "sheet", "sheets": sheets}


# ---------------------------------------------------------------------------
# Word
# ---------------------------------------------------------------------------

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _docx(path: Path, cnt: _Counter) -> dict:
    from lxml import etree

    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("word/document.xml"))

    def ptext(p) -> str:
        return "".join(cnt.fix(t.text or "") for t in p.iter(f"{_W}t"))

    paragraphs, tables = [], []
    body = root.find(f"{_W}body")
    for el in body if body is not None else []:
        if el.tag == f"{_W}p":
            t = ptext(el)
            if t.strip():
                paragraphs.append(t)
        elif el.tag == f"{_W}tbl":
            rows = []
            for tr in el.iter(f"{_W}tr"):
                rows.append(["\n".join(ptext(p) for p in tc.iter(f"{_W}p")) for tc in tr.iter(f"{_W}tc")])
            tables.append({"rows": rows})
            paragraphs.append(f"[table {len(tables)}]")
    return {"kind": "text", "text": "\n".join(paragraphs), "tables": tables}


def _doc(path: Path, cnt: _Counter) -> dict:
    text = None
    if shutil.which("textutil"):
        r = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)], capture_output=True, check=False)
        if r.returncode == 0:
            text = r.stdout.decode("utf-8", errors="replace")
    if text is None:
        exe = shutil.which("soffice") or shutil.which("libreoffice")
        if not exe:
            raise RuntimeError("cannot read .doc: needs textutil (macOS) or soffice")
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([exe, "--headless", "--convert-to", "txt:Text (encoded):UTF8", "--outdir", tmp, str(path)],
                           check=True, capture_output=True, timeout=300)
            text = next(Path(tmp).glob("*.txt")).read_text(encoding="utf-8", errors="replace")
    lines = [cnt.fix(line) for line in text.splitlines()]
    return {"kind": "text", "text": "\n".join(lines), "tables": []}


READERS = {"pdf": _pdf, "xls": _xls, "xlsx": _xlsx, "docx": _docx, "doc": _doc}


def extract_file(path: str, ext: str, sha256: str) -> dict:
    """Extract one file and write its cache entry (runs in a worker process)."""
    cnt = _Counter()
    try:
        obj = READERS[ext](Path(path), cnt)
        obj["error"] = None
    except Exception as exc:  # noqa: BLE001 - keep going: the error is recorded in meta_file
        log.warning("%s: extraction failed: %s", path, exc)
        obj = {"kind": None, "error": f"{type(exc).__name__}: {exc}"}
    obj.update({"version": VERSION, "sha256": sha256, "ext": ext, "legacy_font_conversions": cnt.converted,
                "glyph_mapped_spans": cnt.glyph_mapped})
    _write_cache(sha256, obj)
    return {"sha256": sha256, "error": obj["error"]}


def run(force: bool = False, only: tuple[str, ...] = (), workers: int | None = None) -> None:
    docs = read_json(config.CATALOG_DIR / "documents.json", [])
    todo: dict[str, tuple[str, str]] = {}
    for rec in docs:
        if rec["group"] != "core" or not rec.get("sha256") or (only and rec["doc_id"] not in only):
            continue
        for f in files_of(rec):
            if f["ext"] not in PARSED_EXT or not f["sha256"]:
                continue
            if not force:
                c = read_cache(f["sha256"])
                if c and c.get("version") == VERSION and not c.get("error"):
                    continue
            todo[f["sha256"]] = (str(f["path"]), f["ext"])
    if not todo:
        log.info("extract: cache is up to date")
        return
    # largest files first so that the pool finishes evenly
    items = sorted(todo.items(), key=lambda kv: -os.path.getsize(kv[1][0]))
    workers = workers or max(1, min(8, (os.cpu_count() or 2) - 1))
    log.info("extract: %d files with %d workers", len(items), workers)
    errors = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(extract_file, p, ext, sha): p for sha, (p, ext) in items}
        for i, fut in enumerate(as_completed(futs), 1):
            res = fut.result()
            errors += bool(res["error"])
            if i % 20 == 0 or i == len(futs):
                log.info("extract: %d / %d", i, len(futs))
    log.info("extract: done, %d errors", errors)

