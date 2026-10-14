import asyncio
import os
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from app.adapter.catalog.configured import load_configuration
from app.adapter.decision.lexical import LexicalDecisionModel
from app.repository.sqlite.uow import SqliteUow
from app.usecase.catalog_contract import ExtractCommand
from app.usecase.dto.feedback import CatalogSnapshot
from app.usecase.feedback import (
    CorrectionConflict,
    FeedbackService,
    InvalidCorrection,
    SaveCorrection,
)
from app.usecase.process_card import ProcessCard
from app.usecase.resolution import ResolveCandidates


@pytest.fixture
def database(tmp_path: Path) -> Path:
    binary = os.environ.get("DBMATE_BIN") or shutil.which("dbmate")
    assert binary, "Install dbmate 2.36.0 or set DBMATE_BIN for SQLite migration tests"
    path = tmp_path / "feedback.db"
    migrations = Path(__file__).resolve().parents[2] / "migrations/sqlite"
    subprocess.run([binary, "--url", f"sqlite:{path}", "--migrations-dir", str(migrations),
                    "--no-dump-schema", "up"], check=True, capture_output=True, text=True)
    return path


def test_catalog_seed_is_idempotent_and_uncommitted_changes_roll_back(database: Path) -> None:
    snapshot = CatalogSnapshot(version="v1", payload='{"synthetic": true}')

    async def check() -> None:
        async with SqliteUow(database) as uow:
            await uow.catalog.seed(snapshot)
        async with SqliteUow(database) as uow:
            assert await uow.catalog.get() is None
            await uow.catalog.seed(snapshot)
            await uow.commit()
        async with SqliteUow(database) as uow:
            await uow.catalog.seed(CatalogSnapshot(version="v2", payload="{}"))
            await uow.commit()
        async with SqliteUow(database) as uow:
            assert await uow.catalog.get() == snapshot

    asyncio.run(check())


def test_correction_survives_reopen_is_idempotent_and_can_be_revoked(database: Path) -> None:

    configuration = load_configuration()
    text = "Смартфон Samsung Galaxy S26 черный\nЦвет: белый"

    async def check() -> None:
        service = FeedbackService(configuration, lambda: SqliteUow(database))
        processor = ProcessCard(configuration, ResolveCandidates(LexicalDecisionModel(), False), service)
        initial = [event async for event in processor.stream(ExtractCommand(text))][-1]
        color = next(field for field in initial.fields if field.attribute == "Цвет")
        assert color.state == "review"
        option = next(option for option in color.alternatives if option.value == "белый")
        command = SaveCorrection("request-one", initial.source_text, 761, "Цвет", option.value,
                                 option.quote, option.start, option.end, True)
        first = await service.save(command)
        assert await service.save(command) == first
        reopened = FeedbackService(configuration, lambda: SqliteUow(database))
        updated = ProcessCard(configuration, ResolveCandidates(LexicalDecisionModel(), False), reopened)
        result = [event async for event in updated.stream(ExtractCommand(text))][-1]
        fixed = next(field for field in result.fields if field.attribute == "Цвет")
        assert fixed.state == "accepted"
        assert fixed.value == "белый"
        assert fixed.source == "human"
        assert fixed.correction_id == first.id
        await reopened.revoke(first.id, first.version)
        await reopened.revoke(first.id, first.version)
        final = [event async for event in updated.stream(ExtractCommand(text))][-1]
        assert next(field for field in final.fields if field.attribute == "Цвет").state == "review"

    asyncio.run(check())


def test_alias_reuse_is_brand_scoped_and_revocation_stops_future_matches(database: Path) -> None:
    configuration = load_configuration()

    async def check() -> None:
        service = FeedbackService(configuration, lambda: SqliteUow(database))
        processor = ProcessCard(configuration, ResolveCandidates(LexicalDecisionModel(), False), service)
        text = "Смартфон Samsung Galaxy S26 midnight"
        initial = [event async for event in processor.stream(ExtractCommand(text))][-1]
        start = initial.source_text.index("midnight")
        record = await service.save(SaveCorrection("alias-request", initial.source_text, 761,
            "Цвет", "черный", "midnight", start, start + len("midnight"), True))
        matched = [event async for event in processor.stream(ExtractCommand(
            "Смартфон Samsung Galaxy S25 midnight"))][-1]
        color = next(field for field in matched.fields if field.attribute == "Цвет")
        assert color.state == "accepted"
        assert color.value == "черный"
        assert color.source == "confirmed_alias"
        other = [event async for event in processor.stream(ExtractCommand(
            "Смартфон Apple iPhone 17 midnight"))][-1]
        assert next(field for field in other.fields if field.attribute == "Цвет").state == "not_stated"
        await service.revoke(record.id, record.version)
        final = [event async for event in processor.stream(ExtractCommand(
            "Смартфон Samsung Galaxy S25 midnight"))][-1]
        assert next(field for field in final.fields if field.attribute == "Цвет").state == "not_stated"

    asyncio.run(check())


def test_competing_corrections_are_serialized_and_reused_id_cannot_change_payload(database: Path) -> None:
    configuration = load_configuration()

    async def check() -> None:
        service = FeedbackService(configuration, lambda: SqliteUow(database))
        text = "Смартфон Samsung Galaxy S26 midnight"
        start = text.index("midnight")
        first = SaveCorrection("first", text, 761, "Цвет", "черный", "midnight", start, start + 8)
        second = replace(first, request_id="second", value="белый")
        results = await asyncio.gather(service.save(first), service.save(second), return_exceptions=True)
        assert sum(isinstance(result, CorrectionConflict) for result in results) == 1, results
        successful = next(result for result in results if not isinstance(result, BaseException))
        original = first if successful.id == "first" else second
        assert await service.save(original) == successful
        with pytest.raises(CorrectionConflict):
            await service.save(replace(original, value="красный"))

    asyncio.run(check())


def test_feedback_rejects_unknown_category_and_numeric_value_without_matching_evidence(database: Path) -> None:
    configuration = load_configuration()

    async def check() -> None:
        service = FeedbackService(configuration, lambda: SqliteUow(database))
        text = "Смартфон Samsung Galaxy S26\nВес: 500 г"
        start = text.index("500")
        valid = SaveCorrection("weight", text, 761, "Вес", "0.5 кг", "500 г", start, start + 5)
        with pytest.raises(InvalidCorrection):
            await service.save(replace(valid, category_id=9999))
        with pytest.raises(InvalidCorrection):
            await service.save(replace(valid, value="500 кг"))
        record = await service.save(valid)
        assert record.value == "0.5 кг"

    asyncio.run(check())
