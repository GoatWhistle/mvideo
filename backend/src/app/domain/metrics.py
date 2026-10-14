from collections import defaultdict
from dataclasses import dataclass, field

from app.domain.card_text import CardText
from app.domain.extractors import extract_candidates
from app.domain.lexicon import Lexicon, match_token, value_tokens
from app.domain.profile import AttributeProfile
from app.domain.values import canonical_key

MACRO_MIN_GOLD = 20


@dataclass(frozen=True, slots=True)
class Observation:
    attribute: str
    has_gold: bool
    predicted: bool
    correct: bool
    reachable: bool
    seller_filled: bool
    weight: float = 1.0
    candidate_found: bool = False
    reviewed: bool = False
    supported: bool = True


@dataclass(slots=True)
class Counts:
    pairs: float = 0.0
    gold: float = 0.0
    predicted: float = 0.0
    tp: float = 0.0
    fp: float = 0.0
    fn: float = 0.0
    extra: float = 0.0
    reachable: float = 0.0
    tp_reachable: float = 0.0
    seller_filled: float = 0.0
    candidate_found: float = 0.0
    reviewed: float = 0.0
    unsupported: float = 0.0

    def add(self, o: Observation, weighted: bool) -> None:
        w = o.weight if weighted else 1.0
        self.pairs += w
        self.predicted += w if o.predicted else 0.0
        self.seller_filled += w if o.seller_filled else 0.0
        self.reviewed += w if o.reviewed else 0.0
        self.unsupported += w if not o.supported else 0.0
        if not o.has_gold:
            self.extra += w if o.predicted else 0.0
            return
        self.gold += w
        self.candidate_found += w if o.candidate_found else 0.0
        self.reachable += w if o.reachable else 0.0
        if o.predicted and o.correct:
            self.tp += w
            self.tp_reachable += w if o.reachable else 0.0
            return
        self.fn += w
        self.fp += w if o.predicted else 0.0

    def summary(self) -> dict[str, float]:
        precision = self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0
        recall = self.tp / self.gold if self.gold else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {
            "pairs": round(self.pairs, 3),
            "gold": round(self.gold, 3),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "ceiling": round(self.reachable / self.gold, 4) if self.gold else 0.0,
            "recall_in_text": round(self.tp_reachable / self.reachable, 4) if self.reachable else 0.0,
            "coverage_before": round(self.seller_filled / self.pairs, 4) if self.pairs else 0.0,
            "coverage_after": round(self.predicted / self.pairs, 4) if self.pairs else 0.0,
            "gold_coverage": round(self.gold / self.pairs, 4) if self.pairs else 0.0,
            "extra_fills": round(self.extra, 3),
            "candidate_recall": round(self.candidate_found / self.gold, 4) if self.gold else 0.0,
            "review_rate": round(self.reviewed / self.pairs, 4) if self.pairs else 0.0,
            "unsupported_rate": round(self.unsupported / self.pairs, 4) if self.pairs else 0.0,
        }


@dataclass(slots=True)
class MetricsBook:
    weighted: bool
    groups: dict[str, dict[str, Counts]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(Counts))
    )

    def add(self, group_names: list[str], observation: Observation) -> None:
        for group in group_names:
            self.groups[group][observation.attribute].add(observation, self.weighted)

    def micro(self, group: str) -> dict[str, float]:
        total = Counts()
        for counts in self.groups.get(group, {}).values():
            for name in Counts.__slots__:
                setattr(total, name, getattr(total, name) + getattr(counts, name))
        return total.summary()

    def macro_f1(self, group: str) -> float:
        scores = [c.summary()["f1"] for c in self.groups.get(group, {}).values()
                  if c.gold >= MACRO_MIN_GOLD or (self.weighted and c.gold > 0)]
        return round(sum(scores) / len(scores), 4) if scores else 0.0

    def attributes(self, group: str) -> dict[str, dict[str, float]]:
        items = self.groups.get(group, {})
        ranked = sorted(items.items(), key=lambda kv: -kv[1].gold)
        return {name: counts.summary() for name, counts in ranked}


def value_in_text(
    card: CardText, value: str, unit: str | None, profile: AttributeProfile
) -> bool:
    if profile.numeric:
        target = canonical_key(value, unit or profile.unit, True)
        profiles = {profile.name: profile}
        candidates = extract_candidates(card, profiles, Lexicon(profiles, (), {}), None)
        return any(c.key == target and (c.affinity > 0 or c.slot >= 0) for c in candidates)
    wanted = value_tokens(value)
    if not wanted:
        return False
    normalized = [match_token(t.text) for t in card.tokens]
    size = len(wanted)
    return any(tuple(normalized[i:i + size]) == wanted for i in range(len(normalized) - size + 1))
