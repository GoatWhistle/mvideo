from pathlib import Path
from typing import Self

import aiosqlite

from app.repository.sqlite.catalog import SqliteCatalogRepository
from app.repository.sqlite.feedback import SqliteFeedbackRepository
from app.usecase.feedback_ports import CatalogRepository, FeedbackRepository


class SqliteUow:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._connection: aiosqlite.Connection | None = None
        self.catalog: CatalogRepository
        self.feedback: FeedbackRepository

    async def __aenter__(self) -> Self:
        if not self._path.is_file():
            raise RuntimeError(
                f"Missing SQLite database {self._path}; run dbmate migrations and seed-catalog"
            )
        connection = await aiosqlite.connect(self._path)
        try:
            connection.row_factory = aiosqlite.Row
            await connection.execute("PRAGMA busy_timeout = 5000")
            await connection.execute("PRAGMA foreign_keys = ON")
            async with connection.execute("PRAGMA journal_mode") as cursor:
                mode = await cursor.fetchone()
            if mode is None or mode[0] != "wal":
                raise RuntimeError("SQLite WAL is not enabled; run dbmate migrations")
            await connection.execute("BEGIN IMMEDIATE")
        except BaseException:
            await connection.close()
            raise
        self._connection = connection
        self.catalog = SqliteCatalogRepository(connection)
        self.feedback = SqliteFeedbackRepository(connection)
        return self

    async def commit(self) -> None:
        if self._connection is None:
            raise RuntimeError("Unit of work is not active")
        await self._connection.commit()

    async def __aexit__(self, *exc: object) -> None:
        if self._connection is not None:
            try:
                await self._connection.rollback()
            finally:
                await self._connection.close()
                self._connection = None
