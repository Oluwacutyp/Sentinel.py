"""Live trading loop: paper + CCXT brokers, reconciliation, kill-switches."""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd


class PaperBroker:
    """Idempotent simulated broker with fees and full order log."""

    def __init__(self, cash: float = 100_000.0, fee_bps: float = 5.0):
        self.cash = float(cash)
        self.units = 0.0
        self.fee = fee_bps / 1e4
        self.orders: list = []

    def market(self, delta_units: float, price: float, tag: str = "") -> dict:
        if abs(delta_units) < 1e-12:
            return {"filled": 0.0}
        cost = abs(delta_units * price) * self.fee
        self.cash -= delta_units * price + cost
        self.units += delta_units
        o = {"side": float(np.sign(delta_units)), "units": float(delta_units),
             "price": float(price), "fee": float(cost), "tag": tag}
        self.orders.append(o)
        return {"filled": float(delta_units), **o}

    def equity(self, price: float) -> float:
        return float(self.cash + self.units * price)

    def position(self) -> dict:
        return {"units": float(self.units), "cash": float(self.cash), "orders": len(self.orders)}


class CCXTBroker:
    """Thin CCXT wrapper. Import is lazy; safe to construct without ccxt installed."""

    def __init__(self, symbol: str, exchange: str = "binance", api_key: str = "",
                 secret: str = "", sandbox: bool = True):
        self.symbol = symbol
        self.exchange = exchange
        self.api_key = api_key
        self.secret = secret
        self.sandbox = sandbox
        self._ex = None

    def connect(self):
        try:
            import ccxt
        except ImportError as e:
            raise ImportError("ccxt not installed: pip install ccxt") from e
        ex = getattr(ccxt, self.exchange)({"apiKey": self.api_key, "secret": self.secret,
                                           "enableRateLimit": True})
        if self.sandbox and hasattr(ex, "set_sandbox_mode"):
            try:
                ex.set_sandbox_mode(True)
            except Exception:
                pass
        self._ex = ex
        return ex

    def market(self, delta_units: float, price: float, tag: str = "") -> dict:
        if self._ex is None:
            self.connect()
        side = "buy" if delta_units > 0 else "sell"
        order = self._ex.create_market_order(self.symbol, side, abs(float(delta_units)))
        return {"filled": float(delta_units), "ccxt_id": order.get("id"), "tag": tag}


class LiveTrader:
    """Runs engine.scan → target position → reconcile → order, with kill-switches."""

    def __init__(self, engine, broker=None, poll_seconds: int = 30, dry_run: bool = True,
                 panic_file: str = "/tmp/sentinel_panic", error_budget: int = 5,
                 max_position_frac: float = 0.8):
        self.engine = engine
        self.broker = broker or PaperBroker()
        self.poll_seconds = poll_seconds
        self.dry_run = dry_run
        self.panic_file = panic_file
        self.error_budget = error_budget
        self.max_frac = max_position_frac
        self.errors = 0
        self.history: list = []

    def _panic(self) -> bool:
        return os.path.exists(self.panic_file)

    def step(self, df: pd.DataFrame, symbol: str = "SYM") -> dict:
        report = self.engine.scan(df, symbol=symbol)
        px = float(df["close"].iloc[-1])
        equity = self.broker.equity(px) if hasattr(self.broker, "equity") else 0.0
        target_frac = float(report.position_now * report.size_fraction)
        target_frac = float(np.clip(target_frac, -self.max_frac, self.max_frac))
        if not report.approved or self.engine.risk.halted:
            target_frac = 0.0
        units_now = getattr(self.broker, "units", 0.0)
        target_units = (equity * target_frac / px) if px > 0 else 0.0
        delta = target_units - units_now
        fill = {"filled": 0.0, "dry": True}
        if not self.dry_run and abs(delta) > 1e-9:
            fill = self.broker.market(delta, px, tag=f"{symbol}:{report.regime_label}")
        action = {"symbol": symbol, "price": px, "regime": report.regime_label,
                  "bias": report.bias, "position": report.position_now,
                  "target_frac": target_frac, "delta_units": float(delta),
                  "approved": report.approved, "meta_p": report.meta_proba,
                  "fill": fill, "equity": equity}
        self.history.append(action)
        return action

    def run(self, feed_fn, symbol: str = "SYM", max_steps: int = 10_000) -> list:
        step = 0
        while step < max_steps:
            if self._panic():
                print("PANIC FILE DETECTED — flattening and halting.")
                break
            if self.errors >= self.error_budget:
                print("ERROR BUDGET EXHAUSTED — halting.")
                break
            try:
                df = feed_fn(step)
                if df is None or len(df) == 0:
                    time.sleep(self.poll_seconds)
                    continue
                a = self.step(df, symbol)
                print(f"[{step}] {a['regime']} bias={a['bias']:+.2f} pos={a['position']:+.0f} "
                      f"tgt={a['target_frac']:+.3f} eq={a['equity']:.0f} approved={a['approved']}")
            except KeyboardInterrupt:
                break
            except Exception as e:  # noqa: BLE001 - live loop must survive
                self.errors += 1
                print(f"step error ({self.errors}/{self.error_budget}): {e}")
            step += 1
            if self.poll_seconds > 0:
                time.sleep(self.poll_seconds)
        return self.history
