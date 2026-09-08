"""AUTO-GENERATED smoke tests for generated_charts."""
from __future__ import annotations

import numpy as np
import pandas as pd

import sentinel.patterns.generated_charts as mod


def _synth(n=300, seed=17):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0002, 0.015, n)
    close = 200.0 * np.exp(np.cumsum(rets))
    spread = np.abs(rng.normal(0.0, 0.008, n))
    open_ = close * (1 + rng.normal(0, 0.003, n))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread)
    vol = np.abs(rng.normal(2000, 500, n))
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol})




def test_ch_fractal_break_up():
    df = _synth(300, 17)
    res = mod.ch_fractal_break_up(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_fractal_break_down():
    df = _synth(300, 18)
    res = mod.ch_fractal_break_down(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_swing_high_breach():
    df = _synth(300, 19)
    res = mod.ch_swing_high_breach(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_swing_low_breach():
    df = _synth(300, 20)
    res = mod.ch_swing_low_breach(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_channel_ride_up():
    df = _synth(300, 21)
    res = mod.ch_channel_ride_up(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_channel_ride_down():
    df = _synth(300, 22)
    res = mod.ch_channel_ride_down(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_squeeze_pop_up():
    df = _synth(300, 23)
    res = mod.ch_squeeze_pop_up(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_squeeze_pop_down():
    df = _synth(300, 24)
    res = mod.ch_squeeze_pop_down(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_range_edge_top():
    df = _synth(300, 25)
    res = mod.ch_range_edge_top(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_range_edge_bottom():
    df = _synth(300, 26)
    res = mod.ch_range_edge_bottom(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_higher_high_run():
    df = _synth(300, 27)
    res = mod.ch_higher_high_run(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_lower_low_run():
    df = _synth(300, 28)
    res = mod.ch_lower_low_run(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_higher_low_stair():
    df = _synth(300, 29)
    res = mod.ch_higher_low_stair(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_lower_high_stair():
    df = _synth(300, 30)
    res = mod.ch_lower_high_stair(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_parabolic_tip():
    df = _synth(300, 31)
    res = mod.ch_parabolic_tip(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_capitulation_wick():
    df = _synth(300, 32)
    res = mod.ch_capitulation_wick(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_spring_washout():
    df = _synth(300, 33)
    res = mod.ch_spring_washout(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_upthrust_trap():
    df = _synth(300, 34)
    res = mod.ch_upthrust_trap(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_accordion_squeeze():
    df = _synth(300, 35)
    res = mod.ch_accordion_squeeze(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_megaphone_top():
    df = _synth(300, 36)
    res = mod.ch_megaphone_top(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_megaphone_bottom():
    df = _synth(300, 37)
    res = mod.ch_megaphone_bottom(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_flagpole_up():
    df = _synth(300, 38)
    res = mod.ch_flagpole_up(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_flagpole_down():
    df = _synth(300, 39)
    res = mod.ch_flagpole_down(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_pennant_coil():
    df = _synth(300, 40)
    res = mod.ch_pennant_coil(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_wedge_rising():
    df = _synth(300, 41)
    res = mod.ch_wedge_rising(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_wedge_falling():
    df = _synth(300, 42)
    res = mod.ch_wedge_falling(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_triple_tap_top():
    df = _synth(300, 43)
    res = mod.ch_triple_tap_top(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_triple_tap_bottom():
    df = _synth(300, 44)
    res = mod.ch_triple_tap_bottom(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_round_trip_reclaim():
    df = _synth(300, 45)
    res = mod.ch_round_trip_reclaim(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_ch_round_trip_reject():
    df = _synth(300, 46)
    res = mod.ch_round_trip_reject(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()

