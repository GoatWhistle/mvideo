from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from app.domain.twin import Transfer
from app.usecase.ranker_ports import RankerSource


@dataclass(frozen=True, slots=True)
class StageValue:
    value: str
    confidence: float
    source: str
    sources: tuple[str, ...]
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class StageRecord:
    raw: Mapping[str, object]
    values: Mapping[str, StageValue]


class TwinSource(RankerSource, Protocol):
    def stage_records(self, name: str) -> Mapping[int, StageRecord]: ...


class TitleIndex(Protocol):
    def fit(self, titles: Sequence[str]) -> None: ...

    def neighbors(self, titles: Sequence[str], k: int) -> list[list[tuple[int, float]]]: ...


@dataclass(frozen=True, slots=True)
class TwinPrediction:
    stage: Mapping[str, object]
    transfers: Mapping[str, tuple[Transfer, float]]


class TwinPredictionSink(Protocol):
    def write(self, predictions: Sequence[TwinPrediction]) -> None: ...

    def close(self) -> None: ...
