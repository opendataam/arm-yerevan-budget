"""HTML of the yerevan.am finance pages: document links and the accordion headings."""

from __future__ import annotations

import re
import urllib.parse

from lxml import html as lxml_html

from .. import config

_WS = re.compile(r"\s+")
_SIZE = re.compile(r"/?\s*ներբեռնել՝?\s*([\d.,]+)\s*([KkКкԿկ][bBբ]|[MmМмՄմ][bBբ]|[Gg][bB])\s*/?")
_YEAR_HEADING = re.compile(r"^(20\d\d)\s*թ")


def clean(s: str | None) -> str:
    return _WS.sub(" ", (s or "").replace("\xa0", " ")).strip()


def normalize_url(href: str) -> str:
    """Absolute https URL with a percent-encoded path (links on the site are mixed: raw Armenian or encoded)."""
    url = urllib.parse.urljoin(config.BASE_URL + "/", href.strip())
    p = urllib.parse.urlsplit(url)
    if p.hostname not in ("www.yerevan.am", "yerevan.am"):
        return url  # external link (e.g. the interactive budget site)
    path = urllib.parse.quote(urllib.parse.unquote(p.path), safe="/")
    return urllib.parse.urlunsplit(("https", "www.yerevan.am", path, "", ""))


def file_name(url: str) -> str:
    return urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1])


def extension(url: str) -> str | None:
    name = file_name(url).lower()
    ext = name.rsplit(".", 1)[-1] if "." in name else ""
    return ext if ext in config.DOC_EXTENSIONS else None


def size_hint(text: str) -> tuple[str, float | None]:
    """Split 'Նախահաշիվներ / ներբեռնել՝ 31 Mb/' into the title and the size in MB stated on the page."""
    m = _SIZE.search(text)
    if not m:
        return text, None
    num = float(m.group(1).replace(",", "."))
    unit = m.group(2)[0].lower()
    mb = num / 1024 if unit in "kкկ" else num * 1024 if unit == "g" else num
    return clean(text[: m.start()].rstrip(" /")), round(mb, 3)


def _content(tree):
    """The main content block of a page (without the site menu and footer)."""
    for xp in ('//div[contains(@class,"submenu-section")]', '//div[contains(@class,"description-section")]'):
        nodes = tree.xpath(xp)
        if nodes:
            return nodes[0]
    return tree


def parse_page(text: str) -> dict:
    """Title of the page and the document links in its content block, in page order.

    For the pages of the institutions the accordion headings are tracked: a link
    ``#collapseTwoN`` names the group of institutions (schools, kindergartens, ...)
    and a link ``#collapseWindowN`` the year; every file link gets the headings above it.
    """
    tree = lxml_html.fromstring(text)
    title = clean(" ".join(tree.xpath("//title//text()"))).replace("yerevan.am | ", "")
    body = _content(tree)
    docs, subpages = [], []
    group = year_heading = None
    pos = 0
    seen: set[str] = set()
    for a in body.iter("a"):
        href = a.get("href") or ""
        label = clean(a.text_content())
        if href.startswith("#collapseTwo"):
            group, year_heading = label, None
            continue
        if href.startswith("#collapseWindow"):
            year_heading = label
            continue
        if href.startswith("/hy/") and href.count("/") == 3:
            subpages.append(href.strip("/").split("/")[-1])
            continue
        if not href or href.startswith("#"):
            continue
        url = normalize_url(href)
        ext = extension(url)
        if url in seen:
            continue
        seen.add(url)
        if not ext:
            if "budget.yerevan.am" in href:
                docs.append({"url": href, "ext": None, "link_text": label, "position": pos, "external": True})
                pos += 1
            continue
        link_text, mb = size_hint(label)
        m = _YEAR_HEADING.match(year_heading or "")
        docs.append({
            "url": url,
            "ext": ext,
            "link_text": re.sub(r"^\s*\d{1,2}\s*[.,]\s*|^\s*[.,+]\s*", "", link_text).strip() or link_text,
            "position": pos,
            "group_heading": group,
            "year_heading": year_heading,
            "heading_year": int(m.group(1)) if m else None,
            "size_mb_stated": mb,
        })
        pos += 1
    # the main finance page puts the archive buttons above the content block
    for a in tree.xpath('//div[contains(@class,"news-area")]//a'):
        href = a.get("href") or ""
        if href.startswith("/hy/") and href.count("/") == 3:
            subpages.append(href.strip("/").split("/")[-1])
    return {"title": title, "documents": docs, "subpages": sorted(set(subpages))}
