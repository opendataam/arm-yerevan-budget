"""Legacy Armenian 8-bit font encoding (ArmSCII-8 / "Arial Armenian" layout) -> Unicode.

Many Yerevan budget documents were typed in legacy Armenian fonts (Arial Armenian,
Times Armenian, ...). Such fonts draw Armenian letters in place of the Latin-1
characters 0xA0-0xFF, so the text layer of the PDF / the cell values of the Excel
file contain strings like ``Ð³í»Éí³Í`` instead of ``Հավելված``.

:func:`to_unicode` maps such strings to Unicode. :func:`looks_armscii` decides
whether a string is in the legacy encoding: it must contain Latin-1 letters from
the Armenian block of the font (0xB2-0xFE) and no Unicode Armenian letters.
Unicode documents use the Latin-1 guillemets ``«»`` as quotes, so a string is only
converted when it is dominated by legacy letters.
"""

from __future__ import annotations

import re

# Punctuation of the font (0xA2-0xB1). The documents use the "Arial Armenian" variant,
# where 0xA8 ('¨') is the ligature և (in the ArmSCII-8 standard it is 0xA2).
_PUNCT = {
    0xA2: "և",
    0xA3: "։",
    0xA4: ")",
    0xA5: "(",
    0xA6: "»",
    0xA7: "«",
    0xA8: "և",
    0xA9: ".",
    0xAA: "՝",
    0xAB: ",",
    0xAC: "-",
    0xAD: "֊",
    0xAE: "…",
    0xAF: "՜",
    0xB0: "՛",
    0xB1: "՞",
    0xFE: "՚",
}

# Letters: 0xB2.. pairs (capital, small) in the order of the Armenian alphabet.
_LETTERS = "ԱաԲբԳգԴդԵեԶզԷէԸըԹթԺժԻիԼլԽխԾծԿկՀհՁձՂղՃճՄմՅյՆնՇշՈոՉչՊպՋջՌռՍսՎվՏտՐրՑցՒւՓփՔքՕօՖֆ"

TABLE: dict[int, str] = dict(_PUNCT)
for _i, _ch in enumerate(_LETTERS):
    TABLE[0xB2 + _i] = _ch

_TRANS = str.maketrans(TABLE)
_LEGACY_LETTER = re.compile(r"[²-ý]")
_UNICODE_ARMENIAN = re.compile(r"[Ա-և]")
_LATIN1 = re.compile(r"[ -ÿ]")


def to_unicode(s: str) -> str:
    """Map every character 0xA2-0xFE of ``s`` through the legacy font table."""
    return s.translate(_TRANS)


def looks_armscii(s: str | None) -> bool:
    """True if ``s`` is (most likely) Armenian text in the legacy 8-bit font encoding."""
    if not s:
        return False
    if _UNICODE_ARMENIAN.search(s):
        return False
    legacy = len(_LEGACY_LETTER.findall(s))
    if legacy == 0:
        return False
    latin1 = len(_LATIN1.findall(s))
    ascii_letters = sum(1 for ch in s if ch.isascii() and ch.isalpha())
    # a lone guillemet or degree sign in Latin text is not Armenian
    return legacy >= 2 and latin1 >= ascii_letters or legacy >= 1 and ascii_letters == 0 and latin1 == len(s.strip())


def fix(s: str | None) -> str | None:
    """Convert ``s`` to Unicode if it looks like legacy-encoded Armenian, else return it unchanged."""
    if s is None:
        return None
    return to_unicode(s) if looks_armscii(s) else s
