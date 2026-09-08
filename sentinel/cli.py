"""Unified command line: scan / backtest / optimize / live."""
from __future__ import annotations

import argparse

from .core.engine import QuantumEngine, load_config
from .data.feed import load_csv, make_synthetic


def load_data(args) -> "pd.DataFrame":
    import pandas as pd  # noqa: F401

    if args.data:
        if args.data.startswith("synthetic"):
            n = int(args.bars or 2000)
            seed = int(args.seed or 42)
            return make_synthetic(n, seed=seed)
        if args.data.startswith("yf:"):
            from .data.feed import load_yfinance

            sym, _, rest = args.data[3:].partition(",")
            period = rest or "2y"
            return load_yfinance(sym, period=period)
        if args.data.startswith("ccxt:"):
            from .data.feed import load_ccxt

            sym = args.data[5:] or "BTC/USDT"
            return load_ccxt(sym)
        return load_csv(args.data)
    return make_synthetic(int(args.bars or 2000), seed=int(args.seed or 42))


def cmd_scan(args) -> int:
    df = load_data(args)
    eng = QuantumEngine(args.config)
    if args.fit_ml:
        info = eng.fit_ml(df)
        print("ml:", info)
    rep = eng.scan(df, symbol=args.symbol or "SYM")
    print(rep.summary())
    print("regime mix:", {k: round(v, 3) for k, v in rep.regime["mix_lookback"].items()})
    print("transition:", rep.transition)
    print("top strategies:\n", rep.ranked[["sharpe", "hit_rate", "turnover", "score"]].head(10))
    return 0


def cmd_backtest(args) -> int:
    df = load_data(args)
    eng = QuantumEngine(args.config)
    res = eng.backtest(df)
    for k in ("final_equity", "total_return", "cagr", "sharpe", "sortino", "max_dd",
              "profit_factor", "win_rate", "trades", "turnover", "exposure"):
        v = res[k]
        print(f"{k:14s} {v:.4f}" if isinstance(v, float) else f"{k:14s} {v}")
    return 0


def cmd_optimize(args) -> int:
    from .optimization.search import StrategySearch, walk_forward

    df = load_data(args)
    if args.strategy:
        s = StrategySearch(args.strategy, df)
        ranked = s.random_search(trials=args.trials, seed=1)
        print(ranked.head(10).to_string())
        best = s.refine(ranked.iloc[0]["params"], iters=20)
        print("refined:", best)
    else:
        from .strategies.base import list_strategies

        for name in list_strategies()[: args.top]:
            wf = walk_forward(name, df, n_folds=3, trials=max(10, args.trials // 4))
            print(f"{name:24s} robust={wf.get('robust')} mean_oos={wf.get('mean_oos', 0):+.3f}")
    return 0


def cmd_live(args) -> int:
    from .data.feed import make_synthetic
    from .live.trader import LiveTrader

    eng = QuantumEngine(args.config)
    live_cfg = eng.cfg.get("live", {})
    trader = LiveTrader(eng, poll_seconds=0 if args.dry_run else int(live_cfg.get("poll_seconds", 20)),
                        dry_run=True if args.dry_run else bool(live_cfg.get("dry_run", True)))
    base = load_data(args)

    def feed(step: int):
        end = min(len(base), 600 + step * 5)
        if end >= len(base):
            return None
        return base.iloc[:end]

    trader.run(feed, symbol=args.symbol or "SYM", max_steps=args.steps)
    return 0


def _common_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--data", default="synthetic", help="csv path | synthetic | yf:SYM | ccxt:SYM")
    ap.add_argument("--bars", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--symbol", default="SYM")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sentinel", description="Sentinel.py divine trading system")
    _common_args(p)
    sub = p.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("scan")
    _common_args(s1)
    s1.add_argument("--fit-ml", action="store_true")
    s1.set_defaults(fn=cmd_scan)
    s2 = sub.add_parser("backtest")
    _common_args(s2)
    s2.set_defaults(fn=cmd_backtest)
    s3 = sub.add_parser("optimize")
    _common_args(s3)
    s3.add_argument("--strategy", default="")
    s3.add_argument("--trials", type=int, default=50)
    s3.add_argument("--top", type=int, default=10)
    s3.set_defaults(fn=cmd_optimize)
    s4 = sub.add_parser("live")
    _common_args(s4)
    s4.add_argument("--dry-run", action="store_true")
    s4.add_argument("--steps", type=int, default=5)
    s4.set_defaults(fn=cmd_live)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
