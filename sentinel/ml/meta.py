"""Meta-labeling gate: supervised veto over base-strategy candidates."""
from __future__ import annotations

import numpy as np
import pandas as pd


def labeled_matrix(vote: pd.Series, agreement: pd.Series, regime: pd.DataFrame,
                   close: pd.Series, horizon: int = 10, min_vote: float = 0.1):
    """Build (X, y, mask): features at t, label = did sign(vote) win over horizon?"""
    idx = vote.index
    fwd = close.shift(-horizon).astype(float) / (close.astype(float) + 1e-12) - 1.0
    v = vote.reindex(idx).fillna(0.0)
    a = agreement.reindex(idx).fillna(0.0)
    X = pd.DataFrame(index=idx)
    X["vote"] = v
    X["agreement"] = a
    X["vote_x_agree"] = v * a
    for c in ("vol_ratio", "range_pos", "width_q", "vol_q", "trend_r2", "efficiency",
              "p_trend", "p_range", "p_squeeze", "p_panic"):
        if c in regime.columns:
            X[c] = regime[c].reindex(idx).fillna(0.0)
    direction = np.sign(v.to_numpy(dtype=float))
    fwd_a = fwd.reindex(idx).fillna(0.0).to_numpy(dtype=float)
    won = (direction * fwd_a) > 0
    active = (np.abs(v.to_numpy(dtype=float)) >= min_vote) & (np.arange(len(idx)) < len(idx) - horizon)
    y = pd.Series(np.where(won & active, 1, 0), index=idx)
    return X.fillna(0.0), y, pd.Series(active, index=idx)


class MetaGate:
    """Calibrated gradient-boosting veto. Graceful fallback if sklearn is missing."""

    def __init__(self, threshold: float = 0.55, random_state: int = 42):
        self.threshold = threshold
        self.random_state = random_state
        self.model = None
        self.n_features = 0
        self.train_pos_rate = 0.5

    def _build(self):
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        base = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08,
                                              max_leaf_nodes=15, random_state=self.random_state)
        clf = CalibratedClassifierCV(estimator=base, cv=3)
        return make_pipeline(StandardScaler(), clf)

    def fit(self, X, y, sample_weight=None) -> "MetaGate":
        Xa = np.asarray(X, dtype=float)
        ya = np.asarray(y, dtype=int)
        self.n_features = Xa.shape[1]
        self.train_pos_rate = float(ya.mean()) if len(ya) else 0.5
        if len(np.unique(ya)) < 2:
            self.model = None
            return self
        try:
            self.model = self._build()
            self.model.fit(Xa, ya)
        except Exception:
            self.model = None
        return self

    def predict_proba(self, X) -> np.ndarray:
        Xa = np.asarray(X, dtype=float)
        if self.model is None or Xa.shape[1] != self.n_features or self.n_features == 0:
            return np.full(len(Xa), 0.5)
        try:
            return self.model.predict_proba(Xa)[:, 1]
        except Exception:
            return np.full(len(Xa), 0.5)

    def approve(self, X, threshold: float | None = None) -> np.ndarray:
        thr = self.threshold if threshold is None else float(threshold)
        return self.predict_proba(X) >= thr

    def importance(self, X, y, reps: int = 5) -> dict:
        Xa = np.asarray(X, dtype=float)
        ya = np.asarray(y, dtype=int)
        cols = list(X.columns) if isinstance(X, pd.DataFrame) else [f"f{i}" for i in range(Xa.shape[1])]
        base = float(np.mean((self.predict_proba(Xa) > 0.5) == ya)) if len(ya) else 0.0
        rng = np.random.default_rng(0)
        out = {}
        for j, c in enumerate(cols):
            drops = []
            for _ in range(reps):
                Xs = Xa.copy()
                Xs[:, j] = rng.permutation(Xs[:, j])
                acc = float(np.mean((self.predict_proba(Xs) > 0.5) == ya)) if len(ya) else 0.0
                drops.append(base - acc)
            out[c] = float(np.mean(drops))
        return dict(sorted(out.items(), key=lambda kv: kv[1], reverse=True))

    def drift(self, X_new) -> dict:
        Xn = np.asarray(X_new, dtype=float)
        p = self.predict_proba(Xn)
        return {"mean_proba": float(np.mean(p)) if len(p) else 0.5,
                "pos_frac": float(np.mean(p >= self.threshold)) if len(p) else 0.0,
                "train_pos_rate": float(self.train_pos_rate)}

    def save(self, path) -> None:
        try:
            import joblib

            joblib.dump({"model": self.model, "thr": self.threshold,
                         "nf": self.n_features, "pos": self.train_pos_rate}, path)
        except Exception:
            pass

    def load(self, path) -> bool:
        try:
            import joblib

            d = joblib.load(path)
            self.model, self.threshold = d["model"], d["thr"]
            self.n_features, self.train_pos_rate = d["nf"], d["pos"]
            return True
        except Exception:
            return False
