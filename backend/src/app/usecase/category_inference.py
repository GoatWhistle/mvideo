import time
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass

from app.domain.category_guess import ClickMapping, majority_mapping, resolve
from app.domain.category_metrics import curve, macro_f1, pick_threshold, top_k_accuracy
from app.usecase.category_ports import (
    CategoryCard,
    CategoryClassifier,
    CategoryCorpus,
    CategorySink,
    ClickVote,
)
from app.usecase.category_report import render_markdown
from app.usecase.interface import Logger

ALL_SPLITS = frozenset({"train", "val", "test", "new_category"})


@dataclass(frozen=True, slots=True)
class CategoryConfig:
    target_precision: float = 0.9
    top_k: int = 3
    batch: int = 20_000


class InferCategories:
    def __init__(
        self,
        corpus: CategoryCorpus,
        classifier: CategoryClassifier,
        sink: CategorySink,
        logger: Logger,
    ) -> None:
        self._corpus = corpus
        self._classifier = classifier
        self._sink = sink
        self._logger = logger

    def run(self, config: CategoryConfig) -> dict[str, object]:
        started = time.perf_counter()
        required = self._corpus.required_categories()
        labelled = list(self._corpus.labelled(ALL_SPLITS))
        by_split = {name: [c for c in labelled if c.split == name
                           and c.catalog_category in required] for name in ALL_SPLITS}
        train = by_split["train"]
        self._logger.info("category_fit", cards=len(train), categories=len(required))
        self._classifier.fit([c.text for c in train], [_label(c) for c in train])
        threshold = self._threshold(by_split["val"], config)
        classifier_report = self._evaluate(by_split["test"], threshold, config)
        top_votes = _top_votes(self._corpus.click_votes())
        clicks_report, mapping = self._click_mapping(labelled, top_votes)
        coverage = self._write_guesses(top_votes, mapping, threshold, config)
        report: dict[str, object] = {
            "required_categories": len(required),
            "train_cards": len(train),
            "target_precision": config.target_precision,
            "threshold": threshold,
            "classifier_test": classifier_report,
            "clicks": clicks_report,
            "coverage": coverage,
            "seconds": round(time.perf_counter() - started, 1),
        }
        self._sink.report(report, render_markdown(report))
        return report

    def _threshold(self, val: Sequence[CategoryCard], config: CategoryConfig) -> float:
        ranked = self._classifier.rank([c.text for c in val], config.top_k)
        threshold = pick_threshold([_label(c) for c in val], ranked, config.target_precision)
        self._logger.info("category_threshold", threshold=threshold, cards=len(val))
        return threshold

    def _evaluate(
        self, test: Sequence[CategoryCard], threshold: float, config: CategoryConfig
    ) -> dict[str, object]:
        truth = [_label(c) for c in test]
        ranked = self._classifier.rank([c.text for c in test], config.top_k)
        accepted = [(t, r[0][0]) for t, r in zip(truth, ranked, strict=True)
                    if r and r[0][1] >= threshold]
        return {
            "cards": len(test),
            "top1": round(top_k_accuracy(truth, ranked, 1), 4),
            "top3": round(top_k_accuracy(truth, ranked, 3), 4),
            "macro_f1": round(macro_f1(truth, [r[0][0] if r else -1 for r in ranked]), 4),
            "coverage_at_threshold": round(len(accepted) / len(test), 4) if test else 0.0,
            "precision_at_threshold": round(
                sum(1 for t, p in accepted if t == p) / len(accepted), 4) if accepted else 0.0,
            "curve": [asdict(p) for p in curve(truth, ranked)],
        }

    def _click_mapping(
        self, labelled: Sequence[CategoryCard], votes: Mapping[int, ClickVote]
    ) -> tuple[dict[str, object], dict[int, ClickMapping]]:
        catalog = {c.sku_id: _label(c) for c in labelled}
        split = {c.sku_id: c.split for c in labelled}
        train_pairs = [(v.click_category, catalog[s], v.clicks) for s, v in votes.items()
                       if split.get(s) == "train"]
        held_out = majority_mapping(train_pairs)
        test = [(v.click_category, catalog[s]) for s, v in votes.items()
                if split.get(s) == "test"]
        hits = sum(1 for click, true in test if click in held_out
                   and held_out[click].category_id == true)
        known = sum(1 for click, _ in test if click in held_out)
        mapping = majority_mapping((v.click_category, catalog[s], v.clicks)
                                   for s, v in votes.items() if s in catalog)
        report: dict[str, object] = {
            "test_cards": len(test),
            "test_mapped": known,
            "test_accuracy": round(hits / known, 4) if known else 0.0,
            "direct_id_match": round(
                sum(1 for click, true in test if click == true) / len(test), 4) if test else 0.0,
            "click_categories": len(mapping),
        }
        return report, mapping

    def _write_guesses(
        self,
        votes: Mapping[int, ClickVote],
        mapping: Mapping[int, ClickMapping],
        threshold: float,
        config: CategoryConfig,
    ) -> dict[str, object]:
        sources: Counter[str] = Counter()
        total = 0
        for batch in self._corpus.cards(config.batch):
            total += len(batch)
            pending = [c for c in batch if c.catalog_category is None
                       and _mapped(votes.get(c.sku_id), mapping) is None]
            ranked = dict(zip((c.sku_id for c in pending),
                              self._classifier.rank([c.text for c in pending], config.top_k),
                              strict=True))
            guesses = [g for c in batch if (g := resolve(
                c.sku_id, c.catalog_category, _mapped(votes.get(c.sku_id), mapping),
                ranked.get(c.sku_id, ()), threshold)) is not None]
            sources.update(g.source.value for g in guesses)
            self._sink.write(guesses)
            self._logger.info("category_batch", cards=total)
        self._sink.close()
        known = sum(sources.values())
        return {"cards": total, "with_category": known, "by_source": dict(sources),
                "share_with_category": round(known / total, 4) if total else 0.0}


def _label(card: CategoryCard) -> int:
    if card.catalog_category is None:
        raise ValueError(f"card {card.sku_id} has no catalog category")
    return card.catalog_category


def _top_votes(votes: Iterable[ClickVote]) -> dict[int, ClickVote]:
    best: dict[int, ClickVote] = {}
    for vote in votes:
        current = best.get(vote.sku_id)
        if current is None or vote.clicks > current.clicks:
            best[vote.sku_id] = vote
    return best


def _mapped(vote: ClickVote | None, mapping: Mapping[int, ClickMapping]) -> ClickMapping | None:
    return mapping.get(vote.click_category) if vote is not None else None
