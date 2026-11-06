"""Step 2: download the documents listed in ``data/catalog/documents.json``.

* core documents go to ``data/raw/files/<doc_id>.<ext>``; ``rar`` / ``zip`` /
  ``7z`` archives are unpacked into ``data/raw/extracted/<doc_id>/``;
* documents of the municipal institutions (≈10 GB of rar archives) are only
  downloaded with ``--institutions`` into ``data/raw/institutions/``; their
  archives are listed (``members``) but not unpacked or parsed.

Archives need ``unrar`` (rar), ``7zz``/``7z`` or ``bsdtar`` (zip, 7z; also rar
when ``unrar`` is missing). The list of members with sizes and hashes is stored in
the catalog, so the database records exactly which files were parsed.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import unicodedata
from pathlib import Path

from . import config
from .http import Client
from .utils import read_json, sha256_file, utc_now, write_json

log = logging.getLogger(__name__)

ARCHIVES = ("rar", "zip", "7z")


def raw_path(rec: dict) -> Path:
    base = config.FILES_DIR if rec["group"] == "core" else config.INSTITUTIONS_DIR
    return base / f"{rec['doc_id']}.{rec['ext']}"


def _tool(*names: str) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def unpack(archive: Path, dest: Path) -> None:
    """Unpack ``archive`` into ``dest`` (replaced if it exists)."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    ext = archive.suffix.lower().lstrip(".")
    unrar, sevenz, bsdtar = _tool("unrar"), _tool("7zz", "7z", "7za"), _tool("bsdtar")
    if ext == "rar" and unrar:
        cmd = [unrar, "x", "-o+", "-inul", str(archive), str(dest) + "/"]
    elif sevenz and ext != "rar":
        cmd = [sevenz, "x", "-y", f"-o{dest}", str(archive)]
    elif bsdtar:
        cmd = [bsdtar, "-xf", str(archive), "-C", str(dest)]
    else:
        raise SystemExit(f"cannot unpack {archive}: install unrar (rar) and 7zz / bsdtar (zip)")
    subprocess.run(cmd, check=True, capture_output=True)


def list_members(archive: Path) -> list[dict]:
    """Members of an archive without unpacking it (used for the institutional archives)."""
    unrar, sevenz = _tool("unrar"), _tool("7zz", "7z", "7za")
    out = []
    if archive.suffix.lower() == ".rar" and unrar:
        r = subprocess.run([unrar, "lb", str(archive)], capture_output=True, text=True, check=False)
        out = [{"path": unicodedata.normalize("NFC", p)} for p in r.stdout.splitlines() if p.strip()]
    elif sevenz:
        r = subprocess.run([sevenz, "l", "-ba", "-slt", str(archive)], capture_output=True, text=True, check=False)
        cur: dict = {}
        for line in r.stdout.splitlines() + [""]:
            if not line.strip():
                if cur.get("Path") and cur.get("Folder") != "+":
                    out.append({"path": unicodedata.normalize("NFC", cur["Path"]), "size": int(cur.get("Size") or 0)})
                cur = {}
            elif " = " in line:
                k, v = line.split(" = ", 1)
                cur[k] = v
    return out


def members_of(dest: Path) -> list[dict]:
    out = []
    for p in sorted(dest.rglob("*")):
        if p.is_file():
            rel = unicodedata.normalize("NFC", str(p.relative_to(dest)))
            out.append({"path": rel, "size": p.stat().st_size, "sha256": sha256_file(p)})
    return out


def download(force: bool = False, institutions: bool = False, client: Client | None = None) -> list[dict]:
    client = client or Client()
    catalog_path = config.CATALOG_DIR / "documents.json"
    docs = read_json(catalog_path, [])
    if not docs:
        raise SystemExit("data/catalog/documents.json is empty: run `python -m yerevan_budget catalog` first")
    by_sha: dict[str, str] = {}
    try:
        for rec in docs:
            if rec["group"] != "core" and not institutions:
                continue
            path = raw_path(rec)
            if force or not path.exists():
                log.info("download %s %s", rec["doc_id"], rec["file_name"])
                try:
                    client.download(rec["url"], path)
                except RuntimeError as exc:
                    log.error("%s: %s", rec["url"], exc.__cause__ or exc)
                    rec["error"] = str(exc.__cause__ or exc)
                    continue
                rec["downloaded_at"] = utc_now()
                rec.pop("error", None)
            rec["size"] = path.stat().st_size
            rec["sha256"] = sha256_file(path)
            rec["path"] = str(path.relative_to(config.DATA_DIR))
            # the same file is sometimes published under two URLs
            first = by_sha.setdefault(rec["sha256"], rec["doc_id"])
            if first != rec["doc_id"]:
                rec["duplicate_of"] = first
            else:
                rec.pop("duplicate_of", None)
            if rec["ext"] in ARCHIVES:
                if rec["group"] == "core":
                    dest = config.EXTRACTED_DIR / rec["doc_id"]
                    if force or not dest.exists() or not rec.get("members"):
                        unpack(path, dest)
                    rec["members"] = members_of(dest)
                elif not rec.get("members"):
                    rec["members"] = list_members(path)
    finally:
        write_json(catalog_path, docs)  # keep progress if interrupted
    n = sum(1 for r in docs if r.get("sha256"))
    log.info("fetch: %d documents on disk", n)
    return docs
