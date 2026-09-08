"""Adaptive parameter control: volatility breathing, quantile gates, rate tuning."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils.helpers import clamp, rolling_quantile


class VolatilityBreath:
    """Maps realized volatility to a lookback scale in [smin, smax]."""

    def __init__(self, vol_window: int = 50, median_window: int = 300,
                 smin: float = 0.5, smax: float = 2.0):
        self.vol_window = vol_window
        self.median_window = median_window
        self.smin = smin
        self.smax = smax

    def scale(self, close: pd.Series) -> pd.Series:
        rets = close.astype(float).pct_change().fillna(0.0)
        vol = rets.rolling(self.vol_window, min_periods=10).std().bfill().ffill().fillna(1e-9)
        med = vol.rolling(self.median_window, min_periods=20).median().bfill().ffill().fillna(1e-9)
        return ((vol / (med + 1e-12)).clip(self.smin, self.smax)).fillna(1.0)

    def dynamic_period(self, close: pd.Series, base: int, lo: int = 2, hi: int = 500) -> pd.Series:
        s = self.scale(close)
        return ((s * base).round().clip(lo, hi)).astype(int)


class QuantileGate:
    """Self-calibrating entry/exit gates from rolling quantiles."""

    def __init__(self, window: int = 300, hi_q: float = 0.8, lo_q: float = 0.2):
        self.window = window
        self.hi_q = hi_q
        self.lo_q = lo_q

    def bands(self, s: pd.Series):
        hi = rolling_quantile(s, self.hi_q, self.window)
        lo = rolling_quantile(s, self.lo_q, self.window)
        return hi, lo

    def position(self, s: pd.Series) -> pd.Series:
        """Position of each value inside its own adaptive band, in [-1, 1]."""
        hi, lo = self.bands(s)
        mid = (hi + lo) / 2.0
        half = ((hi - lo) / 2.0).replace(0, np.nan).bfill().ffill().fillna(1e-9)
        return (((s - mid) / (half + 1e-12)).clip(-1, 1)).fillna(0.0)


class SignalRateTuner:
    """Integral controller that holds a strategy near a target flip-rate.

    If a system over-trades, the gate multiplier rises (fewer trades);
    if it starves, the multiplier falls. Bounded and drift-safe.
    """

    def __init__(self, target_rate: float = 0.05, ki: float = 0.5,
                 lo: float = 0.25, hi: float = 4.0):
        self.target = target_rate
        self.ki = ki
        self.lo = lo
        self.hi = hi
        self.mult = 1.0

    def update(self, recent_signals: pd.Series) -> float:
        s = np.sign(np.asarray(recent_signals, dtype=float))
        if len(s) < 10:
            return self.mult
        flips = float(np.mean(np.abs(np.diff(s)) > 0))
        err = flips - self.target
        self.mult = clamp(self.mult * (1.0 + self.ki * err), self.lo, self.hi)
        return self.mult


class DrawdownThrottle:
    """Smooth exposure throttle from current drawdown depth."""

    def __init__(self, soft_dd: float = 0.05, hard_dd: float = 0.15):
        self.soft = abs(soft_dd)
        self.hard = abs(hard_dd)

    def factor(self, equity: pd.Series) -> float:
        eq = np.asarray(equity, dtype=float)
        if len(eq) < 2:
            return 1.0
        dd = float((eq[-1] - np.max(eq)) / (np.max(eq) + 1e-12))
        depth = abs(min(0.0, dd))
        if depth <= self.soft:
            return 1.0
        if depth >= self.hard:
            return 0.0
        span = self.hard - self.soft + 1e-12
        x = (depth - self.soft) / span
        return float(0.5 + 0.5 * np.cos(np.pi * x))
