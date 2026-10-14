import re
from collections import defaultdict
from collections.abc import Iterable

from app.domain.candidate import Candidate
from app.domain.card_text import CardText

BOUNDARY = re.compile(r"[;\n!?]|(?<!\d)[.,]|[.,](?!\d)")
ACCESSORY = re.compile(r"\b(?:чех\w*|ремеш\w*|кабел\w*|пленк\w*|case|cover|strap)\b")
MAIN_PRODUCT = re.compile(r"\b(?:смартфон\w*|ноутбук\w*|телефон\w*|smartphone|laptop|phone)\b")
EXCLUSION = re.compile(r"\b(?:совместим\w*|подходит для|в отличие|compatible|compared to)\b")
NEGATION = re.compile(r"\b(?:не|нет|без|not|without)\s+(?:\w+\s+){0,2}$")
NEGATED_VALUE = re.compile(r"^(?:не|нет|без|not|without)\b")
RANGE = re.compile(r"(?:\b(?:от|до|более|менее|from|up to)\s*$)|(?:\d\s*[-–—]\s*$)")


def context_of(card: CardText, start: int, end: int) -> tuple[str, str]:
    before = card.match[:start]
    boundaries = list(BOUNDARY.finditer(before))
    left = boundaries[-1].end() if boundaries else 0
    after = BOUNDARY.search(card.match, end)
    right = after.start() if after else len(card.match)
    return card.match[left:right], card.match[left:start]


def supported(card: CardText, candidate: Candidate) -> bool:
    if not candidate.evidence or card.span(candidate.start, candidate.end) != candidate.evidence:
        return False
    clause, before = context_of(card, candidate.start, candidate.end)
    if EXCLUSION.search(clause) or NEGATION.search(before):
        return False
    if NEGATED_VALUE.search(card.match[candidate.start : candidate.end]):
        return False
    if candidate.source == "number" and (RANGE.search(before) or before.rstrip().endswith("-")):
        return False
    title = card.match[: card.title_end]
    product = MAIN_PRODUCT.search(title)
    accessory = ACCESSORY.search(title)
    main_first = product is not None and (accessory is None or product.start() < accessory.start())
    return not (main_first and ACCESSORY.search(clause) and not MAIN_PRODUCT.search(clause))


def conflicts(candidates: Iterable[Candidate]) -> frozenset[str]:
    keys: dict[str, set[str]] = defaultdict(set)
    for candidate in candidates:
        keys[candidate.attribute].add(candidate.key)
    return frozenset(name for name, values in keys.items() if len(values) > 1)
