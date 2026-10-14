from collections.abc import Mapping


def render_markdown(report: Mapping[str, object]) -> str:
    test = _mapping(report.get("classifier_test"))
    clicks = _mapping(report.get("clicks"))
    coverage = _mapping(report.get("coverage"))
    lines = [
        "# Категории для карточек вне каталога",
        "",
        (f"Категорий с обязательными атрибутами: {report.get('required_categories')}; "
        f"обучающих карточек: {report.get('train_cards')}; порог уверенности "
        f"{report.get('threshold')} выбран на val под точность {report.get('target_precision')}."),
        "",
        "## Классификатор по названию (test)",
        "",
        "| Карточек | Top-1 | Top-3 | Macro-F1 | Покрытие при пороге | Точность при пороге |",
        "|---|---|---|---|---|---|",
        (f"| {test.get('cards')} | {test.get('top1')} | {test.get('top3')} | "
        f"{test.get('macro_f1')} | {test.get('coverage_at_threshold')} | "
        f"{test.get('precision_at_threshold')} |"),
        "",
        "| Порог | Покрытие | Точность |",
        "|---|---|---|",
    ]
    for point in _points(test.get("curve")):
        lines.append(f"| {point.get('threshold')} | {_pct(point.get('coverage'))} | "
                     f"{_pct(point.get('precision'))} |")
    lines += [
        "",
        "## Категория из кликов (test)",
        "",
        (f"Карточек test с кликами: {clicks.get('test_cards')}; сопоставлено: "
        f"{clicks.get('test_mapped')}; точность сопоставления: {clicks.get('test_accuracy')}; "
        f"`sku_seo_id` совпадает с категорией каталога напрямую: {clicks.get('direct_id_match')}."),
        "",
        "## Итог по всем карточкам с текстом",
        "",
        (f"Карточек: {coverage.get('cards')}; с категорией: {coverage.get('with_category')} "
        f"({coverage.get('share_with_category')}); по источникам: {coverage.get('by_source')}."),
        "",
    ]
    return "\n".join(lines)


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _points(value: object) -> list[Mapping[str, object]]:
    return [p for p in value if isinstance(p, Mapping)] if isinstance(value, list) else []


def _pct(value: object) -> str:
    return f"{value * 100:.1f}%" if isinstance(value, int | float) else "—"
