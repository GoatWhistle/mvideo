from decimal import Decimal

MEASURES: dict[str, tuple[str, str]] = {
    "кг": ("кг", "1"), "г": ("кг", "0.001"), "мг": ("кг", "0.000001"),
    "см": ("см", "1"), "мм": ("см", "0.1"), "м": ("см", "100"),
    '"': ("см", "2.54"),
    "вт": ("вт", "1"), "квт": ("вт", "1000"),
    "гб": ("гб", "1"), "тб": ("гб", "1000"), "мб": ("гб", "0.001"),
    "gib": ("гб", "1.073741824"), "mib": ("гб", "0.001048576"),
    "tib": ("гб", "1099.511627776"),
    "гц": ("гц", "1"), "мгц": ("гц", "1000000"), "ггц": ("гц", "1000000000"),
    "л": ("л", "1"), "мл": ("л", "0.001"),
    "мач": ("мач", "1"), "ач": ("мач", "1000"),
}


def convert_number(number: float, source: str, target: str) -> float | None:
    if source == target:
        return number
    source_base, source_scale = MEASURES.get(source, (source, "1"))
    target_base, target_scale = MEASURES.get(target, (target, "1"))
    if source_base != target_base:
        return None
    return float(Decimal(str(number)) * Decimal(source_scale) / Decimal(target_scale))


def base_unit(unit: str) -> str:
    return MEASURES.get(unit, (unit, "1"))[0]
