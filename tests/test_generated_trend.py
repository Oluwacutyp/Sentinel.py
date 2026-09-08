"""AUTO-GENERATED smoke tests for generated_trend."""
from __future__ import annotations

import numpy as np
import pandas as pd

import sentinel.indicators.generated_trend as mod


def _synth(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    close = 100.0 * np.exp(np.cumsum(rets))
    spread = np.abs(rng.normal(0.0, 0.005, n))
    open_ = close * (1 + rng.normal(0, 0.002, n))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    vol = np.abs(rng.normal(1000, 200, n))
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol})




def test_t_ema_cascade_halo():
    df = _synth(300, 7)
    out = mod.t_ema_cascade_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_halo(df, period=5, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_quantum():
    df = _synth(300, 8)
    out = mod.t_ema_cascade_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_quantum(df, period=12, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_nebula():
    df = _synth(300, 9)
    out = mod.t_ema_cascade_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_nebula(df, period=19, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_vortex():
    df = _synth(300, 10)
    out = mod.t_ema_cascade_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_vortex(df, period=26, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_apex():
    df = _synth(300, 11)
    out = mod.t_ema_cascade_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_apex(df, period=33, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_pulse():
    df = _synth(300, 12)
    out = mod.t_ema_cascade_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_pulse(df, period=40, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_surge():
    df = _synth(300, 13)
    out = mod.t_ema_cascade_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_surge(df, period=47, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ema_cascade_cascade():
    df = _synth(300, 14)
    out = mod.t_ema_cascade_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ema_cascade_cascade(df, period=54, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_halo():
    df = _synth(300, 15)
    out = mod.t_hull_drift_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_halo(df, period=6, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_quantum():
    df = _synth(300, 16)
    out = mod.t_hull_drift_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_quantum(df, period=13, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_nebula():
    df = _synth(300, 17)
    out = mod.t_hull_drift_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_nebula(df, period=20, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_vortex():
    df = _synth(300, 18)
    out = mod.t_hull_drift_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_vortex(df, period=27, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_apex():
    df = _synth(300, 19)
    out = mod.t_hull_drift_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_apex(df, period=34, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_pulse():
    df = _synth(300, 20)
    out = mod.t_hull_drift_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_pulse(df, period=41, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_surge():
    df = _synth(300, 21)
    out = mod.t_hull_drift_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_surge(df, period=48, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_hull_drift_cascade():
    df = _synth(300, 22)
    out = mod.t_hull_drift_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_hull_drift_cascade(df, period=55, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_halo():
    df = _synth(300, 23)
    out = mod.t_kama_glide_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_halo(df, period=7, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_quantum():
    df = _synth(300, 24)
    out = mod.t_kama_glide_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_quantum(df, period=14, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_nebula():
    df = _synth(300, 25)
    out = mod.t_kama_glide_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_nebula(df, period=21, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_vortex():
    df = _synth(300, 26)
    out = mod.t_kama_glide_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_vortex(df, period=28, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_apex():
    df = _synth(300, 27)
    out = mod.t_kama_glide_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_apex(df, period=35, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_pulse():
    df = _synth(300, 28)
    out = mod.t_kama_glide_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_pulse(df, period=42, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_surge():
    df = _synth(300, 29)
    out = mod.t_kama_glide_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_surge(df, period=49, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_kama_glide_cascade():
    df = _synth(300, 30)
    out = mod.t_kama_glide_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_kama_glide_cascade(df, period=56, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_halo():
    df = _synth(300, 31)
    out = mod.t_t3_silk_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_halo(df, period=8, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_quantum():
    df = _synth(300, 32)
    out = mod.t_t3_silk_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_quantum(df, period=15, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_nebula():
    df = _synth(300, 33)
    out = mod.t_t3_silk_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_nebula(df, period=22, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_vortex():
    df = _synth(300, 34)
    out = mod.t_t3_silk_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_vortex(df, period=29, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_apex():
    df = _synth(300, 35)
    out = mod.t_t3_silk_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_apex(df, period=36, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_pulse():
    df = _synth(300, 36)
    out = mod.t_t3_silk_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_pulse(df, period=43, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_surge():
    df = _synth(300, 37)
    out = mod.t_t3_silk_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_surge(df, period=50, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_t3_silk_cascade():
    df = _synth(300, 38)
    out = mod.t_t3_silk_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_t3_silk_cascade(df, period=57, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_halo():
    df = _synth(300, 39)
    out = mod.t_dema_rail_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_halo(df, period=9, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_quantum():
    df = _synth(300, 40)
    out = mod.t_dema_rail_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_quantum(df, period=16, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_nebula():
    df = _synth(300, 41)
    out = mod.t_dema_rail_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_nebula(df, period=23, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_vortex():
    df = _synth(300, 42)
    out = mod.t_dema_rail_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_vortex(df, period=30, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_apex():
    df = _synth(300, 43)
    out = mod.t_dema_rail_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_apex(df, period=37, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_pulse():
    df = _synth(300, 44)
    out = mod.t_dema_rail_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_pulse(df, period=44, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_surge():
    df = _synth(300, 45)
    out = mod.t_dema_rail_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_surge(df, period=51, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_dema_rail_cascade():
    df = _synth(300, 46)
    out = mod.t_dema_rail_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_dema_rail_cascade(df, period=58, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_halo():
    df = _synth(300, 47)
    out = mod.t_tema_arc_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_halo(df, period=10, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_quantum():
    df = _synth(300, 48)
    out = mod.t_tema_arc_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_quantum(df, period=17, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_nebula():
    df = _synth(300, 49)
    out = mod.t_tema_arc_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_nebula(df, period=24, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_vortex():
    df = _synth(300, 50)
    out = mod.t_tema_arc_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_vortex(df, period=31, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_apex():
    df = _synth(300, 51)
    out = mod.t_tema_arc_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_apex(df, period=38, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_pulse():
    df = _synth(300, 52)
    out = mod.t_tema_arc_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_pulse(df, period=45, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_surge():
    df = _synth(300, 53)
    out = mod.t_tema_arc_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_surge(df, period=52, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tema_arc_cascade():
    df = _synth(300, 54)
    out = mod.t_tema_arc_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tema_arc_cascade(df, period=59, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_halo():
    df = _synth(300, 55)
    out = mod.t_wma_stream_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_halo(df, period=11, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_quantum():
    df = _synth(300, 56)
    out = mod.t_wma_stream_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_quantum(df, period=18, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_nebula():
    df = _synth(300, 57)
    out = mod.t_wma_stream_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_nebula(df, period=25, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_vortex():
    df = _synth(300, 58)
    out = mod.t_wma_stream_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_vortex(df, period=32, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_apex():
    df = _synth(300, 59)
    out = mod.t_wma_stream_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_apex(df, period=39, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_pulse():
    df = _synth(300, 60)
    out = mod.t_wma_stream_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_pulse(df, period=46, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_surge():
    df = _synth(300, 61)
    out = mod.t_wma_stream_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_surge(df, period=53, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_wma_stream_cascade():
    df = _synth(300, 62)
    out = mod.t_wma_stream_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_wma_stream_cascade(df, period=5, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_halo():
    df = _synth(300, 63)
    out = mod.t_zlema_orbit_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_halo(df, period=12, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_quantum():
    df = _synth(300, 64)
    out = mod.t_zlema_orbit_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_quantum(df, period=19, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_nebula():
    df = _synth(300, 65)
    out = mod.t_zlema_orbit_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_nebula(df, period=26, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_vortex():
    df = _synth(300, 66)
    out = mod.t_zlema_orbit_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_vortex(df, period=33, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_apex():
    df = _synth(300, 67)
    out = mod.t_zlema_orbit_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_apex(df, period=40, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_pulse():
    df = _synth(300, 68)
    out = mod.t_zlema_orbit_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_pulse(df, period=47, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_surge():
    df = _synth(300, 69)
    out = mod.t_zlema_orbit_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_surge(df, period=54, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_zlema_orbit_cascade():
    df = _synth(300, 70)
    out = mod.t_zlema_orbit_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_zlema_orbit_cascade(df, period=6, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_halo():
    df = _synth(300, 71)
    out = mod.t_tilson_halo_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_halo(df, period=13, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_quantum():
    df = _synth(300, 72)
    out = mod.t_tilson_halo_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_quantum(df, period=20, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_nebula():
    df = _synth(300, 73)
    out = mod.t_tilson_halo_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_nebula(df, period=27, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_vortex():
    df = _synth(300, 74)
    out = mod.t_tilson_halo_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_vortex(df, period=34, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_apex():
    df = _synth(300, 75)
    out = mod.t_tilson_halo_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_apex(df, period=41, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_pulse():
    df = _synth(300, 76)
    out = mod.t_tilson_halo_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_pulse(df, period=48, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_surge():
    df = _synth(300, 77)
    out = mod.t_tilson_halo_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_surge(df, period=55, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_tilson_halo_cascade():
    df = _synth(300, 78)
    out = mod.t_tilson_halo_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_tilson_halo_cascade(df, period=7, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_halo():
    df = _synth(300, 79)
    out = mod.t_ribbon_nexus_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_halo(df, period=14, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_quantum():
    df = _synth(300, 80)
    out = mod.t_ribbon_nexus_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_quantum(df, period=21, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_nebula():
    df = _synth(300, 81)
    out = mod.t_ribbon_nexus_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_nebula(df, period=28, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_vortex():
    df = _synth(300, 82)
    out = mod.t_ribbon_nexus_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_vortex(df, period=35, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_apex():
    df = _synth(300, 83)
    out = mod.t_ribbon_nexus_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_apex(df, period=42, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_pulse():
    df = _synth(300, 84)
    out = mod.t_ribbon_nexus_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_pulse(df, period=49, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_surge():
    df = _synth(300, 85)
    out = mod.t_ribbon_nexus_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_surge(df, period=56, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_t_ribbon_nexus_cascade():
    df = _synth(300, 86)
    out = mod.t_ribbon_nexus_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.t_ribbon_nexus_cascade(df, period=8, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()

