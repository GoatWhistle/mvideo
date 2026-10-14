from collections.abc import Sequence

import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import HashingVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier

from app.domain.category_guess import Ranked

CHAR_FEATURES = 2**16
WORD_FEATURES = 2**16
RANK_BATCH = 5_000


class TfidfLinearClassifier:
    def __init__(self, seed: int = 0, jobs: int = 5, epochs: int = 8) -> None:
        self._chars = HashingVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                        n_features=CHAR_FEATURES, alternate_sign=False,
                                        norm=None)
        self._words = HashingVectorizer(analyzer="word", ngram_range=(1, 2),
                                        n_features=WORD_FEATURES, alternate_sign=False,
                                        norm=None, token_pattern=r"(?u)\b\w+\b")
        self._tfidf = TfidfTransformer(sublinear_tf=True)
        self._model = SGDClassifier(loss="log_loss", alpha=2e-6, max_iter=epochs, tol=None,
                                    n_jobs=jobs, random_state=seed)
        self._classes: np.ndarray | None = None

    def _features(self, texts: Sequence[str]) -> object:
        return hstack([self._chars.transform(texts), self._words.transform(texts)]).tocsr()

    def fit(self, texts: Sequence[str], labels: Sequence[int]) -> None:
        matrix = self._tfidf.fit_transform(self._features(texts))
        self._model.fit(matrix, np.asarray(labels))
        self._classes = self._model.classes_

    def rank(self, texts: Sequence[str], k: int) -> list[Ranked]:
        if self._classes is None:
            raise RuntimeError("classifier is not fitted")
        ranked: list[Ranked] = []
        for start in range(0, len(texts), RANK_BATCH):
            chunk = texts[start:start + RANK_BATCH]
            probabilities = self._model.predict_proba(self._tfidf.transform(self._features(chunk)))
            top = np.argsort(-probabilities, axis=1)[:, :k]
            for row, indices in zip(probabilities, top, strict=True):
                ranked.append([(int(self._classes[i]), float(row[i])) for i in indices])
        return ranked
