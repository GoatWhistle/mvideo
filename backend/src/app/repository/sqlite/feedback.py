from dataclasses import asdict

import aiosqlite

from app.usecase.dto.feedback import Correction

COLUMNS = "id, fingerprint, source_hash, category_id, brand, attribute, value, key, quote, start, end, learn_alias, created_at, revoked, version"
GET = f"SELECT {COLUMNS} FROM corrections WHERE id = ?"
APPLICABLE = f"""SELECT {COLUMNS} FROM corrections
WHERE revoked = 0 AND category_id = ? AND (source_hash = ? OR (learn_alias = 1 AND brand = ?))
ORDER BY created_at, id"""
ADD = f"""INSERT INTO corrections ({COLUMNS}) VALUES (
:id, :fingerprint, :source_hash, :category_id, :brand, :attribute, :value, :key,
:quote, :start, :end, :learn_alias, :created_at, :revoked, :version)"""
REVOKE = "UPDATE corrections SET revoked = 1, version = version + 1 WHERE id = ? AND version = ? AND revoked = 0"


def correction(row: aiosqlite.Row) -> Correction:
    values = dict(row)
    values["learn_alias"] = bool(values["learn_alias"])
    values["revoked"] = bool(values["revoked"])
    return Correction(**values)


class SqliteFeedbackRepository:
    def __init__(self, connection: aiosqlite.Connection) -> None:
        self._connection = connection

    async def get(self, identifier: str) -> Correction | None:
        async with self._connection.execute(GET, (identifier,)) as cursor:
            row = await cursor.fetchone()
        return correction(row) if row else None

    async def applicable(
        self, source_hash: str, category_id: int, brand: str
    ) -> tuple[Correction, ...]:
        async with self._connection.execute(
            APPLICABLE, (category_id, source_hash, brand)
        ) as cursor:
            rows = await cursor.fetchall()
        return tuple(correction(row) for row in rows)

    async def add(self, value: Correction) -> None:
        await self._connection.execute(ADD, asdict(value))

    async def revoke(self, identifier: str, version: int) -> None:
        await self._connection.execute(REVOKE, (identifier, version))
