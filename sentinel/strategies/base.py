"""Strategy base class + zoo discovery, execution, and ranking."""
from __future__ import annotations

from importlib import import_module

import numpy as np
import pandas as pd

from ..utils.helpers import sharpe

_REG = None
_MODS: dict = {}


class BaseStrategy:
    """Contract every strategy honors: params, generate_signals, describe."""

    name = "BaseStrategy"
    kind = "custom"
    default_params: dict = {}

    def __init__(self, **overrides):
        self.params = dict(self.default_params)
        for k, v in overrides.items():
            if k in self.params:
                self.params[k] = v

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def describe(self) -> dict:
        return {"name": self.name, "kind": self.kind, "params": dict(self.params)}


def _registry() -> dict:
    global _REG
    if _REG is None:
        gi = import_module("sentinel.strategies.generated_index")
        _REG = dict(gi.REGISTRY)
    return _REG


def _module(mod_name: str):
    if mod_name not in _MODS:
        _MODS[mod_name] = import_module(f"sentinel.strategies.{mod_name}")
    return _MODS[mod_name]


def list_strategies(kind: str | None = None) -> list:
    reg = _registry()
    names = sorted(reg)
    if kind is None:
        return names
    out = []
    for n in names:
        try:
            cls = getattr(_module(reg[n][0]), n)
            if str(getattr(cls, "kind", "")).lower() == kind.lower():
                out.append(n)
        except Exception:
            continue
    return out


def load_strategy(name: str, **overrides):
    reg = _registry()
    if name not in reg:
        raise KeyError(f"unknown strategy '{name}'")
    mod_name, cls_name = reg[name]
    cls = getattr(_module(mod_name), cls_name)
    return cls(**overrides)


def run_zoo(names: list, df: pd.DataFrame, params: dict | None = None) -> dict:
    """Run many strategies; returns {name: signal-frame}. Failures isolated per strategy."""
    params = params or {}
    out = {}
    for n in names:
        try:
            strat = load_strategy(n, **params.get(n, {}))
            sig = strat.generate_signals(df)
            if set(sig.columns) == {"signal", "confidence", "gate"} and len(sig) == len(df):
                out[n] = sig
        except Exception:
            continue
    return out


def quick_score(sig: pd.DataFrame, close: pd.Series, periods: int = 252) -> dict:
    """Strategy quality from sign returns: Sharpe, hit-rate, turnover."""
    px = close.astype(float)
    rets = px.pct_change().fillna(0.0).to_numpy()
    pos = np.sign(sig["signal"].to_numpy(dtype=float))
    pos = np.roll(pos, 1)
    pos[0] = 0.0
    strat_rets = pos * rets
    w = sig["confidence"].to_numpy(dtype=float) * sig["gate"].to_numpy(dtype=float)
    strat_rets = strat_rets * np.clip(w, 0, 1)
    active = strat_rets[np.abs(pos) > 0]
    return {
        "sharpe": sharpe(pd.Series(strat_rets), periods),
        "hit_rate": float(np.mean(active > 0)) if len(active) else 0.0,
        "turnover": float(np.mean(np.abs(np.diff(pos)) > 0)) if len(pos) > 1 else 0.0,
        "exposure": float(np.mean(np.abs(pos))),
        "trades": int(np.sum(np.abs(np.diff(pos)) > 0)) if len(pos) > 1 else 0,
    }


def rank_strategies(frames: dict, close: pd.Series, periods: int = 252,
                    min_trades: int = 5) -> pd.DataFrame:
    rows = []
    for name, sig in frames.items():
        try:
            s = quick_score(sig, close, periods)
            s["name"] = name
            rows.append(s)
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(columns=["name", "sharpe", "hit_rate", "turnover", "exposure", "trades"])
    df = pd.DataFrame(rows).set_index("name")
    df = df[df["trades"] >= min_trades]
    if df.empty:
        return df
    df["score"] = df["sharpe"] - 2.0 * df["turnover"]
    return df.sort_values("score", ascending=False)
