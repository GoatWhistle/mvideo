from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace

from app.domain.candidate import Candidate
from app.domain.lexicon import Lexicon
from app.domain.profile import BRAND, MODEL
from app.domain.scoring import Pick
from app.domain.twin import (
    TWIN_SOURCE,
    Transfer,
    TwinEntry,
    TwinQuery,
    TwinValue,
    title_numbers,
    twin_title,
)
from app.domain.values import canonical_key, display_value
from app.usecase.baseline_ports import CardRecord, GoldRecord
from app.usecase.extraction import CardExtraction
from app.usecase.twin_ports import StageRecord


@dataclass(slots=True)
class TwinIndexData:
    entries: list[TwinEntry] = field(default_factory=list)

    @property
    def titles(self) -> list[str]:
        return [e.title for e in self.entries]


def numeric_of(lexicon: Lexicon, attribute: str) -> bool:
    profile = lexicon.profiles.get(attribute)
    return profile.numeric if profile is not None else False


def entry_of(card: CardRecord, gold: Sequence[GoldRecord], lexicon: Lexicon) -> TwinEntry | None:
    title = twin_title(card.title)
    if not title:
        return None
    values: dict[str, TwinValue] = {}
    brand = model = ""
    for record in gold:
        if not record.value:
            continue
        key = canonical_key(record.value, record.unit, numeric_of(lexicon, record.attribute))
        values[record.attribute] = TwinValue(key, display_value(record.value, record.unit))
        if record.attribute == BRAND:
            brand = key
        elif record.attribute == MODEL:
            model = key
    return TwinEntry(card.sku_id, title, title_numbers(title), brand, model, values)


def query_of(card: CardRecord, picks: Mapping[str, Pick]) -> TwinQuery:
    title = twin_title(card.title)
    brand = picks.get(BRAND)
    return TwinQuery(title, title_numbers(title), brand.candidate.key if brand else None)


def stage_picks(extraction: CardExtraction, record: StageRecord | None) -> dict[str, Pick]:
    if record is None:
        return {}
    by_span = {(c.attribute, c.start, c.end): c for c in extraction.candidates}
    picks: dict[str, Pick] = {}
    for name, value in record.values.items():
        if name not in extraction.profiles:
            continue
        candidate = by_span.get((name, value.start, value.end))
        if candidate is None:
            numeric = extraction.profiles[name].numeric
            candidate = Candidate(name, canonical_key(value.value, None, numeric), value.value,
                                  value.value, value.start, value.end, value.source, "stage",
                                  0.0, 0.0, 0)
        picks[name] = Pick(candidate, value.confidence, value.sources)
    return picks


def twin_pick(transfer: Transfer, confidence: float) -> Pick:
    candidate = Candidate(transfer.attribute, transfer.key, transfer.value,
                          f"SKU {transfer.twin_sku}", -1, -1, TWIN_SOURCE, "twin",
                          round(transfer.similarity, 4), 0.0, 0)
    return Pick(candidate, confidence, (TWIN_SOURCE,))


def with_picks(extraction: CardExtraction, picks: Mapping[str, Pick]) -> CardExtraction:
    return replace(extraction, picks=dict(picks), review={})


def open_slots(extraction: CardExtraction, picks: Mapping[str, Pick]) -> list[str]:
    return [name for name in extraction.profiles if name not in picks]
