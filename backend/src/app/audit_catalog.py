import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from app.adapter.dataset.baseline_source import ParquetBaselineSource
from app.usecase.catalog_audit import AuditCatalog, AuditConfig

FILES = ("cards.parquet", "gold.parquet", "splits.parquet", "required_attributes.parquet")


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Audit split overlap and label discrepancies offline"
    )
    parser.add_argument("--data", type=Path, default=Path("../data/processed"))
    parser.add_argument("--out", type=Path, default=Path("../reports/catalog-audit.json"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples-per-group", type=int, default=5)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args(argv)
    missing = [name for name in FILES if not (args.data / name).is_file()]
    if missing:
        parser.error(
            f"Missing processed data in {args.data}: {', '.join(missing)}; run prepare-data"
        )
    if args.out.exists():
        parser.error(f"Output already exists: {args.out}; use a new --out path")
    if args.samples_per_group < 1:
        parser.error("--samples-per-group must be positive")
    report = AuditCatalog(ParquetBaselineSource(args.data)).run(
        AuditConfig(seed=args.seed, samples_per_group=args.samples_per_group),
    )
    payload = {
        **report,
        "created_at": datetime.now(UTC).isoformat(),
        "revision": args.revision,
        "source_sha256": {name: fingerprint(args.data / name) for name in FILES},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as target:
        json.dump(payload, target, ensure_ascii=False, indent=2)
        target.write("\n")
    print(json.dumps({"cards": report["cards"], "report": str(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
