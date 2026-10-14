from pydantic import BaseModel, ConfigDict, Field

from app.usecase.catalog_contract import FieldState, Stage


class ExtractRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=30000)
    category_id: int | None = Field(default=None, gt=0)


class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category_id: int
    name: str


class OptionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    value: str
    quote: str
    start: int
    end: int


class FieldSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    attribute: str
    state: FieldState
    reason: str
    value: str | None
    quote: str | None
    start: int | None
    end: int | None
    source: str | None
    score: float | None
    score_kind: str
    confidence: float | None
    alternatives: list[OptionSchema]
    correction_id: str | None
    correction_version: int | None
    alias_brand: str | None


class ModelUsageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    model: str
    duration_ms: int
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: float | None


class ExtractionEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    stage: Stage
    category_id: int | None
    category_name: str | None
    category_reason: str
    source_text: str
    fields: list[FieldSchema]
    categories: list[CategorySchema]
    elapsed_ms: int
    model_calls: int
    model_usage: list[ModelUsageSchema]
    cached: bool
    warning: str | None
    synthetic_catalog: bool
    catalog_version: str
