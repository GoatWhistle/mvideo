from collections.abc import Sequence

import numpy as np
from sklearn.isotonic import IsotonicRegression


class IsotonicCalibrator:
    def __init__(self) -> None:
        self._model = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")

    def fit(self, scores: Sequence[float], labels: Sequence[bool]) -> None:
        self._model.fit(np.asarray(scores, dtype=np.float64), np.asarray(labels, dtype=np.float64))

    def transform(self, scores: Sequence[float]) -> Sequence[float]:
        values: list[float] = self._model.predict(np.asarray(scores, dtype=np.float64)).tolist()
        return values
