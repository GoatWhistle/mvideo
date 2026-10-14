import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI

from app.adapter.dataset.stand_pack_file import StandPackFile
from app.adapter.decision.lexical import LexicalDecisionModel
from app.adapter.decision.system_one import SystemOneModel
from app.adapter.log.stdlib import StdlibLogger
from app.adapter.system.clock import SystemClock, UuidIds
from app.controller.errors import ErrorHandlers
from app.controller.router import api_router_v1
from app.repository.memory.review import MemoryAliasRepository, MemoryReviewRepository
from app.settings import ConfigError, DecisionProvider, LanguageProvider, Settings, load_settings
from app.usecase.extract_card import BaselineChooser, ExtractCard
from app.usecase.interface import DecisionModel, LanguageModel, Logger
from app.usecase.review_queue import ReviewQueue
from app.usecase.stand_catalog import StandCatalog


@dataclass(frozen=True, slots=True)
class Providers:
    decision: DecisionModel
    language: LanguageModel | None
    logger: Logger

    async def aclose(self) -> None:
        await self.decision.aclose()


@dataclass(frozen=True, slots=True)
class StandServices:
    extract: ExtractCard
    review: ReviewQueue
    catalog: StandCatalog


def build_stand(settings: Settings, logger: Logger) -> StandServices:
    pack = StandPackFile(Path(settings.stand_pack)).load()
    if pack is None:
        logger.warning("stand_pack_missing", path=settings.stand_pack)
    else:
        logger.info("stand_pack_loaded", categories=len(pack.categories),
                    examples=len(pack.examples))
    reviews, aliases, clock = MemoryReviewRepository(), MemoryAliasRepository(), SystemClock()
    return StandServices(
        extract=ExtractCard(pack, aliases, reviews, BaselineChooser(), clock, UuidIds()),
        review=ReviewQueue(reviews, aliases, clock),
        catalog=StandCatalog(pack),
    )


def build_decision_model(settings: Settings) -> DecisionModel:
    match settings.decision_provider:
        case DecisionProvider.LEXICAL:
            return LexicalDecisionModel()
        case DecisionProvider.SYSTEM_ONE:
            return SystemOneModel(
                base_url=settings.decision_url,
                api_key=settings.decision_api_key,
                timeout_s=settings.decision_timeout_s,
            )


def build_language_model(settings: Settings) -> LanguageModel | None:
    match settings.language_provider:
        case LanguageProvider.NONE:
            return None
        case LanguageProvider.CLAUDE:
            try:
                from app.adapter.llm.claude_agent import ClaudeAgentModel
            except ModuleNotFoundError as exc:
                raise _missing_llm_group(settings, exc) from exc
            return ClaudeAgentModel()
        case LanguageProvider.CODEX:
            try:
                from app.adapter.llm.codex_agent import CodexAgentModel
            except ModuleNotFoundError as exc:
                raise _missing_llm_group(settings, exc) from exc
            return CodexAgentModel()


def _missing_llm_group(settings: Settings, exc: ModuleNotFoundError) -> ConfigError:
    return ConfigError(
        f"LANGUAGE_MODEL={settings.language_provider.value} needs package {exc.name!r}; "
        "install the llm dependency group (uv sync --group llm) or build the image with LLM=true"
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or load_settings(os.environ)
    language = build_language_model(config)
    logger = StdlibLogger("app")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        providers = Providers(
            decision=build_decision_model(config), language=language, logger=logger
        )
        app.state.providers = providers
        app.state.stand = build_stand(config, logger)
        try:
            yield
        finally:
            await providers.aclose()

    app = FastAPI(title="app", lifespan=lifespan)
    ErrorHandlers(logger).register(app)
    app.include_router(api_router_v1)
    return app
