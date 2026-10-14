import hashlib
import re
from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, TypedDict

from app.domain.card_text import match_form
from app.domain.profile import BRAND, MODEL, Kind
from app.domain.values import canonical_key, canonical_text
from app.usecase.baseline import extra_attributes
from app.usecase.baseline_ports import CardRecord, GoldRecord, RequiredRecord
from app.usecase.extraction import CardExtraction, RequiredAttributes, extract_card
from app.usecase.lexicon_builder import TrainValue, build_lexicon

SPLITS = frozenset({"train", "val", "test", "new_category"})
MEMORY = re.compile(r"\b\d+(?:/\d+)?\s*(?:gb|гб|tb|тб)\b")


class AuditSource(Protocol):
    def required(self) -> Sequence[RequiredRecord]: ...
    def train_values(self, attributes: frozenset[str]) -> Iterator[TrainValue]: ...
    def gold(self, splits: frozenset[str]) -> Mapping[int, Sequence[GoldRecord]]: ...
    def cards(self, splits: frozenset[str] | None, batch: int) -> Iterator[list[CardRecord]]: ...


class Example(TypedDict):
    sku_id: int
    split: str | None
    text: str
    gold: str
    predicted: str | None
    quote: str | None
    reason: str


class Discrepancy(TypedDict):
    count: int
    examples: list[Example]


class Overlap(TypedDict):
    groups: int
    cards: int
    examples: list[list[int]]


class AuditReport(TypedDict):
    schema_version: int
    seed: int
    samples_per_group: int
    cards: int
    splits: dict[str, int]
    independent_human_validation: bool
    policy: str
    overlaps: dict[str, Overlap]
    discrepancies: dict[str, Discrepancy]


@dataclass(frozen=True, slots=True)
class AuditConfig:
    seed: int = 42
    samples_per_group: int = 5
    batch: int = 2000


class OverlapIndex:
    def __init__(self) -> None:
        self._groups: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))

    def add(self, key: str, card: CardRecord) -> None:
        if key and card.split in SPLITS:
            self._groups[key][str(card.split)].append(card.sku_id)

    def report(self, limit: int) -> Overlap:
        groups = [sorted(sku for ids in splits.values() for sku in ids)
                  for _, splits in sorted(self._groups.items()) if len(splits) > 1]
        return {"groups": len(groups), "cards": sum(map(len, groups)),
                "examples": [ids[:10] for ids in groups[:limit]]}


def family_key(card: CardRecord, gold: Sequence[GoldRecord]) -> str:
    labels = {g.attribute: g.value for g in gold}
    model = canonical_text(labels.get(MODEL, ""))
    if not model:
        return ""
    model = " ".join(MEMORY.sub("", model).split())
    return f"{card.category_id}:{canonical_text(labels.get(BRAND, ''))}:{model}"


def discrepancy(extraction: CardExtraction, gold: GoldRecord) -> tuple[str, Example] | None:
    profile = extraction.profiles.get(gold.attribute)
    if profile is None:
        return None
    pick = extraction.picks.get(gold.attribute)
    expected = canonical_key(gold.value, gold.unit or profile.unit, profile.numeric)
    if pick and pick.candidate.key == expected:
        return None
    if profile.kind is Kind.UNSUPPORTED:
        reason = "unsupported"
    elif pick:
        reason = "wrong_selection"
    elif gold.attribute in extraction.review:
        reason = "review"
    else:
        reason = "missing_candidate"
    suggested = pick or extraction.review.get(gold.attribute)
    example: Example = {
        "sku_id": 0, "split": None, "text": extraction.text.text,
        "gold": gold.value, "predicted": suggested.candidate.value if suggested else None,
        "quote": suggested.candidate.evidence if suggested else None, "reason": reason,
    }
    return f"{gold.attribute}:{reason}", example


class AuditCatalog:
    def __init__(self, source: AuditSource) -> None:
        self._source = source

    def run(self, config: AuditConfig) -> AuditReport:
        if config.samples_per_group < 1 or config.batch < 1:
            raise ValueError("Audit sample and batch sizes must be positive")
        records = self._source.required()
        names = frozenset(r.attribute for r in records) | extra_attributes()
        lexicon = build_lexicon(self._source.train_values(names))
        required = RequiredAttributes(records, lexicon)
        gold = self._source.gold(SPLITS)
        exact, family = OverlapIndex(), OverlapIndex()
        counts: Counter[str] = Counter()
        sizes: Counter[str] = Counter()
        samples: dict[str, list[tuple[str, Example]]] = defaultdict(list)
        for batch in self._source.cards(SPLITS, config.batch):
            for card in batch:
                extraction = extract_card(card, required, lexicon, 0.35)
                labels = gold.get(card.sku_id, ())
                normalized = " ".join(match_form(extraction.text.text).split())
                exact.add(hashlib.sha256(normalized.encode()).hexdigest(), card)
                family.add(family_key(card, labels), card)
                sizes[str(card.split)] += 1
                for label in labels:
                    found = discrepancy(extraction, label)
                    if found is None:
                        continue
                    group, example = found
                    example["sku_id"] = card.sku_id
                    example["split"] = card.split
                    counts[group] += 1
                    key = hashlib.sha256(f"{config.seed}:{card.sku_id}:{group}".encode()).hexdigest()
                    samples[group].append((key, example))
                    samples[group].sort(key=lambda pair: pair[0])
                    del samples[group][config.samples_per_group:]
        return {
            "schema_version": 1, "seed": config.seed, "samples_per_group": config.samples_per_group,
            "cards": sum(sizes.values()), "splits": dict(sorted(sizes.items())),
            "independent_human_validation": False,
            "policy": "normalized exact text; category+gold brand/model without memory; "
                      "lowest seeded SHA256 per attribute/reason; reasons are hypotheses; "
                      "only cards with text; original splits unchanged",
            "overlaps": {"exact_text": exact.report(config.samples_per_group),
                         "model_family": family.report(config.samples_per_group)},
            "discrepancies": {group: {"count": count,
                                      "examples": [example for _, example in samples[group]]}
                              for group, count in sorted(counts.items())},
        }
