import argparse
import asyncio
import sys
from typing import cast

from app.controller.extraction.schemas import ExtractionEventSchema, ExtractRequest
from app.main import Providers, create_app
from app.settings import Settings
from app.usecase.catalog_contract import ExtractCommand


async def run(body: ExtractRequest, database: str) -> None:
    app = create_app(Settings(database_path=database))
    async with app.router.lifespan_context(app):
        providers = cast(Providers, app.state.providers)
        command = ExtractCommand(body.text, body.category_id)
        async for event in providers.processor.stream(command):
            print(ExtractionEventSchema.model_validate(event).model_dump_json(), flush=True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Extract a product through the offline stand cascade"
    )
    parser.add_argument("--text", help="card text; reads stdin when omitted")
    parser.add_argument("--category", type=int)
    parser.add_argument("--database", default="data/app.db")
    args = parser.parse_args(argv)
    try:
        body = ExtractRequest(
            text=args.text if args.text is not None else sys.stdin.read(),
            category_id=args.category,
        )
        asyncio.run(run(body, args.database))
    except (ValueError, OSError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
