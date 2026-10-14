import argparse
import asyncio
import hashlib
from importlib.resources import files
from pathlib import Path

from app.adapter.catalog.configured import parse_configuration
from app.repository.sqlite.uow import SqliteUow
from app.usecase.dto.feedback import CatalogSnapshot
from app.usecase.seed_catalog import SeedCatalog


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Seed the demo catalog through the storage use case"
    )
    parser.add_argument("--database", type=Path, default=Path("data/app.db"))
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args(argv)
    raw = (
        args.catalog.read_text()
        if args.catalog
        else files("app").joinpath("assets/demo-catalog.json").read_text()
    )
    parse_configuration(raw)
    snapshot = CatalogSnapshot(version=hashlib.sha256(raw.encode()).hexdigest()[:16], payload=raw)
    asyncio.run(SeedCatalog(lambda: SqliteUow(args.database)).run(snapshot))
    print(f"Catalog seed completed: {args.database}")


if __name__ == "__main__":
    main()
