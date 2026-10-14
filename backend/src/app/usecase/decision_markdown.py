from collections.abc import Mapping
from typing import cast

from app.usecase.report import render_markdown


def _pct(value: object) -> str:
    return f"{float(cast(float, value)) * 100:.1f}"


def render_decision_markdown(report: Mapping[str, object]) -> str:
    body = render_markdown(report).split("\n", 1)[1]
    usage = cast(Mapping[str, object], report["usage"])
    calibration = cast(Mapping[str, object], report["calibration"])
    lines = [f"# Отчёт метрик: {report['stage']}", ""]
    if report.get("offline_stub"):
        lines += [
            "> Офлайн-заглушка `lexical`: это проверка пайплайна, а не качество продукта.",
            "",
        ]
    lines += [
        "## Сравнение с базлайном на той же выборке",
        "",
        "| срез | F1 базлайн | F1 decision | P базлайн | P decision | R базлайн | R decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    compare = cast(Mapping[str, Mapping[str, Mapping[str, float]]], report["baseline_same_sample"])
    for group, pair in compare.items():
        b, d = pair["baseline"], pair["decision"]
        lines.append(
            f"| {group} | {_pct(b['f1'])} | {_pct(d['f1'])} | {_pct(b['precision'])} | "
            f"{_pct(d['precision'])} | {_pct(b['recall'])} | {_pct(d['recall'])} |"
        )
    lines += [
        "",
        "## Калибровка вероятностей",
        "",
        f"Пар с эталоном: {calibration['pairs']}; ECE: {calibration['ece']}.",
        "",
        "| корзина | пар | средняя уверенность | точность |",
        "| --- | --- | --- | --- |",
    ]
    for b in cast(list[Mapping[str, float]], calibration["bins"]):
        lines.append(
            f"| {b['low']:.1f}–{b['high']:.1f} | {int(b['count'])} | "
            f"{b['mean_confidence']:.3f} | {b['accuracy']:.3f} |"
        )
    routing = cast(Mapping[str, object], report.get("routing", {}))
    lines += ["", "## Слоты, отправленные в decision-модель", ""]
    lines += [f"- {k}: {v}" for k, v in routing.items() if k != "attributes"]
    lines += [
        "",
        "| атрибут | слотов с эталоном | базлайн верно | decision верно | decision ответил |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, counts in cast(
        Mapping[str, Mapping[str, int]], routing.get("attributes", {})
    ).items():
        lines.append(
            f"| {name} | {counts['slots']} | {counts['baseline_correct']} | "
            f"{counts['decision_correct']} | {counts['decision_answered']} |"
        )
    lines += [
        "",
        "## Порог переопределения базлайна",
        "",
        "| порог | снять при «не указано» ≥ | P | R | F1 | покрытие | F1 взвеш. | macro F1 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cast(list[Mapping[str, float]], report.get("override_grid", [])):
        drop = "—" if row.get("drop") is None else row["drop"]
        lines.append(
            f"| {row['override']} | {drop} | {_pct(row['precision'])} | {_pct(row['recall'])} | "
            f"{_pct(row['f1'])} | {_pct(row['coverage_after'])} | "
            f"{_pct(row['weighted_f1'])} | {_pct(row['macro_f1'])} |"
        )
    lines += ["", "## Вызовы и стоимость", ""]
    lines += [f"- {key}: {value}" for key, value in usage.items()]
    lines += ["", body]
    return "\n".join(lines)
