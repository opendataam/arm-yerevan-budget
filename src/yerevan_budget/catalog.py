"""Step 1: crawl the "Finance" section of yerevan.am and list every document.

Saves the page HTML to ``data/raw/pages/<slug>.html`` and writes the manifests

* ``data/catalog/pages.json``     – the crawled pages;
* ``data/catalog/documents.json`` – every distinct document (by URL) with its
  title, the pages that link it, its classification (type / year / period) and,
  after ``fetch``, the download information (size, sha256, archive members).

Only the Armenian version of the section has content: the English and Russian
pages say "The content is available only in Armenian version".
"""

from __future__ import annotations

import hashlib
import logging

from . import classify, config
from .http import Client
from .parsers.pages import file_name, parse_page
from .utils import read_json, sha256_bytes, utc_now, write_json

log = logging.getLogger(__name__)

# fields filled by later steps and kept when the catalog is rebuilt
KEEP = ("size", "sha256", "downloaded_at", "http_last_modified", "members", "duplicate_of", "path")


def page_url(slug: str) -> str:
    return f"{config.BASE_URL}/{config.LANG}/{slug}/"


def doc_id(url: str) -> str:
    """Stable id of a document: the first 10 hex digits of the SHA-1 of its URL."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]


def crawl(client: Client | None = None) -> dict:
    client = client or Client()
    pages, docs = [], {}
    for slug, meta in config.PAGES.items():
        url = page_url(slug)
        log.info("page %s", url)
        raw = client.get(url).content
        path = config.PAGES_DIR / f"{slug}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        parsed = parse_page(raw.decode("utf-8", errors="replace"))
        pages.append({
            "slug": slug,
            "url": url,
            "group": meta["group"],
            "year": meta.get("year"),
            "title_hy": parsed["title"] if meta["group"] == "core" else None,
            "title_en": meta["title_en"],
            "fetched_at": utc_now(),
            "sha256": sha256_bytes(raw),
            "n_documents": len(parsed["documents"]),
            "subpages": parsed["subpages"],
        })
        for d in parsed["documents"]:
            if d.get("external"):
                continue
            rec = docs.get(d["url"])
            link = {"page": slug, "position": d["position"], "link_text": d["link_text"]}
            if rec is not None:
                rec["links"].append(link)
                continue
            cls = classify.classify(d["link_text"], page_year=meta.get("year"), group=meta["group"],
                                    heading_year=d.get("heading_year"), group_heading=d.get("group_heading"))
            did = doc_id(d["url"])
            cls.update(classify.OVERRIDES.get(did, {}))
            docs[d["url"]] = {
                "doc_id": did,
                "group": meta["group"],
                "url": d["url"],
                "file_name": file_name(d["url"]),
                "ext": d["ext"],
                "title_hy": d["link_text"],
                **cls,
                "institution_group_hy": d.get("group_heading"),
                "size_mb_stated": d.get("size_mb_stated"),
                "links": [link],
            }
    write_json(config.CATALOG_DIR / "pages.json", pages)
    old = {d["doc_id"]: d for d in read_json(config.CATALOG_DIR / "documents.json", [])}
    out = []
    for rec in docs.values():
        prev = old.get(rec["doc_id"], {})
        for k in KEEP:
            if k in prev:
                rec[k] = prev[k]
        out.append(rec)
    out.sort(key=lambda r: (r["group"] != "core", r["fiscal_year"] or 0, r["doc_type"], r["doc_id"]))
    write_json(config.CATALOG_DIR / "documents.json", out)
    n_core = sum(r["group"] == "core" for r in out)
    log.info("catalog: %d pages, %d documents (%d core, %d institutional)", len(pages), len(out), n_core, len(out) - n_core)
    return {"pages": pages, "documents": out}
