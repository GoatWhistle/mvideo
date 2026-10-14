import re
from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.card_text import match_form
from app.domain.evidence import ACCESSORY, EXCLUSION


@dataclass(frozen=True, slots=True)
class CategoryOption:
    category_id: int
    name: str
    keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CategorySelection:
    category_id: int | None
    reason: str
    alternatives: tuple[CategoryOption, ...] = ()


def select_category(text: str, categories: Sequence[CategoryOption]) -> CategorySelection:
    title = match_form(text).split("\n")[0]
    exclusion = EXCLUSION.search(title)
    if exclusion:
        title = title[: exclusion.start()]
    accessory = ACCESSORY.search(title)
    matches = []
    for category in categories:
        found = [
            m
            for keyword in category.keywords
            if (m := re.search(r"\b" + re.escape(match_form(keyword)) + r"\w*", title))
        ]
        if not found:
            continue
        first = min(m.start() for m in found)
        if accessory and accessory.start() < first:
            continue
        matches.append(category)
    if len(matches) == 1:
        return CategorySelection(matches[0].category_id, "category_detected", tuple(matches))
    return CategorySelection(
        None,
        "category_ambiguous" if matches else "category_unknown",
        tuple(matches) if matches else tuple(categories),
    )
