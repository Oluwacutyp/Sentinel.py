#!/usr/bin/env python3
"""Factor-ablation backtest for the GOD Conviction Engine.

A faithful-but-honest Python twin of the Pine engine's entry/exit core:

  * signals computed on the confirmed bar, FILLED AT THE NEXT BAR'S OPEN
    (the Pine indicator assumes close-fills; that is optimistic, so we don't).
  * conservative intra-bar resolution: if stop and target are both inside a
    bar's range, the stop is assumed to fill first.
  * round-trip costs (spread + commission + slippage) in bps deducted from
    every round trip, plus an explicit slippage on fills.
  * the same risk machinery as the Pine script: 1% equity risk, swing-based
    stop capped at 2 ATR, TP1 = 1.5R (half off + break-even), TP2 = 3R,
    simplified Hydra trail + profit lock, beyond-FVG / trap / cost gates and
    the daily circuit breaker.

The seven confluence families mirror the Pine weights:
    T trend-stack (18) · H htf-bias (15) · S liquidity-sweep (25)
    Z zones: OB tap / beyond-FVG reclaim / iFVG / bait-penalty (22)
    P premium-discount (8) · O oscillators (8) · D traps (15)

No parameter is optimized here: everything ships at the Pine defaults.
Usage:
    python scripts/factor_ablation.py data/btcusd_daily.csv --freq D
    python scripts/factor_ablation.py data/xauusd_h1.csv   --freq h
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np
import pandas as pd

# ────────────────────────────── defaults (Pine values) ──────────────────────
W = dict(T=18.0, H=15.0, S=25.0, Z=22.0, P=8.0, O=8.0, D=15.0)
THRESHOLD = 70.0
MIN_FACTORS = 4
RISK_PCT = 0.01
SL_ATR_BUF = 1.0
SL_CAP_ATR = 2.0
TP1_RR, TP2_RR = 1.5, 3.0
COST_BPS_RT = 4.0        # round-trip spread+commission+slippage
SLIP_BPS = 1.0           # extra directional slippage per fill
MIN_NET_RR = 0.6
TRAP_MEM = 12
FAKE_BRK_WIN = 6
ZONE_MAX_AGE = 120
MAX_ZONES = 5
CB_DAY_R, CB_MAX_TRADES = -3.0, 4
SWING_LEN = 20
EQUITY0 = 10_000.0

FAMS = ["T", "H", "S", "Z", "P", "O", "D"]


# ────────────────────────────── indicators ──────────────────────────────────
def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0.0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0.0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0.0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(),
                    (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def hma(close: pd.Series, n: int = 50) -> pd.Series:
    half = ema(close, max(n // 2, 1))
    full = ema(close, n)
    return ema(2 * half - full, max(int(math.sqrt(n)), 1))


def htf_bias(df: pd.DataFrame, rule: str) -> pd.Series:
    """True = higher-TF bullish, using only CLOSED htf bars (shifted)."""
    htf_close = df["close"].resample(rule).last()
    htf_ema = htf_close.ewm(span=50, adjust=False).mean()
    bull = (htf_close > htf_ema)
    aligned = bull.reindex(df.index, method="ffill").shift(1)
    return aligned.fillna(False)


# ────────────────────────────── precompute ──────────────────────────────────
def build(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    out = df.copy()
    c = out["close"]
    out["ema9"], out["ema21"] = ema(c, 9), ema(c, 21)
    out["ema50"], out["ema200"] = ema(c, 50), ema(c, 200)
    out["hma50"] = hma(c, 50)
    out["atr"] = atr(out)
    out["rsi"] = rsi(c)
    macd = ema(c, 12) - ema(c, 26)
    out["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()
    out["vol_sma"] = out["volume"].rolling(20).mean()
    # swings of the PRIOR 20 bars (liquidity resting above/below)
    out["swing_lo"] = out["low"].rolling(SWING_LEN).min().shift(1)
    out["swing_hi"] = out["high"].rolling(SWING_LEN).max().shift(1)
    # premium/discount over rolling 100-bar range
    hh, ll = c.rolling(100).max(), c.rolling(100).min()
    out["in_discount"] = c <= (hh + ll) / 2
    out["in_premium"] = c >= (hh + ll) / 2
    out["swing5_lo"] = out["low"].rolling(5).min()
    out["swing5_hi"] = out["high"].rolling(5).max()
    rule1 = "4D" if freq == "D" else "4h"
    rule2 = "16D" if freq == "D" else "1D"
    out["htf1_bull"] = htf_bias(out, rule1)
    out["htf1_bear"] = htf_bias(out, rule1) == False  # noqa: E712
    out["htf2_bull"] = htf_bias(out, rule2)
    out["htf2_bear"] = htf_bias(out, rule2) == False  # noqa: E712
    out["day"] = out.index.normalize()
    return out


# ────────────────────────────── engine ──────────────────────────────────────
class Zone:
    __slots__ = ("top", "bot", "bar")

    def __init__(self, top, bot, bar):
        self.top, self.bot, self.bar = top, bot, bar


def run(df: pd.DataFrame, enabled: set[str], thresh: float = THRESHOLD,
        minf: int = MIN_FACTORS) -> dict:
    o, h, l, c = df["open"].values, df["high"].values, df["low"].values, df["close"].values
    v = df["volume"].values
    A = df["atr"].values
    rsi_v = df["rsi"].values
    mh = df["macd_hist"].values
    vsma = df["vol_sma"].values
    slo, shi = df["swing_lo"].values, df["swing_hi"].values
    s5lo, s5hi = df["swing5_lo"].values, df["swing5_hi"].values
    disc, prem = df["in_discount"].values, df["in_premium"].values
    h1b, h1s, h2b, h2s = (df["htf1_bull"].values, df["htf1_bear"].values,
                          df["htf2_bull"].values, df["htf2_bear"].values)
    e9, e21, e50, e200, hm = (df["ema9"].values, df["ema21"].values, df["ema50"].values,
                              df["ema200"].values, df["hma50"].values)
    days = df["day"].values
    n = len(df)
    WARM = 220

    equity = EQUITY0
    peak_eq, max_dd = equity, 0.0
    pos = None            # dict: dir, entry, sl, qty, riskR, tp1, tp2, tp1done
    pending = 0           # +1 long / -1 short to fill at next open
    bull_ob, bear_ob, bull_fvg, bear_fvg = [], [], [], []
    ifvg_sup, ifvg_dem = [], []
    bfg_state, bfg_bot, bfg_top, bfg_bar = 0, np.nan, np.nan, -10**9
    rfg_state, rfg_top, rfg_bot, rfg_bar = 0, np.nan, np.nan, -10**9
    bull_trap_bar, bear_trap_bar = -10**9, -10**9
    bull_trap_eng, bear_trap_eng = False, False
    brk_up_bar, brk_up_lvl = -10**9, np.nan
    brk_dn_bar, brk_dn_lvl = -10**9, np.nan
    day_key, day_r, trades_today = None, 0.0, 0
    trades, eq_curve = [], []
    pend_why = ""

    def close_trade(i, px, qty, note):
        nonlocal equity, peak_eq, max_dd
        gross = (px - pos["entry"]) * qty if pos["dir"] == 1 else (pos["entry"] - px) * qty
        cost = pos["entry"] * qty * COST_BPS_RT / 10000.0
        pnl = gross - cost
        equity += pnl
        peak_eq = max(peak_eq, equity)
        max_dd = max(max_dd, (peak_eq - equity) / peak_eq)
        r_mult = pnl / max(pos["risk0"], 1e-9)
        trades.append({"bar": i, "dir": pos["dir"], "r": r_mult, "pnl": pnl,
                       "note": note, "day": days[i]})
        return r_mult

    for i in range(WARM, n):
        # daily circuit-breaker reset
        if days[i] != day_key:
            day_key, day_r, trades_today = days[i], 0.0, 0
        if np.isnan(A[i]):
            eq_curve.append(equity)
            continue

        # ── 1. fill pending entry at this bar's open ──
        if pending != 0 and pos is None:
            slip = o[i] * SLIP_BPS / 10000.0
            entry = o[i] + slip if pending == 1 else o[i] - slip
            if pending == 1:
                sl = max(s5lo[i] - SL_ATR_BUF * A[i], entry - SL_CAP_ATR * A[i])
                risk = entry - sl
            else:
                sl = min(s5hi[i] + SL_ATR_BUF * A[i], entry + SL_CAP_ATR * A[i])
                risk = sl - entry
            if risk > 0 and not math.isnan(sl):
                qty = (equity * RISK_PCT) / risk
                pos = {"dir": pending, "entry": entry, "sl": sl, "qty": qty,
                       "risk_amt": equity * RISK_PCT,
                       "tp1": entry + pending * risk * TP1_RR,
                       "tp2": entry + pending * risk * TP2_RR,
                       "tp1done": False, "peak_r": 0.0, "why": pend_why,
                       "ebar": i, "risk0": equity * RISK_PCT}
                trades_today += 1
            pending = 0

        # ── 2. manage the open position on this bar ──
        if pos is not None:
            d, hi, lo = pos["dir"], h[i], l[i]
            cur_r = ((c[i] - pos["entry"]) * d) / (pos["risk_amt"] / pos["qty"])
            pos["peak_r"] = max(pos["peak_r"], cur_r)
            exited = False
            # gap through the stop → fill at the open (worse than stop price)
            if (d == 1 and o[i] <= pos["sl"]) or (d == -1 and o[i] >= pos["sl"]):
                r_mult = close_trade(i, o[i], pos["qty"], "gap-stop")
                day_r += r_mult
                pos, exited = None, True
            # stop first (conservative), then targets
            if not exited and ((d == 1 and lo <= pos["sl"]) or (d == -1 and hi >= pos["sl"])):
                note = "be-stop" if (d == 1 and pos["sl"] >= pos["entry"]) or \
                       (d == -1 and pos["sl"] <= pos["entry"]) else "stop"
                r_mult = close_trade(i, pos["sl"], pos["qty"], note)
                day_r += r_mult
                pos, exited = None, True
            if not exited and pos is not None and not pos["tp1done"] and \
               ((d == 1 and hi >= pos["tp1"]) or (d == -1 and lo <= pos["tp1"])):
                # half off at TP1, stop to break-even
                half = pos["qty"] / 2
                r_mult = close_trade(i, pos["tp1"], half, "tp1")
                day_r += 0.5 * r_mult
                pos["qty"] -= half
                pos["risk_amt"] /= 2
                pos["sl"] = pos["entry"]
                pos["tp1done"] = True
            if not exited and pos is not None and \
               ((d == 1 and hi >= pos["tp2"]) or (d == -1 and lo <= pos["tp2"])):
                r_mult = close_trade(i, pos["tp2"], pos["qty"], "tp2")
                day_r += r_mult
                pos, exited = None, True
            # simplified Hydra trail on remaining runner
            if pos is not None and pos["tp1done"]:
                if pos["peak_r"] >= 1.5:
                    lock = pos["entry"] + pos["dir"] * (pos["peak_r"] - 0.5) * \
                           (pos["risk_amt"] / pos["qty"])
                    pos["sl"] = max(pos["sl"], lock) if pos["dir"] == 1 else min(pos["sl"], lock)
                else:
                    trail = c[i] - pos["dir"] * 1.2 * A[i]
                    pos["sl"] = max(pos["sl"], trail) if pos["dir"] == 1 else \
                                min(pos["sl"], trail)
        eq_curve.append(equity)

        # ── 3. zone bookkeeping (OB / FVG / iFVG) ──
        if i >= 2:
            imp_th = 1.2 * A[i]
            if (c[i - 1] - o[i - 1]) > imp_th and c[i - 1] > h[i - 2] and c[i - 2] < o[i - 2]:
                bull_ob.append(Zone(h[i - 1], l[i - 1], i))
                if len(bull_ob) > MAX_ZONES:
                    bull_ob.pop(0)
            if (o[i - 1] - c[i - 1]) > imp_th and c[i - 1] < l[i - 2] and c[i - 2] > o[i - 2]:
                bear_ob.append(Zone(l[i - 1], h[i - 1], i))
                if len(bear_ob) > MAX_ZONES:
                    bear_ob.pop(0)
            fvg_min = 0.2 * A[i]
            if l[i] > h[i - 2] and (l[i] - h[i - 2]) >= fvg_min:
                bull_fvg.append(Zone(l[i], h[i - 2], i))
                if len(bull_fvg) > MAX_ZONES:
                    bull_fvg.pop(0)
            if h[i] < l[i - 2] and (l[i - 2] - h[i]) >= fvg_min:
                bear_fvg.append(Zone(l[i - 2], h[i], i))
                if len(bear_fvg) > MAX_ZONES:
                    bear_fvg.pop(0)

        b_ob_hit = b_fvg_hit = r_ob_hit = r_fvg_hit = False
        ifvg_sup_test = ifvg_dem_test = False
        bfg_sweep_ev = bfg_reclaim_ev = rfg_sweep_ev = rfg_reclaim_ev = False
        ifvg_flip_sup = ifvg_flip_dem = False
        bfg_full = rfg_full = False

        for z in [z for z in bull_ob]:
            if l[i] <= z.top and c[i] >= z.bot:
                b_ob_hit = True
            if c[i] < z.bot or i - z.bar > ZONE_MAX_AGE:
                bull_ob.remove(z)
        for z in [z for z in bear_ob]:
            if h[i] >= z.bot and c[i] <= z.top:
                r_ob_hit = True
            if c[i] > z.top or i - z.bar > ZONE_MAX_AGE:
                bear_ob.remove(z)
        for z in [z for z in bull_fvg]:
            if l[i] <= z.top and c[i] >= z.bot:
                b_fvg_hit = True
            failed = c[i] < z.bot
            if failed or i - z.bar > ZONE_MAX_AGE:
                bull_fvg.remove(z)
                if failed:
                    ifvg_flip_sup = True
                    ifvg_sup.append(Zone(z.top, z.bot, i))
                    if len(ifvg_sup) > 4:
                        ifvg_sup.pop(0)
        for z in [z for z in bear_fvg]:
            if h[i] >= z.bot and c[i] <= z.top:
                r_fvg_hit = True
            failed = c[i] > z.top
            if failed or i - z.bar > ZONE_MAX_AGE:
                bear_fvg.remove(z)
                if failed:
                    ifvg_flip_dem = True
                    ifvg_dem.append(Zone(z.top, z.bot, i))
                    if len(ifvg_dem) > 4:
                        ifvg_dem.pop(0)
        for z in [z for z in ifvg_sup]:
            if h[i] >= z.bot and c[i] <= z.top and c[i] <= o[i]:
                ifvg_sup_test = True
            if c[i] > z.top or i - z.bar > ZONE_MAX_AGE:
                ifvg_sup.remove(z)
        for z in [z for z in ifvg_dem]:
            if l[i] <= z.top and c[i] >= z.bot and c[i] >= o[i]:
                ifvg_dem_test = True
            if c[i] < z.bot or i - z.bar > ZONE_MAX_AGE:
                ifvg_dem.remove(z)

        # beyond-FVG state machine (port of Pine section 16B)
        if "Z" in enabled:
            fresh_bull = [z for z in bull_fvg if i - z.bar <= ZONE_MAX_AGE] + \
                         ([Zone(bfg_top, bfg_bot, bfg_bar)] if bfg_state == 1 else [])
            for z in [z for z in bull_fvg]:
                if bfg_state == 0 and l[i] < z.bot and c[i] > z.bot:
                    bfg_state, bfg_bot, bfg_top, bfg_bar = 2, z.bot, z.top, i
                    bfg_full = c[i] > z.top
                    bfg_sweep_ev = bfg_reclaim_ev = True
                elif bfg_state == 0 and c[i] < z.bot:
                    bfg_state, bfg_bot, bfg_top, bfg_bar = 1, z.bot, z.top, i
                    bfg_sweep_ev = True
            if bfg_state == 1 and c[i] > bfg_bot:
                bfg_state, bfg_bar = 2, i
                bfg_full = c[i] > bfg_top
                bfg_reclaim_ev = True
            if bfg_state > 0 and i - bfg_bar > TRAP_MEM:
                bfg_state = 0
            for z in [z for z in bear_fvg]:
                if rfg_state == 0 and h[i] > z.top and c[i] < z.top:
                    rfg_state, rfg_top, rfg_bot, rfg_bar = 2, z.top, z.bot, i
                    rfg_full = c[i] < z.bot
                    rfg_sweep_ev = rfg_reclaim_ev = True
                elif rfg_state == 0 and c[i] > z.top:
                    rfg_state, rfg_top, rfg_bot, rfg_bar = 1, z.top, z.bot, i
                    rfg_sweep_ev = True
            if rfg_state == 1 and c[i] < rfg_top:
                rfg_state, rfg_bar = 2, i
                rfg_full = c[i] < rfg_bot
                rfg_reclaim_ev = True
            if rfg_state > 0 and i - rfg_bar > TRAP_MEM:
                rfg_state = 0

        inside_bull_fvg = any(c[i] >= z.bot and c[i] <= z.top for z in bull_fvg)
        inside_bear_fvg = any(c[i] >= z.bot and c[i] <= z.top for z in bear_fvg)
        bait_long = inside_bull_fvg and bfg_state != 2
        bait_short = inside_bear_fvg and rfg_state != 2

        # ── 4. sweeps & traps ──
        ssl_sweep = bsl_sweep = False
        bull_trap_now = bear_trap_now = False
        if not np.isnan(slo[i]) and not np.isnan(shi[i]):
            ssl_sweep = l[i] < slo[i] and c[i] > slo[i] and c[i] > o[i]
            bsl_sweep = h[i] > shi[i] and c[i] < shi[i] and c[i] < o[i]
            sfp_vol = v[i] > vsma[i] * 1.15 if not np.isnan(vsma[i]) else False
            bull_trap_now = bsl_sweep and sfp_vol
            bear_trap_now = ssl_sweep and sfp_vol
        # fake breakout tracking
        if not np.isnan(shi[i]) and c[i] > shi[i] and c[i - 1] <= shi[i]:
            brk_up_bar, brk_up_lvl = i, shi[i]
        if not np.isnan(slo[i]) and c[i] < slo[i] and c[i - 1] >= slo[i]:
            brk_dn_bar, brk_dn_lvl = i, slo[i]
        fake_up = fake_dn = False
        if i - brk_up_bar <= FAKE_BRK_WIN and not np.isnan(brk_up_lvl) and c[i] < brk_up_lvl:
            fake_up, brk_up_bar = True, -10**9
            bull_trap_bar = i
        if i - brk_dn_bar <= FAKE_BRK_WIN and not np.isnan(brk_dn_lvl) and c[i] > brk_dn_lvl:
            fake_dn, brk_dn_bar = True, -10**9
            bear_trap_bar = i
        if bull_trap_now:
            bull_trap_bar, bull_trap_eng = i, bsl_sweep
        if bear_trap_now:
            bear_trap_bar, bear_trap_eng = i, ssl_sweep
        bull_trap_active = i - bull_trap_bar <= TRAP_MEM
        bear_trap_active = i - bear_trap_bar <= TRAP_MEM
        brk_up_sus = (i == brk_up_bar) and (not np.isnan(vsma[i]) and v[i] < vsma[i])
        brk_dn_sus = (i == brk_dn_bar) and (not np.isnan(vsma[i]) and v[i] < vsma[i])

        # ── 5. confluence scoring ──
        bs, ss = 0.0, 0.0
        fb, fs = set(), set()
        if "T" in enabled:
            tb, ts2 = 0.0, 0.0
            if e9[i] > e21[i] > e50[i] and c[i] > e200[i]:
                tb += 12.0
            if e9[i] < e21[i] < e50[i] and c[i] < e200[i]:
                ts2 += 12.0
            if c[i] > hm[i]:
                tb += 6.0
            elif c[i] < hm[i]:
                ts2 += 6.0
            bs += tb; ss += ts2
            if tb > 0: fb.add("T")
            if ts2 > 0: fs.add("T")
        if "H" in enabled:
            hb, hs2 = 0.0, 0.0
            if h1b[i]: hb += 8.0
            if h2b[i]: hb += 7.0
            if h1s[i]: hs2 += 8.0
            if h2s[i]: hs2 += 7.0
            bs += min(hb, W["H"]); ss += min(hs2, W["H"])
            if hb > 0: fb.add("H")
            if hs2 > 0: fs.add("H")
        if "S" in enabled:
            volimb = (not np.isnan(vsma[i])) and v[i] > vsma[i] * 2.0
            if ssl_sweep:
                bs += 25.0 if volimb else 18.0
                fb.add("S")
            if bsl_sweep:
                ss += 25.0 if volimb else 18.0
                fs.add("S")
        if "Z" in enabled:
            if b_ob_hit:
                bs += 12.0; fb.add("Z")
            if r_ob_hit:
                ss += 12.0; fs.add("Z")
            if bfg_state == 2:
                bs += 15.0 if bfg_full else 11.0
                fb.add("Z")
            elif bait_long:
                bs -= 8.0
            if rfg_state == 2:
                ss += 15.0 if rfg_full else 11.0
                fs.add("Z")
            elif bait_short:
                ss -= 8.0
            if ifvg_dem_test:
                bs += 6.0; fb.add("Z")
            if ifvg_sup_test:
                ss += 6.0; fs.add("Z")
        if "P" in enabled:
            if disc[i]:
                bs += 8.0; fb.add("P")
            if prem[i]:
                ss += 8.0; fs.add("P")
        if "O" in enabled:
            ob_, os_ = 0.0, 0.0
            if mh[i] > 0: ob_ += 4.0
            if mh[i] < 0: os_ += 4.0
            if i >= 1 and mh[i] > 0 > mh[i - 1]: ob_ += 4.0
            elif rsi_v[i] < 45 and rsi_v[i] > rsi_v[i - 1]: ob_ += 2.0
            if i >= 1 and mh[i] < 0 < mh[i - 1]: os_ += 4.0
            elif rsi_v[i] > 55 and rsi_v[i] < rsi_v[i - 1]: os_ += 2.0
            bs += min(ob_, W["O"]); ss += min(os_, W["O"])
            if ob_ > 0: fb.add("O")
            if os_ > 0: fs.add("O")
        if "D" in enabled:
            if bear_trap_active:
                bs += 15.0 if bear_trap_eng else 10.0
                fb.add("D")
            if bull_trap_active:
                ss += 15.0 if bull_trap_eng else 10.0
                fs.add("D")

        bs = max(0.0, min(100.0, bs))
        ss = max(0.0, min(100.0, ss))

        # ── 6. entry gates ──
        cb_halt = day_r <= CB_DAY_R or trades_today >= CB_MAX_TRADES
        if pos is None and pending == 0 and not cb_halt:
            cost_px = c[i] * COST_BPS_RT / 10000.0
            buy_ok = bs >= thresh and len(fb) >= minf and \
                not bait_long and not brk_up_sus
            sell_ok = ss >= thresh and len(fs) >= minf and \
                not bait_short and not brk_dn_sus
            # cost gate (prospective)
            psl_l = max(s5lo[i] - SL_ATR_BUF * A[i], c[i] - SL_CAP_ATR * A[i])
            prk_l = max(c[i] - psl_l, 0.0)
            psl_s = min(s5hi[i] + SL_ATR_BUF * A[i], c[i] + SL_CAP_ATR * A[i])
            prk_s = max(psl_s - c[i], 0.0)
            if prk_l < cost_px * 2 or TP1_RR - cost_px / max(prk_l, 1e-9) < MIN_NET_RR:
                buy_ok = False
            if prk_s < cost_px * 2 or TP1_RR - cost_px / max(prk_s, 1e-9) < MIN_NET_RR:
                sell_ok = False
            if buy_ok and (not sell_ok or bs >= ss + 5.0):
                pending, pend_why = 1, "+".join(sorted(fb))
            elif sell_ok and (not buy_ok or ss >= bs + 5.0):
                pending, pend_why = -1, "+".join(sorted(fs))

    if pos is not None:  # mark-to-market at the end
        d = pos["dir"]
        px = c[-1]
        r_mult = close_trade(n - 1, px, pos["qty"], "eod-flatten")
        day_r += r_mult
        eq_curve[-1] = equity

    eq = pd.Series(eq_curve, index=df.index[WARM:])
    ret = equity / EQUITY0 - 1
    bh = c[-1] / c[WARM] - 1
    wr = 100 * sum(1 for t in trades if t["r"] > 0) / len(trades) if trades else 0.0
    wins = sum(t["r"] for t in trades if t["r"] > 0)
    losses = -sum(t["r"] for t in trades if t["r"] <= 0)
    pf = wins / losses if losses > 0 else float("inf") if wins > 0 else 0.0
    avg_r = float(np.mean([t["r"] for t in trades])) if trades else 0.0
    per_year = {}
    for t in trades:
        y = str(pd.Timestamp(t["day"]).year)
        per_year[y] = per_year.get(y, 0.0) + t["r"]
    return {"n": len(trades), "wr": wr, "pf": pf, "avg_r": avg_r, "ret": ret,
            "max_dd": max_dd, "bh": bh, "per_year": per_year, "equity": eq,
            "final_eq": equity, "trades": trades}


# ────────────────────────────── CLI ─────────────────────────────────────────
ABLATIONS = (
    [("FULL", set(FAMS))] +
    [(f"-{f}", set(FAMS) - {f}) for f in FAMS] +
    [("CORE-LIQ (S+Z+D)", {"S", "Z", "D"}),
     ("RETAIL (T+H+O)", {"T", "H", "O"})]
)


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [str(x).lower().strip() for x in df.columns]
    tcol = next((x for x in df.columns if x in ("datetime", "date", "timestamp")),
                df.columns[0])
    ts = pd.to_datetime(df[tcol], format="mixed", utc=True)
    df = df.drop(columns=[tcol])
    idx = pd.DatetimeIndex(ts)
    df.index = idx.tz_localize(None) if idx.tz is not None else idx
    df = df.sort_index()
    if len(df.columns) >= 5:
        df = df.iloc[:, :5]
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna()
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--freq", default="D", choices=["D", "h"])
    ap.add_argument("--report", default=None)
    ap.add_argument("--thresh", type=float, default=THRESHOLD,
                    help="confluence threshold (shipped default=70)")
    ap.add_argument("--minf", type=int, default=MIN_FACTORS,
                    help="min distinct factor families (shipped default=4)")
    args = ap.parse_args()

    raw = load(args.csv)
    df = build(raw, args.freq)
    rows = []
    for name, fams in ABLATIONS:
        r = run(df, fams, thresh=args.thresh, minf=args.minf)
        rows.append((name, r))
        print(f"{name:20s} trades={r['n']:4d}  WR={r['wr']:5.1f}%  "
              f"avgR={r['avg_r']:+.3f}  PF={r['pf']:5.2f}  "
              f"net={r['ret']*100:+8.1f}%  maxDD={r['max_dd']*100:5.1f}%  "
              f"(buy&hold {r['bh']*100:+.0f}%)")
    full = dict(rows)["FULL"]
    if full["n"]:
        print("\nFULL model realized R by year:")
        for y in sorted(full["per_year"]):
            print(f"  {y}: {full['per_year'][y]:+.2f}R")
        longs = [t for t in full["trades"] if t["dir"] == 1]
        shorts = [t for t in full["trades"] if t["dir"] == -1]
        for tag, side in (("LONG ", longs), ("SHORT", shorts)):
            if side:
                sr = sum(t["r"] for t in side)
                wr = 100 * sum(1 for t in side if t["r"] > 0) / len(side)
                print(f"  {tag}: {len(side):3d} trades  WR {wr:5.1f}%  sumR {sr:+.2f}  "
                      f"avgR {sr/len(side):+.3f}")
    if args.report:
        with open(args.report, "w") as f:
            f.write("| variant | trades | win% | avg R | PF | net % | maxDD % |\n|---|---|---|---|---|---|---|\n")
            for name, r in rows:
                f.write(f"| {name} | {r['n']} | {r['wr']:.1f} | {r['avg_r']:+.3f} | "
                        f"{r['pf']:.2f} | {r['ret']*100:+.1f} | {r['max_dd']*100:.1f} |\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
