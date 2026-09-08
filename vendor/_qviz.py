
# ============================================================================
# VIZ — TERMINAL DASHBOARDS (the whole system on one screen, no browser)
# ----------------------------------------------------------------------------
# sparkline / equity_screen / regime_ribbon / l2_board_text / status_screen
# Every renderer is pure-text, width-capped, and total (never raises).
# ============================================================================

def qspark(vals, w=60, glyphs=" .:-=+*#%@"):
    """Unicode sparkline for any float series."""
    try:
        v = [float(x) for x in vals if x is not None and x == x][-w:]
        if len(v) < 2:
            return "(flat)"
        mn, mx = min(v), max(v)
        rng = (mx - mn) or 1.0
        return "".join(glyphs[min(len(glyphs) - 1, max(0, int((x - mn) / rng * (len(glyphs) - 1))))]
                       for x in v)
    except Exception:
        return "(n/a)"


def qbar(frac, w=20, fill="#", empty="-"):
    try:
        f = qclip(float(frac), 0, 1)
        n = int(round(f * w))
        return fill * n + empty * (w - n) + f" {f:.0%}"
    except Exception:
        return "(n/a)"


def qequity_screen(equity, w=64, h=12):
    """ASCII equity mountain + drawdown readout."""
    try:
        eq = [float(x) for x in equity if x is not None and x == x]
        if len(eq) < 2:
            return "equity: need 2+ points"
        # Downsample to width
        step = max(1, len(eq) // w)
        s = eq[::step][:w]
        mn, mx = min(s), max(s)
        rng = (mx - mn) or 1.0
        rows = []
        for r in range(h, -1, -1):
            lvl = mn + rng * r / h
            line = "".join("#" if v >= lvl else " " for v in s)
            rows.append(f"{lvl:+8.1f} {line}")
        peak, mdd = -1e18, 0.0
        for v in eq:
            peak = max(peak, v)
            mdd = min(mdd, v - peak)
        rows.append(f" last:{eq[-1]:+.1f}R  peak:{peak:+.1f}R  mdd:{mdd:+.1f}R  n:{len(eq)}")
        return "\n".join(rows)
    except Exception:
        return "equity: n/a"


def qregime_ribbon(regimes, w=64):
    """One-char-per-bar regime history strip."""
    try:
        glyph = {"TREND_UP": "^", "TREND_DOWN": "v", "RANGE": "=",
                 "QUIET": ".", "VOLATILE": "!", "SESSION": "s",
                 "MEAN_REVERT": "~", "CHAOS": "X", "NEWS": "N"}
        s = "".join(glyph.get(str(r).upper(), "?") for r in list(regimes)[-w:])
        return f"[{s}]  ^=up v=dn ==range .=quiet !=vol s=session ~=revert X=chaos N=news"
    except Exception:
        return "regime: n/a"


def ql2_board_text(top=15):
    """Leaderboard as a fixed-width table."""
    try:
        lb = l2_leaderboard()
        if not lb:
            return "L2: no data"
        lines = ["STRATEGY          N   WIN%    EXP_R   W     STATE"]
        for r in lb[:top]:
            st = "PARKED" if r.get("parked") else ("HOT" if r.get("expectancy", 0) > 0.1 else "ok")
            lines.append(f"{r.get('strategy','?'):16.16s} {r.get('n',0):3d} "
                         f"{r.get('win_rate',0):6.0%} {r.get('expectancy',0):+7.3f} "
                         f"{r.get('weight',0):5.2f} {st}")
        return "\n".join(lines)
    except Exception:
        return "L2: n/a"


def qimportance_text():
    try:
        imp = quantum_global_importance()
        if not imp:
            return "attribution: collecting..."
        mx = max(imp.values()) or 1.0
        return "\n".join(f"{k:12.12s} {qbar(v / mx, 24)}" for k, v in imp.items())
    except Exception:
        return "attribution: n/a"


def qstatus_screen(equity=None, regimes=None):
    """THE dashboard: verdict, governors, board, attribution, equity."""
    try:
        L = []
        L.append("=" * 70)
        try:
            L.append(quantum_version() + "   " + __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
        except Exception:
            L.append("SENTINEL QUANTUM")
        L.append("=" * 70)
        try:
            mv = quantum_meta_verdict()
            L.append(f"VERDICT: {mv.get('verdict')}  score={mv.get('score')}  [{' | '.join(mv.get('parts', []))}]")
        except Exception:
            L.append("VERDICT: n/a")
        try:
            o = _DRIFT.get("obj")
            L.append(f"DRIFT: {o.state if o else 'WARMUP'}  size_factor={quantum_drift_factor()}")
        except Exception:
            pass
        try:
            h = quantum_heat()
            L.append(f"HEAT: {h.get('heat')}R / cap {h.get('cap')}R")
        except Exception:
            pass
        if regimes:
            L.append(qregime_ribbon(regimes))
        L.append("-" * 70)
        L.append(ql2_board_text())
        L.append("-" * 70)
        L.append("SIGNAL ATTRIBUTION (global importance)")
        L.append(qimportance_text())
        if equity:
            L.append("-" * 70)
            L.append(qequity_screen(equity))
        L.append("=" * 70)
        return "\n".join(L)
    except Exception as e:
        return f"status screen error: {e}"


def qjournal_tail_text(n=12):
    """Last-n decision journal rows as text (falls back gracefully)."""
    try:
        if "quantum_journal_tail" in dir():
            try:
                return quantum_journal_tail(n)
            except Exception:
                pass
        # Fallback: cycle tickets from any live QuantumCycle is out of scope;
        # surface autopsy + fill quality instead (always available).
        parts = []
        try:
            parts.append("AUTOPSY: " + str(quantum_autopsy2_report().get("verdict")))
        except Exception:
            pass
        try:
            parts.append("FILLQ: " + str(quantum_fillq_report().get("verdict")))
        except Exception:
            pass
        return "\n".join(parts) if parts else "journal: n/a"
    except Exception:
        return "journal: n/a"


SECTION_VIZ_OK = True
