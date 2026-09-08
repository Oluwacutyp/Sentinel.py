
# ============================================================================
# PHASE K — QUANTUM MONITOR (journal, digest, health)
# ============================================================================

class DecisionJournal:
    """SQLite audit trail: every quantum verdict, queryable for learning."""

    TABLE = "quantum_decisions"

    @staticmethod
    def _conn():
        try:
            st = _qstore()
            return getattr(st, "conn", None)
        except Exception:
            return None

    @classmethod
    def ensure(cls):
        try:
            c = cls._conn()
            if c is None:
                return False
            c.execute(
                f"CREATE TABLE IF NOT EXISTS {cls.TABLE} ("
                "ts TEXT, symbol TEXT, action TEXT, p_win REAL, edge_r REAL, "
                "size_mult REAL, regime TEXT, session TEXT, strategy TEXT, "
                "direction TEXT, reasons TEXT, audit TEXT)")
            try:
                c.commit()
            except Exception:
                pass
            return True
        except Exception:
            return False

    @classmethod
    def log(cls, verdict, symbol=None):
        try:
            if not cls.ensure():
                return False
            import json as _j
            from datetime import datetime as _dt, timezone as _tz
            v = verdict or {}
            sig = v.get("signal") or {}
            aud = dict(v.get("audit") or {})
            aud.pop("candidates", None)
            cls._conn().execute(
                f"INSERT INTO {cls.TABLE} VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (_dt.now(_tz.utc).isoformat(), str(symbol or _qcfg("symbol", "?")),
                 str(v.get("action", "?")), float(v.get("p_win", 0) or 0),
                 float(v.get("edge_r", 0) or 0), float(v.get("size_mult", 0) or 0),
                 str(aud.get("regime", "")), str(aud.get("session", "")),
                 str(sig.get("strategy", "")), str(sig.get("dir", "")),
                 "; ".join(v.get("reasons", []) or [])[:500], _j.dumps(aud)[:2000]))
            try:
                cls._conn().commit()
            except Exception:
                pass
            return True
        except Exception:
            return False

    @classmethod
    def veto_stats(cls, hours=24):
        out = {"n": 0, "trades": 0, "holds": 0, "top_vetoes": []}
        try:
            if not cls.ensure():
                return out
            from datetime import datetime as _dt, timezone as _tz, timedelta as _td
            since = (_dt.now(_tz.utc) - _td(hours=hours)).isoformat()
            rows = cls._conn().execute(
                f"SELECT action, reasons FROM {cls.TABLE} WHERE ts >= ?", (since,)).fetchall()
            out["n"] = len(rows)
            vetoes = {}
            for a, r in rows:
                if str(a).upper() == "TRADE":
                    out["trades"] += 1
                else:
                    out["holds"] += 1
                    key = str(r or "")[:60].split(":")[0]
                    vetoes[key] = vetoes.get(key, 0) + 1
            out["top_vetoes"] = sorted(vetoes.items(), key=lambda kv: -kv[1])[:6]
            return out
        except Exception:
            return out


class QuantumDailyDigest:
    """Evening digest: R tape + regime mix + vetoes + learner health."""

    @staticmethod
    def build(symbol=None, day_trades=None):
        sym = str(symbol or _qcfg("symbol", "XAUUSDm"))
        try:
            trs = day_trades or []
            if not trs:
                try:
                    st = _qstore()
                    if st is not None and hasattr(st, "get_recent_pnls"):
                        pnls = st.get_recent_pnls(limit=50) or []
                        trs = [{"pnl": p} for p in pnls]
                except Exception:
                    pass
            rs = [float(t.get("r", 0) or 0) for t in trs]
            n = len(trs)
            wins = sum(1 for t in trs if float(t.get("pnl", t.get("r", 0)) or 0) > 0)
            tot_r = sum(rs)
            veto = DecisionJournal.veto_stats(24)
            try:
                cal = get_calibrated_scorer(sym)
                learned = int(getattr(cal, "n_learned", 0) or 0)
            except Exception:
                learned = 0
            lines = [f"📊 QUANTUM DIGEST — {sym}",
                     f"Trades: {n} ({wins}W) | R: {tot_r:+.2f}R | "
                     f"Decisions: {veto['trades']}T/{veto['holds']}H",
                     f"Learner samples: {learned}"]
            if veto["top_vetoes"]:
                lines.append("Top vetoes: " + ", ".join(f"{k}×{v}" for k, v in veto["top_vetoes"][:4]))
            return "\n".join(lines)
        except Exception as e:
            return f"(digest error: {e})"


class QuantumHealth:
    """Readiness probe: flags, tables, models, data freshness."""

    @staticmethod
    def check(symbol=None):
        sym = str(symbol or _qcfg("symbol", "XAUUSDm"))
        rep = {"symbol": sym, "ok": True, "checks": {}}
        try:
            g = globals()
            for sec in ("E1", "E2", "E3", "E4", "E5", "E6", "E7", "H", "F12", "F3", "G", "O", "I", "J"):
                rep["checks"][f"section_{sec}"] = bool(g.get(f"SECTION_{sec}_OK", False))
            rep["checks"]["quantum_enabled"] = bool(_qcfg("quantum_core_enabled", False))
            rep["checks"]["shadow"] = bool(_qcfg("quantum_shadow_mode", False))
            try:
                st = _qstore()
                rep["checks"]["store"] = st is not None
                if st is not None and getattr(st, "conn", None) is not None:
                    tabs = [r[0] for r in st.conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                    for t in ("raw_signals", "signals", "trades", "signal_outcomes",
                              "feature_store", "quantum_decisions"):
                        rep["checks"][f"table_{t}"] = t in tabs
            except Exception:
                rep["checks"]["store"] = False
            try:
                cal = get_calibrated_scorer(sym)
                rep["checks"]["cal_samples"] = int(getattr(cal, "n_learned", 0) or 0)
            except Exception:
                rep["checks"]["cal_samples"] = 0
            rep["ok"] = all(v for k, v in rep["checks"].items()
                            if not k.startswith("table_") and k != "cal_samples" and k != "shadow")
            return rep
        except Exception as e:
            rep["ok"] = False
            rep["error"] = str(e)
            return rep


SECTION_K_OK = True


# ============================================================================
# PHASE L — STRATEGY ADAPTERS (v12 strategies, quantum-groomed)
# ----------------------------------------------------------------------------
# Each adapter resolves its v12 strategy class LAZILY, runs it defensively,
# and grooms every emitted signal with regime-route + session + pine votes
# BEFORE the decider sees it. No v12 class is modified or subclassed.
# ============================================================================

class _AdapterBase:
    """Shared grooming: route/session/pine enrichment of raw v12 signals."""

    family = "trend"
    candidates = ()

    def resolve(self):
        for name in self.candidates:
            try:
                obj = globals().get(name)
                if obj is not None:
                    return obj() if isinstance(obj, type) else obj
            except Exception:
                continue
        return None

    @staticmethod
    def _call_strat(obj, dfs, *extra):
        """Try every known strategy entry-point signature. Returns signals list."""
        if obj is None:
            return []
        for meth in ("generate_signal", "generate_signals", "evaluate", "analyze",
                     "scan", "check_signal", "on_bar"):
            try:
                fn = getattr(obj, meth, None)
                if fn is None:
                    continue
                for args in ((dfs,), (dfs, extra[0]) if extra else (dfs,)):
                    try:
                        r = fn(*args)
                        return _AdapterBase._norm_signals(r)
                    except TypeError:
                        continue
                    except Exception:
                        break
            except Exception:
                continue
        return []

    @staticmethod
    def _norm_signals(r):
        if r is None:
            return []
        if isinstance(r, dict):
            # Single signal OR {tf: signal} map
            if "dir" in r or "direction" in r:
                return [r]
            out = []
            for v in r.values():
                if isinstance(v, dict) and ("dir" in v or "direction" in v):
                    out.append(v)
                elif isinstance(v, list):
                    out.extend([x for x in v if isinstance(x, dict)])
            return out
        if isinstance(r, (list, tuple)):
            return [x for x in r if isinstance(x, dict)]
        return []

    def groom(self, signals, ctx=None):
        ctx = ctx or {}
        reg = (ctx.get("regime") or {})
        rlab = str(reg.get("label", "RANGE")).upper()
        sess = str(ctx.get("session", "OFF")).upper()
        out = []
        try:
            eng = get_quantum_regime()
            si = get_session_intelligence()
            for s in signals or []:
                try:
                    g = dict(s)
                    if "dir" not in g and "direction" in g:
                        g["dir"] = g.pop("direction")
                    try:
                        g["dir"] = normalize_direction(g.get("dir"))
                    except Exception:
                        pass
                    g.setdefault("strategy", self.family)
                    g.setdefault("score", 6.0)
                    rm = eng.route_mult(rlab, self.family) if eng else 0.6
                    sm = si.multiplier(sess) if si else 1.0
                    g["quantum_route_mult"] = round(rm, 3)
                    g["quantum_sess_mult"] = round(sm, 3)
                    g["quantum_family"] = self.family
                    try:
                        base = float(g.get("score", 6.0))
                        g["score"] = base * (0.45 + 0.55 * rm) * sm
                    except Exception:
                        pass
                    out.append(g)
                except Exception:
                    continue
        except Exception:
            return list(signals or [])
        return out

    def run(self, dfs, ctx=None, **kw):
        try:
            obj = self.resolve()
            if obj is None:
                return []
            main_tf = str(_qcfg("timeframes", ["M15"])[0])
            df0 = (dfs or {}).get(main_tf)
            sigs = self._call_strat(obj, dfs, df0)
            if not sigs and df0 is not None:
                sigs = self._call_strat(obj, df0)
            return self.groom(sigs, ctx)
        except Exception:
            return []


class TrendAdapter(_AdapterBase):
    family = "trend"
    candidates = ("TrendFollowingStrategy", "TREND_STRAT", "TrendStrategy")


class BreakoutAdapter(_AdapterBase):
    family = "breakout"
    candidates = ("BreakoutStrategy", "BreakoutMomentumStrategy", "BREAKOUT_STRAT")


class PullbackAdapter(_AdapterBase):
    family = "pullback"
    candidates = ("PullbackRetracementStrategy", "PULLBACK_STRAT")


class MeanRevAdapter(_AdapterBase):
    family = "meanrev"
    candidates = ("MeanReversionStrategy", "MeanReversionStrategyV18", "ZScoreMeanReversion", "MEANREV_STRAT")


class ScalpAdapter(_AdapterBase):
    family = "scalp"
    candidates = ("ScalpingStrategy", "ScalpingEngine", "SCALP_STRAT")


class SmcAdapter(_AdapterBase):
    family = "smc"
    candidates = ("SMCLiquidityStrategy", "SmartMoneyDetector", "SMC_STRAT")


class NewsAdapter(_AdapterBase):
    family = "news"
    candidates = ("NewsImpactStrategy", "DynamicNewsStraddle", "NEWS_STRAT")


class DivergenceAdapter(_AdapterBase):
    family = "divergence"
    candidates = ("DivergenceStrategy", "RSIDivergenceDetector",
                  "StochasticRSIDivergenceDetector", "DIV_STRAT")


class AsianAdapter(_AdapterBase):
    family = "asian"
    candidates = ("AsianRangeEngine", "ASIAN_RANGE", "ASIAN_STRAT")


ADAPTER_REGISTRY = {"trend": TrendAdapter, "breakout": BreakoutAdapter,
                    "pullback": PullbackAdapter, "meanrev": MeanRevAdapter,
                    "scalp": ScalpAdapter, "smc": SmcAdapter, "news": NewsAdapter,
                    "divergence": DivergenceAdapter, "asian": AsianAdapter}


def adapt_all_strategies(dfs, ctx=None, families=None):
    """Run every resolvable v12 strategy; return pooled groomed signals."""
    pooled = []
    fams = families or list(ADAPTER_REGISTRY.keys())
    for fam in fams:
        try:
            cls = ADAPTER_REGISTRY.get(fam)
            if cls is None:
                continue
            pooled.extend(cls().run(dfs, ctx))
        except Exception:
            continue
    # Dedupe identical (strategy, dir, tf) keeping max score
    try:
        best = {}
        for s in pooled:
            k = (str(s.get("strategy", "")), str(s.get("dir", "")), str(s.get("tf", "")))
            if k not in best or float(s.get("score", 0) or 0) > float(best[k].get("score", 0) or 0):
                best[k] = s
        pooled = list(best.values())
    except Exception:
        pass
    return pooled


SECTION_L_OK = True


# ============================================================================
# PHASE M — DIAGNOSTICS (self-test + status + one-shot calibration)
# ============================================================================

def quantum_selftest(symbol="XAUUSDm", bars=500):
    """Exercise every quantum module on synthetic data. Returns report dict."""
    rep = {"symbol": symbol, "modules": {}, "ok": True}
    try:
        import math as _m
        import random as _r
        rng = _r.Random(11)

        class _DF(dict):
            def __len__(self):
                return len(self["close"])

        def _mk(n, drift, vol):
            o, h, l, c, v = [], [], [], [], []
            px = 2650.0
            for _ in range(n):
                nc = px * _m.exp(drift + rng.gauss(0, vol))
                oo = px * (1 + rng.gauss(0, 0.0008))
                s = abs(rng.gauss(0, 0.002))
                o.append(oo)
                h.append(max(oo, nc) * (1 + s))
                l.append(min(oo, nc) * (1 - s))
                c.append(nc)
                v.append(abs(rng.gauss(800, 150)))
                px = nc
            return _DF(open=o, high=h, low=l, close=c, tick_volume=v)

        dfs = {"M5": _mk(bars, 0.0002, 0.004), "M15": _mk(bars, 0.0004, 0.006),
               "H1": _mk(bars, 0.0008, 0.009), "H4": _mk(max(200, bars // 2), 0.0012, 0.012)}

        def _t(name, fn):
            try:
                r = fn()
                rep["modules"][name] = {"ok": True, "note": str(r)[:120]}
            except Exception as e:
                rep["modules"][name] = {"ok": False, "note": f"{type(e).__name__}: {e}"[:160]}
                rep["ok"] = False

        _t("regime", lambda: get_quantum_regime(symbol).update(dfs)["label"])
        _t("early", lambda: get_early_gate(symbol).check(dfs, {"spread": 0.25})["pass"])
        _t("session", lambda: get_session_intelligence(symbol).table()[0]["session"])
        _t("calibration", lambda: round(get_calibrated_scorer(symbol).predict(
            {"dir": "BUY", "score": 8, "tf": "H1"}, {})["p_win"], 3))
        _t("decider", lambda: quantum_junction(
            [{"dir": "BUY", "score": 8, "tf": "H1", "strategy": "trend",
              "entry": 2650, "sl": 2640, "tp": 2670}], dfs=dfs,
            tick={"spread": 0.25})["action"])
        _t("narrator", lambda: get_quantum_narrator(symbol).morning_briefing(
            {"label": "RANGE"})[:40])
        _t("risk_overlay", lambda: get_risk_overlay(symbol).govern(
            0.5, "BUY", closes=dfs["H1"]["close"][-200:], open_trades=[],
            equity=10000, equity_curve=[10000] * 50)["lot"])
        _t("radar", lambda: round(pine_confluence(dfs["H1"])["conf"], 3))
        _t("indicators", lambda: round(quantum_indicators(dfs["H1"])["rsi"], 1))
        _t("walkforward", lambda: quantum_walkforward(symbol)[0]["verdict"][:30])
        _t("portfolio", lambda: get_portfolio_brain().review(
            symbol, "TRADE", 1.0, "BUY", equity=10000,
            book={"positions": [], "n": 0, "symbols": {}})["allow"])
        _t("adapters", lambda: len(adapt_all_strategies(dfs, {"regime": {"label": "RANGE"}})))
        _t("health", lambda: QuantumHealth.check(symbol)["ok"])
        return rep
    except Exception as e:
        rep["ok"] = False
        rep["fatal"] = str(e)
        return rep


def quantum_selftest_text(symbol="XAUUSDm"):
    rep = quantum_selftest(symbol)
    try:
        lines = [f"🧪 QUANTUM SELF-TEST — {symbol}: {'PASS' if rep['ok'] else 'FAIL'}"]
        for name, r in rep["modules"].items():
            lines.append(f"  {'✅' if r['ok'] else '❌'} {name}: {r['note']}")
        return "\n".join(lines)
    except Exception as e:
        return f"(selftest text error: {e})"


def quantum_status(symbol=None):
    """One-dict readiness snapshot for CLI/TG/status command."""
    sym = str(symbol or _qcfg("symbol", "XAUUSDm"))
    try:
        h = QuantumHealth.check(sym)
        out = {"symbol": sym, "ok": h["ok"], "enabled": _qcfg("quantum_core_enabled", False),
               "shadow": _qcfg("quantum_shadow_mode", False), "checks": h["checks"]}
        try:
            si = get_session_intelligence(sym)
            out["sessions"] = si.table() if si else []
        except Exception:
            out["sessions"] = []
        try:
            eng = get_quantum_regime(sym)
            out["regime"] = eng.summary() if eng else {}
        except Exception:
            out["regime"] = {}
        out["vetoes_24h"] = DecisionJournal.veto_stats(24)
        return out
    except Exception as e:
        return {"symbol": sym, "ok": False, "error": str(e)}


def quantum_calibrate_now(symbol=None, limit=4000):
    """One-shot: fit calibrator + sync sessions + report. For CLI/TG."""
    sym = str(symbol or _qcfg("symbol", "XAUUSDm"))
    out = {"symbol": sym}
    try:
        cal = get_calibrated_scorer(sym)
        out["fit"] = cal.fit_from_store(limit=limit) if cal else {"fitted": False}
        try:
            si = get_session_intelligence(sym)
            out["session_rows"] = si.sync_from_store(force=True) if si else 0
        except Exception as e:
            out["session_rows"] = f"err: {e}"
        return out
    except Exception as e:
        out["error"] = str(e)
        return out


SECTION_M_OK = True
