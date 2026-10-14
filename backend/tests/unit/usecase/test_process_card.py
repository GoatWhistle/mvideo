import asyncio

from app.adapter.catalog.configured import load_configuration
from app.adapter.decision.lexical import LexicalDecisionModel
from app.usecase.catalog_contract import ExtractCommand, ExtractionEvent
from app.usecase.process_card import ProcessCard
from app.usecase.resolution import ResolveCandidates


def test_paste_to_fields_has_automatic_category_and_real_progress() -> None:
    processor = ProcessCard(
        load_configuration(), ResolveCandidates(LexicalDecisionModel(), enabled=False)
    )

    async def collect() -> list[ExtractionEvent]:
        return [
            event
            async for event in processor.stream(
                ExtractCommand("Смартфон Samsung Galaxy S26 Black\nВес: 500 г\nБатарея: 5000 мАч")
            )
        ]

    events = asyncio.run(collect())

    assert [e.stage for e in events] == ["category", "rules", "complete"]
    final = events[-1]
    assert final.category_id == 761
    fields = {f.attribute: f for f in final.fields}
    assert fields["Вес"].value == "0.5 кг"
    assert fields["Цвет"].value == "черный"
    assert fields["Бренд"].value == "Samsung"
    assert fields["Диагональ"].state == "not_stated"
    assert final.synthetic_catalog
    assert final.model_calls == 0
    for field in final.fields:
        if field.quote is not None:
            assert final.source_text[field.start : field.end] == field.quote


def test_slash_memory_fills_ram_and_storage_without_false_conflicts() -> None:
    processor = ProcessCard(
        load_configuration(), ResolveCandidates(LexicalDecisionModel(), enabled=False)
    )

    async def collect() -> list[ExtractionEvent]:
        return [
            event
            async for event in processor.stream(
                ExtractCommand("Смартфон Samsung Galaxy S26 12/256GB Black")
            )
        ]

    final = asyncio.run(collect())[-1]
    fields = {f.attribute: f for f in final.fields}
    assert fields["Оперативная память (RAM)"].value == "12 гб"
    assert fields["Оперативная память (RAM)"].state == "accepted"
    assert fields["Встроенная память (ROM)"].value == "256 гб"
    assert fields["Встроенная память (ROM)"].state == "accepted"
