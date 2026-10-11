"""Candlestick entry triggers at ICT levels, gated by the proven pullback trend filter.

Combines three layers:
  1. Trend filter (from the winning XAUUSD pullback backtest, +310.8% / Sharpe 1.45):
     triple-EMA 9/21/50 alignment + ADX(14) > 22.
  2. ICT levels (from docs/ict_smc_mining.md):
     - Fair Value Gaps: 3-candle definition (c1.high < c3.low = bullish gap).
       Only FRESH gaps are tradeable; a gap dies on a body close through it.
     - Order blocks: last opposite-color candle before a displacement candle
       (body > 1.0x ATR breaking the prior 5-bar extreme).
     - Liquidity sweeps: wick beyond the 20-bar swing extreme with a close
       back inside (turtle-soup footprint).
     - Premium/discount: 50% of the trailing 50-bar dealing range.
  3. Candlestick triggers (must print AT an ICT level, never mid-range):
     - bullish/bearish engulfing
     - pin bar / hammer (rejection wick > 2x body)
     - doji at level + confirmation candle next bar
     - inside-bar breakout in the trend direction

Entry: next-bar open after the signal bar closes. No counter-trend entries.
Stop: tighter of (pattern extreme +/- buffer) or 1.2x ATR.
Target: 2x risk (1:2 R:R), matching the winning pullback profile.

No lookahead: every quantity used at bar t is computed from bars <= t only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .base import BaseStrategy


# ---------------------------------------------------------------------------
# Indicator helpers (all causal: value at t uses data <= t)
# ---------------------------------------------------------------------------

def _ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(n, min_periods=1).mean()


def _adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    up = high.diff()
    dn = -low.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat(
        [(high - low), (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
        axis=1,
    ).max(axis=1)
    atr_s = pd.Series(tr, index=df.index).rolling(n, min_periods=1).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).rolling(n, min_periods=1).mean() / atr_s.replace(0, np.nan)
    minus_di = 100 * pd.Series(minus_dm, index=df.index).rolling(n, min_periods=1).mean() / atr_s.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.rolling(n, min_periods=1).mean().fillna(0.0)


# ---------------------------------------------------------------------------
# ICT level detectors (event-based, causal)
# ---------------------------------------------------------------------------

def detect_fvgs(df: pd.DataFrame, max_age_bars: int = 48) -> list[dict]:
    """Bullish FVG: candle[i-2].high < candle[i].low (3-candle gap).

    Returns list of dicts: {dir, top, bottom, born(bar idx), dead(bar idx or None)}.
    A gap dies when a later candle's body closes through it.
    """
    o, h, l, c = df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy()
    n = len(df)
    fvgs: list[dict] = []
    for i in range(2, n):
        # bullish gap: prior candle's high below current candle's low
        if h[i - 2] < l[i]:
            fvgs.append({"dir": 1, "top": l[i], "bottom": h[i - 2], "born": i, "dead": None})
        # bearish gap: prior candle's low above current candle's high
        elif l[i - 2] > h[i]:
            fvgs.append({"dir": -1, "top": l[i - 2], "bottom": h[i], "born": i, "dead": None})
    # kill gaps on body close through, expire by age
    for g in fvgs:
        for j in range(g["born"] + 1, n):
            if g["dir"] == 1 and c[j] < g["bottom"]:
                g["dead"] = j
                break
            if g["dir"] == -1 and c[j] > g["top"]:
                g["dead"] = j
                break
            if j - g["born"] > max_age_bars:
                g["dead"] = j
                break
    return fvgs


def detect_order_blocks(df: pd.DataFrame, atr: pd.Series, max_age_bars: int = 48) -> list[dict]:
    """Order block = last opposite-color candle before a displacement candle.

    Displacement: body > 1.0x ATR and break of the prior 5-bar extreme.
    """
    o, h, l, c = df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy()
    a = atr.to_numpy()
    n = len(df)
    obs: list[dict] = []
    for i in range(6, n):
        body = abs(c[i] - o[i])
        if body < 1.0 * a[i]:
            continue
        broke_high = h[i] > np.max(h[i - 5:i])
        broke_low = l[i] < np.min(l[i - 5:i])
        if not (broke_high or broke_low):
            continue
        # last opposite candle before displacement
        for k in range(i - 1, max(i - 6, 0), -1):
            bull_k = c[k] > o[k]
            if broke_high and not bull_k:  # bearish candle before up-displacement
                obs.append({"dir": 1, "top": h[k], "bottom": l[k], "born": i, "dead": None})
                break
            if broke_low and bull_k:  # bullish candle before down-displacement
                obs.append({"dir": -1, "top": h[k], "bottom": l[k], "born": i, "dead": None})
                break
    for g in obs:
        for j in range(g["born"] + 1, n):
            if g["dir"] == 1 and c[j] < g["bottom"]:
                g["dead"] = j
                break
            if g["dir"] == -1 and c[j] > g["top"]:
                g["dead"] = j
                break
            if j - g["born"] > max_age_bars:
                g["dead"] = j
                break
    return obs


def detect_sweeps(df: pd.DataFrame, lookback: int = 20, max_age_bars: int = 12) -> list[dict]:
    """Liquidity sweep: wick beyond trailing `lookback`-bar swing extreme,
    close back inside. Returns the swept level as a fresh demand/supply zone.
    """
    h, l, c = df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy()
    n = len(df)
    sweeps: list[dict] = []
    for i in range(lookback, n):
        swing_high = np.max(h[i - lookback:i])
        swing_low = np.min(l[i - lookback:i])
        # sweep of lows: wick below, close back above
        if l[i] < swing_low and c[i] > swing_low:
            sweeps.append({"dir": 1, "level": swing_low, "born": i, "wick": l[i]})
        # sweep of highs: wick above, close back below
        elif h[i] > swing_high and c[i] < swing_high:
            sweeps.append({"dir": -1, "level": swing_high, "born": i, "wick": h[i]})
    return [s for s in sweeps if True]  # age filtering done at query time


def active_levels_at(fvgs, obs, sweeps, bar: int, sweep_age: int = 12, tol_atr: float = 0.25,
                     atr_val: float = 1.0) -> dict:
    """Collect ICT levels alive at `bar`. Returns dict of demand/supply zones.

    Each zone: (low, high). Demand zones support longs, supply zones shorts.
    Sweeps are treated as point levels with a small tolerance band.
    """
    demand: list[tuple[float, float]] = []
    supply: list[tuple[float, float]] = []
    tol = tol_atr * atr_val
    for g in fvgs:
        if g["born"] <= bar and (g["dead"] is None or g["dead"] > bar):
            (demand if g["dir"] == 1 else supply).append((g["bottom"], g["top"]))
    for g in obs:
        if g["born"] <= bar and (g["dead"] is None or g["dead"] > bar):
            (demand if g["dir"] == 1 else supply).append((g["bottom"], g["top"]))
    for s in sweeps:
        if bar - sweep_age <= s["born"] <= bar:
            if s["dir"] == 1:
                demand.append((s["level"] - tol, s["level"] + tol))
            else:
                supply.append((s["level"] - tol, s["level"] + tol))
    return {"demand": demand, "supply": supply}


def touches(price_low: float, price_high: float, zones: list[tuple[float, float]]) -> bool:
    """True if the candle's range overlaps any zone."""
    for zlo, zhi in zones:
        if price_low <= zhi and price_high >= zlo:
            return True
    return False


# ---------------------------------------------------------------------------
# Candlestick patterns (each evaluated on data <= signal bar t)
# ---------------------------------------------------------------------------

def _body(o, c):
    return abs(c - o)


def bullish_engulfing(o, h, l, c, t: int) -> bool:
    if t < 1:
        return False
    prev_bear = c[t - 1] < o[t - 1]
    curr_bull = c[t] > o[t]
    return prev_bear and curr_bull and c[t] >= o[t - 1] and o[t] <= c[t - 1]


def bearish_engulfing(o, h, l, c, t: int) -> bool:
    if t < 1:
        return False
    prev_bull = c[t - 1] > o[t - 1]
    curr_bear = c[t] < o[t]
    return prev_bull and curr_bear and c[t] <= o[t - 1] and o[t] >= c[t - 1]


def bullish_pin(o, h, l, c, t: int) -> bool:
    rng = h[t] - l[t]
    if rng <= 0:
        return False
    body = _body(o[t], c[t])
    lower_wick = min(o[t], c[t]) - l[t]
    # long lower wick (>2x body), body in upper half
    return lower_wick > 2.0 * body and (max(o[t], c[t]) - l[t]) / rng > 0.6 and body / rng < 0.4


def bearish_pin(o, h, l, c, t: int) -> bool:
    rng = h[t] - l[t]
    if rng <= 0:
        return False
    body = _body(o[t], c[t])
    upper_wick = h[t] - max(o[t], c[t])
    return upper_wick > 2.0 * body and (h[t] - min(o[t], c[t])) / rng > 0.6 and body / rng < 0.4


def _is_doji(o, h, l, c, t: int) -> bool:
    rng = h[t] - l[t]
    return rng > 0 and _body(o[t], c[t]) / rng < 0.1


def bullish_doji_confirm(o, h, l, c, t: int) -> bool:
    """Doji at t-1, bullish confirmation close at t."""
    if t < 1:
        return False
    return _is_doji(o, h, l, c, t - 1) and c[t] > o[t] and c[t] > c[t - 1]


def bearish_doji_confirm(o, h, l, c, t: int) -> bool:
    if t < 1:
        return False
    return _is_doji(o, h, l, c, t - 1) and c[t] < o[t] and c[t] < c[t - 1]


def bullish_inside_break(o, h, l, c, t: int) -> bool:
    """Mother bar t-2, inside bar t-1, breakout close above mother high at t."""
    if t < 2:
        return False
    mother_rng = h[t - 2] - l[t - 2]
    if mother_rng <= 0:
        return False
    inside = h[t - 1] <= h[t - 2] and l[t - 1] >= l[t - 2]
    # inside bar should be meaningful, not dust
    meaningful = (h[t - 1] - l[t - 1]) / mother_rng > 0.25
    breakout = c[t] > h[t - 2]
    return inside and meaningful and breakout


def bearish_inside_break(o, h, l, c, t: int) -> bool:
    if t < 2:
        return False
    mother_rng = h[t - 2] - l[t - 2]
    if mother_rng <= 0:
        return False
    inside = h[t - 1] <= h[t - 2] and l[t - 1] >= l[t - 2]
    meaningful = (h[t - 1] - l[t - 1]) / mother_rng > 0.25
    breakout = c[t] < l[t - 2]
    return inside and meaningful and breakout


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------

class CandleICTEntries(BaseStrategy):
    """Candlestick triggers at ICT levels, trend-filtered.

    Signal convention: +1 long, -1 short, 0 flat (signal bar t).
    The backtest harness enters at the open of t+1.
    Frame columns: signal, stop_dist (in price), pattern (name), level (str).
    """

    name = "CandleICTEntries"
    kind = "candle_ict"
    default_params = {
        "ema_fast": 9,
        "ema_mid": 21,
        "ema_slow": 50,
        "adx_n": 14,
        "adx_min": 22,
        "atr_n": 14,
        "atr_stop_mult": 1.2,
        "rr_target": 2.0,
        "fvg_max_age": 48,
        "ob_max_age": 48,
        "sweep_lookback": 20,
        "sweep_max_age": 12,
        "range_lookback": 50,   # dealing-range for premium/discount
        "stop_buffer_atr": 0.1,  # buffer beyond pattern extreme
    }

    def __init__(self, **overrides):
        self.params = dict(self.default_params)
        for k, v in overrides.items():
            if k in self.params:
                self.params[k] = v

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        n = len(df)
        o = df["open"].to_numpy(dtype=float)
        h = df["high"].to_numpy(dtype=float)
        l = df["low"].to_numpy(dtype=float)
        c = df["close"].to_numpy(dtype=float)

        ema_f = _ema(df["close"], p["ema_fast"])
        ema_m = _ema(df["close"], p["ema_mid"])
        ema_s = _ema(df["close"], p["ema_slow"])
        adx = _adx(df, p["adx_n"])
        atr = _atr(df, p["atr_n"])
        atr_v = atr.to_numpy(dtype=float)

        fvgs = detect_fvgs(df, max_age_bars=p["fvg_max_age"])
        obs = detect_order_blocks(df, atr, max_age_bars=p["ob_max_age"])
        sweeps = detect_sweeps(df, lookback=p["sweep_lookback"])

        sig = np.zeros(n)
        stop_dist = np.full(n, np.nan)
        pattern = np.array([""] * n, dtype=object)
        level = np.array([""] * n, dtype=object)

        bull_trend = (ema_f > ema_m) & (ema_m > ema_s)
        bear_trend = (ema_f < ema_m) & (ema_m < ema_s)
        adx_ok = adx > p["adx_min"]

        for t in range(60, n):  # warmup for indicators/levels
            lv = active_levels_at(fvgs, obs, sweeps, t,
                                  sweep_age=p["sweep_max_age"],
                                  atr_val=atr_v[t])
            # dealing range for premium/discount discipline
            rh = np.max(h[max(0, t - p["range_lookback"]):t + 1])
            rl = np.min(l[max(0, t - p["range_lookback"]):t + 1])
            eq = 0.5 * (rh + rl)
            in_discount = l[t] < eq
            in_premium = h[t] > eq

            if bool(bull_trend.iloc[t]) and bool(adx_ok.iloc[t]):
                if not touches(l[t], h[t], lv["demand"]) or not in_discount:
                    continue
                trig, pname, pext = None, "", np.nan
                if bullish_engulfing(o, h, l, c, t):
                    trig, pname, pext = 1, "bull_engulf", l[t]
                elif bullish_pin(o, h, l, c, t):
                    trig, pname, pext = 1, "bull_pin", l[t]
                elif bullish_doji_confirm(o, h, l, c, t):
                    trig, pname, pext = 1, "bull_doji_conf", min(l[t], l[t - 1])
                elif bullish_inside_break(o, h, l, c, t):
                    trig, pname, pext = 1, "bull_inside_brk", l[t - 2]
                if trig:
                    lvl = self._level_tag(l[t], h[t], fvgs, obs, sweeps, t, atr_v[t], 1)
                    entry_ref = c[t]
                    pat_stop = entry_ref - (entry_ref - pext) - p["stop_buffer_atr"] * atr_v[t]
                    atr_stop = entry_ref - p["atr_stop_mult"] * atr_v[t]
                    # tighter of the two (larger price = tighter for longs)
                    stop_px = max(pat_stop, atr_stop)
                    sd = entry_ref - stop_px
                    if sd > 0 and atr_v[t] > 0:
                        sig[t] = 1
                        stop_dist[t] = sd
                        pattern[t] = pname
                        level[t] = lvl

            elif bool(bear_trend.iloc[t]) and bool(adx_ok.iloc[t]):
                if not touches(l[t], h[t], lv["supply"]) or not in_premium:
                    continue
                trig, pname, pext = None, "", np.nan
                if bearish_engulfing(o, h, l, c, t):
                    trig, pname, pext = -1, "bear_engulf", h[t]
                elif bearish_pin(o, h, l, c, t):
                    trig, pname, pext = -1, "bear_pin", h[t]
                elif bearish_doji_confirm(o, h, l, c, t):
                    trig, pname, pext = -1, "bear_doji_conf", max(h[t], h[t - 1])
                elif bearish_inside_break(o, h, l, c, t):
                    trig, pname, pext = -1, "bear_inside_brk", h[t - 2]
                if trig:
                    lvl = self._level_tag(l[t], h[t], fvgs, obs, sweeps, t, atr_v[t], -1)
                    entry_ref = c[t]
                    pat_stop = entry_ref + (pext - entry_ref) + p["stop_buffer_atr"] * atr_v[t]
                    atr_stop = entry_ref + p["atr_stop_mult"] * atr_v[t]
                    stop_px = min(pat_stop, atr_stop)
                    sd = stop_px - entry_ref
                    if sd > 0 and atr_v[t] > 0:
                        sig[t] = -1
                        stop_dist[t] = sd
                        pattern[t] = pname
                        level[t] = lvl

        return pd.DataFrame(
            {"signal": sig, "stop_dist": stop_dist, "pattern": pattern, "level": level},
            index=df.index,
        )

    @staticmethod
    def _level_tag(lo, hi, fvgs, obs, sweeps, t, atr_v, direction) -> str:
        tol = 0.25 * atr_v
        for g in fvgs:
            if g["dir"] == direction and g["born"] <= t and (g["dead"] is None or g["dead"] > t):
                if lo <= g["top"] and hi >= g["bottom"]:
                    return "fvg"
        for g in obs:
            if g["dir"] == direction and g["born"] <= t and (g["dead"] is None or g["dead"] > t):
                if lo <= g["top"] and hi >= g["bottom"]:
                    return "ob"
        for s in sweeps:
            if s["dir"] == direction and t - 12 <= s["born"] <= t:
                if lo <= s["level"] + tol and hi >= s["level"] - tol:
                    return "sweep"
        return "premium_discount"

    def describe(self) -> dict:
        return {"name": self.name, "kind": self.kind, "params": dict(self.params)}
