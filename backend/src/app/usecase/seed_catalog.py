from app.usecase.dto.feedback import CatalogSnapshot
from app.usecase.feedback_ports import FeedbackUowFactory


class SeedCatalog:
    def __init__(self, uow: FeedbackUowFactory) -> None:
        self._uow = uow

    async def run(self, snapshot: CatalogSnapshot) -> None:
        async with self._uow() as uow:
            await uow.catalog.seed(snapshot)
            await uow.commit()
