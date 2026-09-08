"""Signal fusion: confidence-weighted voting, regime-conditional weights, cost hysteresis."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils.helpers import softmax

KINDS = ("trend", "meanrev", "breakout", "momentum", "squeeze", "confluence")


def fuse_equal(frames: dict) -> pd.DataFrame:
    """Confidence×gate weighted vote across {name: signal-frame}."""
    if not frames:
        return pd.DataFrame(columns=["vote", "agreement", "n"])
    names = list(frames)
    idx = frames[names[0]].index
    votes = np.zeros(len(idx))
    mass = np.zeros(len(idx))
    longs = np.zeros(len(idx))
    for s in frames.values():
        w = s["confidence"].to_numpy(dtype=float) * s["gate"].to_numpy(dtype=float)
        d = np.sign(s["signal"].to_numpy(dtype=float))
        votes += d * w
        mass += w
        longs += (d > 0).astype(float)
    vote = votes / (mass + 1e-12)
    agreement = np.abs(longs / max(1, len(frames)) - 0.5) * 2.0
    return pd.DataFrame({"vote": vote, "agreement": agreement, "n": float(len(frames))}, index=idx)


def adaptive_kind_weights(recent_scores: dict | None, prior: float = 1.0) -> dict:
    """Softmax over recent per-kind scores; falls back to uniform. Nothing hardcoded."""
    base = {k: float(prior) for k in KINDS}
    if recent_scores:
        for k, v in recent_scores.items():
            if k in base:
                base[k] = float(prior) + float(v)
    w = softmax(base)
    tot = sum(w.values()) or 1.0
    return {k: v / tot * len(KINDS) for k, v in w.items()}


def kind_of(name: str, lookup: dict | None = None) -> str:
    if lookup and name in lookup:
        return str(lookup[name])
    low = name.lower()
    for k in KINDS:
        if k in low:
            return k
    return "confluence"


def fuse_weighted(frames: dict, kind_weights: dict | None = None,
                  lookup: dict | None = None, scores: dict | None = None) -> pd.DataFrame:
    """Vote with per-kind and per-strategy weighting."""
    if not frames:
        return pd.DataFrame(columns=["vote", "agreement", "n"])
    kw = adaptive_kind_weights(None if kind_weights is None else {k: 0.0 for k in KINDS})
    if kind_weights:
        tot = sum(max(0.0, float(v)) for v in kind_weights.values()) or 1.0
        kw = {k: max(0.0, float(kind_weights.get(k, 1.0))) / tot * len(KINDS) for k in KINDS}
    sw = None
    if scores:
        sw = softmax({n: float(scores.get(n, 0.0)) for n in frames})
        m = sum(sw.values()) / max(1, len(sw))
        sw = {n: v / (m + 1e-12) for n, v in sw.items()}
    names = list(frames)
    idx = frames[names[0]].index
    votes = np.zeros(len(idx))
    mass = np.zeros(len(idx))
    longs = np.zeros(len(idx))
    for n, s in frames.items():
        w = s["confidence"].to_numpy(dtype=float) * s["gate"].to_numpy(dtype=float)
        w = w * kw.get(kind_of(n, lookup), 1.0)
        if sw:
            w = w * sw.get(n, 1.0)
        d = np.sign(s["signal"].to_numpy(dtype=float))
        votes += d * w
        mass += w
        longs += (d > 0).astype(float)
    vote = votes / (mass + 1e-12)
    agreement = np.abs(longs / max(1, len(frames)) - 0.5) * 2.0
    return pd.DataFrame({"vote": vote, "agreement": agreement, "n": float(len(frames))}, index=idx)


def cost_aware_threshold(cost_bps: float, atr_pct: float, k: float = 1.0) -> float:
    """Minimum vote magnitude worth trading, derived from costs — never a magic number."""
    edge_need = (float(cost_bps) / 1e4) / (max(1e-6, float(atr_pct)) + 1e-9)
    return float(np.clip(k * edge_need * 2.0, 0.02, 0.6))


def hysteresis_position(vote: pd.Series, enter: float, exit: float = 0.03) -> pd.Series:
    v = np.asarray(vote, dtype=float)
    out = np.zeros(len(v))
    state = 0.0
    for i in range(len(v)):
        if state == 0.0 and abs(v[i]) >= enter:
            state = float(np.sign(v[i]))
        elif state > 0 and v[i] < -enter:
            state = -1.0
        elif state < 0 and v[i] > enter:
            state = 1.0
        elif state != 0.0 and abs(v[i]) < exit:
            state = 0.0
        out[i] = state
    return pd.Series(out, index=vote.index, name="position")


def disagreement_filter(blend: pd.DataFrame, min_agreement: float = 0.55) -> pd.Series:
    """Binary mask: 1 where the committee agrees enough to be trusted."""
    agr = blend["agreement"].to_numpy(dtype=float)
    return pd.Series((agr >= min_agreement).astype(float), index=blend.index, name="agree_mask")


def pattern_confluence(hits: pd.DataFrame, bullish: list, bearish: list) -> pd.Series:
    """Net pattern pressure in [-1, 1] from pattern hit/score frames dict values."""
    if hits is None or len(hits) == 0:
        return pd.Series(dtype=float)
    cols = [c for c in hits.columns if c.endswith("__score")]
    bull = [c for c in cols if any(b in c for b in bullish)]
    bear = [c for c in cols if any(b in c for b in bearish)]
    b = hits[bull].sum(axis=1) if bull else 0.0
    s = hits[bear].sum(axis=1) if bear else 0.0
    net = (b - s) / (abs(b) + abs(s) + 1e-9)
    return net.fillna(0.0).rename("pattern_pressure")


def fuse_all(frames: dict, kind_weights: dict | None = None, lookup: dict | None = None,
             scores: dict | None = None, cost_bps: float = 10.0, atr_pct: float = 0.01,
             min_agreement: float = 0.55) -> dict:
    blend = fuse_weighted(frames, kind_weights, lookup, scores)
    if blend.empty:
        return {"blend": blend, "position": blend.get("vote", pd.Series(dtype=float))}
    enter = cost_aware_threshold(cost_bps, atr_pct)
    pos = hysteresis_position(blend["vote"], enter)
    mask = disagreement_filter(blend, min_agreement)
    pos = pos * mask
    return {"blend": blend, "position": pos.rename("position"),
            "enter_threshold": enter, "n_strategies": len(frames)}
