import pytest

from app.domain.card_text import SellerParam
from app.domain.values import canonical_key
from app.usecase.baseline_ports import CardRecord, RequiredRecord
from app.usecase.extraction import RequiredAttributes, extract_card
from app.usecase.lexicon_builder import TrainValue, build_lexicon


def test_seller_weight_is_converted_without_changing_the_quote() -> None:
    lexicon = build_lexicon([TrainValue(1, "Вес", "1", "кг")] * 3)
    required = RequiredAttributes([RequiredRecord(1, "Вес", 1)], lexicon)
    card = CardRecord(1, 1, None, "Товар", None, (SellerParam("Вес", "500 г"),), None)

    result = extract_card(card, required, lexicon, 0.35)

    assert result.picks["Вес"].candidate.value == "0.5 кг"
    assert result.picks["Вес"].candidate.evidence == "500 г"


@pytest.mark.parametrize(
    ("left", "right"),
    [("1 кг", "1000 г"), ("1 м", "100 см"), ("1 кВт", "1000 Вт"),
     ("1 TB", "1000 GB"), ("1 GiB", "1.073741824 GB")],
)
def test_equivalent_measurements_match(left: str, right: str) -> None:
    assert canonical_key(left, None, True) == canonical_key(right, None, True)


def test_equal_numbers_with_different_units_do_not_match() -> None:
    assert canonical_key("1 г", None, True) != canonical_key("1 кг", None, True)
    assert canonical_key("1 GB", None, True) != canonical_key("1 GiB", None, True)


@pytest.mark.parametrize("value", ["500", "500 ГБ", "100–500 г", "от 500 г", "-500 г"])
def test_ambiguous_or_invalid_weight_is_not_filled(value: str) -> None:
    lexicon = build_lexicon([TrainValue(1, "Вес", "1", "кг")] * 3)
    required = RequiredAttributes([RequiredRecord(1, "Вес", 1)], lexicon)
    card = CardRecord(1, 1, None, "Товар", None, (SellerParam("Вес", value),), None)

    result = extract_card(card, required, lexicon, 0.35)

    assert "Вес" not in result.picks


@pytest.mark.parametrize("value", ["-500 г", "от 500 г", "100–500 г"])
def test_description_ranges_and_negative_values_are_not_exact_weight(value: str) -> None:
    lexicon = build_lexicon([TrainValue(1, "Вес", "1", "кг")] * 3)
    required = RequiredAttributes([RequiredRecord(1, "Вес", 1)], lexicon)
    card = CardRecord(1, 1, None, "Товар", f"Вес: {value}", (), None)
    result = extract_card(card, required, lexicon, 0.35)
    assert "Вес" not in result.picks


def test_seller_range_uses_compatible_units_when_checking_title_weight() -> None:
    lexicon = build_lexicon([TrainValue(1, "Вес", "1", "кг")] * 3)
    required = RequiredAttributes([RequiredRecord(1, "Вес", 1)], lexicon)
    card = CardRecord(1, 1, None, "Товар 0.5 кг", None,
                      (SellerParam("Вес", "400–600 г"),), None)
    result = extract_card(card, required, lexicon, 0.35)
    assert result.picks["Вес"].candidate.value == "0.5 кг"
