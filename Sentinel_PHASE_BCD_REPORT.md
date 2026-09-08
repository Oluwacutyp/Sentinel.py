# Sentinel — Phase B / C / D Full-System Backtest Report

**Date:** 2026-09-07 · **Capital:** $10,000 per scenario · **ML:** OFF (no passing champion — strategy engine scores alone)
**File:** `sentinel_bot.py` (23,719 lines) · All phases A→D implemented before this backtest, per the agreed sequence.

---

## 1. What the new layers do (implemented this round)

| Phase | Layer | Symbol | Mechanism | Backtest parity |
|---|---|---|---|---|
| B | **Macro Trinity** (STAGE-18) | XAU | DXY 20d ±0.2% + US10Y 20d ±0.03pts + 50d XAU/DXY correlation (decoupling flag). Background yfinance refresh (15-min TTL), votes ±1.5 on every signal. | Daily bias precomputed with the **same** `compute_bias` formula, joined on the last *completed* daily close (12h lookback — no lookahead). |
| B | **Asian Range Breakout** (STAGE-18) | XAU | 00:00–07:00 UTC high/low; wick-proof (CLOSE beyond range), max 1 entry/side/day, SL = opposite range end, TP = 1.75×width, base score 7.5 (+1.0 H4 trend, +1.0 trinity). | Fresh engine instance per run, bar-driven, self-persist disabled. |
| B | **ADR Stop Floor** | XAU | SL widened to ≥ 0.5 × ADR14 (14-day mean D1 high−low); TP re-anchored at `tp_mult` R. | ADR14 from D1 series (D1 added to 15m mode), last completed day. |
| C | **BTC Microstructure** (STAGE-19) | BTC | Binance public API: funding, OI 5d, taker ratio, 24h chg, Fear&Greed. Flags: `crowded_long` (bearish, BUY −2.0), `squeeze_long`/`div_bull` (bullish), `div_bear` (bearish), `stress` (−0.5). | Historical funding (paged full-depth) + OI/taker (90d) + F&G (365d) per bar. **OFF in these runs — Binance API blocked from this sandbox (HTTP 451). It will be ON on your machine** (disclosed in every report header). |
| D | **Narrative Sentinel** (STAGE-20) | both | Deterministic daily digest (session, H4 structure, regime, macro/micro layer, risk state, ML gate, last-20 trades) → `logs/narratives/` + Telegram at 13:30 UTC. Optional Gemini polish (off). `--narrate` one-shot CLI. | n/a (live-only) |

Also carried into these runs: **STAGE-17 backtester parity** — the 14-day high-water-mark peak expiry is now mirrored in the harness (the Phase-A artifacts predate that parity; see §3).

## 2. Four scenarios — complete system

| Scenario | Return | MaxDD | Trades | WR | PF | Emergency 20% stop | Layers active |
|---|---|---|---|---|---|---|---|
| XAUUSDm 1h · 730d | **−23.23%** ($7,677) | 29.69% | 46 | 52.2% | 0.76 | **YES ~day 46** | trinity 576d ON · ADR floor ON · asian ON |
| XAUUSDm 15m · 60d | **−19.93%** ($8,007) | 28.56% | 10 | 30.0% | 0.27 | **YES ~day 3** | trinity 24d ON · ADR floor ON · asian ON |
| BTCUSDm 1h · 730d | **+16.54%** ($11,654) | 13.92% | 573 | 44.0% | 1.06 | no | sentiment **OFF (sandbox block)** |
| BTCUSDm 15m · 60d | **−17.38%** ($8,262) | 19.89% | 169 | 38.5% | 0.73 | no | sentiment **OFF (sandbox block)** |

Artifacts: `state/backtest_XAUUSDm_20260907_1508.json` (1h), `..._1506.json` (15m), `state/backtest_BTCUSDm_20260907_1507.json` (1h), `..._1508.json` (15m). Charts: `charts/backtest_XAUUSDm.html`, `charts/backtest_BTCUSDm.html`.

## 3. What actually changed vs Phase A — attribution (no sugar-coating)

| Scenario | Phase A | Now | Why |
|---|---|---|---|
| BTC 1h | +12.5% | **+16.54%** | Mostly the **STAGE-17 peak-expiry backtester parity** (Phase-A artifacts were generated before it landed in the harness) + Yahoo drift. The sentiment layer was OFF, so it contributed **nothing** here. |
| XAU 1h | −25.10% | −23.23% | Trinity voting + ADR floor trimmed losses slightly; still halted by the 20% emergency stop ~day 46 (Phase A: ~day 91 — earlier halt = fewer trades, 46 vs 73). |
| XAU 15m | −19.93% | −19.93% | Identical. In this 60-day window trinity voted neutral and the ADR floor never bound. Honest: the new layers did not move this config. |
| BTC 15m | −9.85% | −17.38% | Worse — same STAGE-17 parity: the bot is no longer pinned below a stale 15% peak, so it re-entered a losing 60-day window more aggressively (169 vs 178 trades, lower WR). The fix is *faithful*, not *flattering*. |

## 4. Layer-by-layer read

- **Asian Range (XAU):** worked exactly as designed — 4 breakout trades in the 2y 1h run (−$147) and 2 in 60d 15m (+$109). n is far too small to be significant. The Asia session as a whole was the best session for XAU 1h (+$982, 73% WR), but that includes non-breakout trades.
- **Trinity (XAU):** 576 daily bias points computed; votes were ±1.5 on signals. Net effect small (±2pp over 2 years). It is a *tie-breaker/veto* layer, not an alpha source — that's the honest role.
- **ADR floor (XAU):** widened stops where ATR was tight; SL exits averaged larger dollar losses when hit (18 SL exits = −$9,134 in 1h). Reduced premature stop-outs, but XAU's losses are driven by trade *selection*, not stop distance.
- **BTC sentiment:** could not be validated in this sandbox (Binance 451). On your machine the history fetch will run and the report header will show `ON — funding history N prints`. Re-run the two BTC scenarios locally if you want the true Phase-C numbers.
- **Narrative (D):** verified end-to-end. Sample output (real data, 2026-09-07 15:00 UTC):
  > *"XAUUSDm — New York session, 2026-09-07 15:00 UTC. … Macro trinity is mixed/neutral (DXY 20d −0.92%, US10Y +0.12pts, corr50 −0.54). ML has no passing champion — strategy engine scores alone."*

## 5. The honest assessment

1. **BTC 1h remains the only green configuration** — and it is now +16.5% / 13.9% DD / PF 1.06 over 730 days with 573 trades. That is real but thin: PF 1.06 means the edge is roughly the size of the friction. Spread/swap/latency in live trading would shave a chunk. It is a *data-collecting* config: run it, let ML learn, do not scale it yet.
2. **XAU has no 2-year edge in its current form.** Both configs hit the 20% emergency stop (day 46 on 1h, day 3 on 15m). The new macro/Asian/ADR layers did not fix it — and I do not believe they can, because the problem is not stops or confluence, it is that the MR-dominant signal mix (37/46 trades) in a 2024–2026 gold tape produces a coin-flip win rate while paying full spread. New layers cannot rescue a negative-expectancy base.
3. **The DD "refuse to trade" pain is fixed at the mechanism level** (one-shot 15% re-arm + 14-day peak expiry, live and backtest). The BTC 15m worsening is the visible cost of that honesty: the bot now *resumes* instead of silently staying pinned. Resuming into a bad window is better than never trading again, but it is not free.
4. **Sizing is still the biggest single lever for XAU.** At $10k the tier gives 0.5 lots ≈ 4% risk/trade; a 20% DD is only 5 consecutive full stops away. Your pending call on `"max_lot": 0.1` (≈0.8% risk/trade) would make a −25% two-year outcome roughly a −9% outcome with the same signal quality. That does not create an edge — it makes the *lack* of an edge survivable while ML collects data.
5. **Overfitting discipline:** nothing here was tuned in-sample. All thresholds are research-published values (fxnx/XT_com/quantjourney frameworks), and every layer is disclosed ON/OFF in the report header. The one thing I will *not* do is keep adjusting until XAU turns green — that is how backtests lie.

## 6. Recommended next steps (tuning round, your call)

1. **Decide the XAU sizing guardrail** (`"max_lot": 0.1` or not) — it changes everything about how survivable XAU is.
2. **Re-run the two BTC scenarios on your machine** (Binance reachable) to get Phase C's true numbers.
3. For XAU, the candidate tuning directions, in order of evidence:
   a. Raise the min-score gate / kill MR-on-H1 in ranging regimes (the 15m 25%-WR MR cluster is the bleed);
   b. Session filter: the data says XAU losses concentrate in NewYork (−$2,161 on 1h) — test NY-only-off or NY-require-breakout-only;
   c. Only *then* consider strategy rewrites. Each change gets a 4-scenario A/B before it ships, OOS windows (last 120 days) checked separately.
4. ML remains OFF by its own gate — let the BTC 1h tape keep feeding it; the champion lifecycle is verified and will promote automatically when a model beats baseline out-of-sample.

**Bottom line:** all phases are in, the system is honest about what it does and doesn't do, and the backtest says exactly what I expected it to say: BTC 1h is a slow real edge, XAU needs the sizing + session/gate work before it earns its place. Nothing was tuned to flatter these numbers, and nothing was deleted.
