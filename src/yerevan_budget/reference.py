"""Static trilingual reference data: administrative districts of Yerevan."""

from __future__ import annotations

import re

# code -> (Armenian, English, Russian, regex on the upper-case Armenian title / sheet name)
DISTRICTS: dict[str, tuple[str, str, str, str]] = {
    "municipality": ("Երևանի քաղաքապետարան (առանց վարչական շրջանների)",
                     "Yerevan Municipality (without the administrative districts)",
                     "Мэрия Еревана (без административных районов)",
                     r"ՔԱՂԱՔԱՊԵՏԱՐԱՆ"),
    "ajapnyak": ("Աջափնյակ", "Ajapnyak", "Аджапняк", r"ԱՋԱՓՆՅԱԿ"),
    "avan": ("Ավան", "Avan", "Аван", r"(?<![Ա-Ֆ])ԱՎԱՆ(?![Ա-Ֆ])"),
    "arabkir": ("Արաբկիր", "Arabkir", "Арабкир", r"ԱՐԱԲԿԻՐ"),
    "davtashen": ("Դավթաշեն", "Davtashen", "Давташен", r"ԴԱՎԹԱՇԵՆ"),
    "erebuni": ("Էրեբունի", "Erebuni", "Эребуни", r"ԷՐԵԲՈՒՆԻ"),
    "kentron": ("Կենտրոն", "Kentron", "Кентрон", r"ԿԵՆՏՐՈՆ"),
    "malatia_sebastia": ("Մալաթիա-Սեբաստիա", "Malatia-Sebastia", "Малатия-Себастия", r"ՄԱԼԱԹԻԱ"),
    "nork_marash": ("Նորք-Մարաշ", "Nork-Marash", "Норк-Мараш", r"ՆՈՐՔ\s*[-–]?\s*ՄԱՐԱՇ"),
    "nor_nork": ("Նոր Նորք", "Nor Nork", "Нор-Норк", r"ՆՈՐ\s*ՆՈՐՔ"),
    "nubarashen": ("Նուբարաշեն", "Nubarashen", "Нубарашен", r"ՆՈՒԲԱՐԱՇԵՆ"),
    "shengavit": ("Շենգավիթ", "Shengavit", "Шенгавит", r"ՇԵՆԳԱՎԻԹ"),
    "kanaker_zeytun": ("Քանաքեռ-Զեյթուն", "Kanaker-Zeytun", "Канакер-Зейтун", r"ՔԱՆԱՔԵՌ"),
}
_ORDER = list(DISTRICTS)
_RX = [(code, re.compile(v[3])) for code, v in DISTRICTS.items() if code != "municipality"]


def district_of(text: str | None) -> str | None:
    """District named in a table title or sheet name ('... ԱՋԱՓՆՅԱԿ ՎԱՐՉԱԿԱՆ ՇՐՋԱՆԻ ՄԱՍՈՎ' -> 'ajapnyak')."""
    if not text:
        return None
    t = text.upper()
    for code, rx in _RX:
        if rx.search(t):
            return code
    if re.search(DISTRICTS["municipality"][3], t):
        return "municipality"
    return None


def district_rows() -> list[tuple]:
    return [(code, v[0], v[1], v[2], i) for i, (code, v) in enumerate(DISTRICTS.items())]


def sort_order(code: str) -> int:
    return _ORDER.index(code)
