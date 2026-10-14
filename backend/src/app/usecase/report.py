from collections.abc import Mapping
from typing import cast

from app.domain.metrics import MetricsBook

TOP_ATTRIBUTES = 30
GROUP_ORDER = (
    "all", "split:test", "split:new_category", "categories:head", "categories:tail",
    "category:smartphones", "category:laptops", "sellers:large", "sellers:medium", "sellers:small",
)
DETAIL_GROUPS = ("category:smartphones", "category:laptops", "split:new_category", "all")
SUMMARY_COLUMNS = (
    ("precision", "P"), ("recall", "R"), ("f1", "F1"), ("ceiling", "совпадение в тексте"),
    ("recall_in_text", "R на совпадениях"), ("coverage_before", "поля продавца"),
    ("coverage_after", "покрытие после"),
    ("candidate_recall", "recall кандидатов"), ("review_rate", "на проверке"),
    ("unsupported_rate", "не поддерживается"),
)
ATTRIBUTE_COLUMNS = (("gold", "пар с эталоном"), *SUMMARY_COLUMNS)


def build_report(
    plain: MetricsBook, weighted: MetricsBook, *, cards: int, lexicon_entries: int,
    attributes: int,
) -> dict[str, object]:
    groups: dict[str, object] = {}
    for group in GROUP_ORDER:
        if group not in plain.groups:
            continue
        groups[group] = {
            "micro": plain.micro(group),
            "macro_f1": plain.macro_f1(group),
            "weighted": weighted.micro(group),
            "weighted_macro_f1": weighted.macro_f1(group),
        }
    details: dict[str, object] = {}
    for group in DETAIL_GROUPS:
        items = plain.attributes(group)
        limit = len(items) if group.startswith("category:") else TOP_ATTRIBUTES
        details[group] = dict(list(items.items())[:limit])
    return {
        "schema_version": 2,
        "stage": "baseline: dictionaries + rules",
        "confidence_calibrated": False,
        "cards": cards,
        "lexicon_entries": lexicon_entries,
        "profiled_attributes": attributes,
        "groups": groups,
        "attributes": details,
    }


def _pct(value: object) -> str:
    return f"{float(cast(float, value)) * 100:.1f}"


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def render_markdown(report: Mapping[str, object]) -> str:
    groups = cast(Mapping[str, Mapping[str, object]], report["groups"])
    lines = [
        "# Отчёт метрик: базлайн (справочники + правила)",
        "",
        (f"Карточек: {report['cards']}; записей справочника: {report['lexicon_entries']}; "
        "уверенность не калибрована. Файл генерируется командой оценки и руками не правится."),
        "",
        "## Сводка по срезам",
        "",
        _row(["срез", "пар", *[t for _, t in SUMMARY_COLUMNS], "macro F1", "F1 взвеш."]),
        _row(["---"] * (len(SUMMARY_COLUMNS) + 4)),
    ]
    for name, data in groups.items():
        micro = cast(Mapping[str, float], data["micro"])
        weighted = cast(Mapping[str, float], data["weighted"])
        cells = [name, str(int(micro["pairs"]))]
        cells += [_pct(micro[key]) for key, _ in SUMMARY_COLUMNS]
        cells += [_pct(data["macro_f1"]), _pct(weighted["f1"])]
        lines.append(_row(cells))
    details = cast(Mapping[str, Mapping[str, Mapping[str, float]]], report["attributes"])
    for group, items in details.items():
        lines += ["", f"## По атрибутам: {group}", "",
                  _row(["атрибут", *[t for _, t in ATTRIBUTE_COLUMNS]]),
                  _row(["---"] * (len(ATTRIBUTE_COLUMNS) + 1))]
        for attribute, summary in items.items():
            cells = [attribute, str(int(summary["gold"]))]
            cells += [_pct(summary[key]) for key, _ in SUMMARY_COLUMNS]
            lines.append(_row(cells))
    lines += ["", ("Значения в процентах. Совпадение в тексте — диагностическая эвристика, "
              "не потолок recall; для чисел проверены единица и контекст атрибута. "
              "Coverage не означает правильность. Неподдерживаемые поля входят в знаменатель. "
              "Ключ ceiling сохранён для совместимости JSON; определения изменены в версии 2."), ""]
    return "\n".join(lines)
