
# ============================================================================
# ZENITH — THE OPERATOR'S FINISH (tournament, A/B lab, EOD, alarms, rollback)
# ----------------------------------------------------------------------------
# ZNa Tournament    round-robin paper arena: all 25 systems, same bars, ranked
# ZNb ABHarness     A/B test any parameter change with significance discipline
# ZNc DecayAlarms   performance-decay watchtower (fires before the DD does)
# ZNd EODWriter     end-of-day report: cards, heat, journal, tomorrow's plan
# ZNe TeleFormatter Telegram/email-ready digest builders (ASCII-safe)
# ZNf Rollback      one-call demote: champion -> last-known-good config
# ============================================================================

class Tournament:
    """Paper arena: every L2 system trades the SAME bars; ranked by R.

    The fairest fight in the book — no cherry-picked regimes, no excuses.
    Losers get parked with evidence; winners earn weight. Run weekly.
    """

    def __init__(self, starting_equity_r=0.0):
        self.eq0 = starting_equity_r
        self.results = {}

    def run(self, rows, symbol="XAUUSD", session="OVERLAP", r_per_trade=1.0):
        """rows: [{open,high,low,close,tickvol,time}]. Simple next-open fills,
        2.0a SL / 2.5a TP structure exits. Returns ranked table."""
        try:
            self.results = {}
            try:
                suite = L2Suite()
            except Exception:
                return {"status": "no_suite"}
            closes = [r["close"] for r in rows]
            n = len(rows)
            start = min(n - 50, 400)
            for s in suite.strats:
                eq, wins, trades = 0.0, 0, 0
                i = start
                while i < n - 1:
                    win = rows[max(0, i - 400):i]
                    if len(win) < 120:
                        i += 1
                        continue
                    df = {k: [w[k] for w in win] for k in ("open", "high", "low", "close")}
                    try:
                        reg = quantum_regime(df)
                        regime = reg.get("regime", "RANGE") if isinstance(reg, dict) else "RANGE"
                    except Exception:
                        regime = "RANGE"
                    if not s.suitable(regime):
                        i += 1
                        continue
                    ctx = {"df": df, "regime": regime, "session": session,
                           "symbol": symbol, "spread": 0,
                           "now_ts": rows[i].get("time", 0) or 0}
                    try:
                        sig = s.analyze(ctx)
                    except Exception:
                        i += 1
                        continue
                    if sig.get("side") not in (1, -1) or sig.get("conf", 0) < 0.5:
                        i += 1
                        continue
                    # Fill next open, exit on SL/TP over next 60 bars
                    try:
                        atrs = q_atr_from_lists(df["high"], df["low"], df["close"], 14)
                        a = atrs[-1] if atrs else 1e-9
                    except Exception:
                        a = 1e-9
                    entry = rows[i]["open"]
                    side = sig["side"]
                    sl = entry - side * sig.get("sl_atr", 2.0) * a
                    tp = entry + side * sig.get("tp_atr", 2.5) * a
                    risk = abs(entry - sl) or 1e-9
                    ex = None
                    for j in range(i, min(n, i + 60)):
                        b = rows[j]
                        if side > 0:
                            if b["low"] <= sl:
                                ex = sl
                                break
                            if b["high"] >= tp:
                                ex = tp
                                break
                        else:
                            if b["high"] >= sl:
                                ex = sl
                                break
                            if b["low"] <= tp:
                                ex = tp
                                break
                    if ex is None:
                        ex = rows[min(n - 1, i + 60)]["close"]
                    r = (ex - entry) * side / risk
                    eq += r
                    trades += 1
                    if r > 0:
                        wins += 1
                    i += 5  # spacing between arena bouts
                self.results[s.name] = {"trades": trades, "net_r": round(eq, 2),
                                        "win_rate": round(wins / trades, 3) if trades else 0,
                                        "ev": round(eq / trades, 4) if trades else 0}
            ranked = sorted(self.results.items(), key=lambda t: (-t[1]["net_r"]))
            return {"status": "ok", "symbol": symbol, "bars": n,
                    "ranked": [(k, v) for k, v in ranked]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def text(self, result=None):
        try:
            res = result or {"ranked": sorted(self.results.items(),
                                             key=lambda t: -t[1]["net_r"])}
            L = ["TOURNAMENT — paper arena, same bars for all 25"]
            for i, (k, v) in enumerate(res.get("ranked", []), 1):
                medal = {1: "[G]", 2: "[S]", 3: "[B]"}.get(i, f"{i:3d}")
                L.append(f"  {medal} {k:18s} n={v['trades']:3d} net={v['net_r']:+7.1f}R "
                         f"ev={v['ev']:+.3f} win={v['win_rate']:.0%}")
            return "\n".join(L)
        except Exception as e:
            return f"tournament text error: {e}"


def quantum_tournament(csv_path, symbol="XAUUSD"):
    try:
        import csv as _csv
        rows = []
        with open(csv_path, newline="") as f:
            for r in _csv.DictReader(f):
                try:
                    rows.append({"time": r.get("time", r.get("date", 0)) or 0,
                                 "open": float(r["open"]), "high": float(r["high"]),
                                 "low": float(r["low"]), "close": float(r["close"]),
                                 "tickvol": float(r.get("tickvol", r.get("volume", 0)) or 0)})
                except Exception:
                    continue
        if len(rows) < 500:
            return {"status": "need_500_bars", "n": len(rows)}
        t = Tournament()
        res = t.run(rows, symbol)
        res["text"] = t.text(res)
        return res
    except Exception as e:
        return {"status": "error", "error": str(e)}


class ABHarness:
    """A/B discipline for parameter changes: same bars, both configs, verdict.

    score_fn(config_id)-> [R...] runs each variant; Welch's t + bootstrap
    decide. Ship B only if better with p < 0.05 AND bootstrap edge holds.
    No more 'feels better' deploys.
    """

    def run(self, rs_a, rs_b, name_a="A", name_b="B"):
        try:
            import math as _m
            a = [float(x) for x in rs_a]
            b = [float(x) for x in rs_b]
            if len(a) < 10 or len(b) < 10:
                return {"status": "need_10_each"}
            ma, mb = sum(a) / len(a), sum(b) / len(b)
            va = sum((x - ma) ** 2 for x in a) / len(a) or 1e-12
            vb = sum((x - mb) ** 2 for x in b) / len(b) or 1e-12
            t = (mb - ma) / ((va / len(a) + vb / len(b)) ** 0.5 or 1e-12)
            # Welch df (approx) then normal-approx p (one-sided)
            ship = t > 1.65 and mb > 0
            # Bootstrap: P(mean_b > mean_a)
            import random as _r
            rng = _r.Random(3)
            wins = 0
            for _ in range(500):
                sa = sum(a[rng.randrange(len(a))] for _ in range(len(a))) / len(a)
                sb = sum(b[rng.randrange(len(b))] for _ in range(len(b))) / len(b)
                if sb > sa:
                    wins += 1
            pboot = wins / 500
            verdict = "SHIP_B" if (ship and pboot > 0.95) else (
                "KEEP_A" if t < 1.65 else "INCONCLUSIVE")
            return {"status": "ok", name_a: {"n": len(a), "ev": round(ma, 4)},
                    name_b: {"n": len(b), "ev": round(mb, 4)},
                    "welch_t": round(t, 2), "p_boot_b_better": round(pboot, 3),
                    "verdict": verdict}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def quantum_ab(rs_a, rs_b, name_a="A", name_b="B"):
    try:
        return ABHarness().run(rs_a, rs_b, name_a, name_b)
    except Exception as e:
        return {"status": "error", "error": str(e)}


class DecayAlarms:
    """Watchtower: fires BEFORE the drawdown does.

    Alarms: expectancy slope negative (20-trade), win-rate collapse, regime
    concentration (all R from one regime), calibration drift, fill decay.
    Each alarm carries severity + the playbook action.
    """

    def __init__(self):
        self.rs = []       # (r, strategy, regime)
        self.fills = []    # slip_r

    def add_trade(self, r, strategy="?", regime="?"):
        try:
            self.rs.append((float(r), str(strategy), str(regime)))
            del self.rs[:-200]
        except Exception:
            pass

    def add_fill(self, slip_r):
        try:
            self.fills.append(float(slip_r))
            del self.fills[:-200]
        except Exception:
            pass

    def scan(self):
        alarms = []
        try:
            rs = [x[0] for x in self.rs]
            if len(rs) >= 40:
                first = sum(rs[-40:-20]) / 20
                last = sum(rs[-20:]) / 20
                if last < first - 0.15 and last < 0:
                    alarms.append({"alarm": "EV_SLOPE_DOWN", "sev": "HIGH",
                                   "detail": f"{first:+.3f}->{last:+.3f}",
                                   "action": "halve_size_run_autopsy"})
                wr = sum(1 for x in rs[-20:] if x > 0) / 20
                if wr < 0.25:
                    alarms.append({"alarm": "WINRATE_COLLAPSE", "sev": "HIGH",
                                   "detail": f"win={wr:.0%}_last20",
                                   "action": "paper_until_two_green_windows"})
                # Concentration: top regime share of gross profit
                by_r = {}
                for x, s, g in self.rs[-60:]:
                    by_r[g] = by_r.get(g, 0) + max(0, x)
                tot = sum(by_r.values()) or 1e-12
                top = max(by_r.values()) / tot if by_r else 0
                if top > 0.8:
                    alarms.append({"alarm": "REGIME_CONCENTRATION", "sev": "MED",
                                   "detail": f"top_regime={top:.0%}_of_profit",
                                   "action": "confirm_other_regimes_or_accept"})
            if len(self.fills) >= 30:
                avg = sum(self.fills[-30:]) / 30
                if avg < -0.08:
                    alarms.append({"alarm": "FILL_DECAY", "sev": "MED",
                                   "detail": f"slip={avg:.3f}R",
                                   "action": "check_broker_session_mix"})
            try:
                o = _DRIFT.get("obj")
                if o is not None and o.state == "DRIFT_DOWN":
                    alarms.append({"alarm": "DRIFT_DOWN", "sev": "HIGH",
                                   "detail": "ADWIN-lite fired",
                                   "action": "halve_size_recalibrate"})
            except Exception:
                pass
            return {"status": "ok", "alarms": alarms,
                    "worst": max([a["sev"] for a in alarms], default="NONE")}
        except Exception as e:
            return {"status": "error", "error": str(e), "alarms": alarms}


_DECAY = {"obj": None}


def quantum_decay(trade=None, slip_r=None):
    try:
        o = _DECAY.get("obj")
        if o is None:
            o = DecayAlarms()
            _DECAY["obj"] = o
        if trade is not None:
            o.add_trade(*trade)
        if slip_r is not None:
            o.add_fill(slip_r)
        return o.scan()
    except Exception as e:
        return {"status": "error", "error": str(e)}


class EODWriter:
    """End-of-day report: today's card, heat, alarms, tomorrow's plan."""

    def write(self, todays_trades=(), equity=None):
        L = []
        try:
            import datetime as _dt
            L.append(f"EOD — {_dt.datetime.utcnow().strftime('%Y-%m-%d')}")
            L.append("=" * 55)
        except Exception:
            pass
        try:
            rs = [float(t.get("r", 0)) for t in todays_trades]
            if rs:
                L.append(f"Trades: {len(rs)}  Net: {sum(rs):+.2f}R  "
                         f"Win: {sum(1 for x in rs if x>0)/len(rs):.0%}  "
                         f"Best: {max(rs):+.2f}  Worst: {min(rs):+.2f}")
                by_s = {}
                for t in todays_trades:
                    by_s.setdefault(str(t.get("strategy", "?")), []).append(float(t.get("r", 0)))
                for s, lrs in sorted(by_s.items(), key=lambda t: -sum(t[1])):
                    L.append(f"  {s:18s} {sum(lrs):+6.2f}R ({len(lrs)})")
            else:
                L.append("Trades: 0 (flat day — sometimes the best trade)")
            if equity is not None:
                L.append(f"Equity: {equity}")
        except Exception:
            pass
        L.append("")
        try:
            d = quantum_decay()
            al = d.get("alarms", [])
            L.append(f"Alarms: {d.get('worst', '?')} ({len(al)})")
            for a in al[:5]:
                L.append(f"  [{a['sev']}] {a['alarm']}: {a['detail']} -> {a['action']}")
        except Exception:
            pass
        L.append("")
        try:
            L.append("Tomorrow:")
            ns = quantum_news_state()
            if ns:
                L.append(f"  next event: {ns.get('title')} in {ns.get('mins_to_event')}m")
            else:
                L.append("  calendar clear > 3h out")
            g = GapGuard.cap()
            if g["frac"] < 1.0:
                L.append(f"  gap guard: {g['reason']} (size x{g['frac']})")
            else:
                L.append("  gap guard: clear")
        except Exception:
            pass
        return "\n".join(L)


def quantum_eod(todays_trades=(), equity=None):
    try:
        return EODWriter().write(todays_trades, equity)
    except Exception as e:
        return f"eod error: {e}"


class TeleFormatter:
    """Telegram/email digests: short, ASCII-safe, copy-paste ready."""

    @staticmethod
    def ticket_msg(ticket_like, lots=None):
        try:
            t = ticket_like.as_dict() if isinstance(ticket_like, EntryTicket) else dict(ticket_like or {})
            d = "BUY" if t.get("side") == 1 else ("SELL" if t.get("side") == -1 else "FLAT")
            L = [f"SENTINEL {d} {t.get('strategy', '?')}"]
            L.append(f"conf {t.get('conf', 0):.2f} reg {t.get('regime', '?')} sess {t.get('session', '?')}")
            L.append(f"SL {t.get('sl_atr', 0):.1f}a TP {t.get('tp_atr', 0):.1f}a TTL {t.get('ttl_bars', 0)}")
            if lots:
                L.append(f"lots {lots}")
            if t.get("veto"):
                L.append(f"VETO: {t['veto']}")
            return "\n".join(L)
        except Exception as e:
            return f"ticket msg error: {e}"

    @staticmethod
    def eod_msg(eod_text):
        try:
            lines = str(eod_text).splitlines()
            return "\n".join(lines[:25]) + ("\n..." if len(lines) > 25 else "")
        except Exception as e:
            return str(e)

    @staticmethod
    def alarm_msg(scan):
        try:
            al = (scan or {}).get("alarms", [])
            if not al:
                return "SENTINEL alarms: NONE - all quiet"
            L = [f"SENTINEL alarms: {(scan or {}).get('worst', '?')}"]
            for a in al[:6]:
                L.append(f"[{a['sev']}] {a['alarm']} -> {a['action']}")
            return "\n".join(L)
        except Exception as e:
            return str(e)}


class Rollback:
    """One-call demote to last-known-good: weights, profile, MTF."""

    _good = {"profile": "balanced", "mtf_w": None, "note": "factory"}

    @classmethod
    def mark_good(cls, note="operator"):
        try:
            o = _MTF_SINGLETON.get("obj")
            cls._good = {"profile": quantum_cfg("profile", "balanced"),
                         "mtf_w": dict(o.w) if o else None, "note": str(note)}
            try:
                quantum_store().save("last_good", cls._good)
            except Exception:
                pass
            return {"status": "marked", "note": cls._good["note"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @classmethod
    def rollback(cls):
        try:
            g = cls._good
            try:
                saved = quantum_store().load("last_good", None)
                if isinstance(saved, dict) and saved.get("profile"):
                    g = saved
            except Exception:
                pass
            quantum_profile(g.get("profile", "balanced"))
            if g.get("mtf_w"):
                o = _MTF_SINGLETON.get("obj")
                if o is None:
                    o = MultiTFConfluence()
                    _MTF_SINGLETON["obj"] = o
                for k, v in g["mtf_w"].items():
                    o.set_weight(k, v)
            return {"status": "rolled_back", "to": g.get("note", "?"),
                    "profile": g.get("profile")}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def quantum_rollback_mark(note="operator"):
    try:
        return Rollback.mark_good(note)
    except Exception as e:
        return {"status": "error", "error": str(e)}


def quantum_rollback():
    try:
        return Rollback.rollback()
    except Exception as e:
        return {"status": "error", "error": str(e)}


SECTION_ZENITH_OK = True
