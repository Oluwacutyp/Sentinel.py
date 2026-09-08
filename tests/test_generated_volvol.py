"""AUTO-GENERATED smoke tests for generated_volatility_volume."""
from __future__ import annotations

import numpy as np
import pandas as pd

import sentinel.indicators.generated_volatility_volume as mod


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




def test_v_atr_channel_halo():
    df = _synth(300, 7)
    out = mod.v_atr_channel_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_halo(df, period=5, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_quantum():
    df = _synth(300, 8)
    out = mod.v_atr_channel_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_quantum(df, period=12, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_nebula():
    df = _synth(300, 9)
    out = mod.v_atr_channel_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_nebula(df, period=19, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_vortex():
    df = _synth(300, 10)
    out = mod.v_atr_channel_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_vortex(df, period=26, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_apex():
    df = _synth(300, 11)
    out = mod.v_atr_channel_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_apex(df, period=33, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_pulse():
    df = _synth(300, 12)
    out = mod.v_atr_channel_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_pulse(df, period=40, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_surge():
    df = _synth(300, 13)
    out = mod.v_atr_channel_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_surge(df, period=47, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_atr_channel_cascade():
    df = _synth(300, 14)
    out = mod.v_atr_channel_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_atr_channel_cascade(df, period=54, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_halo():
    df = _synth(300, 15)
    out = mod.v_keltner_halo_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_halo(df, period=6, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_quantum():
    df = _synth(300, 16)
    out = mod.v_keltner_halo_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_quantum(df, period=13, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_nebula():
    df = _synth(300, 17)
    out = mod.v_keltner_halo_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_nebula(df, period=20, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_vortex():
    df = _synth(300, 18)
    out = mod.v_keltner_halo_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_vortex(df, period=27, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_apex():
    df = _synth(300, 19)
    out = mod.v_keltner_halo_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_apex(df, period=34, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_pulse():
    df = _synth(300, 20)
    out = mod.v_keltner_halo_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_pulse(df, period=41, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_surge():
    df = _synth(300, 21)
    out = mod.v_keltner_halo_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_surge(df, period=48, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_keltner_halo_cascade():
    df = _synth(300, 22)
    out = mod.v_keltner_halo_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_keltner_halo_cascade(df, period=55, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_halo():
    df = _synth(300, 23)
    out = mod.v_bollinger_b_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_halo(df, period=7, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_quantum():
    df = _synth(300, 24)
    out = mod.v_bollinger_b_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_quantum(df, period=14, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_nebula():
    df = _synth(300, 25)
    out = mod.v_bollinger_b_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_nebula(df, period=21, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_vortex():
    df = _synth(300, 26)
    out = mod.v_bollinger_b_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_vortex(df, period=28, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_apex():
    df = _synth(300, 27)
    out = mod.v_bollinger_b_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_apex(df, period=35, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_pulse():
    df = _synth(300, 28)
    out = mod.v_bollinger_b_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_pulse(df, period=42, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_surge():
    df = _synth(300, 29)
    out = mod.v_bollinger_b_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_surge(df, period=49, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_bollinger_b_cascade():
    df = _synth(300, 30)
    out = mod.v_bollinger_b_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_bollinger_b_cascade(df, period=56, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_halo():
    df = _synth(300, 31)
    out = mod.v_skew_band_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_halo(df, period=8, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_quantum():
    df = _synth(300, 32)
    out = mod.v_skew_band_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_quantum(df, period=15, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_nebula():
    df = _synth(300, 33)
    out = mod.v_skew_band_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_nebula(df, period=22, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_vortex():
    df = _synth(300, 34)
    out = mod.v_skew_band_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_vortex(df, period=29, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_apex():
    df = _synth(300, 35)
    out = mod.v_skew_band_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_apex(df, period=36, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_pulse():
    df = _synth(300, 36)
    out = mod.v_skew_band_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_pulse(df, period=43, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_surge():
    df = _synth(300, 37)
    out = mod.v_skew_band_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_surge(df, period=50, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_skew_band_cascade():
    df = _synth(300, 38)
    out = mod.v_skew_band_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_skew_band_cascade(df, period=57, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_halo():
    df = _synth(300, 39)
    out = mod.v_pressure_flow_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_halo(df, period=9, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_quantum():
    df = _synth(300, 40)
    out = mod.v_pressure_flow_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_quantum(df, period=16, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_nebula():
    df = _synth(300, 41)
    out = mod.v_pressure_flow_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_nebula(df, period=23, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_vortex():
    df = _synth(300, 42)
    out = mod.v_pressure_flow_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_vortex(df, period=30, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_apex():
    df = _synth(300, 43)
    out = mod.v_pressure_flow_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_apex(df, period=37, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_pulse():
    df = _synth(300, 44)
    out = mod.v_pressure_flow_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_pulse(df, period=44, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_surge():
    df = _synth(300, 45)
    out = mod.v_pressure_flow_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_surge(df, period=51, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_pressure_flow_cascade():
    df = _synth(300, 46)
    out = mod.v_pressure_flow_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_pressure_flow_cascade(df, period=58, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_halo():
    df = _synth(300, 47)
    out = mod.v_volume_tide_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_halo(df, period=10, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_quantum():
    df = _synth(300, 48)
    out = mod.v_volume_tide_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_quantum(df, period=17, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_nebula():
    df = _synth(300, 49)
    out = mod.v_volume_tide_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_nebula(df, period=24, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_vortex():
    df = _synth(300, 50)
    out = mod.v_volume_tide_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_vortex(df, period=31, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_apex():
    df = _synth(300, 51)
    out = mod.v_volume_tide_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_apex(df, period=38, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_pulse():
    df = _synth(300, 52)
    out = mod.v_volume_tide_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_pulse(df, period=45, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_surge():
    df = _synth(300, 53)
    out = mod.v_volume_tide_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_surge(df, period=52, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_volume_tide_cascade():
    df = _synth(300, 54)
    out = mod.v_volume_tide_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_volume_tide_cascade(df, period=59, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_halo():
    df = _synth(300, 55)
    out = mod.v_range_squeeze_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_halo(df, period=11, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_quantum():
    df = _synth(300, 56)
    out = mod.v_range_squeeze_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_quantum(df, period=18, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_nebula():
    df = _synth(300, 57)
    out = mod.v_range_squeeze_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_nebula(df, period=25, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_vortex():
    df = _synth(300, 58)
    out = mod.v_range_squeeze_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_vortex(df, period=32, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_apex():
    df = _synth(300, 59)
    out = mod.v_range_squeeze_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_apex(df, period=39, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_pulse():
    df = _synth(300, 60)
    out = mod.v_range_squeeze_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_pulse(df, period=46, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_surge():
    df = _synth(300, 61)
    out = mod.v_range_squeeze_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_surge(df, period=53, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_range_squeeze_cascade():
    df = _synth(300, 62)
    out = mod.v_range_squeeze_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_range_squeeze_cascade(df, period=5, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_halo():
    df = _synth(300, 63)
    out = mod.v_band_rider_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_halo(df, period=12, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_quantum():
    df = _synth(300, 64)
    out = mod.v_band_rider_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_quantum(df, period=19, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_nebula():
    df = _synth(300, 65)
    out = mod.v_band_rider_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_nebula(df, period=26, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_vortex():
    df = _synth(300, 66)
    out = mod.v_band_rider_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_vortex(df, period=33, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_apex():
    df = _synth(300, 67)
    out = mod.v_band_rider_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_apex(df, period=40, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_pulse():
    df = _synth(300, 68)
    out = mod.v_band_rider_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_pulse(df, period=47, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_surge():
    df = _synth(300, 69)
    out = mod.v_band_rider_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_surge(df, period=54, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_band_rider_cascade():
    df = _synth(300, 70)
    out = mod.v_band_rider_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_band_rider_cascade(df, period=6, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_halo():
    df = _synth(300, 71)
    out = mod.v_chaos_gauge_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_halo(df, period=13, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_quantum():
    df = _synth(300, 72)
    out = mod.v_chaos_gauge_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_quantum(df, period=20, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_nebula():
    df = _synth(300, 73)
    out = mod.v_chaos_gauge_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_nebula(df, period=27, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_vortex():
    df = _synth(300, 74)
    out = mod.v_chaos_gauge_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_vortex(df, period=34, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_apex():
    df = _synth(300, 75)
    out = mod.v_chaos_gauge_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_apex(df, period=41, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_pulse():
    df = _synth(300, 76)
    out = mod.v_chaos_gauge_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_pulse(df, period=48, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_surge():
    df = _synth(300, 77)
    out = mod.v_chaos_gauge_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_surge(df, period=55, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_chaos_gauge_cascade():
    df = _synth(300, 78)
    out = mod.v_chaos_gauge_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_chaos_gauge_cascade(df, period=7, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_halo():
    df = _synth(300, 79)
    out = mod.v_tide_osc_halo(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_halo(df, period=14, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_quantum():
    df = _synth(300, 80)
    out = mod.v_tide_osc_quantum(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_quantum(df, period=21, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_nebula():
    df = _synth(300, 81)
    out = mod.v_tide_osc_nebula(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_nebula(df, period=28, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_vortex():
    df = _synth(300, 82)
    out = mod.v_tide_osc_vortex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_vortex(df, period=35, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_apex():
    df = _synth(300, 83)
    out = mod.v_tide_osc_apex(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_apex(df, period=42, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_pulse():
    df = _synth(300, 84)
    out = mod.v_tide_osc_pulse(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_pulse(df, period=49, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_surge():
    df = _synth(300, 85)
    out = mod.v_tide_osc_surge(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_surge(df, period=56, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()


def test_v_tide_osc_cascade():
    df = _synth(300, 86)
    out = mod.v_tide_osc_cascade(df)
    assert len(out) == len(df)
    assert np.isfinite(out.to_numpy(dtype=float)).all()
    out2 = mod.v_tide_osc_cascade(df, period=8, adapt=False)
    assert len(out2) == len(df)
    assert np.isfinite(out2.to_numpy(dtype=float)).all()

