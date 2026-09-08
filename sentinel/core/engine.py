"""QuantumEngine: the divine orchestrator — regime → zoo → fusion → ML gate → risk."""
from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

from ..backtest.engine import EventBacktester
from ..core.adaptive import QuantileGate
from ..core.regime import RegimeDetector
from ..ml.meta import MetaGate, labeled_matrix
from ..risk.manager import RiskManager
from ..signals.fusion import fuse_all
from ..strategies.base import list_strategies, load_strategy, quick_score, rank_strategies, run_zoo
from ..utils.helpers import atr, ensure_ohlcv


def load_config(path: str | pathlib.Path | dict) -> dict:
    if isinstance(path, dict):
        return path
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class ScanReport:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def summary(self) -> str:
        return (f"regime={self.regime_label} bias={self.bias:+.2f} pos={self.position_now:+.0f} "
                f"agree={self.agreement:.2f} approved={self.approved} meta_p={self.meta_proba:.2f} "
                f"size={self.size_fraction:.3f} stop={self.stop_distance:.4f} "
                f"strategies={self.n_strategies}")

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


BULL_WORDS = ("bull", "hammer", "piercing", "engulfing_bull", "harami_bull", "kicker_bull",
              "reclaim", "break_up", "ride_up", "pop_up", "tweezer_bottom", "tasuki_up")
BEAR_WORDS = ("bear", "hanging", "shooting", "dark_cloud", "engulfing_bear", "harami_bear",
              "kicker_bear", "reject", "break_down", "ride_down", "pop_down", "tweezer_top", "tasuki_down")


class QuantumEngine:
    """End-to-end adaptive trading engine driven by a YAML preset."""

    def __init__(self, config: str | pathlib.Path | dict = "configs/default.yaml"):
        self.cfg = load_config(config)
        eng = self.cfg.get("engine", {})
        reg = self.cfg.get("regime", {})
        risk = dict(self.cfg.get("risk", {}))
        risk.setdefault("base_risk", eng.get("base_risk", 0.01))
        self.equity = float(eng.get("equity", 100_000))
        self.max_strategies = int(eng.get("max_strategies", 120))
        self.regime = RegimeDetector(lookback=int(reg.get("lookback", 200)),
                                     hysteresis=3)
        self.regime_kw = {"squeeze_q": float(reg.get("squeeze_quantile", 0.15)),
                          "panic_q": float(reg.get("panic_vol_quantile", 0.95))}
        self.risk = RiskManager(risk)
        self.costs = self.cfg.get("costs", {})
        self.sig_cfg = self.cfg.get("signals", {})
        self.ml_cfg = self.cfg.get("ml", {})
        self.meta = MetaGate(threshold=float(self.ml_cfg.get("threshold", 0.55)))
        self._kind_lookup: dict = {}
        self._fitted = False

    # ------------------------------------------------------------- helpers
    def _kinds(self, names: list) -> dict:
        missing = [n for n in names if n not in self._kind_lookup]
        for n in missing:
            try:
                self._kind_lookup[n] = str(load_strategy(n).kind)
            except Exception:
                self._kind_lookup[n] = "confluence"
        return {n: self._kind_lookup[n] for n in names}

    def _atr_pct(self, df: pd.DataFrame) -> float:
        a = atr(df).iloc[-1]
        px = float(df["close"].iloc[-1])
        return float(a / (px + 1e-12))

    def _pattern_pressure(self, df: pd.DataFrame) -> pd.Series:
        try:
            from ..patterns import generated_candles as C
            from ..patterns import generated_charts as H
        except Exception:
            return pd.Series(0.0, index=df.index)
        bull, bear = 0.0, 0.0
        for nm in list(C.__all__)[:24]:
            try:
                r = getattr(C, nm)(df)
                s = (r["hit"] * r["score"]).fillna(0.0)
                low = nm.lower()
                if any(w in low for w in BULL_WORDS):
                    bull += s
                elif any(w in low for w in BEAR_WORDS):
                    bear += s
            except Exception:
                continue
        for nm in list(H.__all__)[:12]:
            try:
                r = getattr(H, nm)(df)
                s = (r["hit"] * r["score"]).fillna(0.0)
                low = nm.lower()
                if any(w in low for w in BULL_WORDS):
                    bull += s
                elif any(w in low for w in BEAR_WORDS):
                    bear += s
            except Exception:
                continue
        net = (bull - bear) / (abs(bull) + abs(bear) + 1e-9)
        return net.fillna(0.0).rename("pattern_pressure")

    # ------------------------------------------------------------- ML fit
    def fit_ml(self, df: pd.DataFrame, horizon: int = 10) -> dict:
        df = ensure_ohlcv(df)
        names = list_strategies()[: self.max_strategies]
        frames = run_zoo(names, df)
        if not frames:
            return {"fitted": False}
        fused = fuse_all(frames, min_agreement=0.0)
        regime = self.regime.fit(df, **self.regime_kw)
        X, y, mask = labeled_matrix(fused["blend"]["vote"], fused["blend"]["agreement"],
                                    regime, df["close"], horizon)
        Xa, ya = X[mask], y[mask]
        if len(Xa) < 100 or len(np.unique(ya.to_numpy())) < 2:
            return {"fitted": False, "samples": len(Xa)}
        self.meta.fit(Xa, ya)
        self._fitted = True
        return {"fitted": True, "samples": len(Xa), "pos_rate": float(ya.mean()),
                "importance": self.meta.importance(Xa.iloc[:500], ya.iloc[:500])}

    # ------------------------------------------------------------- scan
    def scan(self, df: pd.DataFrame, symbol: str = "SYM") -> ScanReport:
        df = ensure_ohlcv(df)
        warmup = int(self.cfg.get("backtest", {}).get("warmup_bars", 300))
        if len(df) < max(150, warmup // 2):
            raise ValueError(f"need >= {warmup // 2} bars, got {len(df)}")
        regime_now = self.regime.current(df, **self.regime_kw)
        trans = self.regime.transition_alert(df, **self.regime_kw)
        names = list_strategies()[: self.max_strategies]
        frames = run_zoo(names, df)
        lookup = self._kinds(list(frames))
        tail = {n: s.tail(500) for n, s in frames.items()}
        ranked = rank_strategies(tail, df["close"].tail(500), min_trades=2)
        scores = ranked["score"].to_dict() if not ranked.empty else {}
        if scores:
            keep = list(ranked.index[: max(12, len(ranked) // 2)])
            frames = {n: frames[n] for n in keep if n in frames}
        atr_pct = self._atr_pct(df)
        cost_bps = float(self.costs.get("fee_bps", 5)) + float(self.costs.get("spread_bps", 2))
        fused = fuse_all(frames, lookup=lookup, scores=scores or None,
                         cost_bps=cost_bps, atr_pct=atr_pct,
                         min_agreement=float(self.sig_cfg.get("min_agreement", 0.55)))
        blend = fused["blend"]
        pressure = self._pattern_pressure(df)
        boost = float(self.sig_cfg.get("pattern_boost", 0.10))
        vote = blend["vote"] + boost * pressure.reindex(blend.index).fillna(0.0)
        pos_now = float(np.sign(vote.iloc[-1])) if abs(float(vote.iloc[-1])) >= fused["enter_threshold"] else 0.0
        if float(blend["agreement"].iloc[-1]) < float(self.sig_cfg.get("min_agreement", 0.55)):
            pos_now = 0.0
        if self.ml_cfg.get("enabled", True) and self._fitted:
            regime_frame = self.regime.fit(df, **self.regime_kw)
            X, _, _ = labeled_matrix(blend["vote"], blend["agreement"], regime_frame, df["close"])
            meta_p = float(self.meta.predict_proba(X.iloc[[-1]])[0])
            approved = bool(meta_p >= self.meta.threshold and pos_now != 0.0)
        else:
            meta_p = 0.5
            approved = bool(pos_now != 0.0)
        px = float(df["close"].iloc[-1])
        a = float(atr(df).iloc[-1])
        win_rate = 0.5
        if not ranked.empty:
            win_rate = float(ranked["hit_rate"].head(10).mean())
        size = self.risk.size_position(self.equity, px, a, win_rate=win_rate, payoff=1.5)
        stops = self.risk.stop_levels(int(pos_now) if pos_now != 0 else 1, px, a)
        gate_pos = QuantileGate().position(vote.fillna(0.0))
        return ScanReport(
            symbol=symbol, bars=len(df), regime_label=regime_now["label"],
            regime=regime_now, transition=trans, bias=float(vote.iloc[-1]),
            agreement=float(blend["agreement"].iloc[-1]), position_now=pos_now,
            gate_position=float(gate_pos.iloc[-1]), approved=approved, meta_proba=meta_p,
            size_fraction=float(size["fraction"]), size_detail=size, stops=stops,
            stop_distance=float(size["stop_dist"] / (px + 1e-12)),
            n_strategies=len(frames), ranked=ranked.head(15),
            enter_threshold=float(fused["enter_threshold"]),
            pattern_pressure=float(pressure.iloc[-1]),
            _blend=blend, _vote=vote,
        )

    # ------------------------------------------------------------- backtest
    def backtest(self, df: pd.DataFrame, fit_ml_first: bool = True) -> dict:
        df = ensure_ohlcv(df)
        if fit_ml_first and self.ml_cfg.get("enabled", True):
            try:
                self.fit_ml(df.iloc[: len(df) // 2])
            except Exception:
                pass
        names = list_strategies()[: self.max_strategies]
        frames = run_zoo(names, df)
        if not frames:
            raise RuntimeError("no strategies ran")
        lookup = self._kinds(list(frames))
        atr_pct = float((atr(df) / (df["close"] + 1e-12)).median())
        cost_bps = float(self.costs.get("fee_bps", 5)) + float(self.costs.get("spread_bps", 2))
        fused = fuse_all(frames, lookup=lookup, cost_bps=cost_bps, atr_pct=atr_pct,
                         min_agreement=float(self.sig_cfg.get("min_agreement", 0.55)))
        bt = EventBacktester(cash=self.equity, fee_bps=float(self.costs.get("fee_bps", 5)),
                             slippage_atr=float(self.costs.get("slippage_atr", 0.05)),
                             spread_bps=float(self.costs.get("spread_bps", 2)),
                             funding_8h_bps=float(self.costs.get("funding_8h_bps", 0)))
        res = bt.run(df, fused["position"])
        res["config"] = self.cfg.get("engine", {})
        return res
