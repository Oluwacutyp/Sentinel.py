
# ============================================================================
# X — CROSS-MARKET PACK (no symbol trades alone)
# ----------------------------------------------------------------------------
# Xa CorrMonitor     rolling correlation matrix across watched symbols
# Xb LeaderLaggard   who moves first: GC vs XAUUSDm, BTC vs alts (lead-lag)
# Xc RiskGauge       risk-on/off from XAU-vs-equities behavior + USD tide
# Xd RotationAlloc   capital rotation: overweight the venue with the edge
# Strategies 22-23: AdaptiveLeaderLag, AdaptiveRiskRotation (L2 contract)
# ============================================================================

class CorrMonitor:
    """Rolling pairwise correlations on log returns (dict of closes)."""

    def __init__(self, window=100):
        self.window = window
        self.matrix = {}
        self.n = 0

    @staticmethod
    def _corr(a, b):
        try:
            n = min(len(a), len(b))
            if n < 20:
                return 0.0
            import math as _m
            ra = [_m.log(a[i] / a[i - 1]) for i in range(1, n) if a[i - 1] > 0 and a[i] > 0]
            rb = [_m.log(b[i] / b[i - 1]) for i in range(1, n) if b[i - 1] > 0 and b[i] > 0]
            m = min(len(ra), len(rb))
            if m < 20:
                return 0.0
            ra, rb = ra[-m:], rb[-m:]
            ma, mb = sum(ra) / m, sum(rb) / m
            num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
            den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
            return num / (den or 1e-12)
        except Exception:
            return 0.0

    def update(self, closes):
        """closes: {symbol: [px]}. Returns {(a,b): corr}."""
        try:
            syms = sorted((closes or {}).keys())
            self.n = len(syms)
            for i, a in enumerate(syms):
                for b in syms[i + 1:]:
                    self.matrix[(a, b)] = round(self._corr(closes[a][-self.window:],
                                                           closes[b][-self.window:]), 3)
            return dict(self.matrix)
        except Exception:
            return dict(self.matrix)

    def partners(self, symbol, min_abs=0.5):
        """Symbols correlated with `symbol` above the threshold."""
        try:
            out = []
            for (a, b), c in self.matrix.items():
                if a == symbol and abs(c) >= min_abs:
                    out.append((b, c))
                elif b == symbol and abs(c) >= min_abs:
                    out.append((a, c))
            out.sort(key=lambda t: -abs(t[1]))
            return out
        except Exception:
            return []

    def text(self):
        try:
            if not self.matrix:
                return "corr: no data"
            lines = ["CROSS-MARKET CORRELATIONS"]
            for (a, b), c in sorted(self.matrix.items(), key=lambda t: -abs(t[1])):
                lines.append(f"  {a:10s} {b:10s} {c:+.2f}")
            return "\n".join(lines)
        except Exception:
            return "corr: n/a"


_CORR = {"obj": None}


def quantum_corr(closes=None):
    try:
        o = _CORR.get("obj")
        if o is None:
            o = CorrMonitor()
            _CORR["obj"] = o
        if closes:
            o.update(closes)
        return dict(o.matrix)
    except Exception:
        return {}


class LeaderLaggard:
    """Lead-lag: does A move before B? (lagged correlation scan).

    leaders[symbol] = [(leader, lag_bars, corr)]. A laggard entry in the
    leader's direction, taken while the laggard hasn't moved yet, is the
    highest-SNR cross-market signal in the book.
    """

    def __init__(self, max_lag=5):
        self.max_lag = max_lag
        self.leads = {}

    def scan(self, closes):
        try:
            import math as _m
            syms = list((closes or {}).keys())
            self.leads = {}
            rets = {}
            for s in syms:
                c = list(closes[s])
                rets[s] = [_m.log(c[i] / c[i - 1]) if c[i - 1] > 0 else 0.0
                           for i in range(1, len(c))]
            for laggard in syms:
                best = []
                for leader in syms:
                    if leader == laggard:
                        continue
                    rl, rg = rets[leader], rets[laggard]
                    m = min(len(rl), len(rg))
                    if m < 40:
                        continue
                    rl, rg = rl[-m:], rg[-m:]
                    for lag in range(1, self.max_lag + 1):
                        x = rl[:-lag]
                        y = rg[lag:]
                        n = min(len(x), len(y))
                        if n < 30:
                            continue
                        x, y = x[-n:], y[-n:]
                        mx, my = sum(x) / n, sum(y) / n
                        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
                        den = (sum((a - mx) ** 2 for a in x) *
                               sum((b - my) ** 2 for b in y)) ** 0.5 or 1e-12
                        c = num / den
                        if abs(c) > 0.25:
                            best.append((leader, lag, round(c, 3)))
                best.sort(key=lambda t: -abs(t[2]))
                self.leads[laggard] = best[:3]
            return dict(self.leads)
        except Exception:
            return dict(self.leads)

    def impulse(self, leader, leader_closes, lag):
        """Current impulse: leader's last-`lag` move in sigma units."""
        try:
            c = list(leader_closes)
            if len(c) < lag + 20:
                return 0.0
            import math as _m
            move = _m.log(c[-1] / c[-lag - 1]) if c[-lag - 1] > 0 else 0.0
            hist = [_m.log(c[i] / c[i - lag]) if c[i - lag] > 0 else 0.0
                    for i in range(-20, 0)]
            mu = sum(hist) / len(hist)
            sd = (sum((x - mu) ** 2 for x in hist) / len(hist)) ** 0.5 or 1e-12
            return (move - mu) / sd
        except Exception:
            return 0.0


_LEADLAG = {"obj": None}


def quantum_leadlag(closes=None):
    try:
        o = _LEADLAG.get("obj")
        if o is None:
            o = LeaderLaggard()
            _LEADLAG["obj"] = o
        if closes:
            o.scan(closes)
        return dict(o.leads)
    except Exception:
        return {}


class RiskGauge:
    """Risk-on/off gauge: gold-vs-cycle behavior + USD tide + vol regime.

    Returns -1 (full risk-off) .. +1 (full risk-on) with a regime tag.
    Gold long into risk-off scores a tailwind; gold short into risk-on does.
    """

    TAGS = ("RISK_OFF", "DEFENSIVE", "NEUTRAL", "RISK_BID", "RISK_ON")

    def __init__(self):
        self.value = 0.0
        self.tag = "NEUTRAL"

    def update(self, xau_closes=None, equity_closes=None, usd_tide=0.0,
               vol_pct=0.5):
        try:
            score, w = 0.0, 0.0
            # 1. Gold vs equities divergence (20-bar drift spread)
            if xau_closes and equity_closes:
                x = list(xau_closes)
                e = list(equity_closes)
                if len(x) >= 21 and len(e) >= 21:
                    dx = (x[-1] - x[-21]) / (x[-21] + 1e-12)
                    de = (e[-1] - e[-21]) / (e[-21] + 1e-12)
                    # Gold up + equities down = risk-off
                    score += qclip((de - dx) * 30, -1, 1)
                    w += 1.0
            # 2. USD tide: strong dollar = defensive
            if usd_tide:
                score -= qclip(usd_tide * 200, -1, 1) * 0.6
                w += 0.6
            # 3. Vol percentile: high vol = risk-off
            score -= qclip((vol_pct - 0.5) * 2, -1, 1) * 0.5
            w += 0.5
            self.value = qclip(score / (w or 1.0), -1, 1)
            idx = min(4, max(0, int((self.value + 1) / 2 * 5 - 0.001)))
            self.tag = self.TAGS[idx]
            return {"gauge": round(self.value, 3), "tag": self.tag}
        except Exception:
            return {"gauge": 0.0, "tag": "NEUTRAL"}

    def tailwind(self, symbol, side):
        """Tailwind (+1) / headwind (-1) for holding `side` of `symbol`."""
        try:
            s = str(symbol).upper()
            if "XAU" in s or "XAG" in s or "JPY" in s or "CHF" in s:
                # Havens love risk-off
                return -self.value * side
            if "BTC" in s or "ETH" in s or "GBP" in s or "AUD" in s:
                # Risk assets love risk-on
                return self.value * side
            return 0.0
        except Exception:
            return 0.0


_RISKGAUGE = {"obj": None}


def quantum_risk_gauge(xau=None, eq=None, tide=0.0, vol_pct=0.5):
    try:
        o = _RISKGAUGE.get("obj")
        if o is None:
            o = RiskGauge()
            _RISKGAUGE["obj"] = o
        return o.update(xau, eq, tide, vol_pct)
    except Exception:
        return {"gauge": 0.0, "tag": "NEUTRAL"}


class RotationAlloc:
    """Capital rotation: split the risk budget across venues by live edge.

    Each symbol gets weight propto max(0, expectancy) x sqrt(n), smoothed.
    Symbols with no data split the remainder equally (exploration budget).
    """

    def __init__(self, symbols=("XAUUSD", "BTCUSD"), explore=0.2):
        self.symbols = list(symbols)
        self.explore = explore
        self.ev = {s: 0.0 for s in self.symbols}
        self.n = {s: 0 for s in self.symbols}

    def record(self, symbol, r):
        try:
            s = str(symbol).upper()
            if s not in self.ev:
                self.ev[s] = 0.0
                self.n[s] = 0
                self.symbols.append(s)
            n = self.n[s]
            self.ev[s] = (self.ev[s] * n + float(r)) / (n + 1)
            self.n[s] = n + 1
        except Exception:
            pass

    def weights(self):
        try:
            raw = {}
            for s in self.symbols:
                e = self.ev.get(s, 0)
                n = self.n.get(s, 0)
                raw[s] = max(0, e) * (n ** 0.5) if n >= 5 else 0.1
            tot = sum(raw.values()) or 1.0
            eq = 1.0 / max(1, len(self.symbols))
            return {s: round((1 - self.explore) * (raw[s] / tot) + self.explore * eq, 3)
                    for s in self.symbols}
        except Exception:
            return {s: 1.0 / max(1, len(self.symbols)) for s in self.symbols}

    def text(self):
        try:
            w = self.weights()
            lines = ["ROTATION (risk-budget weights)"]
            for s, x in sorted(w.items(), key=lambda t: -t[1]):
                lines.append(f"  {s:10s} {qbar(x, 24)} ev={self.ev.get(s, 0):+.3f} n={self.n.get(s, 0)}")
            return "\n".join(lines)
        except Exception:
            return "rotation: n/a"


_ROT = {"obj": None}


def quantum_rotation(symbols=None, record=None):
    try:
        o = _ROT.get("obj")
        if o is None:
            o = RotationAlloc(tuple(symbols or ("XAUUSD", "BTCUSD")))
            _ROT["obj"] = o
        if record:
            o.record(record[0], record[1])
        return o.weights()
    except Exception:
        return {}


# ----------------------------------------------------------------------------
# X strategies 22-23 (L2 contract)
# ----------------------------------------------------------------------------

class AdaptiveLeaderLag(_L2Base):
    name = "leader_lag"

    def suitable(self, regime):
        return regime in ("TREND_UP", "TREND_DOWN", "VOLATILE", "SESSION")

    def analyze(self, ctx):
        try:
            closes = ctx.get("x closes") or ctx.get("xcloses")
            sym = str(ctx.get("symbol", "XAUUSD")).upper()
            if not closes or sym not in closes:
                return self._sig(reason="no_xdata")
            o = _LEADLAG.get("obj")
            if o is None:
                o = LeaderLaggard()
                _LEADLAG["obj"] = o
            leads = o.scan(closes).get(sym, [])
            if not leads:
                return self._sig(reason="no_leader")
            leader, lag, corr = leads[0]
            imp = o.impulse(leader, closes[leader], lag)
            if abs(imp) < 1.5:
                return self._sig(reason="no_impulse")
            # Laggard must NOT have moved yet (else the edge is gone)
            df = ctx.get("df")
            c = qas_series(df, "close")
            import math as _m
            lag_move = _m.log(c[-1] / c[-lag - 1]) if len(c) > lag + 1 and c[-lag - 1] > 0 else 0.0
            if abs(lag_move) > 0.5 * abs(imp) * 0.002:
                return self._sig(reason="already_moved")
            side = qsign(imp) * qsign(corr)
            return self._sig(side, 0.6 + min(0.2, abs(imp) / 20), 1.6, 2.4,
                             f"{leader}->{sym}_lag{lag}_z{imp:+.1f}")
        except Exception:
            return self._sig(reason="error")


class AdaptiveRiskRotation(_L2Base):
    name = "risk_rotation"

    def suitable(self, regime):
        return True

    def analyze(self, ctx):
        try:
            sym = str(ctx.get("symbol", "XAUUSD")).upper()
            g = _RISKGAUGE.get("obj")
            if g is None:
                return self._sig(reason="no_gauge")
            # With-trend-of-risk only: havens long in risk-off, risk short... etc.
            df = ctx.get("df")
            c = qas_series(df, "close")
            if len(c) < 40:
                return self._sig(reason="warmup")
            mo = (c[-1] - c[-20]) / (c[-20] + 1e-12)
            side = qsign(mo) if abs(mo) > 1e-6 else 0
            if side == 0:
                return self._sig(reason="flat_momo")
            tw = g.tailwind(sym, side)
            if tw < 0.25:
                return self._sig(reason="risk_headwind")
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            atrs = q_atr_from_lists(h, l, c, 14)
            a = atrs[-1] if atrs else 1e-9
            return self._sig(side, 0.52 + min(0.25, tw / 3), 1.8, 2.4,
                             f"risk_{g.tag}_tw{tw:+.2f}", size_mult=0.7)
        except Exception:
            return self._sig(reason="error")


_L2D_CLASSES = (AdaptiveLeaderLag, AdaptiveRiskRotation)

try:
    L2Suite.CLASSES = tuple(L2Suite.CLASSES) + _L2D_CLASSES
    if _L2_SINGLETON.get("obj") is not None:
        _keep_stats = {s.name: s.stats for s in _L2_SINGLETON["obj"].strats}
        _L2_SINGLETON["obj"] = L2Suite()
        for _s in _L2_SINGLETON["obj"].strats:
            if _s.name in _keep_stats:
                _s.stats = _keep_stats[_s.name]
except Exception:
    pass

SECTION_X_OK = True
