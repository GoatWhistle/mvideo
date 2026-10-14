import hashlib
import json
from importlib.resources import files
from pathlib import Path

from app.domain.category_selection import CategoryOption
from app.domain.lexicon import Lexicon, LexiconEntry, value_tokens
from app.domain.profile import AttributeProfile, Kind, name_keywords
from app.domain.values import canonical_key
from app.usecase.baseline_ports import RequiredRecord
from app.usecase.catalog_contract import CatalogConfiguration


def load_configuration(path: Path | None = None) -> CatalogConfiguration:
    raw = path.read_text() if path else files("app").joinpath("assets/demo-catalog.json").read_text()
    return parse_configuration(raw)


def parse_configuration(raw: str) -> CatalogConfiguration:
    payload = json.loads(raw)
    categories = tuple(CategoryOption(int(c["id"]), str(c["name"]), tuple(c["keywords"]))
                       for c in payload["categories"])
    profiles = {}
    entries = []
    required = []
    for attribute in payload["attributes"]:
        name = str(attribute["name"])
        kind = Kind(attribute["kind"])
        unit = str(attribute.get("unit", ""))
        extra = name_keywords(" ".join(attribute.get("keywords", [])))
        keywords = tuple(dict.fromkeys((*name_keywords(name), *extra)))
        profiles[name] = AttributeProfile(name, kind, unit, keywords)
        for value in attribute.get("values", []):
            key = canonical_key(value, unit, kind is Kind.NUMERIC)
            entries.append(LexiconEntry(name, value_tokens(value), key, value))
        for category in attribute["categories"]:
            required.append(RequiredRecord(int(category), name, 1))
    lexicon = Lexicon(profiles, entries, {})
    return CatalogConfiguration(categories, tuple(required), lexicon,
                                hashlib.sha256(raw.encode()).hexdigest()[:16],
                                bool(payload["synthetic"]))
