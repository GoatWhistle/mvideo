import asyncio
from dataclasses import replace

from app.domain.decision import ChoiceAnswer, Decision, DecisionRequest
from app.domain.inference import Usage
from app.usecase.baseline_ports import CardRecord, RequiredRecord
from app.usecase.extraction import RequiredAttributes, extract_card
from app.usecase.lexicon_builder import TrainValue, build_lexicon
from app.usecase.resolution import ResolveCandidates


class SelectingModel:
    def __init__(self) -> None:
        self.calls = 0

    async def decide(self, request: DecisionRequest) -> Decision:
        self.calls += 1
        answers = {
            name: ChoiceAnswer("c0", 0.95, {"c0": 0.95, "c1": 0.03, "none": 0.02})
            for name in request.questions
        }
        return Decision(answers, Usage("test-model"))

    async def aclose(self) -> None: ...


def test_sporadic_conflict_routes_automatically_and_reuses_validated_result() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", color, None) for color in ("черный", "белый") for _ in range(3)]
    )
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    card = CardRecord(1, 1, None, "Черный смартфон", "Цвет: белый", (), None)
    initial = extract_card(card, required, lexicon, 0.35)
    model = SelectingModel()
    resolver = ResolveCandidates(model, enabled=True)

    first = asyncio.run(resolver.run(initial, category=1, version="test"))
    second = asyncio.run(resolver.run(initial, category=1, version="test"))

    assert model.calls == 1
    assert first.picks["Цвет"].candidate in initial.candidates
    assert first.picks["Цвет"].candidate.evidence
    assert first.source == "decision_model"
    assert second.cached


def test_offline_mode_keeps_conflict_for_review_without_a_model_call() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", c, None) for c in ("черный", "белый") for _ in range(3)]
    )
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    card = CardRecord(1, 1, None, "Черный смартфон", "Цвет: белый", (), None)
    initial = extract_card(card, required, lexicon, 0.35)
    model = SelectingModel()

    result = asyncio.run(ResolveCandidates(model, enabled=False).run(initial, 1, "test"))

    assert model.calls == 0
    assert not result.picks
    assert "Цвет" in result.review
    assert result.source == "rules"


class InvalidModel(SelectingModel):
    async def decide(self, request: DecisionRequest) -> Decision:
        self.calls += 1
        return Decision(
            {name: ChoiceAnswer("invented", 1, {"invented": 1}) for name in request.questions},
            Usage("test-model"),
        )


def test_invalid_decision_is_retried_once_and_never_becomes_a_value() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", c, None) for c in ("черный", "белый") for _ in range(3)]
    )
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    initial = extract_card(
        CardRecord(1, 1, None, "Черный смартфон", "Цвет: белый", (), None), required, lexicon, 0.35
    )
    model = InvalidModel()

    result = asyncio.run(ResolveCandidates(model, enabled=True).run(initial, 1, "test"))

    assert model.calls == 2
    assert result.failure == "decision_unavailable"
    assert not result.picks
    assert "Цвет" in result.review


class SlowModel(SelectingModel):
    async def decide(self, request: DecisionRequest) -> Decision:
        self.calls += 1
        await asyncio.Event().wait()
        raise AssertionError("unreachable")


def test_deadline_keeps_rule_result_and_does_not_cache_failure() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", c, None) for c in ("черный", "белый") for _ in range(3)]
    )
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    initial = extract_card(
        CardRecord(1, 1, None, "Черный смартфон", "Цвет: белый", (), None), required, lexicon, 0.35
    )
    model = SlowModel()
    resolver = ResolveCandidates(model, enabled=True, timeout_s=0.01)
    result = asyncio.run(resolver.run(initial, 1, "test"))
    repeated = asyncio.run(resolver.run(initial, 1, "test"))
    assert result.failure == "decision_timeout"
    assert result.review == initial.review
    assert not repeated.cached
    assert model.calls == 2


class RecheckingModel(SelectingModel):
    async def decide(self, request: DecisionRequest) -> Decision:
        if self.calls == 0:
            self.calls += 1
            return Decision(
                {
                    name: ChoiceAnswer("none", 0.95, {"c0": 0.03, "c1": 0.02, "none": 0.95})
                    for name in request.questions
                },
                Usage("test-model"),
            )
        assert "recheck" in request.state
        return await super().decide(request)


def test_unresolved_choice_gets_one_automatic_context_recheck() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", c, None) for c in ("черный", "белый") for _ in range(3)]
    )
    required = RequiredAttributes([RequiredRecord(1, "Цвет", 1)], lexicon)
    initial = extract_card(
        CardRecord(1, 1, None, "Черный смартфон", "Цвет: белый", (), None), required, lexicon, 0.35
    )
    model = RecheckingModel()
    result = asyncio.run(ResolveCandidates(model, enabled=True).run(initial, 1, "test"))
    assert result.calls == 2
    assert "Цвет" in result.picks
    assert not result.review


def test_cached_resolution_cannot_replace_a_newly_corrected_field() -> None:
    lexicon = build_lexicon(
        [TrainValue(1, "Цвет", c, None) for c in ("черный", "белый") for _ in range(3)]
        + [TrainValue(1, "Бренд", "Samsung", None)]
    )
    required = RequiredAttributes(
        [RequiredRecord(1, "Цвет", 1), RequiredRecord(1, "Бренд", 1)], lexicon
    )
    initial = extract_card(
        CardRecord(1, 1, None, "Черный смартфон Samsung", "Цвет: белый", (), None),
        required,
        lexicon,
        0.35,
    )
    resolver = ResolveCandidates(SelectingModel(), enabled=True)
    asyncio.run(resolver.run(initial, 1, "test"))
    original = initial.picks["Бренд"]
    corrected = replace(original, candidate=replace(original.candidate, source="human"))
    updated = replace(initial, picks={**initial.picks, "Бренд": corrected})

    result = asyncio.run(resolver.run(updated, 1, "test"))

    assert result.picks["Бренд"].candidate.source == "human"
