
# ============================================================================
# DEEP — DEEP RESEARCH SYSTEMS (fractal, entropy, GARCH, Kelly, meta-blend)
# ----------------------------------------------------------------------------
# D1 FractalClock    fractal-dimension timing: persistence vs anti-persistence
# D2 EntropySizer    entropy-based size: predictable => size, noise => hide
# D3 GarchForecaster GARCH(1,1) vol forecast -> forward risk pricing
# D4 KellySqueezer   fractional-Kelly multiplier from E5 p + R multiples
# D5 MetaBlender     learned blend: E5 + L2 + MTF -> ONE final probability
# Strategies 24-25: AdaptiveFractal, AdaptiveKellyBreak (L2 contract)
# ============================================================================

class FractalClock:
    """Hurst-by-R/S + fractal dimension D = 2 - H, rolled into timing.

    H > 0.55: persistent (trend-following works) — allow riders/hunters.
    H < 0.45: anti-persistent (chop) — allow faders/catchers only.
    Else: mixed — full pool, standard size.
    """

    def __init__(self, window=100):
        self.window = window
        self.h = 0.5
        self.d = 1.5
        self.zone = "MIXED"

    @staticmethod
    def _hurst_rs(closes, min_n=16):
        try:
            import math as _m
            c = [float(x) for x in closes if x > 0]
            n = len(c)
            if n < min_n * 2:
                return 0.5
            rets = [_m.log(c[i] / c[i - 1]) for i in range(1, n)]
            # R/S over halving windows
            scales, rs = [], []
            k = len(rets) // 2
            while k >= min_n:
                m = len(rets) // k
                vals = []
                for j in range(m):
                    seg = rets[j * k:(j + 1) * k]
                    mu = sum(seg) / k
                    dev = [x - mu for x in seg]
                    run, mx, mn = 0.0, -1e18, 1e18
                    for x in dev:
                        run += x
                        mx, mn = max(mx, run), min(mn, run)
                    rng = mx - mn
                    sd = (sum(x * x for x in dev) / k) ** 0.5 or 1e-12
                    vals.append(rng / sd)
                scales.append(_m.log(k))
                rs.append(_m.log(sum(vals) / len(vals)))
                k //= 2
            if len(scales) < 2:
                return 0.5
            ms, mr = sum(scales) / len(scales), sum(rs) / len(rs)
            num = sum((s - ms) * (r - mr) for s, r in zip(scales, rs))
            den = sum((s - ms) ** 2 for s in scales) or 1e-12
            return qclip(num / den, 0.05, 0.95)
        except Exception:
            return 0.5

    def update(self, closes):
        try:
            self.h = self._hurst_rs(list(closes)[-self.window:])
            self.d = 2 - self.h
            self.zone = ("PERSIST" if self.h > 0.55 else
                         "ANTIPERSIST" if self.h < 0.45 else "MIXED")
            return {"H": round(self.h, 3), "D": round(self.d, 3), "zone": self.zone}
        except Exception:
            return {"H": 0.5, "D": 1.5, "zone": "MIXED"}

    def gate(self, strategy_name):
        """True if this strategy family suits the current fractal zone."""
        try:
            riders = ("trend_rider", "breakout_hunter", "session_break",
                      "session_drift", "leader_lag", "vol_squeeze")
            faders = ("swing_catcher", "fib_sniper", "sweep_fader", "gap_filler",
                      "grid_weaver", "divergence_sniper", "expiry_fade")
            if self.zone == "PERSIST" and strategy_name in faders:
                return False
            if self.zone == "ANTIPERSIST" and strategy_name in riders:
                return False
            return True
        except Exception:
            return True


_FRACT = {}


def quantum_fractal(symbol, closes=None):
    try:
        k = str(symbol).upper()
        o = _FRACT.get(k)
        if o is None:
            o = FractalClock()
            _FRACT[k] = o
        if closes is not None:
            return o.update(closes)
        return {"H": round(o.h, 3), "D": round(o.d, 3), "zone": o.zone}
    except Exception:
        return {"H": 0.5, "D": 1.5, "zone": "MIXED"}


class EntropySizer:
    """Shannon entropy of return-sign runs -> size multiplier.

    Low entropy (long runs, predictable) => size up to 1.4x.
    High entropy (coin-flip) => shrink to 0.4x. Max entropy is where
    accounts go to die; this keeps you small there.
    """

    def __init__(self, window=60, bins=8):
        self.window = window
        self.bins = bins

    def measure(self, closes):
        try:
            import math as _m
            c = [float(x) for x in closes][-self.window - 1:]
            if len(c) < 20:
                return {"entropy": 1.0, "mult": 1.0, "state": "WARMUP"}
            rets = [c[i] - c[i - 1] for i in range(1, len(c))]
            sd = (sum(x * x for x in rets) / len(rets)) ** 0.5 or 1e-12
            z = [x / sd for x in rets]
            lo, hi = min(z), max(z)
            span = (hi - lo) or 1.0
            hist = [0] * self.bins
            for v in z:
                hist[min(self.bins - 1, int((v - lo) / span * self.bins))] += 1
            ent = 0.0
            for h in hist:
                if h:
                    p = h / len(z)
                    ent -= p * _m.log(p, 2)
            norm = ent / _m.log(self.bins, 2)  # 0..1
            mult = qclip(1.4 - norm * 1.2, 0.4, 1.4)
            return {"entropy": round(norm, 3), "mult": round(mult, 3),
                    "state": "ORDERLY" if norm < 0.7 else ("NOISY" if norm < 0.88 else "MAXENT")}
        except Exception:
            return {"entropy": 1.0, "mult": 1.0, "state": "UNKNOWN"}


def quantum_entropy(closes):
    try:
        return EntropySizer().measure(closes)
    except Exception:
        return {"entropy": 1.0, "mult": 1.0}


class GarchForecaster:
    """GARCH(1,1) vol forecast by grid MLE-lite (no scipy needed).

    Forecasts next-bar variance; converts to an event-risk premium:
    forecast much above recent realized => shrink (something is coming).
    """

    def __init__(self):
        self.omega = self.alpha = self.beta = None

    def fit(self, closes, lookback=250):
        try:
            import math as _m
            c = [float(x) for x in closes][-lookback - 1:]
            if len(c) < 60:
                return {"status": "warmup"}
            r = [_m.log(c[i] / c[i - 1]) if c[i - 1] > 0 else 0.0 for i in range(1, len(c))]
            var0 = sum(x * x for x in r) / len(r) or 1e-12
            best = None
            # Coarse grid over (alpha, beta); omega from unconditional var
            for a in (0.03, 0.06, 0.10, 0.15):
                for b in (0.80, 0.86, 0.90, 0.94):
                    if a + b >= 0.999:
                        continue
                    w = var0 * (1 - a - b)
                    v, ll = var0, 0.0
                    for x in r:
                        v = w + a * x * x + b * v
                        v = max(v, 1e-12)
                        ll += -0.5 * (_m.log(v) + x * x / v)
                    if best is None or ll > best[0]:
                        best = (ll, a, b, w)
            ll, a, b, w = best
            self.alpha, self.beta, self.omega = a, b, w
            # Forecast: iterate to steady state from last variance
            v = var0
            for x in r[-20:]:
                v = w + a * x * x + b * v
            fcast = w + a * r[-1] ** 2 + b * v
            persistence = a + b
            halflife = _m.log(0.5) / _m.log(persistence) if persistence < 1 else 999
            return {"status": "ok", "alpha": a, "beta": b,
                    "fcast_var": fcast, "realized_var": var0,
                    "ratio": round(fcast / (var0 or 1e-12), 3),
                    "halflife_bars": round(halflife, 1)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def premium(self, closes):
        """Size multiplier from forecast-vs-realized (< 1 when vol incoming)."""
        try:
            f = self.fit(closes)
            if f.get("status") != "ok":
                return {"mult": 1.0, "note": "warmup"}
            ratio = f["ratio"]
            mult = qclip(1.3 - ratio * 0.4, 0.5, 1.2)
            return {"mult": round(mult, 3), "ratio": ratio,
                    "note": "vol_incoming" if ratio > 1.5 else "calm"}
        except Exception:
            return {"mult": 1.0}


def quantum_garch(closes):
    try:
        return GarchForecaster().premium(closes)
    except Exception:
        return {"mult": 1.0}


class KellySqueezer:
    """Fractional Kelly from E5 probability + setup R multiples.

    f* = (p*(Rw+1) - 1) / Rw ... squeezed: half-Kelly, capped at 1.5x base,
    floored at 0.25x. Negative edge => 0.25x (exploration), never 0 (the
    veto system handles true zeroes; Kelly only sizes).
    """

    @staticmethod
    def fraction(p, win_r=2.0, loss_r=1.0, kelly_frac=0.5, cap=1.5):
        try:
            p = qclip(float(p), 0.01, 0.99)
            b = float(win_r) / max(1e-9, float(loss_r))
            f_star = (p * (b + 1) - 1) / b
            f = f_star * kelly_frac
            if f <= 0:
                return {"mult": 0.25, "f_star": round(f_star, 3), "note": "no_edge_floor"}
            return {"mult": round(qclip(f * 4, 0.25, cap), 3),
                    "f_star": round(f_star, 3), "note": "ok"}
        except Exception:
            return {"mult": 0.5, "note": "fallback"}

    @staticmethod
    def from_ticket(ticket_like):
        try:
            t = ticket_like.as_dict() if isinstance(ticket_like, EntryTicket) else dict(ticket_like or {})
            return KellySqueezer.fraction(t.get("conf", 0.5),
                                          t.get("tp_atr", 2.0), t.get("sl_atr", 1.0))
        except Exception:
            return {"mult": 0.5}


def quantum_kelly(p, win_r=2.0, loss_r=1.0):
    try:
        return KellySqueezer.fraction(p, win_r, loss_r)
    except Exception:
        return {"mult": 0.5}


class MetaBlender:
    """ONE final probability from E5 + L2 + MTF + regime-cal (learned blend).

    Logistic weights fit online (SGD on log-loss) from realized outcomes.
    Cold start: sane priors (E5 0.5, L2 0.25, MTF 0.15, regime 0.10).
    """

    def __init__(self, lr=0.05):
        self.w = [0.5, 0.25, 0.15, 0.10]
        self.b = 0.0
        self.lr = lr
        self.n = 0

    @staticmethod
    def _sig(z):
        try:
            import math as _m
            return 1 / (1 + _m.exp(-max(-30, min(30, z))))
        except Exception:
            return 0.5

    def blend(self, p_e5, conf_l2, align_mtf, p_reg):
        try:
            x = [qclip(float(p_e5), 0, 1), qclip(float(conf_l2), 0, 1),
                 qclip((float(align_mtf) + 1) / 2, 0, 1), qclip(float(p_reg), 0, 1)]
            z = sum(wi * xi for wi, xi in zip(self.w, x)) * 4 - 2 + self.b
            return self._sig(z)
        except Exception:
            return 0.5

    def learn(self, p_e5, conf_l2, align_mtf, p_reg, won):
        try:
            p = self.blend(p_e5, conf_l2, align_mtf, p_reg)
            y = 1.0 if won else 0.0
            err = p - y
            x = [qclip(float(p_e5), 0, 1), qclip(float(conf_l2), 0, 1),
                 qclip((float(align_mtf) + 1) / 2, 0, 1), qclip(float(p_reg), 0, 1)]
            self.w = [wi - self.lr * err * xi * 4 for wi, xi in zip(self.w, x)]
            s = sum(self.w) or 1.0
            self.w = [max(0.02, wi / s) for wi in self.w]
            s2 = sum(self.w)
            self.w = [wi / s2 for wi in self.w]
            self.b -= self.lr * err
            self.n += 1
            return {"p": round(p, 3), "w": [round(v, 3) for v in self.w], "n": self.n}
        except Exception:
            return {}

    def status(self):
        return {"w": [round(v, 3) for v in self.w], "b": round(self.b, 3), "n": self.n}


_BLEND = {"obj": None}


def quantum_blend(p_e5, conf_l2, align_mtf, p_reg, won=None):
    try:
        o = _BLEND.get("obj")
        if o is None:
            o = MetaBlender()
            _BLEND["obj"] = o
        if won is not None:
            o.learn(p_e5, conf_l2, align_mtf, p_reg, won)
        return o.blend(p_e5, conf_l2, align_mtf, p_reg)
    except Exception:
        return 0.5


# ----------------------------------------------------------------------------
# DEEP strategies 24-25 (L2 contract)
# ----------------------------------------------------------------------------

class AdaptiveFractal(_L2Base):
    name = "fractal_clock"

    def suitable(self, regime):
        return True  # it routes itself by fractal zone

    def analyze(self, ctx):
        try:
            df = ctx.get("df")
            c = qas_series(df, "close")
            if len(c) < 120:
                return self._sig(reason="warmup")
            fc = quantum_fractal(ctx.get("symbol", "XAUUSD"), c)
            zone = fc["zone"]
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            atrs = q_atr_from_lists(h, l, c, 14)
            a = atrs[-1] if atrs else 1e-9
            if zone == "PERSIST":
                mo = (c[-1] - c[-20]) / (a + 1e-12)
                if abs(mo) < 0.6:
                    return self._sig(reason="no_momo")
                return self._sig(qsign(mo), 0.55 + min(0.2, abs(mo) / 12), 1.8, 2.6,
                                 f"persist_H{fc['H']}")
            if zone == "ANTIPERSIST":
                n = 40
                seg = c[-n:]
                mu = sum(seg) / n
                sd = (sum((x - mu) ** 2 for x in seg) / n) ** 0.5 + 1e-12
                z = (c[-1] - mu) / sd
                if abs(z) < 1.5:
                    return self._sig(reason="no_stretch")
                return self._sig(-qsign(z), 0.55 + min(0.2, abs(z) / 15), 1.8, 2.2,
                                 f"antipersist_H{fc['H']}_z{z:+.1f}")
            return self._sig(reason="mixed_zone")
        except Exception:
            return self._sig(reason="error")


class AdaptiveKellyBreak(_L2Base):
    name = "kelly_break"

    def suitable(self, regime):
        return regime in ("TREND_UP", "TREND_DOWN", "VOLATILE", "SESSION")

    def analyze(self, ctx):
        try:
            o, h, l, c = self._cols(ctx)
            if len(c) < 80:
                return self._sig(reason="warmup")
            # Breakout + Kelly confirmation: only swing when edge*size align
            n = 20
            hi, lo = max(h[-n - 1:-1]), min(l[-n - 1:-1])
            px = c[-1]
            side = 0
            if px > hi:
                side = 1
            elif px < lo:
                side = -1
            else:
                return self._sig(reason="inside")
            atrs = q_atr_from_lists(h, l, c, 14)
            a = atrs[-1] if atrs else 1e-9
            lvl = hi if side > 0 else lo
            sl_a = qclip(abs(px - lvl) / (a + 1e-12) + 1.0, 1.0, 3.0)
            feats = {"break_dist": abs(px - lvl) / (a + 1e-12)}
            try:
                p = quantum_calibrated_prob(feats)
            except Exception:
                p = 0.55
            k = KellySqueezer.fraction(p, 2.5, sl_a)
            if k["mult"] < 0.5:
                return self._sig(reason="kelly_says_small")
            return self._sig(side, p, sl_a, 2.5, f"kelly{k['mult']:.2f}_p{p:.2f}",
                             size_mult=k["mult"])
        except Exception:
            return self._sig(reason="error")


_L2E_CLASSES = (AdaptiveFractal, AdaptiveKellyBreak)

try:
    L2Suite.CLASSES = tuple(L2Suite.CLASSES) + _L2E_CLASSES
    if _L2_SINGLETON.get("obj") is not None:
        _keep_stats = {s.name: s.stats for s in _L2_SINGLETON["obj"].strats}
        _L2_SINGLETON["obj"] = L2Suite()
        for _s in _L2_SINGLETON["obj"].strats:
            if _s.name in _keep_stats:
                _s.stats = _keep_stats[_s.name]
except Exception:
    pass


def quantum_size_deep(base_lots, ticket_like, closes, ctx=None):
    """Compose the DEEP sizers: Kelly x entropy x GARCH x edge-overlay."""
    ctx = dict(ctx or {})
    try:
        mult, notes = 1.0, []
        k = KellySqueezer.from_ticket(ticket_like)
        mult *= k["mult"]
        notes.append(f"kelly{k['mult']:.2f}")
        e = quantum_entropy(closes)
        mult *= e["mult"]
        notes.append(f"entropy{e['mult']:.2f}")
        g = quantum_garch(closes)
        mult *= g["mult"]
        notes.append(f"garch{g['mult']:.2f}")
        try:
            ov = quantum_edge_overlay(ctx.get("symbol", "XAUUSD"), ctx.get("now_ts"),
                                      ctx.get("usd_proxy_closes"), list(closes)[-60:])
            mult *= ov.get("size_mult", 1.0)
            notes.append(f"edge{ov.get('size_mult', 1.0):.2f}")
        except Exception:
            pass
        lots = float(base_lots) * mult
        try:
            lots = quantum_spec(ctx.get("symbol", "XAUUSD")).round_vol(lots)
        except Exception:
            lots = round(lots, 2)
        return {"lots": lots, "mult": round(mult, 3), "notes": notes}
    except Exception as ex:
        return {"lots": base_lots, "mult": 1.0, "error": str(ex)}


SECTION_DEEP_OK = True
