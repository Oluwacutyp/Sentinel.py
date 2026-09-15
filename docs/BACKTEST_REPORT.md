# GOD Conviction Engine — Factor-Ablation Backtest Report

**Date:** 2026-09-15 · **Data:** BTC/USD daily (Binance, 2017-08 → 2026-09, 3,316 bars) and XAU/USD H1 (2026-02-25 → 2026-05-26, 1,449 bars) · **Engine:** `scripts/factor_ablation.py` (Python twin of the Pine logic) + `pine/GOD-CONVICTION-STRATEGY.pine` (TradingView `strategy()` twin)

---

## TL;DR verdict

> **No evidence of edge was found at any tested gate, on either asset.**
> The shipped default configuration barely trades at all on daily data (4 trades in 9 years, all losers). Loosened to a tradeable frequency, the full system loses money after costs (PF 0.93 on 81 trades; −7.4% net on 171 trades) against a +804% buy-and-hold benchmark. The short side is the dominant source of losses. No single factor family shows robust, gate-independent value. The trap/beyond-FVG family, the conceptual heart of the v16 upgrade, is neutral-to-harmful in these tests.
>
> This does **not** prove the system has zero edge — the sample sizes can't distinguish PF 0.9–1.3 from 1.0. It means the burden of proof is unmet, and running this with real money would be speculation, not trading.

---

## Methodology (integrity rules)

1. **No parameter was optimized.** Every weight, threshold and R-multiple is the value shipped in the Pine indicator. Ablation = remove one factor family at a time, nothing else changes.
2. **Signals on the confirmed bar, fills at the NEXT bar's open** + 1bp slippage. The indicator's implicit close-fill assumption is optimistic; the backtest doesn't use it.
3. **Costs:** 4bp round-trip (spread + commission + slippage) deducted from every round trip, plus a cost gate that refuses entries whose TP1 can't clear costs.
4. **Conservative intra-bar resolution:** if stop and target both sit inside a bar's range, the stop is assumed to fill first.
5. **Risk model identical to the Pine script:** 1% equity risk/trade, swing stop capped at 2×ATR, TP1 at 1.5R (half off + break-even), TP2 at 3R, simplified Hydra trail + profit lock, daily circuit breaker (−3R/day, max 4 trades/day).
7 factor families mirror the Pine weights: **T** trend-stack (18) · **H** HTF bias (15) · **S** liquidity sweep (25) · **Z** zones/beyond-FVG/iFVG (22) · **P** premium/discount (8) · **O** oscillators (8) · **D** traps (15).

Reproduce:
```bash
.venv/bin/python scripts/factor_ablation.py data/btcusd_daily.csv --freq D --thresh 70 --minf 4   # shipped gate
.venv/bin/python scripts/factor_ablation.py data/btcusd_daily.csv --freq D --thresh 55 --minf 3   # diagnostic gate
```

---

## Results — BTC/USD daily, 2018→2026 (3,095 bars after warmup)

### Gate A — shipped defaults (threshold 70, ≥4 families)

| variant | trades | win % | avg R | PF | net % |
|---|---|---|---|---|---|
| **FULL** | **4** | **0.0** | **−1.006** | **0.00** | **−4.0** |

**Finding #1 (structural): the shipped engine is effectively always flat on daily bars.** Its highest-weight factor (liquidity sweeps) fires *against* the trend stack — sweeps are reversals, the trend factor rewards continuation — so reaching 70 points with 4 aligned families is a near-impossible coincidence. In 9 years the engine took 4 trades and stopped out of all of them.

### Gate B — diagnostic (threshold 55, ≥3 families)

| variant | trades | win % | avg R | PF | net % | maxDD % |
|---|---|---|---|---|---|---|
| FULL | 81 | 55.6 | −0.033 | 0.93 | −3.1 | 9.6 |
| −T (no trend) | 50 | 58.0 | +0.010 | 1.02 | +0.2 | 3.0 |
| −H (no HTF) | 26 | 46.2 | −0.218 | 0.60 | −5.6 | 6.8 |
| −S (no sweeps) | 55 | 54.5 | −0.010 | 0.98 | −0.9 | 7.5 |
| −Z (no zones/FVG) | 22 | 54.5 | −0.032 | 0.93 | −0.8 | 5.6 |
| −P (no premium/disc.) | 57 | 49.1 | −0.120 | 0.76 | −6.9 | 10.5 |
| −O (no oscillators) | 53 | 58.5 | +0.010 | 1.02 | +0.3 | 7.1 |
| −D (no traps) | 25 | 48.0 | −0.102 | 0.81 | −2.7 | 7.5 |
| CORE-LIQ (S+Z+D only) | 1 | — | — | — | −1.0 | — |
| RETAIL (T+H+O only) | 0 | — | — | — | 0.0 | — |

Direction split (FULL): LONG 51 trades, WR 58.8%, **+0.73R** · SHORT 30 trades, WR 50.0%, **−3.44R**

### Gate C — loose (threshold 45, ≥2 families)

| variant | trades | win % | avg R | PF | net % | maxDD % |
|---|---|---|---|---|---|---|
| FULL | 171 | 54.4 | ≈−0.03 | ≈0.95 | −7.4 | 12.8 |
| −P | 154 | 56.5 | +0.300 | 1.69 | +4.8 | 8.2 |
| −D | 133 | 60.9 | +0.102 | 1.26 | +13.5 | 7.5 |
| −Z | 76 | 46.1 | −0.060 | 0.89 | −15.5 | 17.5 |
| CORE-LIQ (S+Z+D only) | 12 | 16.7 | −0.731 | 0.13 | −8.5 | 8.5 |
| RETAIL (T+H+O only) | 0 | — | — | — | 0.0 | — |

Direction split (FULL): LONG 113 trades, WR 58.4%, **+4.81R** · SHORT 58 trades, WR 46.6%, **−11.50R**

FULL realized R by year (Gate C): 2018 +2.2 · 2019 −6.4 · 2020 +1.9 · 2021 −4.6 · 2022 −1.0 · 2023 +4.5 · 2024 +2.8 · 2025 −3.2 · 2026 −2.9 — **no stable year-to-year sign**.

### XAU/USD H1 (90-day sample, Gate C — indicative only)

| variant | trades | win % | avg R | PF | net % |
|---|---|---|---|---|---|
| FULL | 62 | 46.8 | −0.18 | 0.85 | −11.1R |
| LONG | 13 | **15.4** | −0.78 | — | −10.1R |
| SHORT | 49 | 55.1 | −0.02 | — | −1.0R |

Gold benchmark over the same window: −12%. The engine's longs were repeatedly stopped out in a falling tape. Sample too small for firm conclusions — treat as "no evidence of edge here either."

---

## Findings

1. **The confluence architecture is self-cancelling.** Liquidity sweeps (25 pts) are counter-trend events; the trend stack (18) and HTF bias (15) reward the opposite direction on the same bar. Requiring both to stack past 70/4 makes entries nearly impossible (Gate A), and loosening the gate doesn't produce edge (Gates B/C). A real trap-trader enters *because of* the sweep, with HTF as a directional filter — not as an independent score hurdle.
2. **The short side bleeds.** Shorts are −3.4R (Gate B) and −11.5R (Gate C) across a +804% drift period. The engine shorts into a secular bull market whenever premium + bearish oscillators align, and pays for it.
3. **The trap/beyond-FVG family (D) does not earn its keep here.** Gate B: removing D is roughly neutral. Gate C: removing D is the single best variant (+13.5%, PF 1.26). At 133 trades, +0.102R/trade is **within one standard error of zero** — read it as "not proven harmful" rather than "proven harmful", but the positive case for the family is not made by this data either.
4. **CORE-LIQ alone (S+Z+D) has no standalone edge** — 12 trades, PF 0.13 at Gate C. The liquidity philosophy needs trend context to survive, which contradicts the pure "fade everything" framing.
5. **RETAIL (T+H+O only) can never enter**: its maximum possible score (41) is below every threshold — an accidental but telling design fact: *every* entry in this engine requires a liquidity event.
6. **The hygiene features work as designed** (cost gate, circuit breaker, bait suppression) — they reduce trade count and prevent the worst entries, but hygiene cannot manufacture edge that isn't in the signal.
7. The Python twin omits the indicator's weakest add-ons (z-score, "dark pool", sentiment vector, weekly-open, Ichimoku, H&S) — all low-weight, additive decorations. Their absence makes entry *harder*, so findings #1–#3 are not caused by the omissions.

---

## Caveats (what this test cannot say)

- **Timeframe mismatch:** the Pine script is tuned for intraday (15m–4h); the anchor data here is daily, because intraday data of sufficient length was not reachable from this environment. The XAU H1 sample is only 90 days. Intraday behavior may differ — but the burden is on the strategy to prove that.
- **Statistical power:** with 81–171 trades, confidence intervals on PF are roughly ±0.2–0.3. We can reject "PF ≥ 1.5"; we cannot distinguish 0.9 from 1.1. Honest phrasing: *no evidence of edge*, not *proof of no edge*.
- The twin approximates the indicator; the `strategy()` file is provided so TradingView's own engine can adjudicate (it will fill TP/SL intra-bar in bar order — slightly optimistic vs. our conservative rule).
- Single-asset results (BTC) can be regime-luck in either direction.

---

## Recommendations (in priority order)

1. **Do not run this with real money as-is.** Forward-test in demo only.
2. **Restructure entry logic around events, not summed scores:** sweep/trap fires → entry candidate; trend/HTF act as *filters* (allowed/blocked), not as co-requisites. Test that variant before anything else.
3. **Kill or gate shorts on BTC** (allowShort=false) unless an intraday test shows they earn; consider trend-regime gating for shorts on all assets.
4. **Cut the decoration** (dark pool, quantum gravity, sentiment) from the indicator — untestable theater consumes attention and drawing budget.
5. If intraday data becomes available, re-run this exact battery on 1h/15m BTC and XAUUSD before revisiting any conclusion.

---

### Data provenance

- BTC/USD daily: Binance spot via `jptrustlearning/btc` (auto-updated mirror), 2017-08-17 → 2026-09-13.
- XAU/USD H1: `Sai310421/xauusd-data` (MIT), 2026-02-25 → 2026-05-26.
- Raw CSVs committed under `data/` for reproducibility.
