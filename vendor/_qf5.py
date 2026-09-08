
# ============================================================================
# F5 — ADAPTIVE SIGNAL SYSTEM PACK (20 classic systems, breathing edition)
# ----------------------------------------------------------------------------
# Every system outputs {bias(-1..1), conf(0..1), detail}. Lengths breathe
# with volatility; trigger levels calibrate to each series' own history.
# F5Suite pools all 20 into one vote the radar/decider consume.
# ============================================================================

class _F5Base:
    @staticmethod
    def _series(df):
        return (qas_series(df, "open"), qas_series(df, "high"),
                qas_series(df, "low"), qas_series(df, "close"))

    @staticmethod
    def _atr(h, l, c, n=14):
        a = q_atr_from_lists(h, l, c, n)
        return a[-1] if a else 0.0

    @staticmethod
    def _out(bias=0.0, conf=0.0, **kw):
        d = {"bias": float(qclip(bias, -1, 1)), "conf": float(qclip(conf, 0, 1))}
        d.update(kw)
        return d


class SupertrendAdaptive(_F5Base):
    """Supertrend with ATR multiplier from the band's own efficiency history."""

    def analyze(self, df, n=10):
        try:
            o, h, l, c = self._series(df)
            if len(c) < n + 30:
                return self._out()
            atr = q_atr_from_lists(h, l, c, n)
            hl2 = [(h[i] + l[i]) / 2 for i in range(len(c))]
            # Adaptive multiplier: efficient trends => tighter (2.2), chop => wider (3.6)
            eff = q_efficiency(c, 50)
            mult = 3.6 - 1.4 * eff
            up = [hl2[0] - mult * atr[0]]
            dn = [hl2[0] + mult * atr[0]]
            trend = [1]
            for i in range(1, len(c)):
                bu = hl2[i] - mult * atr[i]
                bd = hl2[i] + mult * atr[i]
                bu = max(bu, up[-1]) if c[i - 1] > up[-1] else bu
                bd = min(bd, dn[-1]) if c[i - 1] < dn[-1] else bd
                up.append(bu)
                dn.append(bd)
                if trend[-1] == 1 and c[i] < bu:
                    trend.append(-1)
                elif trend[-1] == -1 and c[i] > bd:
                    trend.append(1)
                else:
                    trend.append(trend[-1])
            t = trend[-1]
            dist = abs(c[-1] - (up[-1] if t > 0 else dn[-1])) / (atr[-1] + 1e-12)
            return self._out(t * qclip(dist / 2 + 0.4, 0, 1), 0.5 + 0.3 * eff,
                             mult=round(mult, 2), line=float(up[-1] if t > 0 else dn[-1]))
        except Exception:
            return self._out()


class ChandelierPack(_F5Base):
    """Chandelier exits: highest-high/lowest-low minus N×ATR (N adaptive)."""

    def analyze(self, df, n=22):
        try:
            o, h, l, c = self._series(df)
            if len(c) < n + 5:
                return self._out()
            a = self._atr(h, l, c)
            mult = 2.4 + 0.8 * (1 - q_efficiency(c, 50))
            long_stop = max(h[-n:]) - mult * a
            short_stop = min(l[-n:]) + mult * a
            px = c[-1]
            if px > long_stop and px > short_stop:
                bias = qclip((px - long_stop) / (a + 1e-12) / 3, 0, 1)
            elif px < short_stop and px < long_stop:
                bias = -qclip((short_stop - px) / (a + 1e-12) / 3, 0, 1)
            else:
                bias = 0.0
            return self._out(bias, 0.55, long_stop=float(long_stop),
                             short_stop=float(short_stop), mult=round(mult, 2))
        except Exception:
            return self._out()


class PsarBreathing(_F5Base):
    """Parabolic SAR with acceleration breathing by ADX strength."""

    def analyze(self, df):
        try:
            o, h, l, c = self._series(df)
            if len(c) < 30:
                return self._out()
            dmi = q_adx_dmi(h, l, c, 14)
            af_max = 0.08 + 0.14 * qclip(dmi["adx"], 0, 1)
            up = c[1] > c[0]
            sar = l[0] if up else h[0]
            ep = h[0] if up else l[0]
            af = 0.02
            for i in range(1, len(c)):
                sar = sar + af * (ep - sar)
                if up:
                    sar = min(sar, l[i - 1], l[i] if i < len(l) else l[-1])
                    if c[i] > ep:
                        ep = c[i]
                        af = min(af_max, af + 0.02)
                    if c[i] < sar:
                        up, sar, ep, af = False, ep, l[i], 0.02
                else:
                    sar = max(sar, h[i - 1], h[i] if i < len(h) else h[-1])
                    if c[i] < ep:
                        ep = c[i]
                        af = min(af_max, af + 0.02)
                    if c[i] > sar:
                        up, sar, ep, af = True, ep, h[i], 0.02
            a = self._atr(h, l, c)
            dist = abs(c[-1] - sar) / (a + 1e-12)
            return self._out((1 if up else -1) * qclip(dist / 2 + 0.35, 0, 1),
                             0.45 + 0.3 * qclip(dmi["adx"], 0, 1), sar=float(sar))
        except Exception:
            return self._out()


class KeltnerIgnition(_F5Base):
    """Squeeze→ignition trigger: compression percentile + break of micro-rail."""

    def analyze(self, df, n=20):
        try:
            o, h, l, c = self._series(df)
            if len(c) < n + 40:
                return self._out()
            m = sum(c[-n:]) / n
            atr = q_atr_from_lists(h, l, c, 14)
            a = atr[-1] if atr else 1e-9
            widths = []
            for k in range(60, 0, -1):
                seg = c[-k - n:-k] or c[:n]
                mm = sum(seg) / max(1, len(seg))
                aa = atr[-k] if k <= len(atr) else a
                widths.append(2 * 1.5 * aa / (abs(mm) + 1e-12))
            now_w = 2 * 1.5 * a / (abs(m) + 1e-12)
            pct = sum(1 for w in widths if w <= now_w) / max(1, len(widths))
            rail = sum(c[-5:]) / 5
            ignite = (c[-1] - rail) / (a + 1e-12)
            if pct < 0.25 and abs(ignite) > 0.6:
                return self._out(qsign(ignite) * qclip(abs(ignite) / 2, 0.4, 1),
                                 0.55 + 0.2 * (1 - pct))
            return self._out(qclip(ignite / 3, -0.5, 0.5), 0.25, squeeze_pct=round(pct, 2))
        except Exception:
            return self._out()


class SchaffPack(_F5Base):
    """Schaff Trend Cycle approximation (stochastic of MACD, double-smoothed)."""

    def analyze(self, df, fast=12, slow=26, cycle=10):
        try:
            c = qas_series(df, "close")
            if len(c) < slow + cycle * 2 + 10:
                return self._out()
            def _ema(v, s):
                o = [v[0]]
                a = 2 / (s + 1)
                for x in v[1:]:
                    o.append(a * x + (1 - a) * o[-1])
                return o
            macd = [a - b for a, b in zip(_ema(c, fast), _ema(c, slow))]
            def _st(v, n):
                o = []
                for i in range(len(v)):
                    w = v[max(0, i - n + 1):i + 1]
                    o.append((v[i] - min(w)) / (max(w) - min(w) + 1e-12) * 100)
                return o
            st1 = _st(macd, cycle)
            st2 = _st(_ema(st1, cycle // 2 or 1), cycle)
            v = st2[-1]
            prev = st2[-2]
            bias = qclip((v - 50) / 50, -1, 1) * 0.6 + qclip((v - prev) / 20, -1, 1) * 0.4
            return self._out(bias, 0.5 + abs(v - 50) / 200, value=round(v, 1))
        except Exception:
            return self._out()


class FisherPack(_F5Base):
    """Fisher Transform of median price (turning-point sharpener)."""

    def analyze(self, df, n=9):
        try:
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            if len(h) < n + 10:
                return self._out()
            med = [(h[i] + l[i]) / 2 for i in range(len(h))]
            fish = [0.0]
            for i in range(1, len(med)):
                w = med[max(0, i - n + 1):i + 1]
                hi, lo = max(w), min(w)
                val = 0.0 if hi == lo else 0.66 * ((med[i] - lo) / (hi - lo) - 0.5) + 0.67 * fish[-1] * 0.5
                val = max(-0.999, min(0.999, val))
                import math as _m
                fish.append(0.5 * _m.log((1 + val) / (1 - val)) + 0.5 * fish[-1])
            trig = fish[-2] if len(fish) > 1 else 0
            cross = fish[-1] - trig
            return self._out(qclip(fish[-1] / 3, -1, 1) * 0.5 + qclip(cross * 2, -1, 1) * 0.5,
                             0.45 + min(0.3, abs(cross)), value=round(fish[-1], 2))
        except Exception:
            return self._out()


class LaguerrePack(_F5Base):
    """Laguerre RSI (time-warped, gamma adaptive to efficiency)."""

    def analyze(self, df, gamma=None):
        try:
            c = qas_series(df, "close")
            if len(c) < 40:
                return self._out()
            eff = q_efficiency(c, 50)
            g = gamma if gamma is not None else (0.55 + 0.3 * eff)
            L0 = L1 = L2 = L3 = [0.0] * len(c)
            L0[0], L1[0], L2[0], L3[0] = c[0], c[0], c[0], c[0]
            for i in range(1, len(c)):
                L0[i] = (1 - g) * c[i] + g * L0[i - 1]
                L1[i] = -g * L0[i] + L0[i - 1] + g * L1[i - 1]
                L2[i] = -g * L1[i] + L1[i - 1] + g * L2[i - 1]
                L3[i] = -g * L2[i] + L2[i - 1] + g * L3[i - 1]
            cu = cd = 0.0
            for a, b in ((L0[-1], L1[-1]), (L1[-1], L2[-1]), (L2[-1], L3[-1])):
                if a >= b:
                    cu += a - b
                else:
                    cd += b - a
            rsi = cu / (cu + cd + 1e-12)
            return self._out(qclip((rsi - 0.5) * 2.2, -1, 1),
                             0.45 + abs(rsi - 0.5) * 0.6, value=round(rsi, 3))
        except Exception:
            return self._out()


class TsiPack(_F5Base):
    """True Strength Index (double-smoothed momentum)."""

    def analyze(self, df, fast=13, slow=25):
        try:
            c = qas_series(df, "close")
            if len(c) < slow + 10:
                return self._out()
            m = [c[i] - c[i - 1] for i in range(1, len(c))]
            am = [abs(x) for x in m]
            def _ema(v, s):
                o = [v[0]]
                a = 2 / (s + 1)
                for x in v[1:]:
                    o.append(a * x + (1 - a) * o[-1])
                return o
            tsi = _ema(_ema(m, slow), fast)[-1] / (_ema(_ema(am, slow), fast)[-1] + 1e-12) * 100
            sig = _ema(_ema(m, slow), fast)
            tsi_prev = sig[-2] / (_ema(_ema(am, slow), fast)[-2] + 1e-12) * 100 if len(sig) > 1 else tsi
            return self._out(qclip(tsi / 50, -1, 1) * 0.6 + qclip((tsi - tsi_prev) / 10, -1, 1) * 0.4,
                             0.5, value=round(tsi, 2))
        except Exception:
            return self._out()


class ElderPack(_F5Base):
    """Elder Impulse: EMA slope × MACD-histogram agreement."""

    def analyze(self, df, n=13):
        try:
            c = qas_series(df, "close")
            if len(c) < 40:
                return self._out()
            def _ema(v, s):
                o = [v[0]]
                a = 2 / (s + 1)
                for x in v[1:]:
                    o.append(a * x + (1 - a) * o[-1])
                return o
            e = _ema(c, n)
            slope = e[-1] - e[-3]
            macd = [a - b for a, b in zip(_ema(c, 12), _ema(c, 26))]
            hist = macd[-1] - _ema(macd, 9)[-1]
            green = slope > 0 and hist > 0
            red = slope < 0 and hist < 0
            a = self._atr(qas_series(df, "high"), qas_series(df, "low"), c)
            mag = qclip(abs(slope) / (a + 1e-12) * 3, 0, 1)
            if green:
                return self._out(0.4 + 0.6 * mag, 0.6 + 0.2 * mag, color="green")
            if red:
                return self._out(-0.4 - 0.6 * mag, 0.6 + 0.2 * mag, color="red")
            return self._out(qsign(slope + hist) * 0.25, 0.3, color="blue")
        except Exception:
            return self._out()


class CoppockPack(_F5Base):
    """Coppock Guide (long-horizon accumulation detector)."""

    def analyze(self, df):
        try:
            c = qas_series(df, "close")
            if len(c) < 60:
                return self._out()
            r11 = [(c[i] / c[i - 11] - 1) * 100 for i in range(11, len(c))]
            r14 = [(c[i] / c[i - 14] - 1) * 100 for i in range(14, len(c))]
            roc = [a + b for a, b in zip(r11[-len(r14):], r14)]
            def _wma(v, n):
                wts = list(range(1, n + 1))
                return sum(x * w for x, w in zip(v[-n:], wts)) / sum(wts)
            cop = _wma(roc, 10)
            cop_prev = _wma(roc[:-1], 10)
            turning = (cop - cop_prev) > 0
            return self._out(qclip(cop / 15, -1, 1) * 0.5 + (0.4 if turning else -0.4),
                             0.5, value=round(cop, 2))
        except Exception:
            return self._out()


class KlingerPack(_F5Base):
    """Klinger Volume Oscillator (trend × volume force)."""

    def analyze(self, df):
        try:
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            c = qas_series(df, "close")
            v = VwapPack._vols(df)
            n = min(len(h), len(l), len(c), len(v))
            if n < 60:
                return self._out()
            hl2 = [((h[i] + l[i] + c[i]) / 3) for i in range(n)]
            vf = []
            for i in range(1, n):
                d = 1 if hl2[i] >= hl2[i - 1] else -1
                vf.append(d * v[i])
            def _ema(vals, s):
                o = [vals[0]]
                a = 2 / (s + 1)
                for x in vals[1:]:
                    o.append(a * x + (1 - a) * o[-1])
                return o
            kvo = _ema(vf, 34)[-1] - _ema(vf, 55)[-1]
            scale = sum(v[-55:]) / 55 + 1e-12
            kn = kvo / scale
            return self._out(qclip(kn * 8, -1, 1), 0.45 + min(0.3, abs(kn) * 4))
        except Exception:
            return self._out()


class ChaikinPack(_F5Base):
    """Chaikin Money Flow + A/D slope (accumulation/distribution)."""

    def analyze(self, df, n=20):
        try:
            h = qas_series(df, "high")
            l = qas_series(df, "low")
            c = qas_series(df, "close")
            v = VwapPack._vols(df)
            m = min(len(h), len(l), len(c), len(v))
            if m < n + 10:
                return self._out()
            mfv = []
            for i in range(m):
                rng = h[i] - l[i]
                mfm = ((c[i] - l[i]) - (h[i] - c[i])) / (rng + 1e-12) if rng > 0 else 0
                mfv.append(mfm * v[i])
            cmf = sum(mfv[-n:]) / (sum(v[-n:]) + 1e-12)
            ad = []
            run = 0.0
            for x in mfv:
                run += x
                ad.append(run)
            slope = (ad[-1] - ad[-10]) / (sum(v[-10:]) + 1e-12)
            return self._out(qclip(cmf * 3, -1, 1) * 0.6 + qclip(slope * 30, -1, 1) * 0.4,
                             0.5, cmf=round(cmf, 3))
        except Exception:
            return self._out()


class ObvPressure(_F5Base):
    """OBV z-score + slope (smart-money footprints)."""

    def analyze(self, df, n=50):
        try:
            c = qas_series(df, "close")
            v = VwapPack._vols(df)
            m = min(len(c), len(v))
            if m < n + 10:
                return self._out()
            obv = [0.0]
            for i in range(1, m):
                d = 0
                if c[i] > c[i - 1]:
                    d = 1
                elif c[i] < c[i - 1]:
                    d = -1
                obv.append(obv[-1] + d * v[i])
            z = q_zscore_list(obv, n)
            slope = (obv[-1] - obv[-11]) / (sum(v[-11:]) + 1e-12)
            # Bear/bull confirmation: price vs OBV z alignment
            pz = q_zscore_list(c, n)
            agree = 1.0 if qsign(z) == qsign(pz) else 0.4
            return self._out(qclip(z / 2.5, -1, 1) * 0.6 + qclip(slope * 400, -1, 1) * 0.4,
                             0.4 + 0.3 * agree, z=round(z, 2))
        except Exception:
            return self._out()


class VwapDeviate(_F5Base):
    """VWAP deviation regime: stretched rubber snaps back, trends ride."""

    def analyze(self, df):
        try:
            v = VwapPack().analyze(df)
            d = v["dist_sd"]
            tr = v["trend"]
            # Regime-aware: range => fade extremes; trend => ride with pullback discount
            if abs