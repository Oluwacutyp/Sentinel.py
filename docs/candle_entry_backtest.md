# Candlestick Entries at ICT Levels — Backtest

*Strategy: `sentinel/strategies/candle_ict_entries.py` · XAUUSD hourly (GC=F) · 11,449 bars · 2024-10-10 → 2026-10-09*
*Costs: $0.45/trade · 1% risk · next-bar entry · no lookahead · 1:2 R:R · 48-bar time stop · one position at a time*

## System

Three layers, all causal (bar t uses data ≤ t only):

1. **Trend filter** (from the winning pullback backtest): EMA9 > EMA21 > EMA50 (or inverse) + ADX(14) > 22. No counter-trend entries.
2. **ICT levels**: fresh Fair Value Gaps (3-candle, die on body close through, 48-bar expiry), Order Blocks (last opposite candle before displacement, 48-bar expiry), liquidity sweeps (20-bar swing wick + close back, 12-bar expiry), premium/discount discipline (50% of trailing 50-bar range — longs only in discount, shorts only in premium).
3. **Candlestick triggers** (must print AT a level): engulfing, pin bar (wick > 2× body), doji + confirmation, inside-bar breakout.

Stop = tighter of pattern extreme or 1.2×ATR. Target = 2× risk.

## Results

| Period | Trades | Win% | PF | Return | MaxDD | Sharpe |
|---|---|---|---|---|---|---|
| FULL (2y) | 115 | 38.8 | 1.21 | **+16.3%** | 12.4% | 0.69 |
| H1 (2024-10 → 2025-10) | 56 | 35.7 | 1.04 | +1.3% | 12.4% | 0.15 |
| H2 (2025-10 → 2026-10) | 60 | 41.7 | 1.35 | +13.6% | 5.9% | 1.14 |

Profitable in both halves → directionally robust. But H1 is marginal (+1.3%), and the full return is modest next to the pullback strategy's +310.8% on the same data.

## Per-pattern attribution (real system: 1%-compounding, one-at-a-time)

| Pattern | Trades | Win% | P&L |
|---|---|---|---|
| bear_pin | 31 | 51.6 | **+$1,755** |
| bear_doji_conf | 6 | 66.7 | +$608 |
| bear_engulf | 15 | 46.7 | +$614 |
| bear_inside_brk | 3 | 33.3 | +$6 |
| bull_pin | 49 | 28.6 | **−$961** |
| bull_engulf | 9 | 33.3 | −$141 |
| bull_doji_conf | 2 | 0.0 | −$205 |

| Level | Trades | Win% | P&L |
|---|---|---|---|
| fvg | ~75 | 31.8 | −$1,594 (fixed-risk attribution) |
| ob | ~43 | 32.6 | −$250 |
| sweep | 4 | 25.0 | −$102 |

## The honest finding

**The system is profitable only because of the bear side.** Bearish pin bars at supply (51.6% win, +$1,755) carry the entire P&L. Every bullish trigger loses money — bull_pin alone bleeds −$961 across 49 trades.

This is backwards from intuition: buy-and-hold was +60% over the same period (strong uptrend), yet the long entries fail. Likely reasons:

1. In a grinding uptrend, pullbacks are shallow — bullish pins print at "demand" but continuation is weak; price chops instead of ripping.
2. The FVG/OB levels that matter on the short side (distribution zones) are cleaner than demand zones in a bid-up market.
3. The premium/discount filter may mislabel levels mid-trend (EQ drifts with the range).

## What this means for entries

- **Pin bars are the only trigger pulling weight** (119 of 174 raw signals). Engulfing, doji-confirm, and inside-breakout add little.
- **FVG is the dominant level** (127 of 174 signals) — confirms the mining doc's "most backtestable ICT concept."
- **Sweep + pattern coincidence is nearly nonexistent** (4 signals) — too rare to matter on H1.
- The immediate improvement is obvious: **cut the bull-side candle triggers** (or require deeper OTE-zone pullbacks for longs) and re-test as a bear-biased system. The bear_pin alone may beat the combined system.

## vs the pullback strategy

| | Candle-ICT | Pullback (rule core) |
|---|---|---|
| Return | +16.3% | +310.8% |
| Sharpe | 0.69 | 1.45 |
| Trades | 115 | 862 |
| PF | 1.21 | 1.23 |

The pullback's simpler entry (price in pullback zone of EMA9 + ADX gate) massively outperforms the candle+ICT stack. Precision ≠ profitability: the extra filters cut 862 trades to 115 and the survivors don't compensate.

**Bottom line:** candle triggers at ICT levels have a real but modest edge, concentrated entirely in bearish pin bars at supply. Not a replacement for the pullback core — a possible overlay/sleeve for short-side entries.
