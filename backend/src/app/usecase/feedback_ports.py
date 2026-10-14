from collections.abc import Callable
from typing import Protocol, Self

from app.usecase.dto.feedback import CatalogSnapshot, Correction


class FeedbackRepository(Protocol):
    async def get(self, identifier: str) -> Correction | None: ...
    async def applicable(
        self, source_hash: str, category_id: int, brand: str
    ) -> tuple[Correction, ...]: ...
    async def add(self, value: Correction) -> None: ...
    async def revoke(self, identifier: str, version: int) -> None: ...


class CatalogRepository(Protocol):
    async def get(self) -> CatalogSnapshot | None: ...
    async def seed(self, snapshot: CatalogSnapshot) -> None: ...


class FeedbackUnitOfWork(Protocol):
    feedback: FeedbackRepository
    catalog: CatalogRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *exc: object) -> None: ...
    async def commit(self) -> None: ...


type FeedbackUowFactory = Callable[[], FeedbackUnitOfWork]
