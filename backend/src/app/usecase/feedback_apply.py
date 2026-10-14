import hashlib
from dataclasses import replace

from app.domain.candidate import Candidate
from app.domain.evidence import conflicts, supported
from app.domain.extractors import dictionary_candidates
from app.domain.lexicon import Lexicon, LexiconEntry, value_tokens
from app.domain.scoring import Pick, pick_values
from app.usecase.dto.feedback import Correction
from app.usecase.extraction import CardExtraction


def source_hash(extraction: CardExtraction) -> str:
    return hashlib.sha256(extraction.text.text.encode()).hexdigest()


def apply_feedback(
    extraction: CardExtraction, records: tuple[Correction, ...], category: int
) -> CardExtraction:
    if not records:
        return extraction
    entries = [
        LexiconEntry(r.attribute, value_tokens(r.quote), r.key, r.value)
        for r in records
        if r.learn_alias and r.attribute in extraction.profiles
    ]
    lexicon = Lexicon(extraction.profiles, entries, {})
    aliases = [
        replace(c, source="confirmed_alias")
        for c in dictionary_candidates(extraction.text, extraction.profiles, lexicon, category)
        if supported(extraction.text, c)
    ]
    spans = {(c.attribute, c.start, c.end) for c in aliases}
    candidates = tuple(
        c for c in extraction.candidates if (c.attribute, c.start, c.end) not in spans
    )
    candidates += tuple(aliases)
    picks = pick_values(candidates, extraction.profiles)
    ambiguous = conflicts(candidates)
    accepted = {
        name: pick
        for name, pick in picks.items()
        if pick.confidence >= 0.35
        and name not in ambiguous
        and (name in extraction.picks or pick.candidate.source == "confirmed_alias")
    }
    review = {name: pick for name, pick in picks.items() if name not in accepted}
    corrections = {}
    for record in records:
        if record.source_hash != source_hash(extraction):
            continue
        candidate = Candidate(
            record.attribute,
            record.key,
            record.value,
            record.quote,
            record.start,
            record.end,
            "human",
            extraction.text.zone(record.start),
            1,
            0,
            0,
        )
        if not supported(extraction.text, candidate):
            continue
        accepted[record.attribute] = Pick(candidate, 1, ("human",))
        review.pop(record.attribute, None)
        corrections[record.attribute] = record
    return replace(
        extraction, candidates=candidates, picks=accepted, review=review, corrections=corrections
    )
