from app.domain.category_selection import CategoryOption, select_category

CATEGORIES = (
    CategoryOption(761, "Смартфоны", ("смартфон", "smartphone", "iphone")),
    CategoryOption(987, "Ноутбуки", ("ноутбук", "laptop", "macbook")),
)


def test_supported_product_is_categorized_without_user_input() -> None:
    assert select_category("Смартфон Samsung Galaxy", CATEGORIES).category_id == 761
    assert select_category("Ноутбук ThinkBook", CATEGORIES).category_id == 987


def test_accessory_is_not_misclassified_as_a_phone() -> None:
    result = select_category("Чехол для смартфона iPhone", CATEGORIES)
    assert result.category_id is None
    assert result.reason == "category_unknown"


def test_unclear_category_returns_choices_without_guessing() -> None:
    result = select_category("Комплект: смартфон и ноутбук", CATEGORIES)
    assert result.category_id is None
    assert result.reason == "category_ambiguous"
