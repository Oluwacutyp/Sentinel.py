"""Indicator registry: lazy loading, caching, and composite builders over the zoo."""
from __future__ import annotations

from importlib import import_module

import pandas as pd

_REG = None
_MODS: dict = {}


def _registry() -> dict:
    global _REG
    if _REG is None:
        gi = import_module("sentinel.indicators.generated_index")
        _REG = dict(gi.REGISTRY)
    return _REG


def _module(mod_name: str):
    if mod_name not in _MODS:
        _MODS[mod_name] = import_module(f"sentinel.indicators.{mod_name}")
    return _MODS[mod_name]


def list_indicators(family: str | None = None) -> list:
    reg = _registry()
    names = sorted(reg)
    if family == "trend":
        return [n for n in names if n.startswith("t_")]
    if family == "momentum":
        return [n for n in names if n.startswith("m_")]
    if family in ("vol", "volatility", "volume"):
        return [n for n in names if n.startswith("v_")]
    return names


def run_indicator(name: str, df: pd.DataFrame, **kw) -> pd.Series:
    reg = _registry()
    if name not in reg:
        raise KeyError(f"unknown indicator '{name}' ({len(reg)} available)")
    mod_name, func_name = reg[name]
    fn = getattr(_module(mod_name), func_name)
    return fn(df, **kw)


def run_many(names: list, df: pd.DataFrame, **kw) -> pd.DataFrame:
    cols = {}
    for n in names:
        try:
            cols[n] = run_indicator(n, df, **kw)
        except Exception:
            continue
    if not cols:
        return pd.DataFrame(index=df.index)
    return pd.DataFrame(cols, index=df.index)


def composite_trend(df: pd.DataFrame, top: int = 12) -> pd.Series:
    """Median blend of a rotating committee of trend rails (robust by construction)."""
    names = list_indicators("trend")[: max(1, top)]
    frame = run_many(names, df)
    if frame.empty:
        return pd.Series(0.0, index=df.index, name="composite_trend")
    return frame.median(axis=1).rename("composite_trend")


def composite_momentum(df: pd.DataFrame, top: int = 12) -> pd.Series:
    names = list_indicators("momentum")[: max(1, top)]
    frame = run_many(names, df)
    if frame.empty:
        return pd.Series(0.0, index=df.index, name="composite_momentum")
    return frame.median(axis=1).rename("composite_momentum")


def composite_pressure(df: pd.DataFrame, top: int = 12) -> pd.Series:
    names = list_indicators("vol")[: max(1, top)]
    frame = run_many(names, df)
    if frame.empty:
        return pd.Series(0.0, index=df.index, name="composite_pressure")
    return frame.median(axis=1).rename("composite_pressure")
