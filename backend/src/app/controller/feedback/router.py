from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.controller.errors import ErrorResponse
from app.usecase.feedback import FeedbackService, SaveCorrection

router = APIRouter(tags=["feedback"])


class CorrectionRequest(BaseModel):
    request_id: UUID
    text: str = Field(min_length=1, max_length=30000)
    category_id: int = Field(gt=0)
    attribute: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1, max_length=200)
    quote: str = Field(min_length=1, max_length=500)
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    learn_alias: bool = False


class CorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    version: int
    revoked: bool
    learn_alias: bool


class RevokeRequest(BaseModel):
    version: int = Field(gt=0)


def feedback(request: Request) -> FeedbackService:
    service = cast(FeedbackService | None, request.app.state.providers.feedback)
    if service is None:
        raise HTTPException(503, "Feedback storage is not configured")
    return service


@router.post("/feedback", response_model=CorrectionResponse,
             responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
async def save_correction(
    body: CorrectionRequest, service: Annotated[FeedbackService, Depends(feedback)],
) -> CorrectionResponse:
    result = await service.save(SaveCorrection(
        str(body.request_id), body.text, body.category_id, body.attribute, body.value,
        body.quote, body.start, body.end, body.learn_alias,
    ))
    return CorrectionResponse.model_validate(result)


@router.post("/feedback/{identifier}/revoke", response_model=CorrectionResponse,
             responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
async def revoke_correction(
    identifier: UUID, body: RevokeRequest, service: Annotated[FeedbackService, Depends(feedback)],
) -> CorrectionResponse:
    return CorrectionResponse.model_validate(await service.revoke(str(identifier), body.version))
