from app.domain.card_text import build_card_text
from app.domain.metrics import MetricsBook, Observation, value_in_text
from app.domain.profile import AttributeProfile, Kind, name_keywords


def obs(has_gold: bool, predicted: bool, correct: bool, reachable: bool = True) -> Observation:
    return Observation("Цвет", has_gold, predicted, correct, reachable, False)


def test_precision_recall_f1_on_tiny_example() -> None:
    book = MetricsBook(weighted=False)
    for o in [
        obs(True, True, True),
        obs(True, True, False),
        obs(True, False, False, False),
        obs(False, True, False),
    ]:
        book.add(["all"], o)
    micro = book.micro("all")
    assert micro["precision"] == 0.5
    assert micro["recall"] == round(1 / 3, 4)
    assert micro["f1"] == 0.4
    assert micro["ceiling"] == round(2 / 3, 4)
    assert micro["recall_in_text"] == 0.5
    assert micro["coverage_after"] == 0.75
    assert micro["extra_fills"] == 1.0


def test_weighted_book_uses_weights() -> None:
    book = MetricsBook(weighted=True)
    book.add(["all"], Observation("Цвет", True, True, True, True, False, weight=3.0))
    book.add(["all"], Observation("Цвет", True, True, False, True, False, weight=1.0))
    assert book.micro("all")["precision"] == 0.75


def test_numeric_text_match_needs_the_attribute_and_compatible_unit() -> None:
    profile = AttributeProfile("Вес", Kind.NUMERIC, "кг", name_keywords("Вес"))
    assert not value_in_text(build_card_text("Накопитель 500 ГБ", None, ()), "500 г", None, profile)
    assert value_in_text(build_card_text("Вес: 500 г", None, ()), "0.5 кг", None, profile)
