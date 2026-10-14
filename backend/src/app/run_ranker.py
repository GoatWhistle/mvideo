import argparse
import json
import resource
from pathlib import Path

from app.adapter.dataset.baseline_sink import FilePredictionSink, FileReportSink
from app.adapter.dataset.ranker_source import ParquetRankerSource
from app.adapter.log.stdlib import StdlibLogger, configure
from app.adapter.ranker.catboost_model import CatBoostScoreModel
from app.adapter.ranker.isotonic import IsotonicCalibrator
from app.usecase.ranker import RankerConfig, RunRanker

DEFAULT_DATA = Path("data/processed")
DEFAULT_OUT = Path("data/predictions")
DEFAULT_REPORTS = Path("reports")
NAME = "ranker"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train the candidate ranker and evaluate it")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--reports", type=Path, default=DEFAULT_REPORTS)
    parser.add_argument("--train-modulo", type=int, default=RankerConfig().train_modulo,
                        help="use train cards whose sku_id is divisible by this number")
    parser.add_argument("--iterations", type=int, default=400)
    parser.add_argument("--batch", type=int, default=2000)
    args = parser.parse_args(argv)
    configure()
    baseline_path = args.reports / "baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() \
        else None
    usecase = RunRanker(
        source=ParquetRankerSource(args.data),
        model=CatBoostScoreModel(iterations=args.iterations),
        calibrator=IsotonicCalibrator(),
        sink=FilePredictionSink(args.out, NAME, candidates=False, calibrated=True),
        reports=FileReportSink(args.reports, NAME),
        logger=StdlibLogger("ranker"),
        baseline_report=baseline,
    )
    report = usecase.run(RankerConfig(train_modulo=args.train_modulo, batch=args.batch))
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    groups = report.get("groups", {})
    summary = groups.get("all", {}) if isinstance(groups, dict) else {}
    print(json.dumps({"cards": report["cards"], "all": summary, "peak_rss_mb": peak_mb},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
