from collections.abc import Iterator, Mapping, Sequence

from app.usecase.baseline_ports import CardRecord, GoldRecord, RequiredRecord
from app.usecase.catalog_audit import AuditCatalog, AuditConfig
from app.usecase.lexicon_builder import TrainValue


class AuditSource:
    def required(self) -> Sequence[RequiredRecord]:
        return [RequiredRecord(1, "Цвет", 1), RequiredRecord(1, "Материал", 1)]

    def train_values(self, attributes: frozenset[str]) -> Iterator[TrainValue]:
        yield from [TrainValue(1, "Цвет", "черный", None)] * 3

    def gold(self, splits: frozenset[str]) -> Mapping[int, Sequence[GoldRecord]]:
        return {
            sku: [
                GoldRecord("Цвет", "белый", None),
                GoldRecord("Модель", "Phone X", None),
                GoldRecord("Материал", "металл", None),
            ]
            for sku in (1, 2)
        }

    def cards(self, splits: frozenset[str] | None, batch: int) -> Iterator[list[CardRecord]]:
        yield [
            CardRecord(1, 1, None, "Phone X black", None, (), "train"),
            CardRecord(2, 1, None, "Phone X black", None, (), "test"),
        ]


def test_audit_finds_cross_split_duplicates_and_reproducible_error_samples() -> None:
    report = AuditCatalog(AuditSource()).run(AuditConfig(seed=42, samples_per_group=1))
    assert report["cards"] == 2
    overlap = report["overlaps"]
    assert overlap["exact_text"]["groups"] == 1
    assert overlap["model_family"]["groups"] == 1
    assert report["independent_human_validation"] is False
    groups = report["discrepancies"]
    assert groups["Цвет:wrong_selection"]["count"] == 2
    assert groups["Материал:unsupported"]["count"] == 2
    sample = groups["Цвет:wrong_selection"]["examples"][0]
    assert sample["gold"] == "белый"
    assert sample["predicted"] == "черный"
    assert sample["quote"] == "black"
    assert report == AuditCatalog(AuditSource()).run(AuditConfig(seed=42, samples_per_group=1))
