from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from app.adapter.decision.system_one import DEFAULT_MODEL_NAME, TYPESAFE_URL

DEFAULT_STAND_PACK = "data/stand/pack.json.gz"


class DecisionProvider(StrEnum):
    LEXICAL = "lexical"
    SYSTEM_ONE = "system_one"


class LanguageProvider(StrEnum):
    NONE = "none"
    CLAUDE = "claude"
    CODEX = "codex"


class ConfigError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Settings:
    decision_provider: DecisionProvider = DecisionProvider.LEXICAL
    decision_url: str = TYPESAFE_URL
    decision_api_key: str | None = None
    decision_timeout_s: float = 10.0
    decision_model_name: str = DEFAULT_MODEL_NAME
    language_provider: LanguageProvider = LanguageProvider.NONE
    stand_pack: str = DEFAULT_STAND_PACK


def load_settings(env: Mapping[str, str]) -> Settings:
    return Settings(
        decision_provider=_choice(
            env, "DECISION_MODEL", DecisionProvider, DecisionProvider.LEXICAL
        ),
        decision_url=env.get("DECISION_MODEL_URL") or TYPESAFE_URL,
        decision_api_key=env.get("DECISION_MODEL_API_KEY") or None,
        decision_timeout_s=_positive(env, "DECISION_MODEL_TIMEOUT_S", 10.0),
        decision_model_name=env.get("DECISION_MODEL_NAME") or DEFAULT_MODEL_NAME,
        language_provider=_choice(env, "LANGUAGE_MODEL", LanguageProvider, LanguageProvider.NONE),
        stand_pack=env.get("STAND_PACK") or DEFAULT_STAND_PACK,
    )


def _choice[E: StrEnum](env: Mapping[str, str], name: str, kind: type[E], default: E) -> E:
    raw = env.get(name) or default.value
    try:
        return kind(raw)
    except ValueError:
        allowed = ", ".join(member.value for member in kind)
        raise ConfigError(f"{name}={raw!r} is not supported; use one of: {allowed}") from None


def _positive(env: Mapping[str, str], name: str, default: float) -> float:
    raw = env.get(name)
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        raise ConfigError(f"{name}={raw!r} is not a number") from None
    if value <= 0:
        raise ConfigError(f"{name}={raw!r} must be positive")
    return value
