import argparse
import json
import resource
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from app.adapter.dataset.baseline_sink import FileReportSink
from app.adapter.dataset.twin_sink import FileTwinPredictionSink
from app.adapter.dataset.twin_source import ParquetTwinSource
from app.adapter.log.stdlib import StdlibLogger, configure
from app.adapter.ranker.isotonic import IsotonicCalibrator
from app.adapter.twin.tfidf_index import TfidfTitleIndex
from app.usecase.twins import RunTwins, TwinConfig

DEFAULT_DATA = Path("data/processed")
DEFAULT_OUT = Path("data/predictions")
DEFAULT_REPORTS = Path("reports")
NAME = "twins"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Transfer attributes from catalog twins")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--reports", type=Path, default=DEFAULT_REPORTS)
    parser.add_argument("--stage", default=TwinConfig().stage,
                        help="predictions file in --out to build on, e.g. ranker")
    parser.add_argument("--k", type=int, default=TwinConfig().k)
    parser.add_argument("--knn-batch", type=int, default=256)
    parser.add_argument("--batch", type=int, default=2000)
    args = parser.parse_args(argv)
    configure()
    usecase = RunTwins(
        source=ParquetTwinSource(args.data, args.out),
        index=TfidfTitleIndex(batch=args.knn_batch),
        calibrator=IsotonicCalibrator(),
        sink=FileTwinPredictionSink(args.out, NAME),
        reports=FileReportSink(args.reports, NAME),
        logger=StdlibLogger("twins"),
    )
    report = usecase.run(TwinConfig(stage=args.stage, k=args.k, batch=args.batch))
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    rows = cast(Sequence[Mapping[str, object]], report["ablation"])
    summary = next((r for r in rows if r["group"] == "all"), None)
    print(json.dumps({"cards": report["cards"], "threshold": report["threshold"],
                      "all": summary, "peak_rss_mb": peak_mb}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
