"""Optimization: random search + hill-climb refine + walk-forward + overfit guards."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..backtest.engine import EventBacktester, VectorBacktester
from ..strategies.base import load_strategy
from ..utils.helpers import ensure_ohlcv


def load_space(strategy_name: str) -> dict:
    try:
        from ..optimization import search_spaces as sp

        return dict(sp.SEARCH_SPACES.get(strategy_name, {}))
    except Exception:
        return {}


def sample_params(space: dict, rng: np.random.Generator) -> dict:
    out = {}
    for k, spec in space.items():
        lo, hi, step = float(spec[0]), float(spec[1]), float(spec[2])
        if step <= 0:
            out[k] = lo
            continue
        n = max(1, int(round((hi - lo) / step)))
        out[k] = lo + float(rng.integers(0, n + 1)) * step
    return out


class StrategySearch:
    """Black-box tuner for one strategy on one dataset."""

    def __init__(self, strategy_name: str, df: pd.DataFrame,
                 fee_bps: float = 5.0, fast: bool = True):
        self.name = strategy_name
        self.df = ensure_ohlcv(df)
        self.space = load_space(strategy_name) or {"p1": [5, 40, 5], "p2": [20, 100, 10],
                                                   "p3": [3, 28, 5], "p4": [0.5, 3.0, 0.5]}
        self.fast = fast
        self.fee_bps = fee_bps

    def objective(self, params: dict) -> dict:
        try:
            strat = load_strategy(self.name, **params)
            sig = strat.generate_signals(self.df)
            pos = np.sign(sig["signal"].to_numpy()) * sig["confidence"].to_numpy() * sig["gate"].to_numpy()
            pos_s = pd.Series(pos, index=self.df.index)
            if self.fast:
                r = VectorBacktester(fee_bps=self.fee_bps).run(self.df, pos_s)
            else:
                r = EventBacktester(cash=100_000, fee_bps=self.fee_bps).run(self.df, pos_s)
            score = r["sharpe"] - 3.0 * r["turnover"] + 2.0 * min(0.0, r.get("max_dd", 0.0) + 0.3)
            return {"score": float(score), "sharpe": float(r["sharpe"]),
                    "turnover": float(r["turnover"]), "max_dd": float(r.get("max_dd", 0.0)),
                    "params": dict(params)}
        except Exception:
            return {"score": -99.0, "sharpe": -99.0, "turnover": 1.0, "max_dd": -1.0, "params": dict(params)}

    def random_search(self, trials: int = 50, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        rows = [self.objective(sample_params(self.space, rng)) for _ in range(trials)]
        df = pd.DataFrame(rows)
        return df.sort_values("score", ascending=False).reset_index(drop=True)

    def refine(self, params: dict, iters: int = 20, seed: int = 1) -> dict:
        rng = np.random.default_rng(seed)
        best = self.objective(params)
        for _ in range(iters):
            cand = dict(best["params"])
            k = rng.choice(list(self.space.keys()))
            lo, hi, step = self.space[k]
            cand[k] = float(np.clip(cand[k] + rng.choice([-1, 1]) * step, lo, hi))
            r = self.objective(cand)
            if r["score"] > best["score"]:
                best = r
        return best


def walk_forward(strategy_name: str, df: pd.DataFrame, n_folds: int = 4,
                 trials: int = 30, embargo: int = 20, seed: int = 0) -> dict:
    """Anchored walk-forward: tune in-sample, score out-of-sample, repeat."""
    df = ensure_ohlcv(df)
    n = len(df)
    fold = n // (n_folds + 1)
    folds = []
    for f in range(n_folds):
        tr_end = fold * (f + 1)
        te_end = min(n, fold * (f + 2))
        train = df.iloc[:tr_end]
        test = df.iloc[tr_end + embargo: te_end]
        if len(test) < 50 or len(train) < 200:
            continue
        search = StrategySearch(strategy_name, train)
        ranked = search.random_search(trials, seed + f)
        best_params = ranked.iloc[0]["params"]
        oos = StrategySearch(strategy_name, test).objective(best_params)
        folds.append({"fold": f, "params": best_params, "is_score": float(ranked.iloc[0]["score"]),
                      "oos_score": float(oos["score"]), "oos_sharpe": float(oos["sharpe"])})
    if not folds:
        return {"folds": [], "robust": False}
    oos = np.array([x["oos_score"] for x in folds])
    iss = np.array([x["is_score"] for x in folds])
    degradation = float(np.mean(iss - oos))
    robust = bool(np.mean(oos) > 0 and np.mean(oos > 0) >= 0.6 and degradation < 2.0)
    return {"folds": folds, "mean_oos": float(np.mean(oos)), "frac_positive": float(np.mean(oos > 0)),
            "degradation": degradation, "robust": robust}


def haircut_sharpe(sharpe_ratio: float, n_obs: int, trials: int,
                   skew: float = 0.0, kurt: float = 3.0) -> dict:
    """Simplified Deflated-Sharpe-style haircut for multiple testing (documented approx)."""
    import math

    sr = float(sharpe_ratio)
    t = max(2, int(n_obs))
    k = max(1, int(trials))
    gamma3, gamma4 = float(skew), float(kurt)
    var_sr = (1 + 0.5 * sr ** 2 - gamma3 * sr + (gamma4 / 4 - 0.75) * sr ** 2 / 2) / max(1, t - 1)
    var_sr = max(var_sr, 1e-9)
    euler = 0.5772156649
    exp_max = (1 - euler) * math.sqrt(var_sr) + euler * math.sqrt(var_sr) * (1 if k == 1 else math.sqrt(2 * math.log(k)))
    dsr = (sr - exp_max) / math.sqrt(var_sr)
    from math import erf

    prob = 0.5 * (1 + erf(dsr / math.sqrt(2)))
    return {"dsr": float(dsr), "prob_skill": float(np.clip(prob, 0, 1)),
            "haircut": float(sr - exp_max), "trials": k}
