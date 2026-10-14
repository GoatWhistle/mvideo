from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class CatalogSnapshot:
    version: str
    payload: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Correction:
    id: str
    fingerprint: str
    source_hash: str
    category_id: int
    brand: str
    attribute: str
    value: str
    key: str
    quote: str
    start: int
    end: int
    learn_alias: bool
    created_at: str
    revoked: bool = False
    version: int = 1
