import json
from collections.abc import Mapping, Sequence
from pathlib import Path

from app.domain.twin import TWIN_SOURCE, Transfer
from app.usecase.twin_ports import TwinPrediction


def transfer_json(transfer: Transfer, confidence: float) -> dict[str, object]:
    return {
        "value": transfer.value,
        "confidence": confidence,
        "source": TWIN_SOURCE,
        "sources": [TWIN_SOURCE],
        "evidence": f"SKU {transfer.twin_sku}",
        "start": -1,
        "end": -1,
        "twin_sku": transfer.twin_sku,
        "similarity": transfer.similarity,
        "exact_title": transfer.exact,
    }


def _section(record: Mapping[str, object], key: str) -> dict[str, object]:
    value = record.get(key)
    return dict(value) if isinstance(value, Mapping) else {}


def twin_record(prediction: TwinPrediction) -> dict[str, object]:
    record = dict(prediction.stage)
    attributes = _section(record, "attributes")
    review = _section(record, "review")
    for name, (transfer, confidence) in prediction.transfers.items():
        attributes[name] = transfer_json(transfer, confidence)
        review.pop(name, None)
    record["attributes"] = attributes
    record["review"] = review
    record["confidence_calibrated"] = True
    return record


class FileTwinPredictionSink:
    def __init__(self, out_dir: Path, name: str) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        self._handle = (out_dir / f"{name}.predictions.jsonl").open("w", encoding="utf-8")

    def write(self, predictions: Sequence[TwinPrediction]) -> None:
        for prediction in predictions:
            line = json.dumps(twin_record(prediction), ensure_ascii=False, sort_keys=True)
            self._handle.write(line + "\n")

    def close(self) -> None:
        self._handle.close()
