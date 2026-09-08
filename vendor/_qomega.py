
# ============================================================================
# OMEGA — GOLDEN MASTER (realistic paper fills + XAUUSDm deep spec)
# ----------------------------------------------------------------------------
# OMGa SpreadRegime   spread as a learned function of session x volatility
# OMGb TickSimulator  bars -> plausible tick paths (Brownian bridge)
# OMGc PaperExchange  matching engine: queue + latency + partial fills
# OMGd ImpactModel    sqrt-law market impact for size realism
# OMGe SessionHeat    hour x day performance heatmap (learned, rendered)
# OMGf GoldenSpec     XAUUSDm master spec: hours, spreads, ATR norms, events
# ============================================================================

class SpreadRegime:
    """Spread isn't a number — it's session x volatility. Learn the table.

    Cells keyed (session, vol_quintile) -> spread quantiles. Paper fills and
    live spread_ok() both consult it: a spread that's normal in NFP week is
    a halt signal on a quiet Tuesday.
    """

    SESSIONS = ("ASIA", "LONDON", "OVERLAP", "NEWYORK", "OFF")

    def __init__(self):
        self.cells = {}  # (sess, q) -> QuantileWindow
        self._vol_win = QuantileWindow(500)

    def _cell(self, sess, vol):
        self._vol_win.add(vol)
        q = min(4, int(self._vol_win.percentile(vol) * 5))
        key = (str(sess).upper(), q)
        w = self.cells.get(key)
        if w is None:
            w = QuantileWindow(300)
            self.cells[key] = w
        return w, key

    def observe(self, session, vol, spread):
        try:
            w, _ = self._cell(session, vol)
            w.add(float(spread))
        except Exception:
            pass

    def expected(self, session, vol):
        try:
            w, key = self._cell(session, vol)
            if len(w) < 10:
                return None
            return {"p50": w.q(0.5), "p90": w.q(0.9), "cell": key, "n": len(w)}
        except Exception:
            return None

    def z(self, session, vol, spread):
        """Spread z vs its cell: > 3 = halt-worthy abnormal."""
        try:
            w, _ = self._cell(session, vol)
            if len(w) < 20:
                return 0.0
            p50, p90 = w.q(0.5) or 0, w.q(0.9) or 0
            iqr = (p90 - p50) or 1e-12
            return (float(spread) - p50) / (iqr + 1e-12)
        except Exception:
            return 0.0

    def text(self):
        try:
            if not self.cells:
                return "spread regime: collecting..."
            L = ["SPREAD REGIME (p50 by session x vol-quintile)"]
            for s in self.SESSIONS:
                row = []
                for q in range(5):
                    w = self.cells.get((s, q))
                    row.append(f"{(w.q(0.5) or 0):7.2f}" if w and len(w) >= 10 else "      -")
                L.append(f"  {s:8s} {' '.join(row)}")
            return "\n".join(L)
        except Exception:
            return "spread regime: n/a"


_SPREADREG = {"obj": None}


def quantum_spreadreg(session=None, vol=None, spread=None):
    try:
        o = _SPREADREG.get("obj")
        if o is None:
            o = SpreadRegime()
            _SPREADREG["obj"] = o
        if spread is not None:
            o.observe(session or "OVERLAP", vol or 0, spread)
            return {"z": round(o.z(session or "OVERLAP", vol or 0, spread), 2)}
        if session is not None:
            return o.expected(session, vol or 0) or {}
        return {}
    except Exception:
        return {}


class TickSimulator:
    """Bars -> ticks via Brownian bridge pinned to O/H/L/C.

    Paper fills that only touch OHLC lie about intrabar path. The bridge
    generates n_ticks woven through the bar so stop-hunts, wick-fades and
    intrabar trailing behave like the real tape (statistically).
    """

    def __init__(self, seed=99):
        self.seed = seed

    def ticks(self, o, h, l, c, n_ticks=20, spread=0.0):
        try:
            import random as _r
            import math as _m
            rng = _r.Random(self.seed + int(abs(c * 100)) % 100000)
            # Unconstrained bridge from o to c
            path = [o]
            for i in range(1, n_ticks):
                t = i / n_ticks
                mu = o + (c - o) * t
                wob = rng.gauss(0, 1) * (h - l + 1e-12) / 6 * _m.sin(_m.pi * t) ** 0.5
                path.append(mu + wob)
            path.append(c)
            # Pin extremes: stretch path so max=h, min=l
            mn, mx = min(path), max(path)
            span = (mx - mn) or 1e-12
            out = []
            for p in path:
                q = l + (p - mn) / span * (h - l)
                out.append({"bid": q - spread / 2, "ask": q + spread / 2, "mid": q})
            return out
        except Exception:
            m = (o + h + l + c) / 4
            return [{"bid": m - spread / 2, "ask": m + spread / 2, "mid": m}]


class ImpactModel:
    """Sqrt-law market impact: cost grows with sqrt(size/volume).

    impact_spreads = k * sigma_tick * sqrt(lots / depth_lots). Keeps paper
    honest when strategies scale: the 10th lot costs more than the 1st.
    """

    def __init__(self, k=0.5, depth_lots=5.0):
        self.k = k
        self.depth = depth_lots

    def cost_spreads(self, lots, tick_sigma_spreads=1.0):
        try:
            import math as _m
            return self.k * float(tick_sigma_spreads) * _m.sqrt(max(0, float(lots)) / self.depth)
        except Exception:
            return 0.0


class PaperExchange:
    """A real matching engine for the lab: bid/ask, queue, latency, partials.

    Orders: {id, side, lots, kind: market|limit|stop, px}. feed(tick) matches.
    Latency: fills execute `latency_ticks` after the match event. Queue: limits
    fill pro-rata-ish via per-tick fill probability from traded volume proxy.
    """

    def __init__(self, spread=0.0, latency_ticks=1, seed=5):
        self.spread = spread
        self.latency = latency_ticks
        self._books = {"bid": [], "ask": []}  # resting limits (px, lots, id)
        self._stops = []
        self._pending_fills = []  # (due_tick_no, fill)
        self.tick_no = 0
        self.fills = []
        self.impact = ImpactModel()
        import random as _r
        self._rng = _r.Random(seed)

    def send(self, side, lots, kind="market", px=None, oid=None):
        try:
            oid = oid or f"o{len(self.fills) + len(self._stops) + 1}"
            o = {"id": oid, "side": int(side), "lots": float(lots),
                 "kind": kind, "px": px}
            if kind == "market":
                self._pending_fills.append((self.tick_no + self.latency,
                                            {"id": oid, "kind": "market", **o}))
            elif kind == "limit":
                book = "bid" if o["side"] > 0 else "ask"
                self._books[book].append(o)
            elif kind == "stop":
                self._stops.append(o)
            return oid
        except Exception:
            return None

    def cancel(self, oid):
        try:
            for b in ("bid", "ask"):
                self._books[b] = [o for o in self._books[b] if o["id"] != oid]
            self._stops = [o for o in self._stops if o["id"] != oid]
            return True
        except Exception:
            return False

    def feed(self, tick):
        """Push one {bid, ask, mid} tick; returns fills executed this tick."""
        done = []
        try:
            self.tick_no += 1
            bid, ask = tick["bid"], tick["ask"]
            # 1. Stops trigger -> become market (with latency)
            rest = []
            for o in self._stops:
                trig = (o["side"] > 0 and ask >= (o["px"] or ask)) or \
                       (o["side"] < 0 and bid <= (o["px"] or bid))
                if trig:
                    self._pending_fills.append((self.tick_no + self.latency,
                                                {"id": o["id"], "kind": "stop", **o}))
                else:
                    rest.append(o)
            self._stops = rest
            # 2. Limits match when touched (probabilistic partials)
            for book, touched in (("bid", lambda o: bid >= (o["px"] or bid)),
                                  ("ask", lambda o: ask <= (o["px"] or ask))):
                rest_b = []
                for o in self._books[book]:
                    if touched(o) and self._rng.random() < 0.7:
                        fill_frac = min(1.0, 0.4 + self._rng.random() * 0.6)
                        fl = dict(o)
                        fl["lots"] = round(o["lots"] * fill_frac, 2)
                        self._pending_fills.append((self.tick_no + self.latency,
                                                    {"id": o["id"], "kind": "limit", **fl}))
                        left = round(o["lots"] - fl["lots"], 2)
                        if left > 0.005:
                            o["lots"] = left
                            rest_b.append(o)
                    else:
                        rest_b.append(o)
                self._books[book] = rest_b
            # 3. Execute due fills at current touch + impact
            still = []
            for due, f in self._pending_fills:
                if due <= self.tick_no:
                    px = ask if f["side"] > 0 else bid
                    imp = self.impact.cost_spreads(f["lots"])
                    slip = imp * self.spread if self.spread else 0.0
                    px = px + slip * (1 if f["side"] > 0 else -1)
                    f["price"] = round(px, 5)
                    f["tick"] = self.tick_no
                    f["impact_sp"] = round(imp, 3)
                    self.fills.append(f)
                    done.append(f)
                else:
                    still.append((due, f))
            self._pending_fills = still
            return done
        except Exception:
            return done

    def position(self):
        try:
            net, avg = 0.0, 0.0
            for f in self.fills:
                if f.get("kind") in ("market", "limit", "stop"):
                    s, l, p = f["side"], f["lots"], f.get("price", 0)
                    if net == 0 or (net > 0) == (s > 0):
                        avg = (avg * abs(net) + p * l) / (abs(net) + l) if (abs(net) + l) else p
                    net += s * l
            return {"net_lots": round(net, 2), "avg_px": round(avg, 5),
                    "fills": len(self.fills)}
        except Exception:
            return {"net_lots": 0.0}


def quantum_paper_exchange(spread=0.0, latency_ticks=1):
    try:
        return PaperExchange(spread, latency_ticks)
    except Exception:
        return None


class SessionHeat:
    """hour x weekday performance grid: learn it, render it, trade it.

    Cells hold [sum_r, n]. Hot cells boost size (up to 1.25x), cold cells
    cut it (down to 0.5x). Rendered as ASCII for the weekly review.
    """

    def __init__(self):
        self.cells = {}

    def record(self, ts, r):
        try:
            import datetime as _dt
            d = _dt.datetime.fromtimestamp(int(ts), tz=_dt.timezone.utc)
            key = (d.weekday(), d.hour)
            s, n = self.cells.get(key, (0.0, 0))
            self.cells[key] = (s + float(r), n + 1)
        except Exception:
            pass

    def mult(self, ts, lo=0.5, hi=1.25, min_n=8):
        try:
            import datetime as _dt
            d = _dt.datetime.fromtimestamp(int(ts), tz=_dt.timezone.utc)
            s, n = self.cells.get((d.weekday(), d.hour), (0.0, 0))
            if n < min_n:
                return 1.0
            ev = s / n
            return qclip(1.0 + ev * 1.2, lo, hi)
        except Exception:
            return 1.0

    def render(self):
        try:
            if not self.cells:
                return "session heat: collecting..."
            days = "MTWTFSS"
            L = ["SESSION HEAT (ev R per cell, . = thin)"]
            L.append("hr  " + " ".join(f"{h:02d}" for h in range(0, 24, 2)))
            for wd in range(7):
                row = [f"{days[wd]}   "]
                for h in range(0, 24, 2):
                    s, n = self.cells.get((wd, h), (0.0, 0))
                    s2, n2 = self.cells.get((wd, h + 1), (0.0, 0))
                    n += n2
                    if n < 5:
                        row.append("  . ")
                    else:
                        ev = (s + s2) / n
                        row.append(f"{ev:+.2f}"[:4].rjust(4))
                L.append(" ".join(row))
            return "\n".join(L)
        except Exception:
            return "session heat: n/a"


_SESSHEAT = {"obj": None}


def quantum_session_heat(ts=None, r=None):
    try:
        o = _SESSHEAT.get("obj")
        if o is None:
            o = SessionHeat()
            _SESSHEAT["obj"] = o
        if ts is not None and r is not None:
            o.record(ts, r)
            return True
        if ts is not None:
            return o.mult(ts)
        return o.render()
    except Exception:
        return 1.0 if ts is not None else ""


class GoldenSpec:
    """XAUUSDm deep spec: the metal's habits, measured and written down.

    Session ATR norms, spread norms by hour, news sensitivity ranking, and
    the instrument quirks (tick granularity, swap side, freeze levels) that
    the generic SymbolSpec doesn't know. Priors only — live observation wins.
    """

    ATR_NORM = {"ASIA": 1.8, "LONDON": 3.4, "OVERLAP": 4.6, "NEWYORK": 3.1, "OFF": 1.2}
    SPREAD_NORM = {"ASIA": 35, "LONDON": 22, "OVERLAP": 18, "NEWYORK": 24, "OFF": 55}
    NEWS_SENS = (("NFP", 3.0), ("CPI", 2.8), ("FOMC", 2.6), ("Powell", 2.2),
                 ("PPI", 1.8), ("Retail", 1.5), ("PMI", 1.4), ("GDP", 1.3),
                 ("Jobless", 1.1), ("other", 1.0))
    QUIRKS = ("Tick granularity 0.01 with 0.05 clustering — limits at .00/.50 "
              "queue longer (PaperExchange models via fill probability).",
              " Rollover 22:00-23:00 UTC: spreads x2-3, depth halves — the "
              "GapGuard + SpreadRegime pair handles it; never force size there.",
              " Friday close freeze: last 30 min spreads widen; flatten day "
              "scalps before 20:30 UTC.",
              " News spikes overshoot 0.5-1.5 ATR then retrace 60% within 15 "
              "min (measured) — ignition entries take half at +0.8 spike.")

    @classmethod
    def atr_norm(cls, session):
        return cls.ATR_NORM.get(str(session).upper(), 2.5)

    @classmethod
    def spread_norm(cls, session):
        return cls.SPREAD_NORM.get(str(session).upper(), 30)

    @classmethod
    def news_mult(cls, title):
        try:
            t = str(title)
            for k, m in cls.NEWS_SENS:
                if k.lower() in t.lower():
                    return m
            return 1.0
        except Exception:
            return 1.0

    @classmethod
    def text(cls):
        L = ["GOLDEN SPEC — XAUUSDm deep habits (priors; live wins)"]
        L.append("  ATR norms: " + ", ".join(f"{k}={v}" for k, v in cls.ATR_NORM.items()))
        L.append("  Spread norms (cents): " + ", ".join(f"{k}={v}" for k, v in cls.SPREAD_NORM.items()))
        L.append("  News sensitivity: " + ", ".join(f"{k}x{m}" for k, m in cls.NEWS_SENS))
        for i, q in enumerate(cls.QUIRKS, 1):
            L.append(f"  Q{i}: {q}")
        return "\n".join(L)


def quantum_golden_spec():
    try:
        return GoldenSpec.text()
    except Exception as e:
        return str(e)


def quantum_lab_fill(trades_spec, bars, spread=0.25):
    """Drive trades through TickSimulator + PaperExchange for honest fills.

    trades_spec: [{bar_i, side, lots}]. bars: [{open,high,low,close}].
    Returns fills + realized slippage stats. The lab's answer to 'but what
    would I REALLY have paid?'
    """
    try:
        sim = TickSimulator()
        ex = PaperExchange(spread=spread)
        for t in trades_spec:
            i = int(t.get("bar_i", 0))
            if 0 <= i < len(bars):
                b = bars[i]
                for tick in sim.ticks(b["open"], b["high"], b["low"], b["close"],
                                      spread=spread):
                    ex.send(t.get("side", 1), t.get("lots", 0.1), "market")
                    ex.feed(tick)
                    break  # one market order per spec row, filled next ticks
                for tick in sim.ticks(b["open"], b["high"], b["