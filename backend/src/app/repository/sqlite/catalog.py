import aiosqlite

from app.usecase.dto.feedback import CatalogSnapshot

GET = "SELECT version, payload FROM catalog_configuration WHERE id = 1"
SEED = "INSERT INTO catalog_configuration (id, version, payload) VALUES (1, ?, ?) ON CONFLICT DO NOTHING"


class SqliteCatalogRepository:
    def __init__(self, connection: aiosqlite.Connection) -> None:
        self._connection = connection

    async def get(self) -> CatalogSnapshot | None:
        async with self._connection.execute(GET) as cursor:
            row = await cursor.fetchone()
        return CatalogSnapshot(version=str(row[0]), payload=str(row[1])) if row else None

    async def seed(self, snapshot: CatalogSnapshot) -> None:
        await self._connection.execute(SEED, (snapshot.version, snapshot.payload))
