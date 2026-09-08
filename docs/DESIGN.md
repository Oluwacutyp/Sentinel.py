# Sentinel.py design notes

## Core philosophy

1. **No hardcoded maths.** Every threshold is either derived from costs, calibrated
   from rolling quantiles, or tuned by the optimizer. A constant in the code is a
   starting point for adaptation — never a law.
2. **Regime first.** The market is a switching process. `core/regime.py` labels every
   bar; everything downstream (weights, gates, sizing) conditions on it.
3. **Committees beat gurus.** 120 strategies vote; the fusion engine weighs them by
   confidence, agreement, recent skill, and regime fit. No single signal can sink us.
4. **The ML model is a veto, not a prophet.** Meta-labeling only answers: "given this
   context, do our base strategies win?" Candidates below threshold are skipped.
5. **Risk is the strategy.** Sizing, stops, governors, and kill-switches are
   first-class citizens sharing one code path in backtest and live.
6. **Backtests must hurt.** Spread, slippage, fees, funding, latency, embargoes,
   walk-forward, and multiple-testing haircuts are all on by default.

## Data flow

```
feed (csv/yf/ccxt/synth) → clean → quality gate → resample/MTF
  → regime.fit → zoo.run_zoo → rank → fuse_all → pattern pressure → ML veto
  → risk.size + stops → broker (paper/ccxt) → journal/monitor
```

## Adaptivity inventory

| component | what adapts | how |
|---|---|---|
| indicators | lookback | volatility breath (rolling median ratio) |
| regime | thresholds | rolling rank/quantiles of own features |
| fusion | kind weights | softmax over trailing per-kind scores |
| fusion | enter threshold | derived from costs ÷ ATR% |
| signals | hysteresis | Schmitt trigger + agreement mask |
| risk | exposure | drawdown throttle + daily halt + corr brake |
| stops | trailing | ATR ratchet + breakeven shift |
| ml | threshold | config + drift watcher retrain |
| optimizer | params | walk-forward + haircut Sharpe |

## Pine lineage (re-imagined, never transliterated)

- Session boxes → `data/feed.session_filter` + MTF alignment
- ATR trailing → `risk/manager.trailing_stop` with structure hooks
- Squeeze dots → five-state regime machine with expansion triggers
- MA confluence → committee fusion with disagreement filters
- RSI/MACD divs → pattern detectors + pivot-validated divergence features

## Extension guide

- New indicator: add a function in `indicators/` + register in `generated_index`-style
  registry, or simply call it from the engine — `run_many` catches failures.
- New strategy: subclass `strategies.base.BaseStrategy`, implement
  `generate_signals(df)` → signal/confidence/gate. It instantly joins ranking,
  fusion, optimization, and attribution.
- New market: copy a preset in `configs/`, set costs/sessions, run
  `sentinel scan --data <csv>` then `optimize` with walk-forward on.
