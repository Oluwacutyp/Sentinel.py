"""AUTO-GENERATED smoke tests for generated_candles."""
from __future__ import annotations

import numpy as np
import pandas as pd

import sentinel.patterns.generated_candles as mod


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




def test_cdl_doji_strict():
    df = _synth(300, 17)
    res = mod.cdl_doji_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_doji_loose():
    df = _synth(300, 18)
    res = mod.cdl_doji_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_dragonfly_doji_strict():
    df = _synth(300, 19)
    res = mod.cdl_dragonfly_doji_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_dragonfly_doji_loose():
    df = _synth(300, 20)
    res = mod.cdl_dragonfly_doji_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_gravestone_doji_strict():
    df = _synth(300, 21)
    res = mod.cdl_gravestone_doji_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_gravestone_doji_loose():
    df = _synth(300, 22)
    res = mod.cdl_gravestone_doji_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_hammer_strict():
    df = _synth(300, 23)
    res = mod.cdl_hammer_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_hammer_loose():
    df = _synth(300, 24)
    res = mod.cdl_hammer_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_inverted_hammer_strict():
    df = _synth(300, 25)
    res = mod.cdl_inverted_hammer_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_inverted_hammer_loose():
    df = _synth(300, 26)
    res = mod.cdl_inverted_hammer_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_hanging_man_strict():
    df = _synth(300, 27)
    res = mod.cdl_hanging_man_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_hanging_man_loose():
    df = _synth(300, 28)
    res = mod.cdl_hanging_man_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_shooting_star_strict():
    df = _synth(300, 29)
    res = mod.cdl_shooting_star_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_shooting_star_loose():
    df = _synth(300, 30)
    res = mod.cdl_shooting_star_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_spinning_top_strict():
    df = _synth(300, 31)
    res = mod.cdl_spinning_top_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_spinning_top_loose():
    df = _synth(300, 32)
    res = mod.cdl_spinning_top_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_marubozu_bull_strict():
    df = _synth(300, 33)
    res = mod.cdl_marubozu_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_marubozu_bull_loose():
    df = _synth(300, 34)
    res = mod.cdl_marubozu_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_marubozu_bear_strict():
    df = _synth(300, 35)
    res = mod.cdl_marubozu_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_marubozu_bear_loose():
    df = _synth(300, 36)
    res = mod.cdl_marubozu_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_belt_hold_bull_strict():
    df = _synth(300, 37)
    res = mod.cdl_belt_hold_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_belt_hold_bull_loose():
    df = _synth(300, 38)
    res = mod.cdl_belt_hold_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_belt_hold_bear_strict():
    df = _synth(300, 39)
    res = mod.cdl_belt_hold_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_belt_hold_bear_loose():
    df = _synth(300, 40)
    res = mod.cdl_belt_hold_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_engulfing_bull_strict():
    df = _synth(300, 41)
    res = mod.cdl_engulfing_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_engulfing_bull_loose():
    df = _synth(300, 42)
    res = mod.cdl_engulfing_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_engulfing_bear_strict():
    df = _synth(300, 43)
    res = mod.cdl_engulfing_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_engulfing_bear_loose():
    df = _synth(300, 44)
    res = mod.cdl_engulfing_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_bull_strict():
    df = _synth(300, 45)
    res = mod.cdl_harami_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_bull_loose():
    df = _synth(300, 46)
    res = mod.cdl_harami_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_bear_strict():
    df = _synth(300, 47)
    res = mod.cdl_harami_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_bear_loose():
    df = _synth(300, 48)
    res = mod.cdl_harami_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_cross_bull_strict():
    df = _synth(300, 49)
    res = mod.cdl_harami_cross_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_cross_bull_loose():
    df = _synth(300, 50)
    res = mod.cdl_harami_cross_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_cross_bear_strict():
    df = _synth(300, 51)
    res = mod.cdl_harami_cross_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_harami_cross_bear_loose():
    df = _synth(300, 52)
    res = mod.cdl_harami_cross_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_piercing_strict():
    df = _synth(300, 53)
    res = mod.cdl_piercing_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_piercing_loose():
    df = _synth(300, 54)
    res = mod.cdl_piercing_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_dark_cloud_strict():
    df = _synth(300, 55)
    res = mod.cdl_dark_cloud_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_dark_cloud_loose():
    df = _synth(300, 56)
    res = mod.cdl_dark_cloud_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tweezer_top_strict():
    df = _synth(300, 57)
    res = mod.cdl_tweezer_top_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tweezer_top_loose():
    df = _synth(300, 58)
    res = mod.cdl_tweezer_top_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tweezer_bottom_strict():
    df = _synth(300, 59)
    res = mod.cdl_tweezer_bottom_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tweezer_bottom_loose():
    df = _synth(300, 60)
    res = mod.cdl_tweezer_bottom_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_kicker_bull_strict():
    df = _synth(300, 61)
    res = mod.cdl_kicker_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_kicker_bull_loose():
    df = _synth(300, 62)
    res = mod.cdl_kicker_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_kicker_bear_strict():
    df = _synth(300, 63)
    res = mod.cdl_kicker_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_kicker_bear_loose():
    df = _synth(300, 64)
    res = mod.cdl_kicker_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tasuki_up_strict():
    df = _synth(300, 65)
    res = mod.cdl_tasuki_up_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tasuki_up_loose():
    df = _synth(300, 66)
    res = mod.cdl_tasuki_up_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tasuki_down_strict():
    df = _synth(300, 67)
    res = mod.cdl_tasuki_down_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tasuki_down_loose():
    df = _synth(300, 68)
    res = mod.cdl_tasuki_down_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_mat_hold_bull_strict():
    df = _synth(300, 69)
    res = mod.cdl_mat_hold_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_mat_hold_bull_loose():
    df = _synth(300, 70)
    res = mod.cdl_mat_hold_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_mat_hold_bear_strict():
    df = _synth(300, 71)
    res = mod.cdl_mat_hold_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_mat_hold_bear_loose():
    df = _synth(300, 72)
    res = mod.cdl_mat_hold_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_rising_three_strict():
    df = _synth(300, 73)
    res = mod.cdl_rising_three_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_rising_three_loose():
    df = _synth(300, 74)
    res = mod.cdl_rising_three_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_falling_three_strict():
    df = _synth(300, 75)
    res = mod.cdl_falling_three_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_falling_three_loose():
    df = _synth(300, 76)
    res = mod.cdl_falling_three_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_stick_sandwich_strict():
    df = _synth(300, 77)
    res = mod.cdl_stick_sandwich_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_stick_sandwich_loose():
    df = _synth(300, 78)
    res = mod.cdl_stick_sandwich_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_thrusting_strict():
    df = _synth(300, 79)
    res = mod.cdl_thrusting_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_thrusting_loose():
    df = _synth(300, 80)
    res = mod.cdl_thrusting_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_separating_bull_strict():
    df = _synth(300, 81)
    res = mod.cdl_separating_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_separating_bull_loose():
    df = _synth(300, 82)
    res = mod.cdl_separating_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_separating_bear_strict():
    df = _synth(300, 83)
    res = mod.cdl_separating_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_separating_bear_loose():
    df = _synth(300, 84)
    res = mod.cdl_separating_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tri_star_bull_strict():
    df = _synth(300, 85)
    res = mod.cdl_tri_star_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tri_star_bull_loose():
    df = _synth(300, 86)
    res = mod.cdl_tri_star_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tri_star_bear_strict():
    df = _synth(300, 87)
    res = mod.cdl_tri_star_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_tri_star_bear_loose():
    df = _synth(300, 88)
    res = mod.cdl_tri_star_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_breakaway_bull_strict():
    df = _synth(300, 89)
    res = mod.cdl_breakaway_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_breakaway_bull_loose():
    df = _synth(300, 90)
    res = mod.cdl_breakaway_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_breakaway_bear_strict():
    df = _synth(300, 91)
    res = mod.cdl_breakaway_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_breakaway_bear_loose():
    df = _synth(300, 92)
    res = mod.cdl_breakaway_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_concealing_baby_strict():
    df = _synth(300, 93)
    res = mod.cdl_concealing_baby_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_concealing_baby_loose():
    df = _synth(300, 94)
    res = mod.cdl_concealing_baby_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_ladder_bottom_strict():
    df = _synth(300, 95)
    res = mod.cdl_ladder_bottom_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_ladder_bottom_loose():
    df = _synth(300, 96)
    res = mod.cdl_ladder_bottom_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_ladder_top_strict():
    df = _synth(300, 97)
    res = mod.cdl_ladder_top_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_ladder_top_loose():
    df = _synth(300, 98)
    res = mod.cdl_ladder_top_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_side_by_side_bull_strict():
    df = _synth(300, 99)
    res = mod.cdl_side_by_side_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_side_by_side_bull_loose():
    df = _synth(300, 100)
    res = mod.cdl_side_by_side_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_side_by_side_bear_strict():
    df = _synth(300, 101)
    res = mod.cdl_side_by_side_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_side_by_side_bear_loose():
    df = _synth(300, 102)
    res = mod.cdl_side_by_side_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_unique_three_river_strict():
    df = _synth(300, 103)
    res = mod.cdl_unique_three_river_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_unique_three_river_loose():
    df = _synth(300, 104)
    res = mod.cdl_unique_three_river_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_abandoned_baby_bull_strict():
    df = _synth(300, 105)
    res = mod.cdl_abandoned_baby_bull_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_abandoned_baby_bull_loose():
    df = _synth(300, 106)
    res = mod.cdl_abandoned_baby_bull_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_abandoned_baby_bear_strict():
    df = _synth(300, 107)
    res = mod.cdl_abandoned_baby_bear_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_abandoned_baby_bear_loose():
    df = _synth(300, 108)
    res = mod.cdl_abandoned_baby_bear_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_high_wave_strict():
    df = _synth(300, 109)
    res = mod.cdl_high_wave_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_high_wave_loose():
    df = _synth(300, 110)
    res = mod.cdl_high_wave_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_rickshaw_man_strict():
    df = _synth(300, 111)
    res = mod.cdl_rickshaw_man_strict(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()


def test_cdl_rickshaw_man_loose():
    df = _synth(300, 112)
    res = mod.cdl_rickshaw_man_loose(df)
    assert list(res.columns) == ["hit", "score"]
    assert len(res) == len(df)
    assert res["hit"].isin([0.0, 1.0]).all()
    assert ((res["score"] >= 0.0) & (res["score"] <= 1.0)).all()

