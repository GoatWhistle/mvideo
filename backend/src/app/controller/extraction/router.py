from collections.abc import AsyncIterator
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request

from app.controller.errors import ErrorResponse
from app.controller.extraction.schemas import ExtractionEventSchema, ExtractRequest
from app.usecase.catalog_contract import CatalogProcessor, ExtractCommand

router = APIRouter(tags=["extraction"])


def processor(request: Request) -> CatalogProcessor:
    return cast(CatalogProcessor, request.app.state.providers.processor)


@router.post("/extract/stream", responses={422: {"model": ErrorResponse}})
async def extract(
    body: ExtractRequest,
    service: Annotated[CatalogProcessor, Depends(processor)],
) -> AsyncIterator[ExtractionEventSchema]:
    async for event in service.stream(ExtractCommand(body.text, body.category_id)):
        yield ExtractionEventSchema.model_validate(event)
