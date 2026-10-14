from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, Pool

from app.usecase.ranker_ports import FeatureTable

ITERATIONS = 400
DEPTH = 6
LEARNING_RATE = 0.1
SEED = 42


class CatBoostScoreModel:
    def __init__(self, iterations: int = ITERATIONS, threads: int = -1) -> None:
        self._model = CatBoostClassifier(
            iterations=iterations,
            depth=DEPTH,
            learning_rate=LEARNING_RATE,
            loss_function="Logloss",
            random_seed=SEED,
            thread_count=threads,
            verbose=False,
            allow_writing_files=False,
        )
        self._names: list[str] = []
        self._categorical: list[str] = []

    def _frame(self, table: FeatureTable) -> pd.DataFrame:
        numeric = np.frombuffer(table.numeric, dtype=np.float32).reshape(table.rows, table.width)
        frame = pd.DataFrame(numeric, columns=self._names)
        for index, name in enumerate(self._categorical):
            frame[name] = [row[index] for row in table.categorical]
        return frame

    def fit(self, train: FeatureTable, names: Sequence[str], categorical: Sequence[str]) -> None:
        self._names = list(names)
        self._categorical = list(categorical)
        labels = np.frombuffer(train.labels, dtype=np.int8)
        pool = Pool(self._frame(train), label=labels, cat_features=self._categorical)
        self._model.fit(pool)

    def predict(self, table: FeatureTable) -> Sequence[float]:
        pool = Pool(self._frame(table), cat_features=self._categorical)
        probabilities: list[float] = self._model.predict_proba(pool)[:, 1].tolist()
        return probabilities

    def importances(self) -> Mapping[str, float]:
        values = self._model.get_feature_importance()
        return {
            name: float(v) for name, v in zip(self._names + self._categorical, values, strict=True)
        }
