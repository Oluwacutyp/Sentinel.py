
# ============================================================================
# N2 — NEWS INTELLIGENCE PACK (events as data, not fear)
# ----------------------------------------------------------------------------
# N2a CalendarStore    CSV/API calendar ingest + normalization
# N2b EventTagger      auto-classify events (tier, currency, type)
# N2c PreNewsDrift     does price drift into this event class? (stats)
# N2d PostNewsFollow   follow-through / reversal stats per class
# N2e NewsState        live state builder for ctx["news_state"]
# Facade: quantum_news_state(ts, calendar) -> news_state dict
# ============================================================================

class CalendarStore:
    """Ingest an economic calendar from CSV or dict rows.

    Canonical row: {ts (epoch), currency, title, impact (high/medium/low),
    forecast, previous}. Accepts ForexFactory-style CSVs with fuzzy headers.
    """

    HEADER_MAP = {"date": "date", "time": "time", "datetime": "ts", "timestamp": "ts",
                  "currency": "currency", "curr": "currency", "country": "currency",
                  "event": "title", "title": "title", "announcement": "title",
                  "impact": "impact", "priority": "impact", "forecast": "forecast",
                  "previous": "previous", "actual": "actual"}

    def __init__(self):
        self.events = []  # sorted canonical dicts

    def load_csv(self, path):
        try:
            import csv as _csv
            import datetime as _dt
            rows = []
            with open(path, newline="", encoding="utf-8-sig") as f:
                rd = _csv.DictReader(f)
                cols = {(c or "").strip().lower(): c for c in (rd.fieldnames or [])}
                for r in rd:
                    try:
                        g = {k: (r.get(cols.get(k, ""), "") or "").strip()
                             for k in ("ts", "date", "time", "currency", "title",
                                       "impact", "forecast", "previous")}
                        # Also try raw header names
                        if not g["title"]:
                            for hk, col in cols.items():
                                if hk in self.HEADER_MAP and self.HEADER_MAP[hk] == "title":
                                    g["title"] = (r.get(col) or "").strip()
                        if not g["title"]:
                            continue
                        ts = self._parse_ts(g, r, cols)
                        if ts is None:
                            continue
                        cur = g.get("currency", "") or ""
                        if not cur:
                            for hk, col in cols.items():
                                if hk in self.HEADER_MAP and self.HEADER_MAP[hk] == "currency":
                                    cur = (r.get(col) or "").strip()
                                    break
                        imp = (g.get("impact", "") or "medium").lower()
                        if imp not in ("high", "medium", "low"):
                            imp = "high" if imp in ("3", "h", "***") else (
                                "medium" if imp in ("2", "m", "**") else "low")
                        rows.append({"ts": ts, "currency": cur.upper()[:3] or "USD",
                                     "title": g["title"], "impact": imp,
                                     "forecast": g.get("forecast", ""),
                                     "previous": g.get("previous", "")})
                    except Exception:
                        continue
            rows.sort(key=lambda e: e["ts"])
            self.events = rows
            return {"status": "ok", "n": len(rows)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @staticmethod
    def _parse_ts(g, raw, cols):
        try:
            import datetime as _dt
            for key in ("ts", "datetime", "timestamp"):
                v = (raw.get(cols.get(key, ""), "") or "").strip()
                if v:
                    try:
                        return int(float(v))
                    except Exception:
                        pass
                    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%m/%d/%Y %H:%M",
                                "%Y-%m-%d", "%m/%d/%Y", "%Y.%m.%d %H:%M"):
                        try:
                            return int(_dt.datetime.strptime(v, fmt).replace(
                                tzinfo=_dt.timezone.utc).timestamp())
                        except Exception:
                            continue
            d = (g.get("date", "") or "").strip()
            t = (g.get("time", "") or "").strip()
            if d:
                for fmt in ("%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%Y-%m-%d",
                            "%m/%d/%Y", "%Y.%m.%d"):
                    try:
                        return int(_dt.datetime.strptime(
                            f"{d} {t}" if t else d, fmt).replace(
                            tzinfo=_dt.timezone.utc).timestamp())
                    except Exception:
                        continue
            return None
        except Exception:
            return None

    def load_rows(self, rows):
        try:
            ev = []
            for r in rows or []:
                ev.append({"ts": int(r["ts"]), "currency": str(r.get("currency", "USD")).upper()[:3],
                           "title": str(r.get("title", "?")), "impact": str(r.get("impact", "medium")).lower(),
                           "forecast": str(r.get("forecast", "")), "previous": str(r.get("previous", ""))})
            ev.sort(key=lambda e: e["ts"])
            self.events = ev
            return {"status": "ok", "n": len(ev)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def window(self, ts, before_min=60, after_min=60, currencies=("USD", "XAU")):
        """Events within [ts-before, ts+after] for relevant currencies."""
        try:
            lo, hi = ts - before_min * 60, ts + after_min * 60
            cur = {str(c).upper()[:3] for c in (currencies or ())}
            cur |= {"USD", "ALL"}
            return [e for e in self.events if lo <= e["ts"] <= hi and
                    (e["currency"] in cur or "XAU" in cur and e["currency"] == "USD")]
        except Exception:
            return []

    def next_after(self, ts, currencies=("USD",)):
        try:
            cur = {str(c).upper()[:3] for c in (currencies or ())} | {"USD"}
            for e in self.events:
                if e["ts"] >= ts and e["currency"] in cur:
                    return e
            return None
        except Exception:
            return None


class EventTagger:
    """Auto-classify events into tradeable classes.

    Classes: rates, cpi, jobs, gdp, pmi, consumer, housing, trade, energy,
    central_speak, minutes, retail, sentiment, other. Tier from impact.
    """

    RULES = (
        ("rates", ("rate decision", "interest rate", "fomc", "ecb press", "boe ")),
        ("cpi", ("cpi", "inflation", "ppi", "pce ")),
        ("jobs", ("nfp", "non-farm", "nonfarm", "unemployment", "jobless", "payroll", "adp")),
        ("gdp", ("gdp", "growth")),
        ("pmi", ("pmi", "ism manufacturing", "ism services")),
        ("consumer", ("consumer", "confidence", "sentiment", "michigan")),
        ("retail", ("retail sales",)),
        ("housing", ("housing", "building permits", "home sales", "case-shiller")),
        ("trade", ("trade balance", "current account")),
        ("energy", ("crude", "inventories", "opec", "gas storage")),
        ("central_speak", ("powell", "lagarde", "bailey", "speech", "testimony", "press conference")),
        ("minutes", ("minutes", "meeting minutes")),
    )

    @classmethod
    def tag(cls, title, impact="medium"):
        try:
            t = str(title).lower()
            for klass, keys in cls.RULES:
                if any(k in t for k in keys):
                    return f"{klass}:{impact}"
            return f"other:{impact}"
        except Exception:
            return "other:medium"

    @classmethod
    def relevant_for(cls, klass, symbol="XAUUSD"):
        """USD events move XAU; tag-gate per symbol family."""
        try:
            s = str(symbol).upper()
            if "XAU" in s or "BTC" in s:
                return True  # macro-driven; everything matters
            base = s[:3]
            return True  # conservative default: respect all scheduled risk
        except Exception:
            return True


class PreNewsDrift:
    """Stat: does price drift INTO this event class (positioning drift)?"""

    def __init__(self):
        self.samples = {}  # klass -> [drift_atr...] (signed, pre-window)

    def add(self, klass, drift_atr):
        try:
            self.samples.setdefault(str(klass), []).append(float(drift_atr))
        except Exception:
            pass

    def report(self, klass):
        try:
            l = self.samples.get(str(klass), [])
            if len(l) < 8:
                return {"status": "collecting", "n": len(l)}
            import math as _m
            mu = sum(l) / len(l)
            sd = (_m.fsum((x - mu) ** 2 for x in l) / len(l)) ** 0.5 or 1e-9
            t = mu / (sd / _m.sqrt(len(l)))
            return {"status": "ok", "n": len(l), "mean_atr": round(mu, 3),
                    "t": round(t, 2),
                    "verdict": ("drifts_up" if t > 2 else "drifts_down" if t < -2 else "no_drift")}
        except Exception:
            return {"status": "error"}


class PostNewsFollow:
    """Stat: follow-through vs reversal after the spike, per class."""

    def __init__(self):
        self.samples = {}  # klass -> [(spike_dir, follow_r)]

    def add(self, klass, spike_dir, follow_r):
        try:
            self.samples.setdefault(str(klass), []).append((int(spike_dir), float(follow_r)))
        except Exception:
            pass

    def report(self, klass):
        try:
            l = self.samples.get(str(klass), [])
            if len(l) < 8:
                return {"status": "collecting", "n": len(l)}
            # Follow-through: spike_dir * follow_r > 0
            ft = sum(1 for d, r in l if d * r > 0.2) / len(l)
            ev = sum(d * r for d, r in l) / len(l)
            return {"status": "ok", "n": len(l),
                    "follow_rate": round(ft, 3), "ev_r": round(ev, 3),
                    "verdict": ("follow" if ft > 0.6 and ev > 0.1 else
                                "fade" if ft < 0.4 and ev < -0.05 else "mixed")}
        except Exception:
            return {"status": "error"}


_NEWSLAB = {"drift": None, "follow": None, "cal": None}


def _newslab():
    try:
        if _NEWSLAB["drift"] is None:
            _NEWSLAB["drift"] = PreNewsDrift()
            _NEWSLAB["follow"] = PostNewsFollow()
            _NEWSLAB["cal"] = CalendarStore()
        return _NEWSLAB["drift"], _NEWSLAB["follow"], _NEWSLAB["cal"]
    except Exception:
        return PreNewsDrift(), PostNewsFollow(), CalendarStore()


def quantum_news_calendar_load(path_or_rows):
    try:
        _, _, cal = _newslab()
        if isinstance(path_or_rows, str):
            return cal.load_csv(path_or_rows)
        return cal.load_rows(path_or_rows)
    except Exception as e:
        return {"status": "error", "error": str(e)}


def quantum_news_state(now_ts=None, symbol="XAUUSD"):
    """Build ctx['news_state']: {mins_to_event, event_class, title, impact}."""
    try:
        import time as _t
        now = int(now_ts or _t.time())
        _, _, cal = _newslab()
        if not cal.events:
            return {}
        cur = "USD"
        e = cal.next_after(now - 30 * 60, currencies=(cur,))
        if e is None:
            return {}
        mins = (e["ts"] - now) / 60
        if abs(mins) > 180:
            return {}
        klass = EventTagger.tag(e["title"], e["impact"]).split(":")[0]
        return {"mins_to_event": round(mins, 1), "event_class": klass,
                "title": e["title"], "impact": e["impact"],
                "currency": e["currency"]}
    except Exception:
        return {}


def quantum_news_learn_fill(klass, drift_atr=None, spike_dir=None, follow_r=None):
    try:
        drift, follow, _ = _newslab()
        if drift_atr is not None:
            drift.add(klass, drift_atr)
        if spike_dir is not None and follow_r is not None:
            follow.add(klass, spike_dir, follow_r)
        return True
    except Exception:
        return False


def quantum_news_class_report(klass):
    try:
        drift, follow, _ = _newslab()
        return {"class": klass, "pre_drift": drift.report(klass),
                "post": follow.report(klass)}
    except Exception as e:
        return {"error": str(e)}


SECTION_N2_OK = True
