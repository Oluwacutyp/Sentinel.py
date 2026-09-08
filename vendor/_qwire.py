
# ============================================================================
# WIRE — QUANTUM CYCLE CONTROLLER + LIVE/BACKTEST JUNCTIONS + MT5 BRIDGE
# ----------------------------------------------------------------------------
# W1 PineVocabBridge   pine 278-feature names -> quantum extractor outputs
# W2 MT5Bridge         candles/ticks in, orders out (paper + live)
# W3 QuantumCycle      the orchestrated trade loop (fetch->ticket->fill->learn)
# W4 LiveJunction      runtime hook wrapping the v12 cycle (no v12 edits needed)
# W5 ParityLab         determinism + cross-TF consistency checks
# W6 quantum_main      argv router (patched into the v12 main guard)
# ============================================================================

# ----------------------------------------------------------------------------
# W1 — Pine vocabulary bridge (E5 Path-0 speaks pine feature names)
# ----------------------------------------------------------------------------

def quantum_pine_features(df, prefix="px"):
    """Compute the pine-vocab feature row for a candle window.

    Returns {pine_name: value} for the ~40 core names E5 Path-0 joins on.
    Names mirror the OMNI-GOD-UNIFIED vocabulary so mined pine patterns and
    live quantum features share one language.
    """
    out = {}
    try:
        o = qas_series(df, "open")
        h = qas_series(df, "high")
        l = qas_series(df, "low")
        c = qas_series(df, "close")
        if len(c) < 60:
            return out
        n = len(c)
        px = c[-1]
        # Price position family
        hi50, lo50 = max(h[-50:]), min(l[-50:])
        out["pos_in_range"] = (px - lo50) / (hi50 - lo50 + 1e-12)
        out["dist_high_atr"] = (hi50 - px)
        out["dist_low_atr"] = (px - lo50)
        # ATR family
        atrs = q_atr_from_lists(h, l, c, 14)
        a = atrs[-1] if atrs else 1e-9
        out["atr"] = a
        out["atr_pct"] = a / (px + 1e-12)
        out["dist_high_atr"] = out["dist_high_atr"] / (a + 1e-12)
        out["dist_low_atr"] = out["dist_low_atr"] / (a + 1e-12)
        # Efficiency / trend family
        out["efficiency_20"] = q_efficiency(c, 20)
        out["efficiency_50"] = q_efficiency(c, 50)
        dmi = q_adx_dmi(h, l, c, 14)
        out["adx"] = dmi.get("adx", 0)
        out["plus_di"] = dmi.get("plus_di", 0)
        out["minus_di"] = dmi.get("minus_di", 0)
        # Momentum family
        try:
            ind = quantum_indicators(df)
            out["rsi_a"] = ind.get("rsi", 50) / 100
            out["rsi_z"] = (ind.get("rsi", 50) - 50) / 25
            out["macd_hist_a"] = ind.get("macd_hist", 0)
            out["squeeze"] = 1.0 if ind.get("sqz") else 0.0
            out["divs"] = float(ind.get("divs", 0) or 0)
            out["indic_bias"] = float(ind.get("bias", 0) or 0)
        except Exception:
            pass
        # Volatility family
        rets = [c[i] - c[i - 1] for i in range(-50, 0)]
        import math as _m
        mu = sum(rets) / len(rets)
        sd = (_m.fsum((x - mu) ** 2 for x in rets) / len(rets)) ** 0.5 + 1e-12
        out["ret_1"] = rets[-1] / (a + 1e-12)
        out["ret_5"] = sum(rets[-5:]) / (a + 1e-12)
        out["ret_20"] = sum(rets[-20:]) / (a + 1e-12)
        out["vol_20"] = sd / (a + 1e-12)
        # Structure family
        out["higher_high"] = 1.0 if h[-1] > max(h[-12:-1]) else 0.0
        out["lower_low"] = 1.0 if l[-1] < min(l[-12:-1]) else 0.0
        out["body_atr"] = abs(c[-1] - o[-1]) / (a + 1e-12)
        out["wick_up_atr"] = (h[-1] - max(c[-1], o[-1])) / (a + 1e-12)
        out["wick_dn_atr"] = (min(c[-1], o[-1]) - l[-1]) / (a + 1e-12)
        out["close_pos_bar"] = (c[-1] - l[-1]) / (h[-1] - l[-1] + 1e-12)
        # Volume family
        try:
            v = VwapPack._vols(df)
            out["vol_ratio_20"] = (sum(v[-3:]) / 3) / (sum(v[-23:-3]) / 20 + 1e-12) if len(v) > 25 else 1.0
            out["vol_trend"] = (sum(v[-5:]) - sum(v[-10:-5])) / (sum(v[-10:]) + 1e-12) if len(v) > 10 else 0.0
        except Exception:
            out["vol_ratio_20"] = 1.0
            out["vol_trend"] = 0.0
        # F-system summaries
        try:
            f5 = f5_confluence(df)
            out["f5_bias"] = f5.get("bias", 0)
            out["f5_conf"] = f5.get("conf", 0)
            out["f5_n"] = f5.get("n", 0) / 20
        except Exception:
            pass
        try:
            reg = quantum_regime(df)
            out["regime_conf"] = reg.get("conf", 0.5) if isinstance(reg, dict) else 0.5
        except Exception:
            pass
        # Clean NaNs
        for k, v in list(out.items()):
            try:
                fv = float(v)
                if fv != fv or fv in (float("inf"), float("-inf")):
                    out[k] = 0.0
                else:
                    out[k] = round(fv, 6)
            except Exception:
                out[k] = 0.0
        return out
    except Exception:
        return out


def quantum_pine_row_for_e5(df):
    """E5 Path-0 join row: pine features + provenance tag."""
    try:
        row = quantum_pine_features(df)
        row["_source"] = "pine_bridge"
        return row
    except Exception:
        return {"_source": "pine_bridge"}


# ----------------------------------------------------------------------------
# W2 — MT5 bridge (data in, orders out; paper mode for the lab)
# ----------------------------------------------------------------------------

class MT5Bridge:
    """Thin MT5 adapter speaking quantum dicts. paper=True simulates fills."""

    TF_MAP = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 16385,
              "H4": 16388, "D1": 16408}

    def __init__(self, paper=True, mt5_module=None):
        self.paper = paper
        self.mt5 = mt5_module
        self.paper_px = {}
        self.paper_pos = []
        if not paper and self.mt5 is None:
            try:
                import MetaTrader5 as _m
                self.mt5 = _m
            except Exception:
                self.mt5 = None

    def candles(self, symbol, tf="M15", n=500):
        """Returns quantum df dict {open,high,low,close,tickvol,time} or {}."""
        try:
            if self.paper or self.mt5 is None:
                return {}
            m = self.mt5
            timeframe = self.TF_MAP.get(str(tf).upper(), 15)
            rates = m.copy_rates_from_pos(symbol, timeframe, 0, n)
            if rates is None or len(rates) == 0:
                return {}
            return {"open": [float(x[1]) for x in rates],
                    "high": [float(x[2]) for x in rates],
                    "low": [float(x[3]) for x in rates],
                    "close": [float(x[4]) for x in rates],
                    "tickvol": [float(x[5]) for x in rates],
                    "time": [int(x[0]) for x in rates]}
        except Exception:
            return {}

    def tick(self, symbol):
        try:
            if self.paper or self.mt5 is None:
                px = self.paper_px.get(symbol, 0)
                return {"bid": px, "ask": px, "spread": 0}
            t = self.mt5.symbol_info_tick(symbol)
            if t is None:
                return {}
            return {"bid": float(t.bid), "ask": float(t.ask),
                    "spread": float(t.ask - t.bid)}
        except Exception:
            return {}

    def broker_fn(self, symbol, deviation=20, magic=130013):
        """Build the broker_fn(action)->fill adapter for quantum_execute."""
        bridge = self

        def _fn(action):
            try:
                side = action.get("side", 1)
                lots = action.get("lots", 0.1)
                if bridge.paper or bridge.mt5 is None:
                    px = bridge.paper_px.get(symbol, 0)
                    return {"ok": True, "lots": lots, "price": px,
                            "slip_spreads": 0.1, "slip_r": -0.005,
                            "paper": True}
                m = bridge.mt5
                t = m.symbol_info_tick(symbol)
                if t is None:
                    return {"ok": False, "fatal": False, "error": "no_tick"}
                px = t.ask if side > 0 else t.bid
                req = {"action": m.TRADE_ACTION_DEAL, "symbol": symbol,
                       "volume": float(lots),
                       "type": m.ORDER_TYPE_BUY if side > 0 else m.ORDER_TYPE_SELL,
                       "price": px, "deviation": deviation, "magic": magic,
                       "comment": f"Q/{action.get('strategy', '?')}",
                       "type_time": m.ORDER_TIME_GTC,
                       "type_filling": m.ORDER_FILLING_IOC}
                res = m.order_send(req)
                if res is None:
                    return {"ok": False, "fatal": False, "error": "no_result"}
                if res.retcode != m.TRADE_RETCODE_DONE:
                    return {"ok": False, "fatal": res.retcode in (
                        getattr(m, "TRADE_RETCODE_NO_MONEY", -1),
                        getattr(m, "TRADE_RETCODE_TRADE_DISABLED", -2)),
                            "error": f"retcode={res.retcode}"}
                slip = (res.price - px) * side
                return {"ok": True, "lots": lots, "price": float(res.price),
                        "ticket": getattr(res, "order", 0),
                        "slip_spreads": abs(slip) / ((t.ask - t.bid) + 1e-12),
                        "slip_r": 0.0}
            except Exception as e:
                return {"ok": False, "fatal": False, "error": str(e)}
        return _fn


# ----------------------------------------------------------------------------
# W3 — QuantumCycle: fetch -> ticket -> fill -> learn
# ----------------------------------------------------------------------------

class QuantumCycle:
    """One orchestrated pass over every watched symbol."""

    def __init__(self, symbols=("XAUUSD",), exec_tf="M15",
                 htfs=("H1", "H4"), paper=True, mode=None):
        import os as _os
        self.symbols = list(symbols)
        self.exec_tf = exec_tf
        self.htfs = list(htfs)
        self.mode = (mode or _os.environ.get("QUANTUM_MODE", "live")).lower()
        self.bridge = MT5Bridge(paper=(paper or self.mode != "live"))
        self.cycle_no = 0
        self.tickets = []

    def run_once(self, data=None):
        """data: {symbol: {TF: df}} override (lab/backtest injection)."""
        self.cycle_no += 1
        out = {"cycle": self.cycle_no, "mode": self.mode, "results": []}
        for sym in self.symbols:
            try:
                if data and sym in data:
                    tf_dfs = data[sym]
                else:
                    tf_dfs = {tf: self.bridge.candles(sym, tf) for tf in [self.exec_tf] + self.htfs}
                    tf_dfs = {k: v for k, v in tf_dfs.items() if v}
                if not tf_dfs:
                    out["results"].append({"symbol": sym, "skip": "no_data"})
                    continue
                exec_df = tf_dfs.get(self.exec_tf) or next(iter(tf_dfs.values()))
                tick = self.bridge.tick(sym)
                ctx = {"spread": tick.get("spread", 0),
                       "broker_mid": (tick.get("bid", 0) + tick.get("ask", 0)) / 2 or None}
                try:
                    import datetime as _dt
                    hr = _dt.datetime.utcnow().hour
                    sess = ("ASIA" if hr < 7 else "LONDON" if hr < 12 else
                            "OVERLAP" if hr < 16 else "NEWYORK" if hr < 21 else "OFF")
                except Exception:
                    sess = "OVERLAP"
                bar_no = len(exec_df.get("close", []))
                ticket = quantum_signal(tf_dfs, ctx, exec_tf=self.exec_tf,
                                        symbol=sym, session=sess, bar_no=bar_no)
                rec = {"symbol": sym, "session": sess,
                       "ticket": ticket.as_dict() if isinstance(ticket, EntryTicket) else ticket}
                if isinstance(ticket, EntryTicket) and ticket.valid() and self.mode == "live":
                    try:
                        atrs = q_atr_from_lists(exec_df["high"], exec_df["low"],
                                               exec_df["close"], 14)
                        a = atrs[-1] if atrs else 1e-9
                        lots = 0.1  # base; risk overlay sizes in production
                        plan = quantum_execute(ticket, {"lots": lots}, self.bridge.broker_fn(sym),
                                               symbol=sym)
                        rec["execution"] = {"lots": plan.get("lots"),
                                            "filled": plan.get("filled_lots"),
                                            "dry_run": plan.get("dry_run")}
                    except Exception as e:
                        rec["execution"] = {"error": str(e)}
                else:
                    rec["execution"] = {"skipped": self.mode if not (
                        isinstance(ticket, EntryTicket) and ticket.valid()) else "vetoed"}
                # Journal + narrative
                try:
                    quantum_journal_add(rec) if "quantum_journal_add" in dir() else None
                except Exception:
                    pass
                try:
                    rec["narrative"] = ticket.narrative() if isinstance(ticket, EntryTicket) else ""
                except Exception:
                    pass
                out["results"].append(rec)
                self.tickets.append(rec)
            except Exception as e:
                out["results"].append({"symbol": sym, "error": str(e)})
        # Periodic snapshot
        try:
            if self.cycle_no % 25 == 0:
                out["snapshot"] = quantum_snapshot()
        except Exception:
            pass
        return out

    def run_loop(self, seconds=60, max_cycles=None):
        import time as _t
        n = 0
        while True:
            r = self.run_once()
            n += 1
            yield r
            if max_cycles is not None and n >= max_cycles:
                break
            _t.sleep(seconds)


# ----------------------------------------------------------------------------
# W4 — Live junction: wrap the v12 cycle at runtime (zero v12 edits)
# ----------------------------------------------------------------------------

_LIVE_HOOK = {"wrapped": [], "calls": 0, "vetoes": 0}


def quantum_consult(symbol="XAUUSD", df=None, session="OVERLAP", regime_hint=None):
    """One-call consult: v12 (or anyone) asks the brain for direction/size.

    Returns {side, conf, lot_mult, veto, reason}. Never raises.
    """
    try:
        if df is None or len(qas_series(df, "close")) < 60:
            return {"side": 0, "conf": 0, "lot_mult": 0, "veto": "no_data"}
        ticket = quantum_signal({"M15": df}, {}, exec_tf="M15",
                                symbol=symbol, session=session, bar_no=0,
                                regime_hint=regime_hint)
        if not isinstance(ticket, EntryTicket):
            return {"side": 0, "conf": 0, "lot_mult": 0, "veto": "no_ticket"}
        d = ticket.as_dict()
        if d.get("veto"):
            _LIVE_HOOK["vetoes"] += 1
            return {"side": 0, "conf": 0, "lot_mult": 0, "veto": d["veto"]}
        _LIVE_HOOK["calls"] += 1
        return {"side": d["side"], "conf": d["conf"], "lot_mult": d["lot_mult"],
                "veto": None, "strategy": d["strategy"], "regime": d["regime"],
                "sl_atr": d["sl_atr"], "tp_atr": d["tp_atr"]}
    except Exception as e:
        return {"side": 0, "conf": 0, "lot_mult": 0, "veto": f"error:{e}"}


def install_live_hook(namespace=None, cycle_names=("run_cycle", "_cycle", "main_cycle",
                                                  "trading_cycle", "cycle")):
    """Wrap a v12 cycle function so every pass consults the quantum brain.

    The wrapper calls the original first (legacy behavior preserved), then
    attaches the quantum consult to its result under '_quantum'. If the
    consult vetoes, the wrapper annotates (it never blocks legacy fills —
    promotion to enforcement happens via QUANTUM_ENFORCE=1 after paper proof).
    """
    import os as _os
    ns = namespace if namespace is not None else globals()
    try:
        if not isinstance(ns, dict):
            ns = vars(ns)
    except Exception:
        return {"status": "no_namespace"}
    out = {"wrapped": [], "enforce": _os.environ.get("QUANTUM_ENFORCE", "0") == "1"}
    for name in cycle_names:
        fn = ns.get(name)
        if not callable(fn) or getattr(fn, "_qwrapped", False):
            continue
        try:
            import functools as _ft

            @_ft.wraps(fn)
            def _wrapper(*a, _orig=fn, **k):
                try:
                    res = _orig(*a, **k)
                except Exception:
                    raise
                try:
                    con = quantum_consult()
                    if isinstance(res, dict):
                        res["_quantum"] = con
                        if out["enforce"] and con.get("veto") and res.get("action") in (
                                "BUY", "SELL", "buy", "sell", 1, -1, "open"):
                            res["_quantum_blocked"] = con["veto"]
                    elif res is None:
                        res = {"_quantum": con}
                except Exception:
                    pass
                return res

            _wrapper._qwrapped = True
            ns[name] = _wrapper
            out["wrapped"].append(name)
            _LIVE_HOOK["wrapped"].append(name)
        except Exception:
            continue
    out["status"] = "ok" if out["wrapped"] else "no_cycle_found"
    return out


def live_hook_stats():
    return dict(_LIVE_HOOK)


# ----------------------------------------------------------------------------
# W5 — Parity lab: determinism + cross-TF consistency
# ----------------------------------------------------------------------------

def quantum_parity(csv_paths, symbol="XAUUSD"):
    """Run the same CSV twice (determinism) + adjacent TFs (consistency).

    csv_paths: {label: path}. Returns {deterministic, tf_agreement, detail}.
    """
    out = {"deterministic": None, "tf_agreement": None, "detail": {}}
    try:
        import csv as _csv
        def _load(p):
            rows = []
            with open(p, newline="") as f:
                for r in _csv.DictReader(f):
                    try:
                        rows.append({"time": r.get("time", r.get("date", "")),
                                     "open": float(r["open"]), "high": float(r["high"]),
                                     "low": float(r["low"]), "close": float(r["close"]),
                                     "tickvol": float(r.get("tickvol", r.get("volume", 0)) or 0)})
                    except Exception:
                        continue
            return rows
        sigs = {}
        for label, p in (csv_paths or {}).items():
            rows = _load(p)
            if len(rows) < 150:
                out["detail"][label] = "too_short"
                continue
            df = {k: [w[k] for w in rows[-400:]] for k in
                  ("open", "high", "low", "close", "tickvol")}
            t1 = quantum_signal({"M15": df}, {}, symbol=symbol, bar_no=1)
            t2 = quantum_signal({"M15": df}, {}, symbol=symbol, bar_no=9999)
            d1 = t1.as_dict() if isinstance(t1, EntryTicket) else {}
            d2 = t2.as_dict() if isinstance(t2, EntryTicket) else {}
            same = (d1.get("side"), d1.get("strategy")) == (d2.get("side"), d2.get("strategy"))
            sigs[label] = d1.get("side", 0)
            out["detail"][label] = {"side": d1.get("side"), "veto": d1.get("veto"),
                                    "strategy": d1.get("strategy"),
                                    "deterministic": bool(same)}
        det = [v["deterministic"] for v in out["detail"].values() if isinstance(v, dict)]
        out["deterministic"] = all(det) if det else None
        sides = [s for s in sigs.values() if s != 0]
        out["tf_agreement"] = (len(set(sides)) <= 1) if sides else None
        out["sides"] = sigs
        return out
    except Exception as e:
        out["error"] = str(e)
        return out


# ----------------------------------------------------------------------------
# W6 — quantum_main argv router (called from the patched v12 main guard)
# ----------------------------------------------------------------------------

QUANTUM_ARGV = ("status", "selftest", "calibrate", "backtest", "report",
                "leaderboard", "importance", "autopsy", "spec", "version",
                "help", "consult", "cycle", "parity", "snapshot", "meta")


def quantum_main(argv=None):
    """Router: quantum subcommands + CLI. Returns exit code or None.

    Returns None when argv is NOT a quantum command (caller proceeds to v12).
    """
    import sys as _sys
    args = list(argv) if argv is not None else _sys.argv[1:]
    if not args or str(args[0]).lower() not in QUANTUM_ARGV:
        return None
    cmd = str(args[0]).lower()
    try:
        if cmd in ("status", "selftest", "calibrate", "backtest", "report",
                   "leaderboard", "importance", "autopsy", "spec", "version", "help"):
            return quantum_cli(args)
        if cmd == "snapshot":
            print(quantum_snapshot())
            return 0
        if cmd == "meta":
            print(quantum_meta_verdict())
            return 0
        if cmd == "parity":
            import glob as _g
            paths = {f"TF{i}": p for i, p in enumerate(args[1:] or
                                                       sorted(_g.glob("*.csv"))[:3])}
            print(paths if paths else "no CSVs found")
            if paths:
                print(quantum_parity(paths))
            return 0
        if cmd == "cycle":
            import os as _os
            syms = args[1:] or ["XAUUSD"]
            cyc = QuantumCycle(symbols=syms, paper=_os.environ.get("QUANTUM_MODE", "live") != "live")
            print(f"quantum cycle x1 over {syms} (mode={cyc.mode})")
            print(cyc.run_once())
            return 0
        if cmd == "consult":
            print("usage: consult needs live data context; see quantum_consult()")
            return 2
        return 2
    except Exception as e:
        print(f"quantum_main error: {e}")
        return 1


SECTION_WIRE_OK = True
