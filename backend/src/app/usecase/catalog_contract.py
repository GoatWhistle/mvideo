from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal, Protocol

from app.domain.category_selection import CategoryOption
from app.domain.inference import Usage
from app.domain.lexicon import Lexicon
from app.usecase.baseline_ports import RequiredRecord

type FieldState = Literal["accepted", "review", "not_stated", "unsupported"]
type Stage = Literal["category", "rules", "complete"]


@dataclass(frozen=True, slots=True)
class CatalogConfiguration:
    categories: tuple[CategoryOption, ...]
    required: tuple[RequiredRecord, ...]
    lexicon: Lexicon
    version: str
    synthetic: bool


@dataclass(frozen=True, slots=True)
class ExtractCommand:
    text: str
    category_id: int | None = None


@dataclass(frozen=True, slots=True)
class FieldOption:
    value: str
    quote: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class FieldResult:
    attribute: str
    state: FieldState
    reason: str
    value: str | None = None
    quote: str | None = None
    start: int | None = None
    end: int | None = None
    source: str | None = None
    score: float | None = None
    score_kind: str = "heuristic"
    confidence: float | None = None
    alternatives: tuple[FieldOption, ...] = ()
    correction_id: str | None = None
    correction_version: int | None = None
    alias_brand: str | None = None


@dataclass(frozen=True, slots=True)
class ExtractionEvent:
    stage: Stage
    category_id: int | None
    category_name: str | None
    category_reason: str
    source_text: str
    fields: tuple[FieldResult, ...] = ()
    categories: tuple[CategoryOption, ...] = ()
    elapsed_ms: int = 0
    model_calls: int = 0
    model_usage: tuple[Usage, ...] = ()
    cached: bool = False
    warning: str | None = None
    synthetic_catalog: bool = False
    catalog_version: str = ""


class CatalogProcessor(Protocol):
    def stream(self, command: ExtractCommand) -> AsyncIterator[ExtractionEvent]: ...
