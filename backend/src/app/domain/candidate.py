import math
import re
from dataclasses import dataclass

from app.domain.card_text import CardText, match_form
from app.domain.profile import STEM, AttributeProfile, keyword_overlap
from app.domain.values import NUMBER, parse_number

NEAR_WINDOW = 60
RANGE_WORDS_OPEN = re.compile(r"(?:более|больше|свыше|от)\s")
RANGE_WORDS_CLOSED = re.compile(r"(?:менее|меньше|до)\s")
RANGE_PAIR = re.compile(rf"{NUMBER}\s*(?:-|–|—|до)\s*{NUMBER}")
NUMBER_RE = re.compile(NUMBER)
NEAR_WORD = re.compile(r"[a-zа-я]+")


class Source:
    KEY_VALUE = "key_value"
    SELLER = "seller"
    DICTIONARY = "dictionary"
    NUMBER = "number"
    TITLE_MODEL = "title_model"


@dataclass(frozen=True, slots=True)
class Candidate:
    attribute: str
    key: str
    value: str
    evidence: str
    start: int
    end: int
    source: str
    zone: str
    affinity: float
    prior: float
    seller_fit: int
    slot: int = -1


@dataclass(frozen=True, slots=True)
class SellerRange:
    low: float
    high: float

    def fit(self, value: float) -> int:
        return 1 if self.low - 1e-9 <= value <= self.high + 1e-9 else -1


def is_range(value: str) -> bool:
    text = match_form(value)
    return bool(RANGE_PAIR.search(text) or RANGE_WORDS_OPEN.search(text)
                or RANGE_WORDS_CLOSED.search(text))


def parse_range(value: str) -> SellerRange | None:
    text = match_form(value)
    numbers = [parse_number(n) for n in NUMBER_RE.findall(text)]
    if not numbers:
        return None
    if len(numbers) >= 2:
        return SellerRange(min(numbers[:2]), max(numbers[:2]))
    if RANGE_WORDS_OPEN.search(text):
        return SellerRange(numbers[0], math.inf)
    if RANGE_WORDS_CLOSED.search(text):
        return SellerRange(0.0, numbers[0])
    return SellerRange(numbers[0], numbers[0])


def nearby_affinity(card: CardText, profile: AttributeProfile, start: int) -> float:
    window = card.match[max(0, start - NEAR_WINDOW):start]
    if not profile.keywords:
        return 0.0
    stems = {w[:STEM] for w in NEAR_WORD.findall(window) if len(w) >= 3}
    return sum(1 for k in profile.keywords if k in stems) / len(profile.keywords)


def name_affinity(profile: AttributeProfile, key: str) -> float:
    return keyword_overlap(profile.keywords, key)
