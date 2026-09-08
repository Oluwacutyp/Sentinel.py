# Sentinel.py — Divine Quantum Adaptive Trading System

> *"No hardcoded maths. No rigid scripts. Only a living system that breathes with the market."*

Sentinel.py is a **fully systematic, ultra-dynamic, adaptive algorithmic trading platform** written in Python.
It takes the *spirit* of classic Pine Script trading ideas — session awareness, ATR trailing, squeeze
detection, multi-filter confluence — and re-imagines them the way only Python can: regime-aware,
volatility-adaptive, machine-learning-gated, walk-forward-validated, and risk-obsessed.

This repository holds **40,000+ lines** of functional code: indicators, strategies, patterns, signal
fusion, ML meta-labeling, risk engines, backtesters, optimizers, live traders, and monitoring.

---

## 1. Why Sentinel.py exists

Pine Script is brilliant for charting, but it is a prisoner of the chart: fixed lengths, fixed
thresholds, one symbol, one timeframe, no memory. Sentinel.py breaks every one of those chains:

| Pine limitation | Sentinel.py answer |
|---|---|
| Fixed indicator lengths (`length = 21`) | **Adaptive lookbacks** that breathe with realized volatility |
| Fixed thresholds (`rsi > 70`) | **Quantile-adaptive gates** calibrated per symbol / regime |
| One timeframe | Native **multi-timeframe fusion** with alignment scoring |
| One regime assumption | **Regime engine** (trend / range / squeeze / panic) that re-weights everything |
| No learning | **ML meta-model** (meta-labeling) that approves or vetoes each trade |
| Manual tuning | **Walk-forward + Bayesian optimization** with overfit guards |
| Naive backtests | Event-driven backtester with **spread, slippage, fees, funding, latency** |
| Hope-based risk | **Kelly-fractional sizing, CPPI, drawdown governors, correlation brakes** |

Nothing here is a toy. Every module is implemented, tested, and wired into the engine.

---

## 2. Architecture

```
sentinel/
├── core/          QuantumEngine, event bus, regime detector, adaptive parameter controller
├── data/          Feeds (CSV/CCXT/yfinance/synthetic), resampling, quality gates, corporate actions
├── indicators/    240+ adaptive indicators (trend / momentum / volatility-volume) + registry
├── patterns/      120+ candlestick + chart pattern detectors with quality scores
├── strategies/    120+ self-contained strategies + base class + portfolio blending
├── signals/       Multi-signal fusion, confluence scoring, disagreement filters
├── ml/            Feature store, meta-labeling, model zoo, calibration, drift watch
├── risk/          Sizing (fixed/kelly/cppi/vol-target), stops, drawdown governor, portfolio brakes
├── execution/     Order manager, paper + live brokers, slippage/fee models, reconciliation
├── portfolio/     Construction (equal/risk-parity/HRP-lite), rebalancing, attribution
├── backtest/      Vectorized + event-driven engines, realistic costs, metrics & tearsheets
├── live/          Live trading loop, dry-run mode, kill-switches, session handling
├── optimization/  Grid / random / Bayesian / genetic + walk-forward + overfit guards
├── monitoring/    Health checks, alerts, performance dashboards, trade journaling
├── utils/         Time, math, statistics, caching, serialization helpers
└── cli.py         Unified command line: backtest / optimize / live / scan / report
```

Supporting substance:

```
configs/    Engine presets (default / crypto / stocks / forex / aggressive / conservative)
scripts/    codegen_megabuild.py (the 40k-line forge), smoke.py, data tools
tests/      500+ smoke + property tests covering every generated module
docs/       Indicator / strategy / pattern catalogs + design notes
examples/   End-to-end showcases you can run in one command
```

---

## 3. Installation

```bash
git clone <this-repo> && cd Sentinel.py
pip install -e ".[all]"        # or: pip install -r requirements.txt (core only)
make build                     # regenerate the indicator/strategy/pattern zoo
make smoke                     # 30-second sanity check
```

Python 3.10+ required. Core engine needs only `numpy`, `pandas`, `scipy`,
`scikit-learn`, `pyyaml`, `joblib`, `matplotlib`.

---

## 4. Quickstart

### 4.1 Scan a market with the full arsenal

```python
import pandas as pd
from sentinel.core.engine import QuantumEngine

df = pd.read_csv("data/BTCUSDT_1h.csv", parse_dates=["timestamp"]).set_index("timestamp")
engine = QuantumEngine("configs/crypto.yaml")
report = engine.scan(df, symbol="BTCUSDT")
print(report.summary())
# => regime: squeeze→expansion | bias: LONG 0.72 | strategies voting: 118/120
# => approved: True (meta-model p=0.68) | size: 1.8% equity | stop: 2.1 ATR
```

### 4.2 Backtest a strategy portfolio

```bash
python -m sentinel backtest --config configs/default.yaml --data data/BTCUSDT_1h.csv --cash 100000
```

### 4.3 Optimize without overfitting

```bash
python -m sentinel optimize --config configs/default.yaml --trials 200 --method bayesian
```

### 4.4 Paper-trade live (dry run)

```bash
python -m sentinel live --dry-run --config configs/crypto.yaml
```

---

## 5. The indicator zoo (240+)

Three generated families, every function volatility-adaptive and NaN-safe:

- `sentinel/indicators/generated_trend.py` — 80 trend rails, cascades, hull-drifts, ribbons
- `sentinel/indicators/generated_momentum.py` — 80 RSI/MACD/ROC hybrids with stochasticization
- `sentinel/indicators/generated_volatility_volume.py` — 80 ATR/Keltner/Bollinger/volume-pressure gauges

Full catalog: [`docs/INDICATORS.md`](docs/INDICATORS.md).

```python
from sentinel.indicators import generated_trend as T
rail = T.t_ema_cascade_quantum(df, period=21)   # adaptive by default
```

## 6. The strategy zoo (120+)

Every strategy is self-contained (`generate_signals(df)` → signal/confidence/gate),
regime-gated, and registered for blending, optimization, and attribution:

- `generated_trend_strategies.py` — rail-cross, momentum-impulse, breakout hybrids
- `generated_meanrev_strategies.py` — stretch-fade, squeeze-armed reversals
- `generated_breakout_strategies.py` — confirmation breakouts, failure fades, expansion riders

Full catalog: [`docs/STRATEGIES.md`](docs/STRATEGIES.md).

## 7. Patterns (120+)

Candle + chart detectors returning `hit`/`score` frames, used as confluence features:

- `generated_candles.py` — doji family, hammers, engulfers, haramis, stars, ladders…
- `generated_charts.py` — fractal breaks, channel rides, squeezes, springs, upthrusts…

Full catalog: [`docs/PATTERNS.md`](docs/PATTERNS.md).

## 8. Signal fusion

`sentinel/signals/fusion.py` blends strategy votes with:

- confidence-weighted voting + gate multiplication
- cross-strategy agreement / disagreement scoring
- regime-conditional weighting (trend strategies muted in ranges, etc.)
- pattern-confluence boosters and vetoes
- cost-aware hysteresis (no flip-flopping inside the spread)

## 9. Machine-learning gate

`sentinel/ml/` implements supervised **meta-labeling**:

1. Base strategies emit candidate trades.
2. A feature store builds regime + indicator + pattern + microstructure features.
3. A calibrated classifier predicts P(trade wins | context).
4. Only candidates above the adaptive threshold execute; the rest are vetoed.

Includes Optuna-free Bayesian search, probability calibration, permutation importance,
and a drift watcher that forces retraining when the market changes character.

## 10. Risk — the реального alpha

- **Sizing:** fixed-fractional,.session, volatility-targeted, Kelly-fractional, CPPI floor
- **Stops:** ATR-multiple, structure-based, time-based, trailing ratchets, breakeven shifts
- **Governors:** daily-loss halt, drawdown throttle, correlation brake, exposure caps,
  news/blackout windows, kill-switches
- Everything is unit-tested and enforced in both backtest and live paths identically.

## 11. Backtesting you can trust

- Vectorized engine for research speed + event-driven engine for realism
- Costs: spread, slippage (volatility-linked), commissions, funding, borrow, latency
- Corporate actions, delisting/survivorship handling hooks, session calendars
- Metrics: CAGR, Sharpe/Sortino/Calmar, maxDD + duration, profit factor, expectancy,
  win rate, turnover, exposure, tail ratios, monthly tearsheet
- Walk-forward harness with embargo + overfit alarms (Deflated Sharpe, White's reality check lite)

## 12. Live trading

`sentinel/live/trader.py` runs the exact same code path as the backtester:

- CCXT spot/futures brokers + paper broker for dry runs
- Idempotent order manager with reconciliation and position-sync
- Session/rollover handling, rate-limit-aware polling, websocket-ready hooks
- Kill-switches: equity guard, error budget, stale-feed halt, manual panic file

## 13. Configuration

Start from a preset and override minimally:

```yaml
# configs/crypto.yaml
engine: { equity: 100000, base_risk: 0.01, max_positions: 6 }
regime: { lookback: 200, squeeze_quantile: 0.15 }
risk:   { sizing: kelly_frac, kelly_cap: 0.25, daily_halt: -0.03, max_drawdown: -0.15 }
ml:     { enabled: true, threshold: 0.55, retrain_bars: 2000 }
costs:  { fee_bps: 5, slippage_atr: 0.05, funding_8h_bps: 1 }
```

Available presets: `default`, `crypto`, `stocks`, `forex`, `aggressive`, `conservative`.

## 14. Testing

```bash
make test        # full suite (500+ tests)
make smoke       # fast import + engine sanity check
```

Every generated indicator, strategy, and pattern has an executable smoke test —
`tests/test_generated_*.py` — plus property tests for risk math and backtest accounting.

## 15. What was borrowed from Pine (conceptually)

Faithful to the mission, Pine ideas were *re-imagined*, never transliterated:

- Session/volume-profile logic → `data/sessions.py` + dynamic POC/VAH/VAL
- ATR trailing stops → `risk/stops.py` ratchets with structure awareness
- Squeeze dots → `core/regime.py` squeeze-state machine with expansion triggers
- Multi-MA confluence → `signals/fusion.py` agreement engine
- RSI/MACD divergences → `patterns/` + `signals/divergence.py` with pivot validation
- Fixed `input.int` knobs → `core/adaptive.py` self-tuning controller + optimizer

## 16. Roadmap

- [ ] Options/volatility-surface module
- [ ] Order-book microstructure feed + queue models
- [ ] Multi-asset statistical arbitrage layer
- [ ] ONNX model export for ultra-low-latency inference
- [ ] Web dashboard (FastAPI + websockets)

---

## 17. Disclaimer

This is research/educational software, not financial advice. Backtests lie, markets
change, and leverage kills. Paper-trade everything, risk tiny size, and never deploy
capital you cannot afford to lose.

## 18. License

Public domain — see [LICENSE](LICENSE) (The Unlicense). Trade well. ⚡
