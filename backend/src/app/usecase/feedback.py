import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime

from app.domain.candidate import Candidate
from app.domain.card_text import clean_text
from app.domain.errors import DomainError
from app.domain.evidence import supported
from app.domain.profile import BRAND, Kind
from app.domain.values import canonical_key
from app.usecase.baseline_ports import CardRecord
from app.usecase.catalog_contract import CatalogConfiguration
from app.usecase.dto.feedback import Correction
from app.usecase.extraction import CardExtraction, RequiredAttributes, extract_card
from app.usecase.feedback_apply import apply_feedback, source_hash
from app.usecase.feedback_ports import FeedbackUowFactory


class InvalidCorrection(DomainError):
    code = "invalid_correction"
    message = "Correction must have a valid attribute and quote"


class CorrectionConflict(DomainError):
    code = "correction_conflict"
    message = "Correction conflicts with an existing or changed record"


@dataclass(frozen=True, slots=True)
class SaveCorrection:
    request_id: str
    text: str
    category_id: int
    attribute: str
    value: str
    quote: str
    start: int
    end: int
    learn_alias: bool = False


class FeedbackService:
    def __init__(self, configuration: CatalogConfiguration, uow: FeedbackUowFactory) -> None:
        self._configuration = configuration
        self._uow = uow
        self._required = RequiredAttributes(configuration.required, configuration.lexicon)

    def _record(self, command: SaveCorrection) -> Correction:
        if command.category_id not in {c.category_id for c in self._configuration.categories}:
            raise InvalidCorrection("Unknown category")
        title, _, description = clean_text(command.text).partition("\n")
        record = CardRecord(0, command.category_id, None, title, description, (), None)
        extraction = extract_card(record, self._required, self._configuration.lexicon, 0.35)
        profile = extraction.profiles.get(command.attribute)
        if (profile is None or profile.kind is Kind.UNSUPPORTED or not command.value.strip()
                or command.start < 0 or command.end <= command.start
                or extraction.text.span(command.start, command.end) != command.quote):
            raise InvalidCorrection()
        key = canonical_key(command.value, profile.unit, profile.numeric)
        if profile.numeric and not any(
            c.attribute == command.attribute and c.key == key
            and command.start <= c.start < c.end <= command.end for c in extraction.candidates
        ):
            raise InvalidCorrection("Numeric correction does not match its quote")
        display = self._configuration.lexicon.display(command.attribute, key)
        if profile.kind is Kind.CATEGORICAL and display is None:
            raise InvalidCorrection("Choose a normalized catalog value")
        candidate = Candidate(command.attribute, key, command.value, command.quote,
                              command.start, command.end, "human", extraction.text.zone(command.start),
                              1, 0, 0)
        if not supported(extraction.text, candidate):
            raise InvalidCorrection()
        brand = extraction.picks.get(BRAND)
        brand_key = brand.candidate.key if brand else ""
        if command.learn_alias and (not brand_key or profile.numeric or command.attribute == BRAND):
            raise InvalidCorrection("Reusable aliases need an unambiguous brand and a text attribute")
        fingerprint = hashlib.sha256(json.dumps(asdict(command), sort_keys=True).encode()).hexdigest()
        return Correction(id=command.request_id, fingerprint=fingerprint,
                          source_hash=source_hash(extraction), category_id=command.category_id,
                          brand=brand_key, attribute=command.attribute, value=display or command.value,
                          key=key, quote=command.quote, start=command.start, end=command.end,
                          learn_alias=command.learn_alias, created_at=datetime.now(UTC).isoformat())

    async def save(self, command: SaveCorrection) -> Correction:
        record = self._record(command)
        async with self._uow() as uow:
            prior = await uow.feedback.get(record.id)
            if prior is not None:
                if prior.fingerprint != record.fingerprint:
                    raise CorrectionConflict()
                return prior
            active = await uow.feedback.applicable(record.source_hash, record.category_id, record.brand)
            for existing in active:
                same_field = existing.attribute == record.attribute
                if same_field and existing.source_hash == record.source_hash:
                    raise CorrectionConflict("Revoke the current correction before replacing it")
                if (same_field and record.learn_alias and existing.learn_alias
                        and existing.quote.casefold() == record.quote.casefold()
                        and existing.key != record.key):
                    raise CorrectionConflict("An active scoped alias maps this quote differently")
            await uow.feedback.add(record)
            await uow.commit()
        return record

    async def revoke(self, identifier: str, version: int) -> Correction:
        async with self._uow() as uow:
            record = await uow.feedback.get(identifier)
            if record is None:
                raise InvalidCorrection("Correction does not exist")
            if record.revoked:
                return record
            if record.version != version:
                raise CorrectionConflict()
            await uow.feedback.revoke(identifier, version)
            await uow.commit()
        return replace(record, revoked=True, version=version + 1)

    async def enrich(self, extraction: CardExtraction, category: int) -> CardExtraction:
        brand = extraction.picks.get(BRAND)
        brand_key = brand.candidate.key if brand else ""
        async with self._uow() as uow:
            records = await uow.feedback.applicable(source_hash(extraction), category, brand_key)
        return apply_feedback(extraction, records, category)
