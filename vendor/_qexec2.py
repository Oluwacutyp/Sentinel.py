
# ============================================================================
# I2 — ADVANCED EXECUTION PACK (institutional fill quality on retail rails)
# ----------------------------------------------------------------------------
# I2a SlicedExecutor   TWAP / VWAP / POV slicing for orders that move the book
# I2b IcebergManager   show-size + reload logic for quiet accumulation
# I2c LatencyArbGuard  stale-quote detector: broker vs reference divergence
# I2d BrokerFingerprint per-broker behavior profile -> adaptive offsets
# I2e FillQualityLedger slippage attribution per strategy/session/symbol
# I2f DeadlineCanceller TTL on every pending, managed per ticket
# Facade: quantum_execute(ticket, ctx, broker) -> fill report
# ============================================================================

class SlicedExecutor:
    """Slice parent orders into children (TWAP/VWAP/POV)."""

    def __init__(self, slice_max_lots=1.0, slice_min_lots=0.01):
        self.slice_max = slice_max_lots
        self.slice_min = slice_min_lots

    def plan(self, total_lots, style="twap", n=5, urgency=0.5):
        """Returns [child_lots...]. urgency 0..1 front-loads the schedule."""
        try:
            total = float(total_lots)
            n = max(1, int(n))
            if total <= self.slice_max or n == 1:
                return [round(total, 2)]
            if style == "twap":
                w = [1.0] * n
            elif style == "vwap":
                # U-shape: heavier at open/close of the window
                w = [1.5 if i == 0 or i == n - 1 else 1.0 for i in range(n)]
            elif style == "pov":
                # Front-loaded by urgency
                w = [(n - i) ** (0.5 + urgency) for i in range(n)]
            else:
                w = [1.0] * n
            tw = sum(w) or 1.0
            kids = [max(self.slice_min, round(total * x / tw, 2)) for x in w]
            # Fix rounding drift on last child
            drift = round(total - sum(kids), 2)
            kids[-1] = round(kids[-1] + drift, 2)
            return [k for k in kids if k > 0]
        except Exception:
            return [float(total_lots)]

    def schedule(self, total_lots, window_sec=300, style="twap", urgency=0.5):
        """Returns [(delay_sec, lots)] execution schedule."""
        try:
            kids = self.plan(total_lots, style, n=max(2, min(12, int(total_lots / self.slice_max) + 2)),
                             urgency=urgency)
            if len(kids) == 1:
                return [(0, kids[0])]
            step = window_sec / len(kids)
            return [(round(i * step, 1), lots) for i, lots in enumerate(kids)]
        except Exception:
            return [(0, float(total_lots))]


class IcebergManager:
    """Show only a tip of the order; reload on fill. For quiet size."""

    def __init__(self, show_frac=0.2, max_reloads=10):
        self.show_frac = show_frac
        self.max_reloads = max_reloads
        self._bergs = {}  # ticket -> {total, shown, filled, reloads, side, px}

    def launch(self, ticket, total_lots, side, limit_px):
        try:
            show = max(0.01, round(total_lots * self.show_frac, 2))
            self._bergs[str(ticket)] = {"total": float(total_lots), "shown": show,
                                        "filled": 0.0, "reloads": 0,
                                        "side": int(side), "px": float(limit_px)}
            return {"show": show, "px": float(limit_px)}
        except Exception:
            return {}

    def on_fill(self, ticket, filled_lots):
        """Returns next show-size or None when complete/exhausted."""
        try:
            b = self._bergs.get(str(ticket))
            if b is None:
                return None
            b["filled"] += float(filled_lots)
            left = b["total"] - b["filled"]
            if left <= 0.005:
                self._bergs.pop(str(ticket), None)
                return None
            if b["reloads"] >= self.max_reloads:
                # Give up hiding; show the rest
                self._bergs.pop(str(ticket), None)
                return {"show": round(left, 2), "px": b["px"], "final": True}
            b["reloads"] += 1
            show = min(round(left, 2), b["shown"])
            return {"show": show, "px": b["px"], "reload": b["reloads"]}
        except Exception:
            return None


class LatencyArbGuard:
    """Detects stale broker quotes vs a reference feed; pauses when diverged.

    Reference can be a second symbol, a synthetic mid, or an external feed
    pushed via push_reference(). Divergence beyond the learned band => HALT.
    """

    def __init__(self, band_mult=3.0, window=300):
        self.band_mult = band_mult
        self._div_win = QuantileWindow(window)
        self._halt_until = 0.0
        self.halts = 0

    def push(self, broker_mid, ref_mid, now_ts=None):
        try:
            import time as _t
            now = now_ts or _t.time()
            if now < self._halt_until:
                return {"ok": False, "reason": "halt_cooldown"}
            div = abs(float(broker_mid) - float(ref_mid))
            base = float(ref_mid) or 1.0
            div_bp = div / base * 10000
            self._div_win.add(div_bp)
            if len(self._div_win) < 30:
                return {"ok": True, "div_bp": round(div_bp, 2)}
            band = (self._div_win.q(0.9) or 1.0) * self.band_mult
            if div_bp > max(band, 5.0):
                self._halt_until = now + 120  # 2-min cooldown
                self.halts += 1
                return {"ok": False, "reason": "stale_quote",
                        "div_bp": round(div_bp, 1), "band": round(band, 1)}
            return {"ok": True, "div_bp": round(div_bp, 2)}
        except Exception:
            return {"ok": True, "reason": "fallback"}


_LAG_SINGLETON = {"obj": None}


def quantum_quote_guard(broker_mid, ref_mid):
    try:
        o = _LAG_SINGLETON.get("obj")
        if o is None:
            o = LatencyArbGuard()
            _LAG_SINGLETON["obj"] = o
        return o.push(broker_mid, ref_mid)
    except Exception:
        return {"ok": True}


class BrokerFingerprint:
    """Learns how YOUR broker behaves: latency, slippage, requotes.

    The fingerprint tunes: price offset (slippage pre-compensation),
    fill deadline (when to give up on a pending), and max size per ticket.
    Per (broker, symbol) — because every feed lies a little differently.
    """

    _prints = {}

    def __init__(self, broker="default", symbol="XAUUSD"):
        self.key = f"{broker}@{symbol}"
        self.lat = QuantileWindow(500)     # fill latency ms
        self.slip = QuantileWindow(500)    # slippage in spread units
        self.requotes = 0
        self.fills = 0

    @classmethod
    def get(cls, broker="default", symbol="XAUUSD"):
        k = f"{broker}@{symbol}"
        o = cls._prints.get(k)
        if o is None:
            o = cls(broker, symbol)
            cls._prints[k] = o
        return o

    def record_fill(self, latency_ms, slip_spreads, requoted=False):
        try:
            self.lat.add(float(latency_ms))
            self.slip.add(float(slip_spreads))
            self.fills += 1
            if requoted:
                self.requotes += 1
        except Exception:
            pass

    def offset_spreads(self):
        """Pre-compensate the usual slippage (capped at 1 spread)."""
        try:
            if self.fills < 20:
                return 0.0
            return float(qclip(self.slip.q(0.6) or 0.0, -1.0, 1.0))
        except Exception:
            return 0.0

    def deadline_sec(self):
        """Give up on a pending after p90 latency x 3 (bounded 5..120s)."""
        try:
            if self.fills < 20:
                return 30
            return int(qclip((self.lat.q(0.9) or 1000) / 1000 * 3, 5, 120))
        except Exception:
            return 30

    def healthy(self):
        try:
            if self.fills < 20:
                return True
            rq = self.requotes / max(1, self.fills)
            return rq < 0.15 and (self.slip.q(0.9) or 0) < 2.0
        except Exception:
            return True

    def as_dict(self):
        return {"key": self.key, "fills": self.fills,
                "requote_rate": round(self.requotes / max(1, self.fills), 3),
                "lat_p50_ms": round(self.lat.q(0.5) or 0, 1),
                "lat_p90_ms": round(self.lat.q(0.9) or 0, 1),
                "slip_p50_sp": round(self.slip.q(0.5) or 0, 2),
                "offset_sp": round(self.offset_spreads(), 2),
                "deadline_s": self.deadline_sec(), "healthy": self.healthy()}


class FillQualityLedger:
    """Slippage attribution: who pays the spread, and when?

    Rows keyed by (strategy, session, symbol) -> slippage in R. The report
    names the strategies whose edge is being eaten by execution.
    """

    def __init__(self, window=1000):
        self.window = window
        self.rows = []

    def add(self, strategy, session, symbol, slip_r, slip_spreads=None):
        try:
            self.rows.append({"strategy": str(strategy), "session": str(session),
                              "symbol": str(symbol), "slip_r": float(slip_r),
                              "slip_sp": float(slip_spreads or 0)})
            self.rows = self.rows[-self.window:]
        except Exception:
            pass

    def report(self):
        try:
            if not self.rows:
                return {"status": "empty"}
            by_s, by_sess = {}, {}
            for r in self.rows:
                by_s.setdefault(r["strategy"], []).append(r["slip_r"])
                by_sess.setdefault(r["session"], []).append(r["slip_r"])
            strat = {k: round(sum(v) / len(v), 4) for k, v in
                     sorted(by_s.items(), key=lambda t: sum(t[1]) / len(t[1]))}
            sess = {k: round(sum(v) / len(v), 4) for k, v in by_sess.items()}
            worst = min(strat.items(), key=lambda t: t[1]) if strat else ("?", 0)
            return {"status": "ok", "n": len(self.rows),
                    "avg_slip_r": round(sum(r["slip_r"] for r in self.rows) / len(self.rows), 4),
                    "by_strategy": strat, "by_session": sess,
                    "worst": {"strategy": worst[0], "avg_slip_r": worst[1]},
                    "verdict": (f"{worst[0]}_bleeds_{abs(worst[1]):.3f}R_per_fill"
                                if worst[1] < -0.05 else "execution_clean")}
        except Exception:
            return {"status": "error"}


_FILLQ = {"obj": None}


def quantum_fillq_add(strategy, session, symbol, slip_r, slip_spreads=None):
    try:
        o = _FILLQ.get("obj")
        if o is None:
            o = FillQualityLedger()
            _FILLQ["obj"] = o
        o.add(strategy, session, symbol, slip_r, slip_spreads)
    except Exception:
        pass


def quantum_fillq_report():
    try:
        o = _FILLQ.get("obj")
        return o.report() if o is not None else {"status": "empty"}
    except Exception:
        return {"status": "error"}


class DeadlineCanceller:
    """Every pending gets a TTL from the broker fingerprint; zombies die."""

    def __init__(self):
        self._pend = {}  # ticket -> deadline_ts

    def arm(self, ticket, ttl_sec=None, broker="default", symbol="XAUUSD"):
        try:
            import time as _t
            ttl = ttl_sec
            if ttl is None:
                try:
                    ttl = BrokerFingerprint.get(broker, symbol).deadline_sec()
                except Exception:
                    ttl = 30
            self._pend[str(ticket)] = _t.time() + float(ttl)
            return ttl
        except Exception:
            return 30

    def expired(self, now_ts=None):
        try:
            import time as _t
            now = now_ts or _t.time()
            dead = [t for t, dl in self._pend.items() if now >= dl]
            for t in dead:
                self._pend.pop(t, None)
            return dead
        except Exception:
            return []

    def disarm(self, ticket):
        try:
            self._pend.pop(str(ticket), None)
        except Exception:
            pass


_DEADLINE = {"obj": None}


def quantum_deadline(ticket, ttl_sec=None, broker="default", symbol="XAUUSD"):
    try:
        o = _DEADLINE.get("obj")
        if o is None:
            o = DeadlineCanceller()
            _DEADLINE["obj"] = o
        return o.arm(ticket, ttl_sec, broker, symbol)
    except Exception:
        return 30


def quantum_deadline_sweep():
    try:
        o = _DEADLINE.get("obj")
        return o.expired() if o is not None else []
    except Exception:
        return []


# ----------------------------------------------------------------------------
# I2 facade: quantum_execute — ticket in, fill report out
# ----------------------------------------------------------------------------

def quantum_execute(ticket, ctx=None, broker_fn=None, broker="default",
                    symbol="XAUUSD", ref_mid=None):
    """Execute an EntryTicket through every guard.

    broker_fn(action_dict) -> fill_dict is the broker adapter (MT5 bridge in
    the wiring layer). Without one, runs in DRY-RUN and returns the plan.
    """
    ctx = dict(ctx or {})
    t = ticket.as_dict() if isinstance(ticket, EntryTicket) else dict(ticket or {})
    plan = {"ticket": t, "dry_run": broker_fn is None, "guards": []}
    try:
        if t.get("veto") is not None or t.get("side") not in (1, -1):
            plan["guards"].append("invalid_ticket")
            return plan
        # 1. Quote guard
        bmid = ctx.get("broker_mid")
        if bmid is not None and ref_mid is not None:
            qg = quantum_quote_guard(bmid, ref_mid)
            plan["guards"].append(f"quote:{qg.get('reason', 'ok')}")
            if not qg.get("ok", True):
                plan["halted"] = qg.get("reason")
                return plan
        # 2. Broker health
        try:
            fp = BrokerFingerprint.get(broker, symbol)
            if not fp.healthy():
                plan["guards"].append("broker_unhealthy")
                plan["halted"] = "broker_unhealthy"
                return plan
            plan["guards"].append("broker:healthy")
        except Exception:
            fp = None
        # 3. Size -> sliced schedule
        base_lots = float(ctx.get("lots", 0.1) or 0.1)
        lots = base_lots * float(t.get("lot_mult", 1.0) or 1.0)
        try:
            lots = quantum_spec(symbol).round_vol(lots)
        except Exception:
            pass
        urgency = qclip(float(t.get("conf", 0.6)), 0, 1)
        sched = SlicedExecutor().schedule(lots, window_sec=180, style="pov", urgency=urgency)
        plan["schedule"] = sched
        plan["lots"] = lots
        if broker_fn is None:
            plan["guards"].append("dry_run_plan_only")
            return plan
        # 4. Fire children through the broker adapter
        fills = []
        import time as _t
        for delay, kid in sched:
            t0 = _t.time() * 1000
            try:
                fill = broker_fn({"action": "market", "side": t["side"],
                                  "lots": kid, "symbol": symbol,
                                  "strategy": t.get("strategy"),
                                  "offset_sp": fp.offset_spreads() if fp else 0.0})
            except Exception as e:
                fill = {"ok": False, "error": str(e)}
            lat = _t.time() * 1000 - t0
            fill["latency_ms"] = round(lat, 1)
            fills.append(fill)
            try:
                if fp is not None and fill.get("ok"):
                    fp.record_fill(lat, fill.get("slip_spreads", 0) or 0,
                                   fill.get("requoted", False))
                quantum_fillq_add(t.get("strategy"), t.get("session"), symbol,
                                  fill.get("slip_r", 0) or 0,
                                  fill.get("slip_spreads", 0) or 0)
            except Exception:
                pass
            if not fill.get("ok") and fill.get("fatal"):
                break
        plan["fills"] = fills
        plan["filled_lots"] = round(sum(f.get("lots", 0) for f in fills if f.get("ok")), 2)
        return plan
    except Exception as e:
        plan["error"] = str(e)
        return plan


SECTION_I2_OK = True
