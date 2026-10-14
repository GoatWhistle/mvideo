import pytest

from app.usecase.baseline_ports import CardRecord, RequiredRecord
from app.usecase.extraction import RequiredAttributes, extract_card
from app.usecase.lexicon_builder import TrainValue, build_lexicon


@pytest.mark.parametrize(
    "text",
    [
        "Белый смартфон, черный чехол в комплекте",
        "Смартфон. Цвет не черный.",
        "Смартфон. Подходит для черного чехла.",
    ],
)
def test_accessory_or_negated_color_is_not_a_product_value(text: str) -> None:
    lexicon = build_lexicon([TrainValue(1, "Цвет", "черный", None)] * 3)
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    card = CardRecord(1, 1, None, text, None, (), None)

    result = extract_card(card, required, lexicon, 0.35)

    assert "Цвет" not in result.picks


def test_conflicting_colors_require_resolution() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", value, None) for value in ("черный", "белый") for _ in range(3)]
    )
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    card = CardRecord(1, 1, None, "Черный смартфон", "Цвет: белый", (), None)

    result = extract_card(card, required, lexicon, 0.35)

    assert "Цвет" not in result.picks
    assert "Цвет" in result.review
    assert {c.key for c in result.candidates} == {"черный", "белый"}


def test_negated_key_value_is_not_a_color() -> None:
    lexicon = build_lexicon([TrainValue(761, "Цвет", "черный", None)] * 3)
    required = RequiredAttributes([RequiredRecord(761, "Цвет", 1)], lexicon)
    card = CardRecord(1, 761, None, "Смартфон", "Цвет: не черный", (), None)
    result = extract_card(card, required, lexicon, 0.35)
    assert "Цвет" not in result.picks


def test_unknown_categorical_value_requires_normalization() -> None:
    lexicon = build_lexicon([TrainValue(761, "Цвет", "черный", None)] * 3)
    required = RequiredAttributes([RequiredRecord(761, "Цвет", 1)], lexicon)
    card = CardRecord(1, 761, None, "Смартфон", "Цвет: midnight", (), None)
    result = extract_card(card, required, lexicon, 0.35)
    assert "Цвет" not in result.picks
    assert result.review["Цвет"].candidate.evidence == "midnight"
