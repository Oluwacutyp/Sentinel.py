
# ============================================================================
# QSIG — QUANTUM SIGNAL INTEGRATION (multi-TF confluence -> entry ticket)
# ----------------------------------------------------------------------------
# The last mile between analysis and order: stack every timeframe's vote,
# gate by killzone + fuse, validate divergence entries, and emit ONE signed
# EntryTicket the executor can fill blindly. Nothing here trades on a single
# timeframe or a single system ever again.
# ============================================================================

class MultiTFConfluence:
    """Stack votes across timeframes with learned TF weights.

    tf_dfs: {label: df} e.g. {"M15": df1, "H1": df2, "H4": df3}.
    Each TF gets regime + F5 + O votes; HTFs set permission, LTF sets timing.
    """

    DEFAULT_W = {"M1": 0.3, "M5": 0.6, "M15": 1.0, "M30": 1.1, "H1": 1.4,
                 "H4": 2.0, "D1": 2.4}

    def __init__(self):
        self.w = dict(self.DEFAULT_W)
        self._tf_hits = {}  # tf -> [1/0] agreement-with-outcome ledger

    def set_weight(self, tf, w):
        try:
            self.w[str(tf).upper()] = qclip(float(w), 0.1, 4.0)
        except Exception:
            pass

    def learn_tf(self, tf, agreed):
        """Online TF weight learning: TFs that agree with winners gain voice."""
        try:
            k = str(tf).upper()
            l = self._tf_hits.setdefault(k, [])
            l.append(1 if agreed else 0)
            del l[:-100]
            if len(l) >= 20:
                rate = sum(l) / len(l)
                # Drift weight toward 0.4 + 2.4*rate
                target = 0.4 + 2.4 * rate
                self.w[k] = qclip(0.9 * self.w.get(k, 1.0) + 0.1 * target, 0.2, 3.5)
        except Exception:
            pass

    def stack(self, tf_dfs, exec_tf="M15"):
        """Returns {bias, conf, align, tf_votes, permission, timing}."""
        out = {"bias": 0.0, "conf": 0.0, "align": 0.0, "tf_votes": {},
               "permission": 0, "timing": 0.0, "n": 0}
        try:
            votes = []
            for tf, df in (tf_dfs or {}).items():
                k = str(tf).upper()
                try:
                    reg = quantum_regime(df)
                    regime = reg.get("regime", "RANGE") if isinstance(reg, dict) else "RANGE"
                except Exception:
                    regime = "RANGE"
                try:
                    f5 = f5_confluence(df)
                except Exception:
                    f5 = {"bias": 0.0, "conf": 0.0}
                try:
                    ind = quantum_indicators(df)
                    ib = float(ind.get("bias", 0) or 0)
                except Exception:
                    ib = 0.0
                bias = 0.45 * float(f5.get("bias", 0) or 0) + 0.35 * ib
                if "TREND_UP" in regime:
                    bias += 0.2
                elif "TREND_DOWN" in regime:
                    bias -= 0.2
                conf = 0.6 * float(f5.get("conf", 0) or 0) + 0.4 * abs(ib)
                w = self.w.get(k, 1.0)
                out["tf_votes"][k] = {"bias": round(qclip(bias, -1, 1), 3),
                                      "conf": round(qclip(conf, 0, 1), 3),
                                      "regime": regime, "w": round(w, 2)}
                votes.append((qclip(bias, -1, 1), conf, w, k))
            out["n"] = len(votes)
            if not votes:
                return out
            tw = sum(w for _, _, w, _ in votes) or 1.0
            out["bias"] = float(sum(b * w for b, _, w, _ in votes) / tw)
            out["conf"] = float(qclip(sum(c * w for _, c, w, _ in votes) / tw, 0, 1))
            # Alignment: fraction of weight agreeing with the stack sign
            s = qsign(out["bias"])
            agree_w = sum(w for b, _, w, _ in votes if qsign(b) == s and b != 0)
            out["align"] = round(agree_w / tw, 3)
            # Permission: HTF (H1+) majority
            htf = [(b, w) for b, _, w, k in votes if k in ("H1", "H4", "D1", "W1")]
            if htf:
                hw = sum(w for _, w in htf) or 1.0
                hb = sum(b * w for b, w in htf) / hw
                out["permission"] = qsign(hb) if abs(hb) > 0.12 else 0
            # Timing: exec-TF lean
            ex = out["tf_votes"].get(str(exec_tf).upper())
            if ex is not None:
                out["timing"] = ex["bias"]
            return out
        except Exception:
            return out


_MTF_SINGLETON = {"obj": None}


def quantum_mtf(tf_dfs, exec_tf="M15"):
    try:
        o = _MTF_SINGLETON.get("obj")
        if o is None:
            o = MultiTFConfluence()
            _MTF_SINGLETON["obj"] = o
        return o.stack(tf_dfs, exec_tf)
    except Exception:
        return {"bias": 0.0, "conf": 0.0, "align": 0.0, "tf_votes": {},
                "permission": 0, "timing": 0.0, "n": 0}


class KillzoneGate:
    """Session killzones from LEARNED per-symbol stats (not folklore).

    Tracks R by session bucket; gates sessions with negative expectancy
    after enough evidence, boosts proven ones. Cold-start: Table T hint.
    """

    BUCKETS = ("ASIA", "LONDON", "OVERLAP", "NEWYORK", "OFF")

    def __init__(self, symbol="XAUUSD"):
        self.symbol = symbol
        self.by_sess = {b: [] for b in self.BUCKETS}
        try:
            spec = quantum_spec(symbol)
            kz = spec.as_dict().get("killzones", ())
        except Exception:
            kz = ()
        self._prior = {b: (0.5 if b in kz else 0.35) for b in self.BUCKETS}

    def record(self, session, r):
        try:
            b = str(session).upper()
            if b in self.by_sess:
                self.by_sess[b].append(float(r))
                del self.by_sess[b][:-200]
        except Exception:
            pass

    def score(self, session):
        """0..1 tradeability. <0.3 => gate (veto), >0.6 => boost."""
        try:
            b = str(session).upper()
            rows = self.by_sess.get(b, [])
            if len(rows) < 15:
                return self._prior.get(b, 0.4)
            ev = sum(rows) / len(rows)
            wr = sum(1 for r in rows if r > 0) / len(rows)
            # Blend expectancy (scaled) with win rate
            return float(qclip(0.5 + ev * 1.5 + (wr - 0.5) * 0.8, 0.0, 1.0))
        except Exception:
            return 0.4

    def check(self, session):
        s = self.score(session)
        if s < 0.3:
            return {"pass": False, "boost": 0.0, "score": round(s, 3),
                    "reason": f"killzone_cold_{session}"}
        boost = 1.0 + (0.25 if s > 0.6 else 0.0)
        return {"pass": True, "boost": boost, "score": round(s, 3),
                "reason": "killzone_ok"}

    def table(self):
        return {b: {"n": len(v), "ev": round(sum(v) / len(v), 3) if v else 0.0,
                    "score": round(self.score(b), 3)} for b, v in self.by_sess.items()}


_KZ_CACHE = {}


def quantum_killzone(symbol, session):
    try:
        k = str(symbol).upper()
        g = _KZ_CACHE.get(k)
        if g is None:
            g = KillzoneGate(k)
            _KZ_CACHE[k] = g
        return g.check(session)
    except Exception:
        return {"pass": True, "boost": 1.0, "score": 0.5, "reason": "fallback"}


def quantum_killzone_record(symbol, session, r):
    try:
        k = str(symbol).upper()
        g = _KZ_CACHE.get(k)
        if g is None:
            g = KillzoneGate(k)
            _KZ_CACHE[k] = g
        g.record(session, r)
    except Exception:
        pass


class DivergenceEntryValidator:
    """Divergence entries need THREE witnesses: div + RSI-quantile + structure.

    Replaces single-indicator divergence trades (a documented loser in the
    autopsy literature and in our own Phase-D attribution).
    """

    def validate(self, df, div_hint=None):
        out = {"ok": False, "side": 0, "conf": 0.0, "witnesses": []}
        try:
            try:
                ind = quantum_indicators(df)
            except Exception:
                return out
            divs = div_hint if div_hint is not None else ind.get("divs", 0)
            if not divs:
                return out
            o, h, l, c = (qas_series(df, "open"), qas_series(df, "high"),
                          qas_series(df, "low"), qas_series(df, "close"))
            if len(c) < 30:
                return out
            rsi = ind.get("rsi", 50)
            side = -qsign(divs)  # bearish div => short
            # Witness 1: divergence present
            out["witnesses"].append(f"div{divs:+d}")
            # Witness 2: RSI in the right quantile zone
            if side < 0 and rsi >= ind.get("rsi_hi", 70):
                out["witnesses"].append(f"rsi{rsi:.0f}_ob")
            elif side > 0 and rsi <= ind.get("rsi_lo", 30):
                out["witnesses"].append(f"rsi{rsi:.0f}_os")
            else:
                return out
            # Witness 3: structure — micro-swing break in our direction
            if side < 0:
                broke = min(c[-3:]) < min(c[-8:-3])
            else:
                broke = max(c[-3:]) > max(c[-8:-3])
            if not broke:
                return out
            out["witnesses"].append("swing_break")
            out.update({"ok": True, "side": side,
                        "conf": 0.55 + 0.1 * len(out["witnesses"])})
            return out
        except Exception:
            return out


class ConfluenceMatrix:
    """Systems x Timeframes heat grid + text render for the journal."""

    SYSTEMS = ("f5", "indic", "l2", "regime")

    def cell(self, system, df, ctx=None):
        try:
            if system == "f5":
                r = f5_confluence(df)
                return {"bias": r.get("bias", 0), "conf": r.get("conf", 0)}
            if system == "indic":
                r = quantum_indicators(df)
                return {"bias": float(r.get("bias", 0) or 0), "conf": 0.5}
            if system == "l2":
                c2 = dict(ctx or {})
                c2["df"] = df
                r = l2_route(c2)
                return {"bias": r.get("bias", 0), "conf": r.get("conf", 0)}
            if system == "regime":
                r = quantum_regime(df)
                reg = r.get("regime", "RANGE") if isinstance(r, dict) else "RANGE"
                b = 0.5 if "UP" in reg else (-0.5 if "DOWN" in reg else 0.0)
                return {"bias": b, "conf": float(r.get("conf", 0.5) if isinstance(r, dict) else 0.5)}
            return {"bias": 0, "conf": 0}
        except Exception:
            return {"bias": 0, "conf": 0}

    def build(self, tf_dfs, ctx=None):
        grid = {}
        try:
            for tf, df in (tf_dfs or {}).items():
                for sys in self.SYSTEMS:
                    grid[(str(tf).upper(), sys)] = self.cell(sys, df, ctx)
            return grid
        except Exception:
            return grid

    def render_text(self, grid):
        try:
            tfs = sorted({k[0] for k in grid})
            lines = ["TF      " + "  ".join(f"{s:>8}" for s in self.SYSTEMS)]
            for tf in tfs:
                row = [f"{tf:>6}"]
                for s in self.SYSTEMS:
                    cell = grid.get((tf, s), {"bias": 0, "conf": 0})
                    b = cell["bias"]
                    arrow = "▲" if b > 0.15 else ("▼" if b < -0.15 else "·")
                    row.append(f"{arrow}{b:+.2f}  ")
                lines.append("  ".join(row))
            return "\n".join(lines)
        except Exception:
            return "matrix n/a"

    def agreement(self, grid):
        """-1..1 signed agreement across all cells (conf-weighted)."""
        try:
            tw = 0.0
            acc = 0.0
            for cell in grid.values():
                w = cell.get("conf", 0.5)
                acc += cell.get("bias", 0) * w
                tw += w
            return acc / tw if tw else 0.0
        except Exception:
            return 0.0


class SignalFuse:
    """Dedupe + cooldown + regime quota: the same idea fires once."""

    def __init__(self, cooldown_bars=6, max_per_regime=3):
        self.cooldown = cooldown_bars
        self.max_per_regime = max_per_regime
        self._last = {}  # (strategy, side) -> bar_no
        self._regime_count = {}  # regime -> count this regime-epoch
        self._epoch = None

    def check(self, strategy, side, regime, bar_no):
        try:
            if regime != self._epoch:
                self._epoch = regime
                self._regime_count = {}
            key = (str(strategy), int(side))
            last = self._last.get(key, -10 ** 9)
            if bar_no - last < self.cooldown:
                return {"pass": False, "reason": "cooldown"}
            n = self._regime_count.get(regime, 0)
            if n >= self.max_per_regime:
                return {"pass": False, "reason": "regime_quota"}
            self._last[key] = bar_no
            self._regime_count[regime] = n + 1
            return {"pass": True, "reason": "fuse_ok"}
        except Exception:
            return {"pass": True, "reason": "fallback"}


_FUSE_SINGLETON = {"obj": None}


def quantum_fuse(strategy, side, regime, bar_no):
    try:
        o = _FUSE_SINGLETON.get("obj")
        if o is None:
            o = SignalFuse()
            _FUSE_SINGLETON["obj"] = o
        return o.check(strategy, side, regime, bar_no)
    except Exception:
        return {"pass": True, "reason": "fallback"}


class EntryTicket:
    """The signed order instruction. Executors fill it blindly."""

    def __init__(self, **kw):
        self.side = int(kw.get("side", 0))
        self.conf = float(kw.get("conf", 0))
        self.strategy = str(kw.get("strategy", "?"))
        self.regime = str(kw.get("regime", "?"))
        self.session = str(kw.get("session", "?"))
        self.sl_atr = float(kw.get("sl_atr", 2.0))
        self.tp_atr = float(kw.get("tp_atr", 3.0))
        self.lot_mult = float(kw.get("lot_mult", 1.0))
        self.ttl_bars = int(kw.get("ttl_bars", 48))
        self.reason = str(kw.get("reason", ""))
        self.chain = list(kw.get("chain", []))  # decision breadcrumb trail
        self.veto = kw.get("veto")

    def valid(self):
        return self.veto is None and self.side in (1, -1) and self.conf > 0

    def as_dict(self):
        return {"side": self.side, "conf": round(self.conf, 3),
                "strategy": self.strategy, "regime": self.regime,
                "session": self.session, "sl_atr": self.sl_atr,
                "tp_atr": self.tp_atr, "lot_mult": round(self.lot_mult, 3),
                "ttl_bars": self.ttl_bars, "reason": self.reason,
                "chain": self.chain, "veto": self.veto}

    def narrative(self):
        try:
            d = "BUY" if self.side > 0 else "SELL"
            return (f"{d} {self.strategy} @{self.session} conf={self.conf:.2f} "
                    f"SL={self.sl_atr:.1f}a TP={self.tp_atr:.1f}a x{self.lot_mult:.2f} "
                    f"[{self.reason}]")
        except Exception:
            return "ticket?"


def quantum_signal(tf_dfs, ctx=None, exec_tf="M15", symbol="XAUUSD",
                   session="OVERLAP", bar_no=0, regime_hint=None):
    """Full signal pipeline -> EntryTicket (or vetoed ticket).

    Stages: MTF stack -> killzone -> L2 route -> fuse -> E5 calibrate ->
    conformal exits -> risk overlay consult -> signed ticket.
    """
    chain = []
    ctx = dict(ctx or {})
    try:
        mtf = quantum_mtf(tf_dfs, exec_tf)
        chain.append(f"mtf:{mtf.get('bias', 0):+.2f}/{mtf.get('conf', 0):.2f}/align{mtf.get('align', 0):.2f}")
        perm = mtf.get("permission", 0)
        df = (tf_dfs or {}).get(exec_tf) or next(iter((tf_dfs or {}).values()), None)
        if df is None:
            return EntryTicket(veto="no_data", chain=chain)
        try:
            reg = quantum_regime(df)
            regime = reg.get("regime", "RANGE") if isinstance(reg, dict) else "RANGE"
        except Exception:
            regime = regime_hint or "RANGE"
        chain.append(f"regime:{regime}")
        # Killzone
        kz = quantum_killzone(symbol, session)
        chain.append(f"kz:{kz.get('score', 0):.2f}")
        if not kz.get("pass", True):
            return EntryTicket(veto=kz.get("reason"), chain=chain, regime=regime,
                               session=session)
        # Early gate
        try:
            early = quantum_early(df, tick={"spread": ctx.get("s