"""Cleaning of values, codes and labels."""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_NUM = re.compile(r"^\(?\s*[-–−]?\s*[\d\s ,]*\.?\d+\s*\)?$")
NOT_APPLICABLE = {"x", "х", "X", "Х"}  # Latin and Cyrillic x: "not applicable" cells of the forms
ZERO = {"-", "–", "—", "−"}


def clean(s) -> str:
    if s is None:
        return ""
    return _WS.sub(" ", str(s).replace("\xa0", " ")).strip()


def parse_amount(s) -> tuple[float | None, str | None]:
    """Parse an amount cell. Returns (value, flag).

    ``'159,399,554.2'`` -> 159399554.2; ``'(87,805.5)'`` and ``'-30,319.1'`` -> negative;
    ``'-'`` -> 0 (flag ``dash``); ``'X'`` -> None (flag ``na``); empty -> (None, None);
    anything else -> (None, ``text``).
    """
    t = clean(s)
    if not t:
        return None, None
    if t in NOT_APPLICABLE:
        return None, "na"
    if t in ZERO:
        return 0.0, "dash"
    if not _NUM.match(t):
        return None, "text"
    neg = t.startswith("(") and t.endswith(")") or t.lstrip("(").lstrip().startswith(("-", "–", "−"))
    digits = re.sub(r"[^\d.]", "", t)
    if digits.count(".") > 1:
        return None, "text"
    try:
        v = float(digits)
    except ValueError:
        return None, "text"
    return (-v if neg else v), None


def is_amount(s) -> bool:
    v, flag = parse_amount(s)
    return v is not None or flag in ("na", "dash")


def code_str(s) -> str | None:
    """'1112.0' -> '1112'; ' 7100 ' -> '7100'; '' -> None."""
    t = clean(s)
    if not t:
        return None
    if re.fullmatch(r"\d+\.0", t):
        t = t[:-2]
    return t


_MARKERS = re.compile(r"^(այդ\s*թվում|որից|այդ թվում՝|այդ թվում`)\s*[`՝':,.]?\s*$", re.IGNORECASE)


def is_marker(label: str) -> bool:
    """'այդ թվում`' ("including"), 'որից`' ("of which"): structural words of the forms, not data."""
    return bool(_MARKERS.match(clean(label)))


def norm_key(s: str | None) -> str:
    """Comparison key of an Armenian label: letters and digits only, lower case, NFC, ու/և unified."""
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s).lower().replace("եւ", "և")
    return re.sub(r"[^\w]+", "", s.replace("_", ""))


def clean_label(s: str | None) -> str | None:
    """Collapse whitespace, drop leading list dashes and the trailing 'այդ թվում`' ("including")."""
    t = clean(s)
    if not t:
        return None
    t = re.sub(r"\s*[,]?\s*(այդ\s*թվում|որից)\s*[`՝':]?\s*$", "", t)
    t = re.sub(r"^[-–]\s*", "", t)
    return t.strip() or None
