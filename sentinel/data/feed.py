"""Market data: synthetic generator, CSV/yfinance/CCXT loaders, resampling, quality gates."""
from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

from ..utils.helpers import ensure_ohlcv


def make_synthetic(n: int = 2000, seed: int = 42, start: str = "2022-01-01",
                   freq: str = "h", regimes: bool = True) -> pd.DataFrame:
    """Regime-switching geometric random walk with realistic OHLCV microstructure."""
    rng = np.random.default_rng(seed)
    if regimes and n >= 300:
        cuts = np.linspace(0, n, 7).astype(int)
        drifts = [0.0012, -0.0004, 0.0002, 0.0018, -0.0011, 0.0005]
        vols = [0.008, 0.016, 0.006, 0.011, 0.022, 0.009]
        rets = np.zeros(n)
        for i in range(6):
            a, b = cuts[i], cuts[i + 1]
            rets[a:b] = drifts[i] + rng.normal(0, vols[i], b - a)
    else:
        rets = 0.0004 + rng.normal(0, 0.01, n)
    close = 100.0 * np.exp(np.cumsum(rets))
    noise_o = rng.normal(0, 0.0015, n)
    open_ = close * (1 + noise_o)
    spread = np.abs(rng.normal(0.0, 0.004, n))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    base_vol = 5000 + 3000 * np.abs(rets) / (np.abs(rets).mean() + 1e-9)
    vol = np.abs(base_vol + rng.normal(0, 800, n))
    idx = pd.date_range(start, periods=n, freq=freq)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol}, index=idx)


def load_csv(path: str | pathlib.Path, ts_col: str = "timestamp") -> pd.DataFrame:
    df = pd.read_csv(path)
    if ts_col in df.columns:
        df[ts_col] = pd.to_datetime(df[ts_col])
        df = df.set_index(ts_col)
    df.columns = [str(c).lower() for c in df.columns]
    rename = {}
    for c in ("open", "high", "low", "close", "volume"):
        for col in df.columns:
            if col.startswith(c):
                rename[col] = c
    df = df.rename(columns=rename)
    return ensure_ohlcv(df)


def load_yfinance(symbol: str, period: str = "2y", interval: str = "1h") -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError("yfinance not installed: pip install yfinance") from e
    raw = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if raw is None or len(raw) == 0:
        raise ValueError(f"no data for {symbol}")
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0].lower() for c in raw.columns]
    else:
        raw.columns = [str(c).lower() for c in raw.columns]
    return ensure_ohlcv(raw)


def load_ccxt(symbol: str, timeframe: str = "1h", limit: int = 2000, exchange: str = "binance") -> pd.DataFrame:
    try:
        import ccxt
    except ImportError as e:
        raise ImportError("ccxt not installed: pip install ccxt") from e
    ex = getattr(ccxt, exchange)({"enableRateLimit": True})
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return ensure_ohlcv(df.set_index("timestamp"))


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    return ensure_ohlcv(df).resample(rule).agg(agg).dropna(subset=["close"])


def quality_report(df: pd.DataFrame) -> dict:
    df = ensure_ohlcv(df)
    idx = df.index
    out = {"bars": len(df), "start": str(idx[0]), "end": str(idx[-1])}
    if isinstance(idx, pd.DatetimeIndex) and len(idx) > 2:
        deltas = idx.to_series().diff().dropna()
        mode = deltas.mode()
        step = mode.iloc[0] if len(mode) else deltas.median()
        gaps = int((deltas > step * 2.5).sum()) if step and step > pd.Timedelta(0) else 0
        out["expected_step"] = str(step)
        out["gaps"] = gaps
    else:
        out["gaps"] = 0
    out["duplicates"] = int(idx.duplicated().sum())
    out["missing_cells"] = int(df[["open", "high", "low", "close"]].isna().sum().sum())
    bad = ((df["high"] < df["low"]) | (df["high"] < df["close"]) | (df["low"] > df["close"])).sum()
    out["bad_ohlc"] = int(bad)
    rets = df["close"].pct_change().abs()
    out["outlier_bars"] = int((rets > 0.25).sum())
    out["zero_volume_frac"] = float((df["volume"] <= 0).mean())
    return out


def clean_ohlcv(df: pd.DataFrame, max_gap_bars: int = 5) -> pd.DataFrame:
    df = ensure_ohlcv(df).copy()
    df.loc[df["high"] < df[["open", "low", "close"]].max(axis=1), "high"] = \
        df[["open", "low", "close"]].max(axis=1)
    df.loc[df["low"] > df[["open", "high", "close"]].min(axis=1), "low"] = \
        df[["open", "high", "close"]].min(axis=1)
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.asfreq(pd.infer_freq(df.index) or "h")
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].ffill(limit=max_gap_bars)
        df["volume"] = df["volume"].fillna(0.0)
        df = df.dropna(subset=["close"])
    return ensure_ohlcv(df)


def session_filter(df: pd.DataFrame, open: str = "09:30", close: str = "16:00") -> pd.DataFrame:
    """Keep only bars inside a daily session window (equities-style)."""
    df = ensure_ohlcv(df)
    if not isinstance(df.index, pd.DatetimeIndex):
        return df
    t = df.index.time
    from datetime import time as dtime
    oh, om = [int(x) for x in open.split(":")]
    ch, cm = [int(x) for x in close.split(":")]
    mask = [(dtime(oh, om) <= x <= dtime(ch, cm)) for x in t]
    return ensure_ohlcv(df.loc[mask])


def split_embargo(df: pd.DataFrame, test_frac: float = 0.25, embargo_bars: int = 20):
    """Chronological split with embargo gap to stop leakage."""
    df = ensure_ohlcv(df)
    n = len(df)
    cut = int(n * (1 - test_frac))
    train = df.iloc[:cut]
    test = df.iloc[cut + embargo_bars:]
    return train, test


def multi_timeframe(df: pd.DataFrame, rules=("4h", "1D")) -> dict:
    out = {"base": ensure_ohlcv(df)}
    for r in rules:
        try:
            out[r] = resample(df, r)
        except Exception:
            continue
    return out
