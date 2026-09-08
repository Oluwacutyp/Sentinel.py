
# ============================================================================
# CFG — QUANTUM CONFIG PROFILES (one knob for the whole risk personality)
# ----------------------------------------------------------------------------
# Four tuned personalities + custom JSON override. A profile sets every
# governor input in one place: RiskStack ctx, L2 routing bias, fuse quotas,
# exit alpha, and harvest cadence. QUANTUM_PROFILE env selects at boot.
# ============================================================================

QUANTUM_PROFILES = {
    "conservative": {
        "desc": "Capital preservation. Small size, only A-grade tickets.",
        "base_lots": 0.05, "max_dd_frac": 0.08, "target_ann": 0.15,
        "heat_cap_r": 2.0, "min_conf": 0.62, "fuse_cooldown": 10,
        "fuse_quota": 2, "exit_alpha": 0.10, "drift_floor": 0.5,
        "streak_cap": 1.15, "harvest_days": 30, "paper_first_bars": 1000,
        "allow_counter_htf": False, "max_symbols": 2,
    },
    "balanced": {
        "desc": "Default. Full system, governors at spec values.",
        "base_lots": 0.10, "max_dd_frac": 0.15, "target_ann": 0.25,
        "heat_cap_r": 4.0, "min_conf": 0.50, "fuse_cooldown": 6,
        "fuse_quota": 3, "exit_alpha": 0.15, "drift_floor": 0.5,
        "streak_cap": 1.30, "harvest_days": 30, "paper_first_bars": 500,
        "allow_counter_htf": True, "max_symbols": 4,
    },
    "aggressive": {
        "desc": "Maximum edge extraction. Bigger heat, faster harvest.",
        "base_lots": 0.20, "max_dd_frac": 0.25, "target_ann": 0.40,
        "heat_cap_r": 6.0, "min_conf": 0.45, "fuse_cooldown": 4,
        "fuse_quota": 5, "exit_alpha": 0.20, "drift_floor": 0.6,
        "streak_cap": 1.50, "harvest_days": 14, "paper_first_bars": 250,
        "allow_counter_htf": True, "max_symbols": 6,
    },
    "moonlight": {
        "desc": "Private build personality: aggressive sizing + all 15 systems.",
        "base_lots": 0.25, "max_dd_frac": 0.25, "target_ann": 0.45,
        "heat_cap_r": 7.0, "min_conf": 0.45, "fuse_cooldown": 3,
        "fuse_quota": 6, "exit_alpha": 0.20, "drift_floor": 0.6,
        "streak_cap": 1.60, "harvest_days": 14, "paper_first_bars": 0,
        "allow_counter_htf": True, "max_symbols": 8,
    },
}

QUANTUM_CFG = dict(QUANTUM_PROFILES["balanced"])
QUANTUM_CFG["profile"] = "balanced"


def quantum_profile(name=None):
    """Get/set the active profile. quantum_profile('aggressive') switches."""
    try:
        import os as _os
        if name is None:
            name = _os.environ.get("QUANTUM_PROFILE", QUANTUM_CFG.get("profile", "balanced"))
        key = str(name).lower()
        if key not in QUANTUM_PROFILES:
            return {"status": "unknown_profile", "active": QUANTUM_CFG.get("profile"),
                    "known": sorted(QUANTUM_PROFILES.keys())}
        QUANTUM_CFG.clear()
        QUANTUM_CFG.update(QUANTUM_PROFILES[key])
        QUANTUM_CFG["profile"] = key
        # Push fuse quotas live
        try:
            o = _FUSE_SINGLETON.get("obj")
            if o is not None:
                o.cooldown = QUANTUM_CFG["fuse_cooldown"]
                o.max_per_regime = QUANTUM_CFG["fuse_quota"]
        except Exception:
            pass
        try:
            o = _HEAT.get("obj")
            if o is not None:
                o.cap = QUANTUM_CFG["heat_cap_r"]
        except Exception:
            pass
        return {"status": "ok", "active": key, "desc": QUANTUM_CFG["desc"]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def quantum_cfg(key=None, default=None):
    try:
        if key is None:
            return dict(QUANTUM_CFG)
        return QUANTUM_CFG.get(key, default)
    except Exception:
        return default


def quantum_profile_ctx(extra=None):
    """RiskStack-ready ctx from the active profile (+ caller overrides)."""
    try:
        ctx = {"max_dd_frac": QUANTUM_CFG.get("max_dd_frac", 0.15),
               "target_ann": QUANTUM_CFG.get("target_ann", 0.25)}
        if extra:
            ctx.update(extra)
        return ctx
    except Exception:
        return dict(extra or {})


def quantum_min_conf():
    try:
        return float(QUANTUM_CFG.get("min_conf", 0.5))
    except Exception:
        return 0.5


def quantum_profile_save(path="quantum_profile.json"):
    try:
        import json as _j
        with open(path, "w", encoding="utf-8") as f:
            _j.dump(QUANTUM_CFG, f, indent=1)
        return path
    except Exception as e:
        return f"ERROR: {e}"


def quantum_profile_load(path="quantum_profile.json"):
    try:
        import json as _j
        with open(path, encoding="utf-8") as f:
            d = _j.load(f)
        if isinstance(d, dict) and "profile" in d:
            base = d.get("profile", "balanced")
            quantum_profile(base)
            for k, v in d.items():
                if k not in ("profile", "desc"):
                    QUANTUM_CFG[k] = v
            return {"status": "ok", "active": QUANTUM_CFG.get("profile"),
                    "overrides": [k for k in d if k not in ("profile", "desc")]}
        return {"status": "bad_file"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def quantum_profile_text():
    try:
        lines = [f"PROFILE: {QUANTUM_CFG.get('profile')} — {QUANTUM_CFG.get('desc', '')}"]
        for k in ("base_lots", "max_dd_frac", "target_ann", "heat_cap_r",
                  "min_conf", "fuse_cooldown", "fuse_quota", "exit_alpha",
                  "harvest_days", "max_symbols"):
            lines.append(f"  {k:14s} {QUANTUM_CFG.get(k)}")
        return "\n".join(lines)
    except Exception:
        return "profile: n/a"


SECTION_CFG_OK = True
