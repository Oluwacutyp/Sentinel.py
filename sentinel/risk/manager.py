"""Risk management: sizing, stops, governors. Identical math in backtest and live."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils.helpers import clamp


class RiskManager:
    """Unified risk brain: sizing models, stop ladders, drawdown/day-loss governors."""

    def __init__(self, cfg: dict | None = None):
        c = cfg or {}
        self.sizing = str(c.get("sizing", "fixed"))
        self.base_risk = float(c.get("base_risk", 0.01))
        self.kelly_cap = float(c.get("kelly_cap", 0.25))
        self.vol_target = float(c.get("vol_target", 0.12))
        self.cppi_floor = float(c.get("cppi_floor", 0.85))
        self.cppi_mult = float(c.get("cppi_multiple", 3.0))
        self.stop_atr = float(c.get("stop_atr", 2.0))
        self.time_stop_bars = int(c.get("time_stop_bars", 120))
        self.breakeven_atr = float(c.get("breakeven_atr", 1.0))
        self.daily_halt = float(c.get("daily_halt", -0.03))
        self.max_dd = float(c.get("max_drawdown", -0.15))
        self.exposure_cap = float(c.get("exposure_cap", 0.80))
        self.peak = None
        self.day_start = None
        self.halted = False

    # ------------------------------------------------------------- sizing
    @staticmethod
    def kelly_fraction(win_rate: float, payoff: float) -> float:
        p = clamp(win_rate, 0.01, 0.99)
        b = max(0.1, payoff)
        return (p * (b + 1) - 1) / b

    def size_position(self, equity: float, price: float, atr: float,
                      win_rate: float = 0.5, payoff: float = 1.5,
                      realized_vol: float | None = None,
                      periods_per_year: int = 8760) -> dict:
        price = max(1e-9, float(price))
        atr = max(1e-9, float(atr))
        risk_frac = self.base_risk
        method = self.sizing
        if method == "kelly_frac":
            k = self.kelly_fraction(win_rate, payoff)
            risk_frac = clamp(0.25 * max(0.0, k), 0.001, self.kelly_cap * self.base_risk * 10)
            risk_frac = clamp(risk_frac, 0.001, 0.05)
        elif method == "vol_target" and realized_vol:
            sig = max(1e-6, float(realized_vol)) * np.sqrt(periods_per_year)
            risk_frac = clamp(self.vol_target / sig, 0.05, 2.0) * self.base_risk * 4
            risk_frac = clamp(risk_frac, 0.001, 0.05)
        elif method == "cppi":
            floor = self.cppi_floor * (self.peak or equity)
            cushion = max(0.0, (equity - floor) / (equity + 1e-12))
            risk_frac = clamp(cushion * self.cppi_mult * self.base_risk * 4, 0.0, 0.05)
        stop_dist = self.stop_atr * atr
        risk_money = equity * risk_frac
        shares = risk_money / stop_dist
        notional = shares * price
        fraction = clamp(notional / (equity + 1e-12), 0.0, self.exposure_cap)
        shares = fraction * equity / price
        return {"fraction": float(fraction), "shares": float(shares),
                "notional": float(fraction * equity), "risk_frac": float(risk_frac),
                "method": method, "stop_dist": float(stop_dist)}

    # ------------------------------------------------------------- stops
    def stop_levels(self, side: int, entry: float, atr: float) -> dict:
        atr = max(1e-9, float(atr))
        if side >= 0:
            return {"stop": entry - self.stop_atr * atr,
                    "breakeven_trigger": entry + self.breakeven_atr * atr,
                    "target_1": entry + self.stop_atr * atr,
                    "target_2": entry + 2 * self.stop_atr * atr}
        return {"stop": entry + self.stop_atr * atr,
                "breakeven_trigger": entry - self.breakeven_atr * atr,
                "target_1": entry - self.stop_atr * atr,
                "target_2": entry - 2 * self.stop_atr * atr}

    @staticmethod
    def trailing_stop(side: int, current_stop: float, price: float, atr: float, mult: float = 2.0) -> float:
        atr = max(1e-9, float(atr))
        if side >= 0:
            return max(current_stop, price - mult * atr)
        return min(current_stop, price + mult * atr)

    # --------------------------------------------------------- governors
    def update_equity(self, equity: float) -> dict:
        equity = float(equity)
        if self.peak is None:
            self.peak = equity
            self.day_start = equity
        self.peak = max(self.peak, equity)
        dd = (equity - self.peak) / (self.peak + 1e-12)
        day = (equity - (self.day_start or equity)) / ((self.day_start or equity) + 1e-12)
        if day <= self.daily_halt or dd <= self.max_dd:
            self.halted = True
        depth = abs(min(0.0, dd))
        soft = abs(self.max_dd) * 0.4
        if depth <= soft:
            throttle = 1.0
        elif depth >= abs(self.max_dd):
            throttle = 0.0
        else:
            x = (depth - soft) / (abs(self.max_dd) - soft + 1e-12)
            throttle = float(0.5 + 0.5 * np.cos(np.pi * x))
        return {"drawdown": float(dd), "day_return": float(day),
                "throttle": throttle, "halted": self.halted}

    def reset_day(self, equity: float) -> None:
        self.day_start = float(equity)
        if self.halted:
            self.halted = False

    def allow_trade(self, equity: float, current_exposure: float, correlation: float = 0.0,
                    max_corr: float = 0.75) -> dict:
        gov = self.update_equity(equity)
        if gov["halted"]:
            return {"allow": False, "reason": "governor-halted", **gov}
        if abs(current_exposure) >= self.exposure_cap:
            return {"allow": False, "reason": "exposure-cap", **gov}
        if abs(correlation) > max_corr and abs(current_exposure) > 0.3:
            return {"allow": False, "reason": "correlation-brake", **gov}
        return {"allow": True, "reason": "ok", **gov}

    def position_heat(self, positions: list) -> dict:
        gross = float(sum(abs(p.get("notional", 0.0)) for p in positions))
        net = float(sum(p.get("notional", 0.0) * (1 if p.get("side", 1) > 0 else -1) for p in positions))
        return {"gross": gross, "net": net, "count": len(positions)}
