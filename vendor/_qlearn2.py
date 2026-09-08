
# ============================================================================
# E8 — META-LEARNING PACK (the brain that watches the brain)
# ----------------------------------------------------------------------------
# E8a RegimeCalibration  per-regime calibration tables (prob means different
#                        things in TREND vs RANGE — stop pretending otherwise)
# E8b DriftSentinel     ADWIN-lite online drift detection on the R stream
# E8c BanditTuner       successive-halving tuner for any param space
# E8d ChampionStore     JSON persistence: champions, calibration, killzones
# E8e MetaReport        "is the system still working?" one-screen verdict
# ============================================================================

class RegimeCalibration:
    """Separate reliability tables per regime; cross-regime borrowing.

    A 0.7 in a roaring trend is not a 0.7 in chop. Each regime keeps its own
    (predicted -> realized) bins; thin regimes borrow from the global prior.
    """

    def __init__(self, n_bins=10, prior_weight=25):
        self.n_bins = n_bins
        self.prior_w = prior_weight
        self.tables = {}  # regime -> [[hits, n]...]
        self.global_t = [[0, 0] for _ in range(n_bins)]

    def _table(self, regime):
        t = self.tables.get(regime)
        if t is None:
            t = [[0, 0] for _ in range(self.n_bins)]
            self.tables[regime] = t
        return t

    def observe(self, regime, p, won):
        try:
            b = min(self.n_bins - 1, max(0, int(float(p) * self.n_bins)))
            t = self._table(str(regime))
            t[b][0] += 1 if won else 0
            t[b][1] += 1
            self.global_t[b][0] += 1 if won else 0
            self.global_t[b][1] += 1
        except Exception:
            pass

    def calibrated(self, regime, p):
        """Borrowing-corrected P(win): regime table + global prior."""
        try:
            b = min(self.n_bins - 1, max(0, int(float(p) * self.n_bins)))
            t = self.tables.get(str(regime))
            gh, gn = self.global_t[b]
            prior = gh / gn if gn > 0 else float(p)
            if t is None:
                return prior
            h, n = t[b]
            w = n / (n + self.prior_w)
            local = h / n if n > 0 else prior
            return w * local + (1 - w) * prior
        except Exception:
            return float(p)

    def regime_reliability(self, regime):
        """TAC-style error for one regime (0 = perfect)."""
        try:
            t = self.tables.get(str(regime))
            if t is None:
                return None
            num = den = 0.0
            for i, (h, n) in enumerate(t):
                if n == 0:
                    continue
                mid = (i + 0.5) / self.n_bins
                num += n * abs(h / n - mid)
                den += n
            return num / den if den else None
        except Exception:
            return None

    def report(self):
        try:
            rows = {}
            for reg in self.tables:
                err = self.regime_reliability(reg)
                n = sum(x[1] for x in self.tables[reg])
                rows[reg] = {"n": n, "tac": round(err, 4) if err is not None else None}
            return rows
        except Exception:
            return {}


_RCAL = {"obj": None}


def quantum_regime_calibrated(regime, p):
    try:
        o = _RCAL.get("obj")
        if o is None:
            o = RegimeCalibration()
            _RCAL["obj"] = o
        return o.calibrated(regime, p)
    except Exception:
        return float(p)


def quantum_regime_observe(regime, p, won):
    try:
        o = _RCAL.get("obj")
        if o is None:
            o = RegimeCalibration()
            _RCAL["obj"] = o
        o.observe(regime, p, won)
    except Exception:
        pass


class DriftSentinel:
    """ADWIN-lite: two-window drift test on the realized-R stream.

    Compares recent-mean vs older-mean with a Hoeffding-style bound.
    DRIFT => widen uncertainty, shrink size, trigger recalibration.
    """

    def __init__(self, window=120, delta=0.05):
        self.window = window
        self.delta = delta
        self.rs = []
        self.drifts = 0
        self.state = "STABLE"

    def add(self, r):
        try:
            self.rs.append(float(r))
            del self.rs[:-self.window * 2]
            if len(self.rs) < self.window:
                return {"state": "WARMUP", "n": len(self.rs)}
            import math as _m
            w = self.window
            recent = self.rs[-w // 2:]
            older = self.rs[-w:-w // 2]
            m1 = sum(recent) / len(recent)
            m0 = sum(older) / len(older)
            # Hoeffding bound for bounded (clip +-5R) variables
            rng = 10.0
            m = 1 / (1 / len(recent) + 1 / len(older))
            eps = _m.sqrt(rng * rng * _m.log(2 / self.delta) / (2 * m))
            gap = abs(m1 - m0)
            if gap > eps and m1 < m0 - eps / 2:
                self.state = "DRIFT_DOWN"
                self.drifts += 1
            elif gap > eps and m1 > m0 + eps / 2:
                self.state = "DRIFT_UP"
                self.drifts += 1
            else:
                self.state = "STABLE"
            return {"state": self.state, "recent_ev": round(m1, 3),
                    "older_ev": round(m0, 3), "eps": round(eps, 3),
                    "drifts": self.drifts}
        except Exception:
            return {"state": "UNKNOWN"}

    def size_factor(self):
        # DRIFT_DOWN halves risk; DRIFT_UP keeps 80% (regime may be new-gold)
        return {"STABLE": 1.0, "WARMUP": 0.7, "DRIFT_UP": 0.8,
                "DRIFT_DOWN": 0.5, "UNKNOWN": 0.7}.get(self.state, 0.7)


_DRIFT = {"obj": None}


def quantum_drift_add(r):
    try:
        o = _DRIFT.get("obj")
        if o is None:
            o = DriftSentinel()
            _DRIFT["obj"] = o
        return o.add(r)
    except Exception:
        return {"state": "UNKNOWN"}


def quantum_drift_factor():
    try:
        o = _DRIFT.get("obj")
        return o.size_factor() if o is not None else 0.7
    except Exception:
        return 0.7


class BanditTuner:
    """Successive-halving tuner: spend trials where they pay.

    candidates: [{name, params}]. Each round every survivor is scored
    (external score_fn), bottom half culled, survivors get more budget.
    Generic: tunes L2 weights, F5 thresholds, exit alphas — anything.
    """

    def __init__(self, candidates, halving=0.5, min_rounds=2):
        self.cands = [dict(c) for c in candidates]
        self.halving = halving
        self.min_rounds = min_rounds
        self.round = 0
        self.scores = {c.get("name", str(i)): [] for i, c in enumerate(self.cands)}
        self.champion = None

    def _name(self, c, i):
        return c.get("name", str(i))

    def survivors(self):
        return [c for c in self.cands if not c.get("_culled")]

    def record(self, name, score):
        try:
            self.scores.setdefault(str(name), []).append(float(score))
        except Exception:
            pass

    def _mean(self, name):
        l = self.scores.get(str(name), [])
        return sum(l) / len(l) if l else float("-inf")

    def step_round(self):
        """Cull bottom half of survivors by mean score. Returns survivors."""
        try:
            surv = self.survivors()
            if len(surv) <= 1:
                if surv:
                    self.champion = surv[0]
                return surv
            self.round += 1
            if self.round < self.min_rounds and len(surv) > 2:
                # Still gathering evidence; cull only the clear worst
                worst = min(surv, key=lambda c: self._mean(self._name(c, 0)))
                worst["_culled"] = True
                return self.survivors()
            ranked = sorted(surv, key=lambda c: self._mean(self._name(c, 0)))
            keep = max(1, int(len(ranked) * (1 - self.halving)))
            for c in ranked[:-keep or []]:
                pass
            for c in ranked[:len(ranked) - keep]:
                c["_culled"] = True
            surv2 = self.survivors()
            if len(surv2) == 1:
                self.champion = surv2[0]
            return surv2
        except Exception:
            return self.survivors()

    def status(self):
        try:
            return {"round": self.round, "champion": (self.champion or {}).get("name"),
                    "alive": [self._name(c, i) for i, c in enumerate(self.survivors())],
                    "means": {k: round(sum(v) / len(v), 4) if v else None
                              for k, v in self.scores.items()}}
        except Exception:
            return {}


class ChampionStore:
    """JSON persistence for everything the brain learns (survives restarts).

    One file per concern under store_dir: champions, regime_cal, killzones,
    exits, broker prints, strategy stats. Atomic writes (tmp + rename).
    """

    def __init__(self, store_dir="quantum_store"):
        self.dir = store_dir

    def _path(self, name):
        import os as _os
        d = self.dir
        try:
            _os.makedirs(d, exist_ok=True)
        except Exception:
            pass
        return _os.path.join(d, f"{name}.json")

    def save(self, name, obj):
        try:
            import json as _j
            import os as _os
            p = self._path(name)
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                _j.dump(obj, f, default=str)
            _os.replace(tmp, p)
            return p
        except Exception as e:
            return f"ERROR: {e}"

    def load(self, name, default=None):
        try:
            import json as _j
            with open(self._path(name), encoding="utf-8") as f:
                return _j.load(f)
        except Exception:
            return default

    def snapshot_all(self):
        """Gather every learnable in the core and persist it."""
        out = {}
        try:
            out["l2"] = l2_leaderboard()
        except Exception:
            pass
        try:
            o = _RCAL.get("obj")
            out["regime_cal"] = o.report() if o else {}
        except Exception:
            pass
        try:
            out["importance"] = quantum_global_importance()
        except Exception:
            pass
        try:
            out["fillq"] = quantum_fillq_report()
        except Exception:
            pass
        try:
            out["killzones"] = {k: g.table() for k, g in _KZ_CACHE.items()}
        except Exception:
            pass
        try:
            o = _MTF_SINGLETON.get("obj")
            out["mtf_w"] = dict(o.w) if o else {}
        except Exception:
            pass
        try:
            o = _DRIFT.get("obj")
            out["drift"] = {"state": o.state, "drifts": o.drifts} if o else {}
        except Exception:
            pass
        for k, v in out.items():
            self.save(k, v)
        return {"saved": sorted(out.keys()), "dir": self.dir}

    def restore_mtf(self):
        try:
            w = self.load("mtf_w", {})
            if w:
                o = _MTF_SINGLETON.get("obj")
                if o is None:
                    o = MultiTFConfluence()
                    _MTF_SINGLETON["obj"] = o
                for k, v in w.items():
                    o.set_weight(k, v)
                return True
            return False
        except Exception:
            return False


_CHAMP = {"obj": None}


def quantum_store():
    try:
        o = _CHAMP.get("obj")
        if o is None:
            o = ChampionStore()
            _CHAMP["obj"] = o
        return o
    except Exception:
        return ChampionStore()


def quantum_snapshot():
    try:
        return quantum_store().snapshot_all()
    except Exception as e:
        return {"error": str(e)}


class MetaReport:
    """'Is the system still working?' — one verdict from every watchdog."""

    @staticmethod
    def verdict():
        parts = []
        score = 1.0
        try:
            # 1. Drift state
            try:
                o = _DRIFT.get("obj")
                ds = o.state if o else "WARMUP"
            except Exception:
                ds = "UNKNOWN"
            parts.append(f"drift:{ds}")
            if ds == "DRIFT_DOWN":
                score *= 0.5
            elif ds in ("WARMUP", "UNKNOWN"):
                score *= 0.85
            # 2. L2 health: any strategy with expectancy > 0?
            try:
                lb = l2_leaderboard()
                alive = [r for r in lb if not r.get("parked")]
                pos = [r for r in alive if r.get("expectancy", 0) > 0]
                parts.append(f"l2:{len(pos)}/{len(alive)}_positive")
                if alive and not pos:
                    score *= 0.6
            except Exception:
                parts.append("l2:n/a")
            # 3. Calibration
            try:
                o = _RCAL.get("obj")
                rep = o.report() if o else {}
                bad = [k for k, v in rep.items()
                       if (v.get("tac") or 0) > 0.15 and (v.get("n") or 0) > 30]
                parts.append(f"miscalibrated_regimes:{len(bad)}")
                if bad:
                    score *= 0.85
            except Exception:
                parts.append("cal:n/a")
            # 4. Execution
            try:
                fq = quantum_fillq_report()
                slip = fq.get("avg_slip_r", 0) if isinstance(fq, dict) else 0
                parts.append(f"avg_slip:{slip}R")
                if isinstance(slip, (int, float)) and slip < -0.1:
                    score *= 0.8
            except Exception:
                parts.append("exec:n/a")
            # 5. Broker prints
            try:
                bad_b = [k for k, p in BrokerFingerprint._prints.items()
                         if not p.healthy()]
                parts.append(f"unhealthy_brokers:{len(bad_b)}")
                if bad_b:
                    score *= 0.7
            except Exception:
                pass
            verdict = ("HEALTHY" if score > 0.8 else
                       "DEGRADED" if score > 0.5 else "HALT_NEW_RISK")
            return {"verdict": verdict, "score": round(score, 3), "parts": parts}
        except Exception as e:
            return {"verdict": "UNKNOWN", "score": 0.0, "error": str(e)}


def quantum_meta_verdict():
    try:
        return MetaReport.verdict()
    except Exception as e:
        return {"verdict": "UNKNOWN", "error": str(e)}


SECTION_E8_OK = True
