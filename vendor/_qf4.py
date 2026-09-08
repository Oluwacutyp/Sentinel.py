
# ============================================================================
# F4 — CHART PATTERN PACK (geometry with validation, not vibes)
# ----------------------------------------------------------------------------
# Triangles (sym/asymmetric), wedges, flags/pennants, channels, doubles,
# rounded turns. Every pattern needs: minimum touches, symmetry bounds,
# apex/convergence math, and a measured invalid level. Returns trade frames:
# {pattern, dir, conf, entry_zone, invalid, target}.
# ============================================================================

class _Geo:
    """Shared geometry: swing regression, touch counting, symmetry."""

    @staticmethod
    def linreg(xs, ys):
        n = len(xs)
        if n < 3:
            return (0.0, ys[-1] if ys else 0.0, 0.0)
        try:
            mx = sum(xs) / n
            my = sum(ys) / n
            sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            sxx = sum((x - mx) ** 2 for x in xs) + 1e-12
            slope = sxy / sxx
            icept = my - slope * mx
            ss_tot = sum((y - my) ** 2 for y in ys) + 1e-12
            ss_res = sum((ys[i] - (slope * xs[i] + icept)) ** 2 for i in range(n))
            r2 = max(0.0, 1 - ss_res / ss_tot)
            return (float(slope), float(icept), float(r2))
        except Exception:
            return (0.0, 0.0, 0.0)

    @staticmethod
    def touches(line_fn, prices, idxs, tol):
        n = 0
        for i, p in zip(idxs, prices):
            try:
                if abs(p - line_fn(i)) <= tol:
                    n += 1
            except Exception:
                pass
        return n


class TrianglePack:
    """Symmetrical / ascending / descending triangles from swing rails."""

    def detect(self, h, l, c, lookback=120):
        res = {"pattern": None, "dir": 0, "conf": 0.0, "apex_in": None,
               "upper": None, "lower": None, "invalid": 0.0}
        try:
            n = len(c)
            if n < lookback // 2 + 20:
                return res
            sw = SwingStructure(width=4)
            his, los = sw.swings(h[-lookback:], l[-lookback:], limit=10)
            if len(his) < 2 or len(los) < 2:
                return res
            base = n - lookback
            hx = [base + i for i, _ in sorted(his, key=lambda t: t[0])]
            hp = [p for _, p in sorted(his, key=lambda t: t[0])]
            lx = [base + i for i, _ in sorted(los, key=lambda t: t[0])]
            lp = [p for _, p in sorted(los, key=lambda t: t[0])]
            su, iu, r2u = _Geo.linreg(hx, hp)
            sl, il, r2l = _Geo.linreg(lx, lp)
            if min(r2u, r2l) < 0.55:
                return res
            atr = q_atr_from_lists(h, l, c, 14)
            a = atr[-1] if atr else (max(h[-50:]) - min(l[-50:])) / 8 + 1e-9
            up_now = su * (n - 1) + iu
            lo_now = sl * (n - 1) + il
            width_now = (up_now - lo_now) / (a + 1e-12)
            if width_now < 0.3 or width_now > 12:
                return res
            flat = a / max(30, lookback)  # slope epsilon scaled to data
            is_sym = su < -flat and sl > flat
            is_asc = abs(su) <= flat * 2 and sl > flat
            is_desc = abs(sl) <= flat * 2 and su < -flat
            if not (is_sym or is_asc or is_desc):
                return res
            # Apex projection (where rails meet)
            if abs(su - sl) > 1e-12:
                apex_x = (il - iu) / (su - sl)
                apex_in = apex_x - (n - 1)
            else:
                apex_in = None
            px = c[-1]
            if is_asc:
                pat, direction = "ASC_TRI", 1
            elif is_desc:
                pat, direction = "DESC_TRI", -1
            else:
                # Symmetrical: trade the break side
                if px > up_now:
                    pat, direction = "SYM_TRI_UP", 1
                elif px < lo_now:
                    pat, direction = "SYM_TRI_DN", -1
                else:
                    pat, direction = "SYM_TRI", 0
            conf = 0.45 + 0.25 * min(r2u, r2l) + (0.15 if direction != 0 else 0)
            res.update({"pattern": pat, "dir": direction, "conf": float(qclip(conf, 0, 0.9)),
                        "apex_in": (float(apex_in) if apex_in is not None else None),
                        "upper": float(up_now), "lower": float(lo_now),
                        "invalid": float(lo_now if direction >= 0 else up_now)})
            return res
        except Exception:
            return res


class WedgePack:
    """Rising/falling wedges: converging rails slanting WITH the move (reversal)."""

    def detect(self, h, l, c, lookback=100):
        res = {"pattern": None, "dir": 0, "conf": 0.0}
        try:
            n = len(c)
            if n < lookback // 2 + 20:
                return res
            sw = SwingStructure(width=4)
            his, los = sw.swings(h[-lookback:], l[-lookback:], limit=8)
            if len(his) < 2 or len(los) < 2:
                return res
            base = n - lookback
            su, _, r2u = _Geo.linreg([base + i for i, _ in sorted(his, key=lambda t: t[0])],
                                     [p for _, p in sorted(his, key=lambda t: t[0])])
            sl, _, r2l = _Geo.linreg([base + i for i, _ in sorted(los, key=lambda t: t[0])],
                                     [p for _, p in sorted(los, key=lambda t: t[0])])
            if min(r2u, r2l) < 0.6:
                return res
            atr = q_atr_from_lists(h, l, c, 14)
            a = atr[-1] if atr else 1e-9
            flat = a / max(30, lookback)
            rising = su > flat and sl > flat and su < sl  # converging upward
            falling = su < -flat and sl < -flat and su > sl  # converging downward
            if rising:
                res.update({"pattern": "RISING_WEDGE", "dir": -1,
                            "conf": float(0.5 + 0.2 * min(r2u, r2l))})
            elif falling:
                res.update({"pattern": "FALLING_WEDGE", "dir": 1,
                            "conf": float(0.5 + 0.2 * min(r2u, r2l))})
            return res
        except Exception:
            return res


class FlagPack:
    """Bull/bear flags + pennants: pole impulse then tight consolidation."""

    def detect(self, h, l, c):
        res = {"pattern": None, "dir": 0, "conf": 0.0, "pole_r": 0.0}
        try:
            n = len(c)
            if n < 60:
                return res
            atr = q_atr_from_lists(h, l, c, 14)
            a = atr[-1] if atr else 1e-9
            # Pole: max 10-bar displacement in last 30 bars
            best, bj = 0.0, 0
            for j in range(n - 30, n - 8):
                disp = abs(c[j + 8] - c[j]) / (a + 1e-12)
                if disp > best:
                    best, bj = disp, j
            if best < 2.0:
                return res
            direction = 1 if c[bj + 8] > c[bj] else -1
            # Consolidation: last 8-20 bars range < 40% of pole
            cons = c[max(bj + 8, n - 20):]
            if len(cons) < 6:
                return res
            crng = (max(cons) - min(cons)) / (a + 1e-12)
            pole = abs(c[bj + 8] - c[bj]) / (a + 1e-12)
            if crng > 0.45 * pole:
                return res
            # Pennant vs flag: contracting range?
            halves = [cons[:len(cons) // 2], cons[len(cons) // 2:]]
            hr = [(max(x) - min(x)) for x in halves]
            kind = "PENNANT" if hr[1] < hr[0] * 0.8 else "FLAG"
            px = c[-1]
            trig = max(cons) if direction > 0 else min(cons)
            fired = (px > trig) if direction > 0 else (px < trig)
            res.update({"pattern": f"{'BULL' if direction > 0 else 'BEAR'}_{kind}",
                        "dir": direction, "pole_r": float(pole),
                        "conf": float(0.5 + (0.2 if fired else 0) + min(0.15, pole / 40))})
            return res
        except Exception:
            return res


class ChannelPack:
    """Parallel channels: equidistance rails with 2+ touches per side."""

    def detect(self, h, l, c, lookback=100):
        res = {"pattern": None, "dir": 0, "conf": 0.0, "pos": 0.5,
               "upper": 0.0, "lower": 0.0}
        try:
            n = len(c)
            if n < lookback // 2 + 20:
                return res
            sw = SwingStructure(width=5)
            his, los = sw.swings(h[-lookback:], l[-lookback:], limit=8)
            if len(his) < 2 or len(los) < 2:
                return res
            base = n - lookback
            su, iu, r2u = _Geo.linreg([base + i for i, _ in sorted(his, key=lambda t: t[0])],
                                      [p for _, p in sorted(his, key=lambda t: t[0])])
            sl, il, r2l = _Geo.linreg([base + i for i, _ in sorted(los, key=lambda t: t[0])],
                                      [p for _, p in sorted(los, key=lambda t: t[0])])
            if min(r2u, r2l) < 0.6:
                return res
            atr = q_atr_from_lists(h, l, c, 14)
            a = atr[-1] if atr else 1e-9
            # Parallelism: slopes within tolerance
            if abs(su - sl) > a / lookback * 2:
                return res
            up_now = su * (n - 1) + iu
            lo_now = sl * (n - 1) + il
            width = (up_now - lo_now) / (a + 1e-12)
            if width < 0.8 or width > 15:
                return res
            pos = (c[-1] - lo_now) / (up_now - lo_now + 1e-12)
            tilt = qsign(su + sl)
            res.update({"pattern": "CHANNEL_UP" if tilt > 0 else ("CHANNEL_DN" if tilt < 0 else "CHANNEL_FLAT"),
                        "dir": int(tilt), "pos": float(qclip(pos, 0, 1)),
                        "upper": float(up_now), "lower": float(lo_now),
                        "conf": float(0.5 + 0.2 * min(r2u, r2l))})
            return res
        except Exception:
            return res


class DoublePack:
    """Double tops/bottoms (and triple): equal-extreme rejections."""

    def detect(self, h, l, c):
        res = {"pattern": None, "dir": 0, "conf": 0.0, "neck": 0.0}
        try:
            n = len(c)
            if n < 60:
                return res
            atr = q_atr_from_lists(h, l, c, 14)
            a = atr[-1] if atr else 1e-9
            sw = SwingStructure(width=5)
            his, los = sw.swings(h, l, limit=8)
            # Double top: two highs within 0.25 ATR, valley between, neck break
            sh = sorted(his, key=lambda t: t[0])
            for i in range(1, len(sh)):
                (x1, p1), (x2, p2) = sh[i - 1], sh[i]
                if x2 - x1 < 8 or abs(p1 - p2) > 0.3 * a:
                    continue
                valley = min(l[x1:x2 + 1]) if x2 < len(l) else None
                if valley is None:
                    continue
                depth = (min(p1, p2) - valley) / (a + 1e-12)
                if depth < 1.0:
                    continue
                broke = c[-1] < valley
                res.update({"pattern": "DOUBLE_TOP", "dir": -1, "neck": float(valley),
                            "conf": float(0.5 + (0.25 if broke else 0) + min(0.15, depth / 20))})
                return res
            sl = sorted(los, key=lambda t: t[0])
            for i in range(1, len(sl)):
                (x1, p1), (x2, p2) = sl[i - 1], sl[i]
                if x2 - x1 < 8 or abs(p1 - p2) > 0.3 * a:
                    continue
                peak = max(h[x1:x2 + 1]) if x2 < len(h) else None
                if peak is None:
                    continue
                height = (peak - max(p1, p2)) / (a + 1e-12)
                if height < 1.0:
                    continue
                broke = c[-1] > peak
                res.update({"pattern": "DOUBLE_BOTTOM", "dir": 1, "neck": float(peak),
                            "conf": float(0.5 + (0.25 if broke else 0) + min(0.15, height / 20))})
                return res
            return res
        except Exception:
            return res


class RoundTurnPack:
    """Rounded tops/bottoms (saucer): curvature + handle break."""

    def detect(self, h, l, c, lookback=90):
        res = {"pattern": None, "dir": 0, "conf": 0.0}
        try:
            seg = [float(v) for v in c[-lookback:]]
            if len(seg) < 60:
                return res
            import statistics as _st
            # Fit parabola: y = A x^2 + B x + C (sign of A = bowl or dome)
            n = len(seg)
            xs = [(i / (n - 1) - 0.5) * 2 for i in range(n)]  # [-1, 1]
            mx2 = sum(x * x for x in xs) / n
            my = sum(seg) / n
            a_num = sum((x * x - mx2) * (y - my) for x, y in zip(xs, seg))
            a_den = sum((x * x - mx2) ** 2 for x in xs) + 1e-12
            acc = a_num / a_den
            rng = max(seg) - min(seg) + 1e-12
            curve = abs(acc) / rng
            if curve < 0.15:
                return res
            # Trend into the turn must oppose the bowl direction (reversal setup)
            first_q = sum(seg[:n // 4]) / (n // 4)
            if acc > 0 and seg[-1] > first_q * 0.999:  # bowl bottoming, price lifting
                res.update({"pattern": "ROUND_BOTTOM", "dir": 1,
                            "conf": float(qclip(0.4 + curve, 0, 0.85))})
            elif acc < 0 and seg[-1] < first_q * 1.001:
                res.update({"pattern": "ROUND_TOP", "dir": -1,
                            "conf": float(qclip(0.4 + curve, 0, 0.85))})
            return res
        except Exception:
            return res


class ChartPatternSuite:
    """F4 facade: all geometry -> ranked frames + net bias."""

    def __init__(self):
        self.tri = TrianglePack()
        self.wedge = WedgePack()
        self.flag = FlagPack()
        self.chan = ChannelPack()
        self.dbl = DoublePack()
        self.rnd = RoundTurnPack()

    def scan(self, df):
        out = {"frames": [], "bias": 0.0, "conf": 0.0}
        try:
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            c = qas_series(df, "close")
            if len(c) < 80:
                return out
            cands = []
            for name, fn in (("triangle", lambda: self.tri.detect(h, l, c)),
                             ("wedge", lambda: self.wedge.detect(h, l, c)),
                             ("flag", lambda: self.flag.detect(h, l, c)),
                             ("channel", lambda: self.chan.detect(h, l, c)),
                             ("double", lambda: self.dbl.detect(h, l, c)),
                             ("round", lambda: self.rnd.detect(h, l, c))):
                try:
                    r = fn()
                    if r.get("pattern"):
                        r["family"] = name
                        cands.append(r)
                except Exception:
                    continue
            cands.sort(key=lambda r: -r.get("conf", 0))
            out["frames"] = cands[:4]
            if cands:
                tot = sum(r["conf"] for r in cands) or 1.0
                out["bias"] = float(sum(r["dir"] * r["conf"] for r in cands) / tot)
                b = [r["dir"] for r in cands]
                out["conf"] = float((1 - (max(b) - min(b)) / 4) * min(1.0, tot / 1.5))
            return out
        except Exception:
            return out


# ============================================================================
# O2 — MICROSTRUCTURE PACK (flow, impact, realized-vol estimators)
# ----------------------------------------------------------------------------
# Garman-Klass / Yang-Zhang volatility, Amihud illiquidity, Kyle-lambda
# impact proxy, VPIN-lite toxicity, tick imbalance. Feeds execution timing
# (when to be patient) and the early gate's liquidity evidence.
# ============================================================================

class RealizedVolPack:
    """Range-based vol estimators (10x more efficient than close-close)."""

    @staticmethod
    def garman_klass(o, h, l, c, n=20):
        try:
            import math as _m
            m = min(len(o), len(h), len(l), len(c))
            if m < n + 2:
                return 0.0
            acc = 0.0
            for i in range(m - n, m):
                if min(o[i], h[i], l[i], c[i]) <= 0:
                    continue
                hl = _m.log(h[i] / l[i])
                co = _m.log(c[i] / o[i])
                acc += 0.5 * hl * hl - (2 * _m.log(2) - 1) * co * co
            return float((acc / n) ** 0.5)
        except Exception:
            return 0.0

    @staticmethod
    def yang_zhang(o, h, l, c, n=20, k=0.34):
        try:
            import math as _m
            m = min(len(o), len(h), len(l), len(c))
            if m < n + 3:
                return 0.0
            co2, oc2, rs = 0.0, 0.0, 0.0
            for i in range(m - n, m):
                if min(o[i], h[i], l[i], c[i], c[i - 1]) <= 0:
                    continue
                co2 += _m.log(o[i] / c[i - 1]) ** 2
                oc2 += _m.log(c[i] / o[i]) ** 2
                hl = _m.log(h[i] / l[i])
                co = _m.log(c[i] / o[i])
                rs += 0.5 * hl * hl - (2 * _m.log(2) - 1) * co * co
            var = (co2 + k * oc2 + (1 - k) * rs) / n
            return float(max(0.0, var) ** 0.5)
        except Exception:
            return 0.0

    def regime_vol(self, df, n=20):
        """Returns {gk, yz, ratio_to_median, state} with adaptive state."""
        out = {"gk": 0.0, "yz": 0.0, "ratio": 1.0, "state": "NORMAL"}
        try:
            o = qas_series(df, "open")
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            c = qas_series(df, "close")
            gk = self.garman_klass(o, h, l, c, n)
            yz = self.yang_zhang(o, h, l, c, n)
            out.update({"gk": float(gk), "yz": float(yz)})
            # Rolling median of past GK for ratio (adaptive, windowed)
            hist = []
            for end in range(len(c) - 120, len(c) - n, 10):
                if end > n + 2:
                    hist.append(self.garman_klass(o[:end], h[:end], l[:end], c[:end], n))
            hist = [x for x in hist if x > 0]
            if hist:
                import statistics as _st
                med = _st.median(hist) or 1e-12
                out["ratio"] = float(gk / med)
                if out["ratio"] >= 2.2:
                    out["state"] = "EXPLOSION"
                elif out["ratio"] >= 1.5:
                    out["state"] = "ELEVATED"
                elif out["ratio"] <= 0.55:
                    out["state"] = "COMPRESSION"
            return out
        except Exception:
            return out


class ImpactPack:
    """Amihud illiquidity + Kyle-lambda impact proxy from OHLCV."""

    def analyze(self, df, n=50):
        res = {"amihud": 0.0, "kyle": 0.0, "illiquid": False}
        try:
            c = qas_series(df, "close")
            v = VwapPack._vols(df)
            m = min(len(c), len(v))
            if m < n + 2:
                return res
            rets = [abs(c[i] / c[i - 1] - 1) for i in range(m - n, m) if c[i - 1]]
            vols = [v[i] for i in range(m - n, m)]
            # Amihud: mean(|r| / volume)
            am = sum(r / (x + 1e-12) for r, x in zip(rets, vols)) / max(1, len(rets))
            # Kyle lambda: slope of signed-sqrt-volume -> return
            import math as _m
            xs, ys = [], []
            for i in range(m - n, m):
                r = (c[i] / c[i - 1] - 1) if c[i - 1] else 0
                xs.append(_m.copysign(_m.sqrt(abs(v[i])), r))
                ys.append(abs(r))
            slope, _, r2 = _Geo.linreg(xs, ys)
            res.update({"amihud": float(am), "kyle": float(max(0.0, slope)),
                        "kyle_r2": float(r2)})
            # Illiquid if Amihud above its own rolling median x1.8
            hist = []
            for end in range(m - 150, m - n, 15):
                if end > n + 2:
                    rr = [abs(c[i] / c[i - 1] - 1) for i in range(end - n, end) if c[i - 1]]
                    vv = [v[i] for i in range(end - n, end)]
                    if rr and vv:
                        hist.append(sum(r / (x + 1e-12) for r, x in zip(rr, vv)) / len(rr))
            if hist:
                import statistics as _st
                res["illiquid"] = bool(am > (_st.median(hist) or 1e-12) * 1.8)
            return res
        except Exception:
            return res


class VpinLite:
    """Toxicity via signed-volume buckets (VPIN spirit, bar implementation)."""

    def toxicity(self, df, buckets=10, window=5):
        res = {"vpin": 0.0, "toxic": False}
        try:
            o = qas_series(df, "open")
            c = qas_series(df, "close")
            v = VwapPack._vols(df)
            n = min(len(o), len(c), len(v))
            if n < buckets * window + 10:
                return res
            vals = []
            for b in range(window):
                seg_o = o[n - (b + 1) * buckets:n - b * buckets or None]
                seg_c = c[n - (b + 1) * buckets:n - b * buckets or None]
                seg_v = v[n - (b + 1) * buckets:n - b * buckets or None]
                buy = sum(x for oo, cc, x in zip(seg_o, seg_c, seg_v) if cc >= oo)
                sell = sum(x for oo, cc, x in zip(seg_o, seg_c, seg_v) if cc < oo)
                tot = buy + sell + 1e-12
                vals.append(abs(buy - sell) / tot)
            vpin = sum(vals) / max(1, len(vals))
            res.update({"vpin": float(vpin), "toxic": bool(vpin > 0.65)})
            return res
        except Exception:
            return res


class ImbalancePack:
    """Tick/dollar imbalance: short-horizon direction pressure."""

    def pressure(self, df, n=20):
        res = {"imbalance": 0.0, "bars_up": 0, "bars_dn": 0}
        try:
            o = qas_series(df, "open")
            c = qas_series(df, "close")
            v = VwapPack._vols(df)
            m = min(len(o), len(c), len(v))
            if m < n + 1:
                return res
            up = sum(v[i] for i in range(m - n, m) if c[i] >= o[i])
            dn = sum(v[i] for i in range(m - n, m) if c[i] < o[i])
            res["imbalance"] = float((up - dn) / (up + dn + 1e-12))
            res["bars_up"] = sum(1 for i in range(m - n, m) if c[i] >= o[i])
            res["bars_dn"] = n - res["bars_up"]
            return res
        except Exception:
            return res


class MicrostructureSuite:
    """O2 facade: execution-timing evidence in one call."""

    def __init__(self):
        self.rv = RealizedVolPack()
        self.impact = ImpactPack()
        self.vpin = VpinLite()
        self.imb = ImbalancePack()

    def scan(self, df):
        out = {"vol": {}, "impact": {}, "vpin": {}, "imbalance": {},
               "patient": False, "reasons": []}
        try:
            out["vol"] = self.rv.regime_vol(df)
            out["impact"] = self.impact.analyze(df)
            out["vpin"] = self.vpin.toxicity(df)
            out["imbalance"] = self.imb.pressure(df)
            if out["vol"].get("state") in ("EXPLOSION",):
                out["patient"] = True
                out["reasons"].append("vol explosion: use limits")
            if out["impact"].get("illiquid"):
                out["patient"] = True
                out["reasons"].append("illiquid: slice/patient")
            if out["vpin"].get("toxic"):
                out["patient"] = True
                out["reasons"].append("toxic flow: stand down briefly")
            return out
        except Exception:
            return out


SECTION_F4O2_OK = True
