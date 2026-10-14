import json
from collections.abc import Mapping
from pathlib import Path

from app.adapter.dataset.ranker_source import ParquetRankerSource
from app.usecase.twin_ports import StageRecord, StageValue


class ParquetTwinSource(ParquetRankerSource):
    def __init__(self, processed: Path, predictions: Path) -> None:
        super().__init__(processed)
        self._predictions = predictions

    def stage_records(self, name: str) -> Mapping[int, StageRecord]:
        path = self._predictions / f"{name}.predictions.jsonl"
        records: dict[int, StageRecord] = {}
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                raw = json.loads(line)
                values = {a: _value(v) for a, v in raw.get("attributes", {}).items()}
                records[int(raw["sku_id"])] = StageRecord(raw, values)
        return records


def _value(raw: Mapping[str, object]) -> StageValue:
    sources = raw.get("sources")
    return StageValue(
        value=str(raw.get("value", "")),
        confidence=float(str(raw.get("confidence", 0.0))),
        source=str(raw.get("source", "")),
        sources=tuple(str(s) for s in sources) if isinstance(sources, list) else (),
        start=int(str(raw.get("start", -1))),
        end=int(str(raw.get("end", -1))),
    )
