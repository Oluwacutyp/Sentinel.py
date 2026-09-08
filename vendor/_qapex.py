
# ============================================================================
# APEX — GRAND INTEGRATION (playbooks, production runner, master entry)
# ----------------------------------------------------------------------------
# APXa SymbolPlaybooks  per-symbol game plans (sessions, sizers, shortlists)
# APXb QuantumRunner    production loop: routine -> cycle -> size -> learn
# APXc SessionRunner    one trading session, start to report
# APXd quantum_run      master one-call entry (lab + live)
# APXe SectionRegistry  every quantum section, status, and map
# APXf ThirtyDayPlan    first-30-days deployment plan + risk disclosure
# ============================================================================

class SymbolPlaybooks:
    """Per-symbol game plans. Shortlists come from measured behavior:
    Phase-B/C/D showed BTC trends (riders earn) while XAU chops (faders
    earn, riders donate). Playbooks encode that as PRIORS — the L2 ledger
    still has the final vote from live results.
    """

    BOOKS = {
        "XAUUSD": {
            "sessions": ("LONDON", "OVERLAP", "NEWYORK"),
            "avoid": ("OFF",),
            "vol_target": 0.22, "max_dd": 0.12, "base_lots": 0.10,
            "core": ("sweep_fader", "swing_catcher", "fib_sniper", "divergence_sniper",
                     "scalp_sniper", "session_break", "news_sentinel", "dxy_tide",
                     "expiry_fade", "fractal_clock"),
            "ban": ("carry_drift",),
            "notes": ("Metals chop 70% of the time: faders first. Riders only with "
                      "HTF permission + ADX top-quartile. CPI/NFP/FOMC = blackout, "
                      "then ignition. USD tide gates size, never direction.")},
        "BTCUSD": {
            "sessions": ("OVERLAP", "NEWYORK", "ASIA"),
            "avoid": (),
            "vol_target": 0.45, "max_dd": 0.20, "base_lots": 0.10,
            "core": ("trend_rider", "breakout_hunter", "kelly_break", "session_drift",
                     "leader_lag", "risk_rotation", "vol_squeeze", "gap_filler",
                     "fractal_clock", "carry_drift"),
            "ban": ("grid_weaver",),
            "notes": ("Crypto trends: riders earn, grids die. 24/7 so no weekend "
                      "flatten, but Sunday-open thin gets 0.5x. Fat tails: "
                      "conformal exits mandatory, Kelly capped.")},
        "EURUSD": {
            "sessions": ("LONDON", "OVERLAP"),
            "avoid": ("ASIA", "OFF"),
            "vol_target": 0.12, "max_dd": 0.10, "base_lots": 0.10,
            "core": ("session_break", "trend_rider", "swing_catcher", "scalp_sniper",
                     "sweep_fader", "session_drift", "news_sentinel"),
            "ban": ("grid_weaver", "expiry_fade"),
            "notes": ("Session-driven major: London open breaks, NY lunch fades. "
                      "Tight spreads reward scalps; thin Asia vetoed.")},
        "GBPUSD": {
            "sessions": ("LONDON", "OVERLAP"),
            "avoid": ("OFF",),
            "vol_target": 0.16, "max_dd": 0.12, "base_lots": 0.08,
            "core": ("sweep_fader", "breakout_hunter", "session_break", "trend_rider",
                     "divergence_sniper", "news_sentinel"),
            "ban": ("grid_weaver",),
            "notes": ("Cable spikes through levels then reverses: sweep-fade is the "
                      "core edge. Extra slippage guard; never scalp the spikes.")},
        "USDJPY": {
            "sessions": ("ASIA", "OVERLAP"),
            "avoid": ("OFF",),
            "vol_target": 0.12, "max_dd": 0.10, "base_lots": 0.10,
            "core": ("carry_drift", "trend_rider", "session_drift", "swing_catcher",
                     "news_sentinel"),
            "ban": ("expiry_fade",),
            "notes": ("Intervention risk: news sentinel always armed, gap guard on. "
                      "Slow drifts pay; chop the interventions, don't ride them.")},
        "XAGUSD": {
            "sessions": ("LONDON", "OVERLAP", "NEWYORK"),
            "avoid": ("OFF",),
            "vol_target": 0.30, "max_dd": 0.15, "base_lots": 0.08,
            "core": ("sweep_fader", "swing_catcher", "fib_sniper", "trend_rider",
                     "leader_lag", "dxy_tide"),
            "ban": ("carry_drift",),
            "notes": ("Silver = gold on leverage with worse manners. Same playbook "
                      "as XAU, smaller size, wider conformal bands.")},
        "US30": {
            "sessions": ("NEWYORK", "OVERLAP"),
            "avoid": ("ASIA", "OFF"),
            "vol_target": 0.20, "max_dd": 0.12, "base_lots": 0.05,
            "core": ("session_break", "gap_filler", "trend_rider", "turn_of_month",
                     "dow_bias", "session_drift"),
            "ban": ("grid_weaver", "overnight"),
            "notes": ("Index: gaps fill, opens trend, month-ends mark up. Cash "
                      "session only; futures overnight drift is a different game.")},
        "GENERIC": {
            "sessions": ("LONDON", "OVERLAP", "NEWYORK"),
            "avoid": ("OFF",),
            "vol_target": 0.25, "max_dd": 0.15, "base_lots": 0.05,
            "core": ("trend_rider", "swing_catcher", "breakout_hunter",
                     "divergence_sniper", "news_sentinel", "fractal_clock"),
            "ban": (),
            "notes": ("Unknown symbol: diversified core, half size, full learning. "
                      "The ledger promotes what works within ~60 trades.")},
    }

    @classmethod
    def get(cls, symbol):
        try:
            s = str(symbol).upper()
            for key in (s, s.rstrip("m"), s.split(".")[0], "GENERIC"):
                if key in cls.BOOKS:
                    b = dict(cls.BOOKS[key])
                    b["symbol"] = s
                    return b
            b = dict(cls.BOOKS["GENERIC"])
            b["symbol"] = s
            return b
        except Exception:
            b = dict(cls.BOOKS["GENERIC"])
            b["symbol"] = str(symbol)
            return b

    @classmethod
    def shortlist_ctx(cls, symbol):
        """ctx hints: preferred strategies get a conf nudge in routing."""
        try:
            b = cls.get(symbol)
            return {"preferred": list(b["core"]), "banned": list(b["ban"]),
                    "sessions": list(b["sessions"])}
        except Exception:
            return {"preferred": [], "banned": [], "sessions": []}

    @classmethod
    def text(cls, symbol):
        try:
            b = cls.get(symbol)
            L = [f"PLAYBOOK: {b['symbol']}",
                 f"  sessions: {', '.join(b['sessions'])} (avoid {', '.join(b['avoid']) or 'none'})",
                 f"  vol_target={b['vol_target']} max_dd={b['max_dd']} base_lots={b['base_lots']}",
                 f"  core({len(b['core'])}): {', '.join(b['core'])}",
                 f"  banned: {', '.join(b['ban']) or 'none'}",
                 f"  notes: {b['notes']}"]
            return "\n".join(L)
        except Exception:
            return "playbook: n/a"


def quantum_playbook(symbol):
    try:
        return SymbolPlaybooks.text(symbol)
    except Exception:
        return "playbook: n/a"


class QuantumRunner:
    """THE production runner: routine -> cycle -> size -> execute -> learn.

    run_session_bars(data) drives the full loop over injected bars (lab) or
    live bridge data. Every fill flows back into EVERY learner (L2, exits,
    calibration, drift, killzones, rotation, blender).
    """

    def __init__(self, symbols=("XAUUSD",), profile="balanced", mode="paper",
                 equity=10000.0):
        self.symbols = list(symbols)
        self.mode = mode
        self.equity = float(equity)
        self.peak = float(equity)
        self.daily_r = 0.0
        self.cycle = QuantumCycle(symbols=self.symbols, paper=(mode != "live"),
                                  mode=mode)
        try:
            quantum_profile(profile)
        except Exception:
            pass
        self.sched = SchedulerLite.standard()
        self.history = []

    def _size_ticket(self, ticket, sym, closes):
        """RiskStack x DEEP: the final word on lots."""
        try:
            t = ticket.as_dict() if isinstance(ticket, EntryTicket) else dict(ticket)
            book = SymbolPlaybooks.get(sym)
            base = quantum_cfg("base_lots", book["base_lots"])
            px = closes[-1] if closes else 0
            prev = closes[-2] if len(closes) > 1 else px
            ctx = quantum_profile_ctx({
                "equity": self.equity, "symbol": sym, "px": px, "prev_px": prev,
                "strategy": t.get("strategy"), "side": t.get("side", 1),
                "new_risk_r": 1.0, "positions": []})
            rs = quantum_risk_stack(base, ctx)
            if rs.get("veto"):
                return {"lots": 0.0, "veto": rs["veto"], "factors": rs.get("factors", {})}
            deep = quantum_size_deep(base, t, closes, {"symbol": sym})
            lots = min(rs["lots"], deep["lots"])
            return {"lots": lots, "mult": round(rs["mult"] * deep["mult"], 3),
                    "factors": rs.get("factors", {}), "deep": deep.get("notes", [])}
        except Exception as e:
            return {"lots": 0.0, "veto": f"sizer_error:{e}"}

    def on_fill_result(self, sym, ticket_like, r, mfe_r=0.0, mae_r=0.0,
                       bars=0, session="?", p_win=None):
        """Feed ONE closed trade into every learner."""
        try:
            t = ticket_like.as_dict() if isinstance(ticket_like, EntryTicket) else dict(ticket_like or {})
            strat, regime = t.get("strategy", "?"), t.get("regime", "?")
            try:
                l2_record(strat, r)
            except Exception:
                pass
            try:
                quantum_exits_record(strat, mfe_r, mae_r, bars)
            except Exception:
                pass
            try:
                quantum_regime_observe(regime, t.get("conf", 0.5), r > 0)
            except Exception:
                pass
            try:
                quantum_drift_add(r)
            except Exception:
                pass
            try:
                quantum_killzone_record(sym, session, r)
            except Exception:
                pass
            try:
                quantum_rotation(record=(sym, r))
            except Exception:
                pass
            try:
                quantum_streak(strat, r > 0)
                quantum_streak("__global__", r > 0)
            except Exception:
                pass
            try:
                if p_win is not None:
                    quantum_blend(p_win, t.get("conf", 0.5), 0.0,
                                  t.get("conf", 0.5), r > 0)
            except Exception:
                pass
            if r < 0:
                try:
                    quantum_autopsy2_add({"strategy": strat}, dict(t), r)
                except Exception:
                    pass
            self.equity += r * 10.0  # $10/R unit default; broker fills override
            self.peak = max(self.peak, self.equity)
            self.daily_r += r
            return True
        except Exception:
            return False

    def routine_gate(self):
        try:
            r = quantum_routine(tuple(self.symbols))
            return r
        except Exception as e:
            return {"trade_allowed": False, "error": str(e)}

    def heartbeat(self):
        try:
            return quantum_heartbeat(equity=round(self.equity, 2),
                                     daily_r=round(self.daily_r, 1))
        except Exception:
            return "heartbeat n/a"


class SessionRunner:
    """Run one session: routine gate -> N paper/live cycles -> session card."""

    def __init__(self, symbols=("XAUUSD",), profile="balanced", mode="paper"):
        self.runner = QuantumRunner(symbols, profile, mode)

    def run(self, data=None, max_cycles=1):
        out = {"gate": None, "cycles": [], "card": ""}
        try:
            out["gate"] = self.runner.routine_gate()
            if not out["gate"].get("trade_allowed", False):
                out["card"] = "SESSION BLOCKED: " + str(out["gate"].get("fails"))
                return out
            for _ in range(max(1, max_cycles)):
                try:
                    c = self.runner.cycle.run_once(data)
                except Exception as e:
                    c = {"error": str(e)}
                out["cycles"].append(c)
                # Size any valid tickets (paper: record plan only)
                for rec in c.get("results", []):
                    t = rec.get("ticket", {})
                    if isinstance(t, dict) and t.get("veto") is None and t.get("side") in (1, -1):
                        try:
                            sym = rec.get("symbol", "?")
                            closes = []
                            if data and sym in data:
                                tf0 = next(iter(data[sym].values()), {})
                                closes = list(tf0.get("close", []))
                            rec["sizing"] = self.runner._size_ticket(t, sym, closes)
                        except Exception as e:
                            rec["sizing"] = {"error": str(e)}
            n_tix = sum(1 for c in out["cycles"] for r in c.get("results", [])
                        if isinstance(r.get("ticket"), dict) and r["ticket"].get("side") in (1, -1))
            out["card"] = (f"SESSION: {len(out['cycles'])} cycles, {n_tix} tickets, "
                           f"equity={self.runner.equity:.0f} mode={self.runner.mode}")
            return out
        except Exception as e:
            out["error"] = str(e)
            return out


def quantum_run(symbols=("XAUUSD",), data=None, profile="balanced",
                mode="paper", max_cycles=1):
    """MASTER ENTRY: one call runs the whole quantum system.

    symbols: watch list. data: {sym: {TF: df}} lab injection (None = bridge).
    Returns the session report. Never raises.
    """
    try:
        return SessionRunner(list(symbols), profile, mode).run(data, max_cycles)
    except Exception as e:
        return {"error": str(e)}


class SectionRegistry:
    """Every quantum section: banner, status light, one-line purpose."""

    SECTIONS = (
        ("E0", "Outcome ledger", "every fill attributed to its decision features"),
        ("E1", "Decision log", "immutable journal of brains choices"),
        ("E2", "Pattern miner", "discovers setups that actually repeat"),
        ("E3", "Param evolution", "genetic tuning under SPA discipline"),
        ("E4", "Feedback loop", "outcomes rewrite priors automatically"),
        ("E5", "Calibrated ensemble", "EWMA + Bayes + stacking + bandit"),
        ("E6", "Narrative + pre-flight", "early analysis, seasons, autopsy"),
        ("E7", "Walk-forward + conformal", "honest validation, coverage bands"),
        ("E8", "Meta-learning", "regime-cal, drift, tuner, champion store"),
        ("F1", "Pine parity I", "SR, volume, fibs, fractals"),
        ("F2", "Structure", "swings, BOS, premium/discount zones"),
        ("F3", "ICT + gangs", "liquidity, killzones, profile, GARCH, options"),
        ("F4", "Chart patterns", "triangles, wedges, flags, channels, doubles"),
        ("F5", "20 adaptive systems", "supertrend..roofing, breathing editions"),
        ("G", "Deflated stats", "DSR, Monte Carlo, SPA, harvest"),
        ("G2", "Forensics + exits", "attribution, autopsy, conformal SL/TP"),
        ("H", "Regime intel", "HMM, change-points, Hurst, MTFA, stress"),
        ("O", "Adaptive indicators", "RSI/MACD/squeeze/div/channel/volume"),
        ("O2", "Microstructure", "GK/YZ vol, Amihud/Kyle, VPIN, imbalance"),
        ("I", "Execution base", "tick cache, fetch, spread log, placer"),
        ("I2", "Execution inst.", "slicing, iceberg, arb guard, fill quality"),
        ("J", "Portfolio brain", "netting, corr cap, DD governor, sizing"),
        ("J2", "Risk pack", "CPPI shield, vol target, heat, streaks, gaps"),
        ("K", "Journal + health", "decision journal, digest, watchdogs"),
        ("L", "Legacy adapters", "9 v12 strategies groomed, parked"),
        ("L2", "Adaptive strategies", "25 systems replacing fixed logic"),
        ("M", "Diagnostics", "selftest, status, calibrate-now"),
        ("N2", "News intel", "calendar, tagger, drift/follow stats"),
        ("Q", "CLI", "operator console + CSV backtest driver"),
        ("R", "Reports", "HTML tearsheets + live status pages"),
        ("R2", "Backtest lab", "reshuffle, bootstrap, sweep, tear, grade"),
        ("T", "Symbol specs", "contract facts + spread/heat gates"),
        ("W", "Wiring", "pine bridge, MT5 bridge, cycle, junctions"),
        ("VIZ", "Dashboards", "sparklines, equity art, status screen"),
        ("CFG", "Profiles", "conservative/balanced/aggressive/moonlight"),
        ("EDGE", "Time edges", "overnight, TOM, DOW, expiry, tide, drift"),
        ("X", "Cross-market", "corr, lead-lag, risk gauge, rotation"),
        ("DEEP", "Deep systems", "fractal, entropy, GARCH, Kelly, blender"),
        ("OPS", "Integrator", "routine, review, cards, brake, heartbeat"),
        ("DOC", "Knowledge base", "api, audit, faq, playbooks in-file"),
        ("QSIG", "Signal pipeline", "MTF stack -> fuse -> signed ticket"),
        ("APEX", "Grand integration", "playbooks, runner, master entry"),
    )

    @classmethod
    def status(cls):
        rows = []
        for code, name, purpose in cls.SECTIONS:
            flag = f"SECTION_{code}_OK" if code not in ("QSIG",) else "SECTION_QSIG_OK"
            try:
                live = bool(globals().get(flag, False))
            except Exception:
                live = False
            rows.append({"section": code, "name": name, "live": live,
                         "purpose": purpose})
        return rows

    @classmethod
    def text(cls):
        try:
            rows = cls.status()
            L = ["QUANTUM SECTION REGISTRY"]
            for r in rows:
                L.append(f"  [{'ON' if r['live'] else '..'}] {r['section']:6s} {r['name']:22.22s} {r['purpose']}")
            on = sum(1 for r in rows if r["live"])
            L.append(f"  {on}/{len(rows)} sections live")
            return "\n".join(L)
        except Exception as e:
            return f"registry error: {e}"


def quantum_sections():
    try:
        return SectionRegistry.text()
    except Exception as e:
        return str(e)


QUANTUM_THIRTY_DAY_PLAN = """FIRST 30 DAYS WITH SENTINEL QUANTUM
=======================================
DAYS 1-3: PAPER. Run 'selftest', 'routine', 'backtest' on your symbol/TF.
  Load the news calendar. Read quantum_help('strategies') + your playbook.
DAYS 4-10: PAPER, FULL LOOP. quantum_run(mode='paper') every session.
  500+ bars then 'calibrate'. TAC must be < 0.08 per traded regime.
DAYS 11-17: MICRO-LIVE (0.01 lots, conservative profile). Prove fills =
  paper fills: read the fillq report. Any strategy bleeding > 0.05R/fill
  gets parked to paper until fixed.
DAYS 18-24: HALF SIZE (balanced). First weekly review. Harvest check #1:
  SPA gate promotes/demotes; you change nothing by hand.
DAYS 25-30: FULL SIZE if and only if: meta-verdict HEALTHY, expectancy >
  0.05R over 60+ live trades, bootstrap edge_significant on live fills.
AFTER: monthly harvest, weekly reviews, daily routine. The system tunes
itself; your job is the calendar, the broker, and the kill switch.
RED LINES (halt to paper immediately): DD floor touch, meta HALT_NEW_RISK,
two straight red weeks with DRIFT_DOWN, broker unhealthy, news feed dead.
""".strip()

QUANTUM_RISK_DISCLOSURE = """RISK DISCLOSURE (read this, operator)
======================================
Trading leveraged FX/metals/CFDs can lose more than your deposit with some
brokers. Backtests — including honest walk-forward ones — do not predict
live fills: spreads widen, slippage happens, regimes die. Sentinel Quantum
reduces overfitting (deflated stats, SPA gates, conformal exits, drift
halts) but cannot remove market risk. Never trade money you need. Start on
paper, then micro, then size by the RiskStack — not by hope. If you override
the governors, you own the outcome; the journal will show exactly when.
""".strip()


def quantum_thirty_day_plan():
    return QUANTUM_THIRTY_DAY_PLAN


def quantum_risk_disclosure():
    return QUANTUM_RISK_DISCLOSURE


SECTION_APEX_OK = True
