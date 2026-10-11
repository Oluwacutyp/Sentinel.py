# XAUUSD Bot Backtest Results

**Date:** 2026-10-11
**Data:** GC=F hourly, 11,449 bars (2024-10-10 → 2026-10-09)
**Costs:** $0.35 spread + $0.10 slippage per trade
**Risk:** 1% per trade
**Method:** Next-bar open entry (no lookahead), SL/TP exits on intrabar high/low

---

## Bots Analyzed

| | v2.0 (`myxauusdbot__2__0_jsf5.py`) | v4.1 (`myxauusdbot__4__1_gn20.py`) |
|---|---|---|
| Lines | 19,794 | 21,900 |
| Strategies in main loop | 5 (trend, meanrev, breakout, pullback, smc) | 4 (trend, breakout, pullback, smc) |
| Key difference | — | **Mean reversion REMOVED from main loop** |

Both bots share the same core strategy logic. v4.1 dropped mean reversion — which our backtest confirms was the right call (it was the worst performer).

---

## Core Strategy Logic (extracted)

### 1. TREND (`TrendFollowingStrategy`)
- **BUY:** EMA9 > EMA21 AND ADX > 25 AND |close − EMA9| ≤ 1.2×ATR (pullback entry)
- **SELL:** EMA9 < EMA21 AND ADX > 25 AND |close − EMA9| ≤ 1.2×ATR
- **SL:** 1.5×ATR | **TP:** 3.0×ATR (1:2 RR)

### 2. MEANREV (`MeanReversionStrategy`)
- **BUY:** close ≤ BB_lower AND RSI < 30 AND ADX ≤ 30
- **SELL:** close ≥ BB_upper AND RSI > 70 AND ADX ≤ 30
- **SL:** 2×ATR | **TP:** 4×ATR (1:2 RR)

### 3. BREAKOUT (`BreakoutStrategy`)
- **BUY:** close > 20-bar high AND ADX > 25 AND BB_width < 0.01 (squeeze)
- **SELL:** close < 20-bar low AND ADX > 25 AND BB_width < 0.01
- **SL:** 3×ATR | **TP:** 6×ATR (1:2 RR)

### 4. PULLBACK (`PullbackRetracementStrategy`)
- **BUY:** EMA9 > EMA21 AND close > EMA9 AND close > EMA50 AND ADX > 22 AND price within pullback zone of EMA9
- **SELL:** mirror
- **SL:** 1.2×ATR | **TP:** 2.4×ATR (1:2 RR)

### 5. SMC (`SMCLiquidityStrategy`)
- **BUY:** uptrend (EMA9>EMA21, ADX>22) AND price retests 5-bar swing low AND bullish close
- **SELL:** mirror
- **SL:** 1.5×ATR | **TP:** 3.0×ATR (1:2 RR)

### Signal Combination
Bots use weighted voting: rule (0.4) + ML (0.3) + DRL (0.2) + macro (0.1). The ML/DRL/macro components require live infrastructure and were NOT backtested — only the rule-based core.

---

## Results

| Strategy | Trades | Win% | PF | Return | MaxDD | Sharpe | Avg Bars |
|---|---|---|---|---|---|---|---|
| **PULLBACK** | 862 | 40.1% | 1.23 | **+310.8%** | 17.6% | 1.45 | 7.2 |
| BREAKOUT | 43 | 37.2% | 1.14 | +3.9% | 9.1% | 0.96 | 33.2 |
| COMBINED (vote) | 17 | 35.3% | 1.02 | +0.3% | 3.2% | 0.18 | 8.5 |
| TREND | 697 | 33.9% | 0.98 | −11.7% | 31.3% | −0.19 | 10.7 |
| MEANREV | 148 | 30.4% | 0.83 | −15.6% | 26.0% | −1.39 | 21.3 |
| SMC | 312 | 31.1% | 0.86 | −26.9% | 38.6% | −1.09 | 12.8 |
| Buy & hold | — | — | — | +60.3% | — | — | — |

---

## Robustness Check (Pullback, split-half)

| Period | Trades | Win% | PF | Return | MaxDD |
|---|---|---|---|---|---|
| H1 (2024-10 → 2025-10) | 430 | 42.1% | 1.31 | +146.9% | 17.6% |
| H2 (2025-10 → 2026-10) | 429 | 38.2% | 1.18 | +66.6% | 14.6% |

Profitable in both halves. Not a fluke of one regime.

---

## Honest Assessment

**What works:** The **pullback strategy** is the real deal in these bots. It's a triple-EMA trend filter (9/21/50) + ADX gate + pullback-zone entry with tight 1:2 RR. 862 trades, PF 1.23, profitable in both halves. This is the logic worth keeping.

**What's dead:**
- **Mean reversion** (−15.6%, PF 0.83) — BB+RSI fading doesn't work on gold H1. v4.1 already removed it.
- **SMC** (−26.9%, PF 0.86) — the swing-retest logic adds nothing beyond the pullback entry.
- **Trend** (−11.7%, PF 0.98) — the looser pullback variant (1.2 ATR zone, no EMA50 filter) bleeds. The tighter pullback version is what works.

**What's marginal:** Breakout (+3.9%, only 43 trades) — too few signals to trust, but not negative.

**The signal mixer** (weighted voting across strategies) produces only 17 trades and +0.3% — combining good and bad strategies dilutes the one that works.

**Bottom line:** These bots contain ONE profitable strategy (pullback) buried among five. The v4.1 cleanup (removing meanrev) was directionally correct but didn't go far enough — trend and SMC should also be cut or replaced. The pullback logic is god-tier material worth building on: it's simple, robust across regimes, and has 862 trades of evidence.
