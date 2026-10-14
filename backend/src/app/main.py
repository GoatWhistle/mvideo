import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI

from app.adapter.catalog.configured import load_configuration, parse_configuration
from app.adapter.decision.lexical import LexicalDecisionModel
from app.adapter.decision.system_one import TYPESAFE_URL, SystemOneModel
from app.adapter.log.stdlib import StdlibLogger
from app.controller.errors import ErrorHandlers
from app.controller.router import api_router_v1
from app.repository.sqlite.uow import SqliteUow
from app.settings import ConfigError, DecisionProvider, LanguageProvider, Settings, load_settings
from app.usecase.feedback import FeedbackService
from app.usecase.interface import DecisionModel, LanguageModel, Logger
from app.usecase.process_card import ProcessCard
from app.usecase.resolution import ResolveCandidates


@dataclass(frozen=True, slots=True)
class Providers:
    decision: DecisionModel
    language: LanguageModel | None
    logger: Logger
    processor: ProcessCard
    feedback: FeedbackService | None = None

    async def aclose(self) -> None:
        await self.decision.aclose()


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
        configuration = load_configuration(Path(config.catalog_path) if config.catalog_path else None)
        feedback = None
        if config.database_path:
            database = Path(config.database_path)
            async with SqliteUow(database) as uow:
                snapshot = await uow.catalog.get()
            if snapshot is None:
                raise ConfigError("Catalog is not seeded; run python -m app.seed_catalog")
            configuration = parse_configuration(snapshot.payload)
            feedback = FeedbackService(configuration, lambda: SqliteUow(database))
        decision = build_decision_model(config)
        resolver = ResolveCandidates(
            decision, enabled=(config.decision_provider is DecisionProvider.SYSTEM_ONE
                               and bool(config.decision_api_key or config.decision_url != TYPESAFE_URL)),
            timeout_s=config.decision_timeout_s,
        )
        providers = Providers(
            decision=decision, language=language, logger=logger,
            processor=ProcessCard(configuration, resolver, feedback), feedback=feedback,
        )
        app.state.providers = providers
        try:
            yield
        finally:
            await providers.aclose()

    app = FastAPI(title="app", lifespan=lifespan)
    ErrorHandlers(logger).register(app)
    app.include_router(api_router_v1)
    return app
