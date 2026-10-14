import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import replace

from app.domain.card_text import clean_text
from app.domain.category_selection import CategorySelection, select_category
from app.domain.evidence import conflicts
from app.domain.profile import BRAND, Kind
from app.usecase.baseline_ports import CardRecord
from app.usecase.catalog_contract import (
    CatalogConfiguration,
    ExtractCommand,
    ExtractionEvent,
    FieldOption,
    FieldResult,
)
from app.usecase.extraction import CardExtraction, RequiredAttributes, extract_card
from app.usecase.feedback import FeedbackService
from app.usecase.resolution import Resolution, ResolveCandidates


def fields_of(extraction: CardExtraction, resolution: Resolution) -> tuple[FieldResult, ...]:
    ambiguous = conflicts(extraction.candidates)
    brand = resolution.picks.get(BRAND)
    fields = []
    for name, profile in extraction.profiles.items():
        pick = resolution.picks.get(name) or resolution.review.get(name)
        options: dict[str, FieldOption] = {}
        normalized = {
            c.key
            for c in extraction.candidates
            if c.attribute == name and c.source in {"dictionary", "confirmed_alias"}
        }
        for c in extraction.candidates:
            if c.attribute == name:
                if profile.kind is Kind.CATEGORICAL and c.key not in normalized:
                    continue
                options.setdefault(c.key, FieldOption(c.value, c.evidence, c.start, c.end))
        if profile.kind is Kind.UNSUPPORTED:
            fields.append(FieldResult(name, "unsupported", "attribute_unsupported"))
        elif pick is None:
            fields.append(
                FieldResult(
                    name,
                    "not_stated",
                    "no_evidence",
                    alias_brand=brand.candidate.value
                    if brand and not profile.numeric and name != BRAND
                    else None,
                )
            )
        else:
            accepted = name in resolution.picks
            model = name in resolution.resolved
            reason = (
                "selected"
                if accepted
                else ("conflicting_evidence" if name in ambiguous else "insufficient_score")
            )
            c = pick.candidate
            correction = extraction.corrections.get(name)
            fields.append(
                FieldResult(
                    name,
                    "accepted" if accepted else "review",
                    reason,
                    c.value,
                    c.evidence,
                    c.start,
                    c.end,
                    "decision_model" if model else c.source,
                    None if correction else pick.confidence,
                    "human_confirmation"
                    if correction
                    else ("model_probability" if model else "heuristic"),
                    alternatives=tuple(options.values()),
                    correction_id=correction.id if correction else None,
                    correction_version=correction.version if correction else None,
                    alias_brand=brand.candidate.value
                    if brand and not profile.numeric and name != BRAND
                    else None,
                )
            )
    return tuple(fields)


class ProcessCard:
    def __init__(
        self,
        configuration: CatalogConfiguration,
        resolver: ResolveCandidates,
        feedback: FeedbackService | None = None,
    ) -> None:
        self._configuration = configuration
        self._resolver = resolver
        self._feedback = feedback
        self._required = RequiredAttributes(configuration.required, configuration.lexicon)

    async def stream(self, command: ExtractCommand) -> AsyncIterator[ExtractionEvent]:
        started = time.monotonic()
        text = clean_text(command.text)
        categories = self._configuration.categories
        selection = select_category(text, categories)
        if command.category_id is not None:
            valid = next((c for c in categories if c.category_id == command.category_id), None)
            if valid is not None:
                selection = CategorySelection(valid.category_id, "category_confirmed", (valid,))
        category = next((c for c in categories if c.category_id == selection.category_id), None)
        event = ExtractionEvent(
            "category",
            selection.category_id,
            category.name if category else None,
            selection.reason,
            text,
            categories=selection.alternatives,
            synthetic_catalog=self._configuration.synthetic,
            catalog_version=self._configuration.version,
        )
        yield event
        if category is None:
            yield replace(event, stage="complete", elapsed_ms=self._elapsed(started))
            return
        title, _, description = text.partition("\n")
        record = CardRecord(0, category.category_id, None, title, description, (), None)
        extraction = await asyncio.to_thread(
            extract_card,
            record,
            self._required,
            self._configuration.lexicon,
            0.35,
        )
        if self._feedback is not None:
            extraction = await self._feedback.enrich(extraction, category.category_id)
        baseline = Resolution(extraction.picks, extraction.review)
        event = replace(
            event,
            stage="rules",
            source_text=extraction.text.text,
            fields=fields_of(extraction, baseline),
            elapsed_ms=self._elapsed(started),
        )
        yield event
        resolution = await self._resolver.run(
            extraction, category.category_id, self._configuration.version
        )
        yield replace(
            event,
            stage="complete",
            fields=fields_of(extraction, resolution),
            elapsed_ms=self._elapsed(started),
            model_calls=resolution.calls,
            model_usage=resolution.usage,
            cached=resolution.cached,
            warning=resolution.failure,
        )

    @staticmethod
    def _elapsed(started: float) -> int:
        return round((time.monotonic() - started) * 1000)
