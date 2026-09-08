"""AUTO-GENERATED smoke tests for generated_momentum."""
from __future__ import annotations

import numpy as np
import pandas as pd

import sentinel.indicators.generated_momentum as mod


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




def test_m_rsi_stoch_halo():
    df = _synth(300, 7)
    out = mod.m_rsi_stoch_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_halo(df, period=5, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_quantum():
    df = _synth(300, 8)
    out = mod.m_rsi_stoch_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_quantum(df, period=12, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_nebula():
    df = _synth(300, 9)
    out = mod.m_rsi_stoch_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_nebula(df, period=19, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_vortex():
    df = _synth(300, 10)
    out = mod.m_rsi_stoch_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_vortex(df, period=26, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_apex():
    df = _synth(300, 11)
    out = mod.m_rsi_stoch_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_apex(df, period=33, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_pulse():
    df = _synth(300, 12)
    out = mod.m_rsi_stoch_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_pulse(df, period=40, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_surge():
    df = _synth(300, 13)
    out = mod.m_rsi_stoch_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_surge(df, period=47, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_rsi_stoch_cascade():
    df = _synth(300, 14)
    out = mod.m_rsi_stoch_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_rsi_stoch_cascade(df, period=54, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_halo():
    df = _synth(300, 15)
    out = mod.m_macd_hist_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_halo(df, period=6, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_quantum():
    df = _synth(300, 16)
    out = mod.m_macd_hist_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_quantum(df, period=13, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_nebula():
    df = _synth(300, 17)
    out = mod.m_macd_hist_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_nebula(df, period=20, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_vortex():
    df = _synth(300, 18)
    out = mod.m_macd_hist_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_vortex(df, period=27, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_apex():
    df = _synth(300, 19)
    out = mod.m_macd_hist_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_apex(df, period=34, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_pulse():
    df = _synth(300, 20)
    out = mod.m_macd_hist_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_pulse(df, period=41, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_surge():
    df = _synth(300, 21)
    out = mod.m_macd_hist_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_surge(df, period=48, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_macd_hist_cascade():
    df = _synth(300, 22)
    out = mod.m_macd_hist_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_macd_hist_cascade(df, period=55, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_halo():
    df = _synth(300, 23)
    out = mod.m_roc_zscore_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_halo(df, period=7, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_quantum():
    df = _synth(300, 24)
    out = mod.m_roc_zscore_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_quantum(df, period=14, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_nebula():
    df = _synth(300, 25)
    out = mod.m_roc_zscore_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_nebula(df, period=21, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_vortex():
    df = _synth(300, 26)
    out = mod.m_roc_zscore_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_vortex(df, period=28, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_apex():
    df = _synth(300, 27)
    out = mod.m_roc_zscore_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_apex(df, period=35, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_pulse():
    df = _synth(300, 28)
    out = mod.m_roc_zscore_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_pulse(df, period=42, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_surge():
    df = _synth(300, 29)
    out = mod.m_roc_zscore_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_surge(df, period=49, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_roc_zscore_cascade():
    df = _synth(300, 30)
    out = mod.m_roc_zscore_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_roc_zscore_cascade(df, period=56, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_halo():
    df = _synth(300, 31)
    out = mod.m_impulse_wave_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_halo(df, period=8, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_quantum():
    df = _synth(300, 32)
    out = mod.m_impulse_wave_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_quantum(df, period=15, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_nebula():
    df = _synth(300, 33)
    out = mod.m_impulse_wave_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_nebula(df, period=22, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_vortex():
    df = _synth(300, 34)
    out = mod.m_impulse_wave_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_vortex(df, period=29, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_apex():
    df = _synth(300, 35)
    out = mod.m_impulse_wave_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_apex(df, period=36, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_pulse():
    df = _synth(300, 36)
    out = mod.m_impulse_wave_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_pulse(df, period=43, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_surge():
    df = _synth(300, 37)
    out = mod.m_impulse_wave_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_surge(df, period=50, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_impulse_wave_cascade():
    df = _synth(300, 38)
    out = mod.m_impulse_wave_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_impulse_wave_cascade(df, period=57, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_halo():
    df = _synth(300, 39)
    out = mod.m_velocity_arc_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_halo(df, period=9, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_quantum():
    df = _synth(300, 40)
    out = mod.m_velocity_arc_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_quantum(df, period=16, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_nebula():
    df = _synth(300, 41)
    out = mod.m_velocity_arc_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_nebula(df, period=23, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_vortex():
    df = _synth(300, 42)
    out = mod.m_velocity_arc_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_vortex(df, period=30, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_apex():
    df = _synth(300, 43)
    out = mod.m_velocity_arc_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_apex(df, period=37, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_pulse():
    df = _synth(300, 44)
    out = mod.m_velocity_arc_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_pulse(df, period=44, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_surge():
    df = _synth(300, 45)
    out = mod.m_velocity_arc_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_surge(df, period=51, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_velocity_arc_cascade():
    df = _synth(300, 46)
    out = mod.m_velocity_arc_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_velocity_arc_cascade(df, period=58, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_halo():
    df = _synth(300, 47)
    out = mod.m_thrust_gauge_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_halo(df, period=10, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_quantum():
    df = _synth(300, 48)
    out = mod.m_thrust_gauge_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_quantum(df, period=17, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_nebula():
    df = _synth(300, 49)
    out = mod.m_thrust_gauge_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_nebula(df, period=24, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_vortex():
    df = _synth(300, 50)
    out = mod.m_thrust_gauge_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_vortex(df, period=31, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_apex():
    df = _synth(300, 51)
    out = mod.m_thrust_gauge_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_apex(df, period=38, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_pulse():
    df = _synth(300, 52)
    out = mod.m_thrust_gauge_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_pulse(df, period=45, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_surge():
    df = _synth(300, 53)
    out = mod.m_thrust_gauge_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_surge(df, period=52, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_thrust_gauge_cascade():
    df = _synth(300, 54)
    out = mod.m_thrust_gauge_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_thrust_gauge_cascade(df, period=59, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_halo():
    df = _synth(300, 55)
    out = mod.m_surge_osc_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_halo(df, period=11, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_quantum():
    df = _synth(300, 56)
    out = mod.m_surge_osc_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_quantum(df, period=18, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_nebula():
    df = _synth(300, 57)
    out = mod.m_surge_osc_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_nebula(df, period=25, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_vortex():
    df = _synth(300, 58)
    out = mod.m_surge_osc_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_vortex(df, period=32, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_apex():
    df = _synth(300, 59)
    out = mod.m_surge_osc_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_apex(df, period=39, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_pulse():
    df = _synth(300, 60)
    out = mod.m_surge_osc_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_pulse(df, period=46, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_surge():
    df = _synth(300, 61)
    out = mod.m_surge_osc_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_surge(df, period=53, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_surge_osc_cascade():
    df = _synth(300, 62)
    out = mod.m_surge_osc_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_surge_osc_cascade(df, period=5, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_halo():
    df = _synth(300, 63)
    out = mod.m_torque_line_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_halo(df, period=12, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_quantum():
    df = _synth(300, 64)
    out = mod.m_torque_line_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_quantum(df, period=19, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_nebula():
    df = _synth(300, 65)
    out = mod.m_torque_line_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_nebula(df, period=26, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_vortex():
    df = _synth(300, 66)
    out = mod.m_torque_line_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_vortex(df, period=33, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_apex():
    df = _synth(300, 67)
    out = mod.m_torque_line_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_apex(df, period=40, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_pulse():
    df = _synth(300, 68)
    out = mod.m_torque_line_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_pulse(df, period=47, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_surge():
    df = _synth(300, 69)
    out = mod.m_torque_line_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_surge(df, period=54, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_torque_line_cascade():
    df = _synth(300, 70)
    out = mod.m_torque_line_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_torque_line_cascade(df, period=6, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_halo():
    df = _synth(300, 71)
    out = mod.m_eddy_flow_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_halo(df, period=13, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_quantum():
    df = _synth(300, 72)
    out = mod.m_eddy_flow_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_quantum(df, period=20, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_nebula():
    df = _synth(300, 73)
    out = mod.m_eddy_flow_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_nebula(df, period=27, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_vortex():
    df = _synth(300, 74)
    out = mod.m_eddy_flow_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_vortex(df, period=34, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_apex():
    df = _synth(300, 75)
    out = mod.m_eddy_flow_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_apex(df, period=41, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_pulse():
    df = _synth(300, 76)
    out = mod.m_eddy_flow_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_pulse(df, period=48, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_surge():
    df = _synth(300, 77)
    out = mod.m_eddy_flow_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_surge(df, period=55, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_eddy_flow_cascade():
    df = _synth(300, 78)
    out = mod.m_eddy_flow_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_eddy_flow_cascade(df, period=7, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_halo():
    df = _synth(300, 79)
    out = mod.m_quasar_mom_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_halo(df, period=14, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_quantum():
    df = _synth(300, 80)
    out = mod.m_quasar_mom_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_quantum(df, period=21, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_nebula():
    df = _synth(300, 81)
    out = mod.m_quasar_mom_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_nebula(df, period=28, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_vortex():
    df = _synth(300, 82)
    out = mod.m_quasar_mom_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_vortex(df, period=35, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_apex():
    df = _synth(300, 83)
    out = mod.m_quasar_mom_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_apex(df, period=42, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_pulse():
    df = _synth(300, 84)
    out = mod.m_quasar_mom_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_pulse(df, period=49, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_surge():
    df = _synth(300, 85)
    out = mod.m_quasar_mom_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_surge(df, period=56, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_m_quasar_mom_cascade():
    df = _synth(300, 86)
    out = mod.m_quasar_mom_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.m_quasar_mom_cascade(df, period=8, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()

