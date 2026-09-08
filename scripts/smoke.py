"""30-second sanity check: imports, data, regime, zoo, fusion, backtest, risk, ML."""
from __future__ import annotations

import numpy as np


def main() -> None:
    from sentinel.data.feed import make_synthetic, quality_report
    from sentinel.core.regime import RegimeDetector
    from sentinel.strategies.base import list_strategies, run_zoo
    from sentinel.signals.fusion import fuse_all
    from sentinel.backtest.engine import EventBacktester
    from sentinel.risk.manager import RiskManager
    from sentinel.ml.meta import MetaGate

    df = make_synthetic(800, seed=7)
    print("quality:", quality_report(df))
    reg = RegimeDetector().current(df)
    print("regime:", reg["label"], {k: round(v, 3) for k, v in reg.items() if k.startswith("p_")})
    names = list_strategies()[:24]
    frames = run_zoo(names, df)
    print(f"zoo: ran {len(frames)}/{len(names)}")
    fused = fuse_all(frames, cost_bps=8, atr_pct=0.01)
    pos = fused["position"]
    print(f"fusion: enter={fused['enter_threshold']:.3f} long={float((pos > 0).mean()):.2f} "
          f"short={float((pos < 0).mean()):.2f}")
    bt = EventBacktester(cash=100_000, fee_bps=5, slippage_atr=0.05)
    res = bt.run(df, pos)
    print(f"backtest: ret={res['total_return']:.3f} sharpe={res['sharpe']:.2f} maxDD={res['max_dd']:.3f} "
          f"trades={res['trades']}")
    rm = RiskManager({"sizing": "kelly_frac", "base_risk": 0.01})
    size = rm.size_position(equity=100_000, price=100.0, atr=2.0, win_rate=0.55, payoff=1.5)
    print(f"risk: size_frac={size['fraction']:.4f} shares={size['shares']:.1f}")
    mg = MetaGate()
    X = np.random.default_rng(0).normal(size=(400, 8))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    mg.fit(X, y)
    print(f"meta: proba_mean={float(mg.predict_proba(X[:5]).mean()):.3f}")
    print("SMOKE PASS")


if __name__ == "__main__":
    main()
