
# ============================================================================
# R2 — BACKTEST LABORATORY (prove it before you trade it)
# ----------------------------------------------------------------------------
# R2a TradeReshuffler  Monte-Carlo trade-order shuffle -> luck vs edge bands
# R2b BootstrapCI      bootstrap confidence intervals on expectancy / PF
# R2c SensitivitySweep one-param-at-a-time robustness surface
# R2d RegimeTear       per-regime equity + stats (where does it REALLY win?)
# R2e Benchmark        strategy vs buy-and-hold on the same bars
# R2f TradeExporter    trade list -> CSV for external analysis
# Facade: quantum_lab(trades, equity, ...) -> full lab report dict + HTML
# ============================================================================

class TradeReshuffler:
    """Monte-Carlo: shuffle trade ORDER (not P&L) to separate edge from path.

    Same trades, random sequence, N paths -> distribution of max-DD, final R.
    If the realized path sits in the luck tail, the backtest flatters you.
    """

    def __init__(self, n_paths=500, seed=7):
        self.n_paths = n_paths
        self.seed = seed

    def run(self, rs):
        try:
            import random as _r
            rs = [float(x) for x in rs]
            if len(rs) < 20:
                return {"status": "need_20_trades", "n": len(rs)}
            rng = _r.Random(self.seed)
            finals, mdds = [], []
            paths = []
            for _ in range(self.n_paths):
                seq = list(rs)
                rng.shuffle(seq)
                eq, peak, mdd = 0.0, 0.0, 0.0
                for x in seq:
                    eq += x
                    peak = max(peak, eq)
                    mdd = min(mdd, eq - peak)
                finals.append(eq)
                mdds.append(mdd)
                if len(paths) < 30:
                    e, run = 0.0, []
                    for x in seq:
                        e += x
                        run.append(round(e, 2))
                    paths.append(run)
            finals.sort()
            mdds.sort()
            real = sum(rs)
            peak, mdd_real = 0.0, 0.0
            e = 0.0
            for x in rs:
                e += x
                peak = max(peak, e)
                mdd_real = min(mdd_real, e - peak)
            # Percentile of realized final within shuffled finals
            pct = sum(1 for f in finals if f <= real) / len(finals)
            return {"status": "ok", "n": len(rs), "paths": self.n_paths,
                    "real_final_r": round(real, 2), "real_mdd_r": round(mdd_real, 2),
                    "final_p5": round(finals[int(len(finals) * 0.05)], 2),
                    "final_p50": round(finals[int(len(finals) * 0.50)], 2),
                    "final_p95": round(finals[int(len(finals) * 0.95)], 2),
                    "mdd_p50": round(mdds[int(len(mdds) * 0.50)], 2),
                    "mdd_p95": round(mdds[int(len(mdds) * 0.95)], 2),
                    "real_percentile": round(pct, 3),
                    "verdict": ("luck_tail" if pct > 0.9 else
                                "unlucky_path" if pct < 0.1 else "typical_path"),
                    "sample_paths": paths}
        except Exception as e:
            return {"status": "error", "error": str(e)}


class BootstrapCI:
    """Bootstrap CIs on expectancy and profit factor (stationary-ish approx)."""

    def __init__(self, n_boot=1000, seed=11):
        self.n_boot = n_boot
        self.seed = seed

    def run(self, rs, ci=0.9):
        try:
            import random as _r
            rs = [float(x) for x in rs]
            if len(rs) < 20:
                return {"status": "need_20_trades", "n": len(rs)}
            rng = _r.Random(self.seed)
            n = len(rs)
            evs, pfs = [], []
            for _ in range(self.n_boot):
                s = [rs[rng.randrange(n)] for _ in range(n)]
                evs.append(sum(s) / n)
                gp = sum(x for x in s if x > 0)
                gl = abs(sum(x for x in s if x <= 0)) or 1e-12
                pfs.append(gp / gl)
            evs.sort()
            pfs.sort()
            lo_i = int(n and len(evs) * (1 - ci) / 2)
            hi_i = int(len(evs) * (1 - (1 - ci) / 2)) - 1
            return {"status": "ok", "n": n, "ci": ci,
                    "ev": round(sum(rs) / n, 4),
                    "ev_lo": round(evs[lo_i], 4), "ev_hi": round(evs[hi_i], 4),
                    "pf_lo": round(pfs[lo_i], 3), "pf_hi": round(pfs[hi_i], 3),
                    "edge_significant": bool(evs[lo_i] > 0),
                    "verdict": ("edge_significant" if evs[lo_i] > 0 else
                                "edge_not_proven")}
        except Exception as e:
            return {"status": "error", "error": str(e)}


class SensitivitySweep:
    """One-param-at-a-time sweep: is the edge a plateau or a spike?

    score_fn(params)->float (e.g. expectancy from a backtest run with those
    params). Each param varied across its grid while others stay at base.
    """

    def run(self, base, grids, score_fn):
        """base: {p: v}, grids: {p: [values]}. Returns robustness table."""
        out = {"params": {}, "robust": [], "fragile": []}
        try:
            base_score = float(score_fn(dict(base)))
            out["base_score"] = round(base_score, 4)
            for p, vals in (grids or {}).items():
                row = []
                for v in vals:
                    trial = dict(base)
                    trial[p] = v
                    try:
                        s = float(score_fn(trial))
                    except Exception:
                        s = float("nan")
                    row.append({"value": v, "score": round(s, 4) if s == s else None})
                scores = [r["score"] for r in row if r["score"] is not None]
                if scores:
                    span = max(scores) - min(scores)
                    pos_frac = sum(1 for s in scores if s > 0) / len(scores)
                    # Robust: profitable across >70% of grid, span small vs base
                    robust = pos_frac >= 0.7 and (abs(base_score) < 1e-9 or span / (abs(base_score) + 1e-9) < 2.0)
                    (out["robust"] if robust else out["fragile"]).append(p)
                    out["params"][p] = {"grid": row, "span": round(span, 4),
                                        "pos_frac": round(pos_frac, 3),
                                        "robust": robust}
                else:
                    out["params"][p] = {"grid": row, "robust": False}
                    out["fragile"].append(p)
            out["verdict"] = ("robust_plateau" if not out["fragile"] else
                              f"fragile:{','.join(out['fragile'])}")
            return out
        except Exception as e:
            out["error"] = str(e)
            return out


class RegimeTear:
    """Per-regime equity curves + stats: find WHERE the edge lives."""

    def run(self, trades):
        try:
            by_r = {}
            for t in trades:
                by_r.setdefault(str(t.get("regime", "?")), []).append(float(t.get("r", 0)))
            out = {"regimes": {}}
            for reg, rs in by_r.items():
                n = len(rs)
                w = sum(1 for r in rs if r > 0) / n if n else 0
                gp = sum(r for r in rs if r > 0)
                gl = abs(sum(r for r in rs if r <= 0))
                eq, peak, mdd = 0.0, 0.0, 0.0
                curve = []
                for x in rs:
                    eq += x
                    peak = max(peak, eq)
                    mdd = min(mdd, eq - peak)
                    curve.append(round(eq, 2))
                out["regimes"][reg] = {"n": n, "win_rate": round(w, 3),
                                       "net_r": round(sum(rs), 2),
                                       "ev": round(sum(rs) / n, 4) if n else 0,
                                       "pf": round(gp / (gl or 1e-12), 3),
                                       "mdd_r": round(mdd, 2),
                                       "equity": curve[-200:]}
            ranked = sorted(out["regimes"].items(),
                            key=lambda t: t[1]["ev"] * min(t[1]["n"], 50))
            out["best"] = ranked[-1][0] if ranked else None
            out["worst"] = ranked[0][0] if ranked else None
            out["verdict"] = (f"edge_lives_in_{out['best']}" if out["best"] else "no_trades")
            return out
        except Exception as e:
            return {"status": "error", "error": str(e)}


class BenchmarkBH:
    """Buy-and-hold on the same bars: the null hypothesis you must beat."""

    def run(self, closes, risk_per_trade_r=1.0, spread_cost_r=0.0, n_trades=1):
        try:
            c = [float(x) for x in closes if x]
            if len(c) < 2:
                return {"status": "need_bars"}
            # B&H return in "R-like" units: total move / mean bar range
            rngs = [abs(c[i] - c[i - 1]) for i in range(1, len(c))]
            mean_rng = sum(rngs) / len(rngs) or 1e-12
            move = c[-1] - c[0]
            bh_r = move / mean_rng - n_trades * spread_cost_r
            # B&H max-DD in same units
            peak, mdd = c[0], 0.0
            for x in c:
                peak = max(peak, x)
                mdd = min(mdd, (x - peak) / mean_rng)
            return {"status": "ok", "bh_r": round(bh_r, 2),
                    "bh_mdd_r": round(mdd, 2), "bars": len(c)}
        except Exception as e:
            return {"status": "error", "error": str(e)}


class TradeExporter:
    """Trade list -> CSV + JSON for Excel/Python autopsy outside the bot."""

    COLS = ("entry_t", "exit_t", "side", "strategy", "regime", "r", "pnl")

    def to_csv(self, trades, path="quantum_trades.csv"):
        try:
            import csv as _csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = _csv.DictWriter(f, fieldnames=list(self.COLS), extrasaction="ignore")
                w.writeheader()
                for t in trades:
                    w.writerow({k: t.get(k, "") for k in self.COLS})
            return path
        except Exception as e:
            return f"ERROR: {e}"

    def to_json(self, trades, path="quantum_trades.json"):
        try:
            import json as _j
            with open(path, "w", encoding="utf-8") as f:
                _j.dump(trades, f, default=str, indent=1)
            return path
        except Exception as e:
            return f"ERROR: {e}"


def quantum_lab(trades, equity=None, closes=None, report_path="quantum_lab.html",
                title="Sentinel Quantum Lab"):
    """Full laboratory: reshuffle + bootstrap + regime tear + benchmark + HTML."""
    try:
        rs = [float(t.get("r", 0)) for t in trades]
        lab = {"n": len(rs)}
        lab["reshuffle"] = TradeReshuffler().run(rs)
        lab["bootstrap"] = BootstrapCI().run(rs)
        lab["regime_tear"] = RegimeTear().run(trades)
        if closes:
            lab["benchmark"] = BenchmarkBH().run(closes, n_trades=len(rs))
        # Composite grade
        score = 0
        checks = []
        b = lab["bootstrap"]
        if isinstance(b, dict) and b.get("edge_significant"):
            score += 2
            checks.append("edge_significant+2")
        r = lab["reshuffle"]
        if isinstance(r, dict) and r.get("verdict") == "typical_path":
            score += 1
            checks.append("typical_path+1")
        rt = lab["regime_tear"]
        if isinstance(rt, dict) and rt.get("regimes"):
            pos_regs = [k for k, v in rt["regimes"].items()
                        if v.get("ev", 0) > 0 and v.get("n", 0) >= 10]
            if len(pos_regs) >= 2:
                score += 1
                checks.append(f"multi_regime({len(pos_regs)})+1")
            if rt.get("worst") and rt["regimes"][rt["worst"]].get("n", 0) >= 10:
                checks.append(f"avoid_{rt['worst']}")
        bh = lab.get("benchmark", {})
        if isinstance(bh, dict) and bh.get("status") == "ok":
            if sum(rs) > (bh.get("bh_r") or 0):
                score += 1
                checks.append("beats_buyhold+1")
        lab["grade"] = {4: "A", 5: "A"}.get(score, {3: "B", 2: "C"}.get(score, "F"))
        lab["score"] = f"{score}/5"
        lab["checks"] = checks
        # HTML
        try:
            rep = QuantumTearsheet(title)
            rep.add_cards([("Grade", lab["grade"], "good" if lab["grade"] in ("A", "B") else "bad"),
                           ("Score", lab["score"], None),
                           ("Trades", str(len(rs)), None),
                           ("Net R", f"{sum(rs):+.1f}R", "good" if sum(rs) > 0 else "bad")])
            if equity:
                rep.add_equity_svg(equity)
            if isinstance(rt, dict) and rt.get("regimes"):
                rows = [(k, v["n"], f"{v['win_rate']:.0%}", f"{v['net_r']:+.1f}",
                         f"{v['ev']:+.4f}", f"{v['pf']:.2f}") for k, v in
                        sorted(rt["regimes"].items(), key=lambda t: -t[1]["net_r"])]
                rep.add_table("Regime Tear", ("Regime", "N", "Win%", "Net R", "EV", "PF"),
                              rows, money_cols=(3, 4))
            rep.add_pre("Bootstrap CI", str(b))
            rep.add_pre("Reshuffle", str({k: v for k, v in r.items() if k != "sample_paths"})
                        if isinstance(r, dict) else str(r))
            rep.add_pre("Benchmark vs Buy-Hold", str(bh))
            rep.add_pre("Checks", "\n".join(checks) or "none")
            lab["report"] = rep.save(report_path)
        except Exception as e:
            lab["report_error"] = str(e)
        return lab
    except Exception as e:
        return {"status": "error", "error": str(e)}


SECTION_R2_OK = True
