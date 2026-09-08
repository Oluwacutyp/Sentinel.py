"""Core engine property tests: helpers, regime, adaptive, risk, backtest, fusion, ML."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _df(n=600, seed=3):
    from sentinel.data.feed import make_synthetic

    return make_synthetic(n, seed=seed)


def test_helpers_math():
    from sentinel.utils.helpers import max_drawdown, profit_factor, sharpe

    r = pd.Series(np.random.default_rng(0).normal(0.001, 0.01, 500))
    assert sharpe(r) != 0.0
    assert profit_factor(r) > 0
    eq = pd.Series(100 * np.exp(np.cumsum(r.to_numpy())))
    dd = max_drawdown(eq)
    assert dd["max_dd"] <= 0.0


def test_regime_labels():
    from sentinel.core.regime import LABELS, RegimeDetector

    df = _df()
    det = RegimeDetector()
    frame = det.fit(df)
    assert set(frame["label"].unique()) <= set(LABELS)
    cur = det.current(df)
    assert cur["label"] in LABELS
    assert 0 <= cur["p_trend"] <= 1


def test_adaptive_breath_and_tuner():
    from sentinel.core.adaptive import DrawdownThrottle, SignalRateTuner, VolatilityBreath

    df = _df()
    vb = VolatilityBreath()
    s = vb.scale(df["close"])
    assert float(s.min()) >= 0.5 and float(s.max()) <= 2.0
    tuner = SignalRateTuner(target_rate=0.02)
    sig = pd.Series(np.sign(np.random.default_rng(1).normal(size=300)))
    m = tuner.update(sig)
    assert 0.25 <= m <= 4.0
    th = DrawdownThrottle()
    eq = pd.Series(np.linspace(100, 90, 100))
    assert 0.0 <= th.factor(eq) <= 1.0


def test_risk_sizing_and_governors():
    from sentinel.risk.manager import RiskManager

    rm = RiskManager({"sizing": "kelly_frac", "base_risk": 0.01})
    size = rm.size_position(100_000, 100.0, 2.0, win_rate=0.55, payoff=1.5)
    assert 0 < size["fraction"] <= 0.8
    stops = rm.stop_levels(1, 100.0, 2.0)
    assert stops["stop"] < 100.0 < stops["target_1"]
    trail = RiskManager.trailing_stop(1, 95.0, 110.0, 2.0)
    assert trail >= 95.0
    gov = rm.update_equity(100_000)
    assert gov["halted"] is False
    allow = rm.allow_trade(100_000, 0.1)
    assert allow["allow"] is True


def test_backtest_accounting():
    from sentinel.backtest.engine import EventBacktester, VectorBacktester

    df = _df()
    flat = pd.Series(0.0, index=df.index)
    r = EventBacktester(cash=50_000).run(df, flat)
    assert r["trades"] == 0 and abs(r["total_return"]) < 1e-9
    hold = pd.Series(1.0, index=df.index)
    r2 = EventBacktester(cash=50_000, fee_bps=0, slippage_atr=0, spread_bps=0,
                         latency_bars=0).run(df, hold)
    bh = float(df["close"].iloc[-1] / df["close"].iloc[0] - 1)
    assert abs(r2["total_return"] - bh) < 0.02
    v = VectorBacktester().run(df, hold)
    assert v["exposure"] > 0.9


def test_fusion_bounds():
    from sentinel.signals.fusion import cost_aware_threshold, fuse_all
    from sentinel.strategies.base import list_strategies, run_zoo

    df = _df()
    frames = run_zoo(list_strategies()[:10], df)
    assert len(frames) >= 5
    out = fuse_all(frames, cost_bps=10, atr_pct=0.01)
    assert out["blend"]["vote"].between(-1, 1).all()
    assert 0.02 <= cost_aware_threshold(10, 0.01) <= 0.6


def test_meta_gate():
    from sentinel.ml.meta import MetaGate

    rng = np.random.default_rng(0)
    X = rng.normal(size=(300, 6))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    mg = MetaGate().fit(X, y)
    p = mg.predict_proba(X[:10])
    assert ((p >= 0) & (p <= 1)).all()
    assert mg.approve(X[:10]).dtype == bool


def test_engine_scan_and_backtest():
    from sentinel.core.engine import QuantumEngine

    df = _df(900, seed=9)
    eng = QuantumEngine("configs/default.yaml")
    rep = eng.scan(df, symbol="TEST")
    assert rep.position_now in (-1.0, 0.0, 1.0)
    assert rep.n_strategies >= 10
    res = eng.backtest(df.iloc[:600], fit_ml_first=False)
    assert "sharpe" in res and res["trades"] >= 0
