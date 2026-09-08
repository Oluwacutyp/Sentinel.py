"""Core math / stats / time utilities (numpy + pandas only)."""
from __future__ import annotations

import math
import time as _time

import numpy as np
import pandas as pd

OHLCV = ("open", "high", "low", "close", "volume")


def ensure_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Validate frame, sort index, coerce dtypes, drop empty rows."""
    if df is None or len(df) == 0:
        raise ValueError("empty dataframe")
    missing = [c for c in ("open", "high", "low", "close") if c not in df.columns]
    if missing:
        raise ValueError(f"missing OHLC columns: {missing}")
    out = df.sort_index()
    out = out[~out.index.duplicated(keep="last")]
    for c in ("open", "high", "low", "close"):
        out[c] = out[c].astype(float)
    if "volume" in out.columns:
        out["volume"] = out["volume"].astype(float).fillna(0.0)
    else:
        out["volume"] = 0.0
    out = out.dropna(subset=["open", "high", "low", "close"])
    return out


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.astype(float).ewm(span=max(2, int(span)), adjust=False).mean()


def sma(s: pd.Series, window: int) -> pd.Series:
    return s.astype(float).rolling(max(2, int(window)), min_periods=1).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    h, l, c = df["high"].astype(float), df["low"].astype(float), df["close"].astype(float)
    pc = c.shift(1)
    return pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    tr = true_range(df)
    return tr.ewm(alpha=1.0 / max(2, int(n)), adjust=False).mean().bfill().fillna(1e-9)


def rolling_zscore(s: pd.Series, window: int) -> pd.Series:
    m = s.rolling(window, min_periods=max(2, window // 4)).mean()
    sd = s.rolling(window, min_periods=max(2, window // 4)).std().bfill().ffill().fillna(1e-9)
    return ((s - m) / (sd + 1e-12)).fillna(0.0)


def rolling_quantile(s: pd.Series, q: float, window: int) -> pd.Series:
    return s.rolling(window, min_periods=max(5, window // 5)).quantile(q).bfill().ffill()


def log_returns(close: pd.Series) -> pd.Series:
    return np.log(close.astype(float) / close.astype(float).shift(1)).fillna(0.0)


def sharpe(returns: pd.Series, periods: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 3:
        return 0.0
    sd = float(np.std(r, ddof=1))
    if sd <= 1e-12:
        return 0.0
    return float(np.mean(r) / sd * math.sqrt(periods))


def sortino(returns: pd.Series, periods: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 3:
        return 0.0
    dn = r[r < 0]
    if len(dn) < 2 or float(np.std(dn)) <= 1e-12:
        return 0.0
    return float(np.mean(r) / float(np.std(dn)) * math.sqrt(periods))


def max_drawdown(equity: pd.Series) -> dict:
    eq = np.asarray(equity, dtype=float)
    if len(eq) == 0:
        return {"max_dd": 0.0, "peak": 0, "trough": 0}
    peak = np.maximum.accumulate(eq)
    dd = np.where(peak > 0, (eq - peak) / peak, 0.0)
    trough = int(np.argmin(dd))
    peak_i = int(np.argmax(eq[: trough + 1])) if trough else 0
    return {"max_dd": float(dd[trough]), "peak": peak_i, "trough": trough}


def profit_factor(returns: pd.Series) -> float:
    r = np.asarray(returns, dtype=float)
    gains = float(r[r > 0].sum())
    losses = float(-r[r < 0].sum())
    if losses <= 1e-12:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def clamp(x: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, x)))


def softmax(d: dict) -> dict:
    if not d:
        return {}
    keys = list(d.keys())
    v = np.array([float(d[k]) for k in keys], dtype=float)
    v = v - float(np.max(v))
    e = np.exp(np.clip(v, -50, 50))
    s = float(e.sum()) or 1.0
    return {k: float(e[i] / s) for i, k in enumerate(keys)}


def quantile_gate(values: pd.Series, q_high: float = 0.8, q_low: float = 0.2, window: int = 200):
    """Adaptive thresholds from rolling quantiles. Returns (hi, lo) series."""
    hi = rolling_quantile(values, q_high, window)
    lo = rolling_quantile(values, q_low, window)
    return hi, lo


class Timer:
    def __init__(self, label: str = ""):
        self.label = label
        self.t0 = 0.0
        self.dt = 0.0

    def __enter__(self):
        self.t0 = _time.perf_counter()
        return self

    def __exit__(self, *a):
        self.dt = _time.perf_counter() - self.t0
        if self.label:
            print(f"[{self.label}] {self.dt:.2f}s")
        return False


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    out = ensure_ohlcv(df).resample(rule).agg(agg).dropna(subset=["close"])
    return out


def seed_all(seed: int = 42) -> None:
    import random

    random.seed(seed)
    np.random.seed(seed % (2 ** 32 - 1))
