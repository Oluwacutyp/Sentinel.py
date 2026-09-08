
# ============================================================================
# DOC — IN-FILE KNOWLEDGE BASE (API reference, audit ledger, operator FAQ)
# ----------------------------------------------------------------------------
# Documentation that ships WITH the code and is queryable at runtime:
# quantum_help("topic"). Topics: api, audit, env, backtest, live, faq,
# strategies, regimes, exits, troubleshoot, glossary.
# ============================================================================

QUANTUM_DOCS = {
"index": """Sentinel Quantum knowledge base — quantum_help(topic):
  api .......... every public quantum_* / f5_ / l2_ entry point
  audit ........ the full shake-up ledger (legacy -> adaptive mapping)
  strategies ... the 15 L2 systems: when each trades, what it needs
  regimes ...... the 9 regimes and who is allowed to trade them
  exits ........ conformal exits, trails, ladders, time stops
  env .......... environment variables + moonlight credentials table
  backtest ..... CSV format, CLI, reading the tearsheet
  live ......... go-live checklist, kill switches, harvest cycle
  faq .......... the questions every operator asks
  troubleshoot . red-week playbook: what to check, in order
  glossary ..... R, TAC, SPA, conformal, killzone, fuse...
""",
"api": """QUANTUM API REFERENCE (public entry points)
================================================
BRAIN
  quantum_calibrated_prob(feats) -> 0..1      E5 ensemble probability
  quantum_expected_r(feats, side) -> R        E5 expected payoff
  quantum_regime(df) -> {regime, conf, ...}   H regime classifier
  quantum_early(df, tick) -> {pass,...}       E6 pre-flight gate
  quantum_regime_calibrated(reg, p) -> p      E8 per-regime correction
  quantum_regime_observe(reg, p, won)         E8 table update
  quantum_drift_add(r) / factor()             E8 drift watch + size factor
  quantum_meta_verdict() -> HEALTHY/...       E8 system verdict
  quantum_snapshot() -> {saved:[...]}         E8 persist all learning
FEATURES
  f5_confluence(df) -> {bias,conf,votes,n}    20 adaptive systems pooled
  quantum_indicators(df) -> {...}             O adaptive indicator pack
  quantum_mtf({TF:df}, exec) -> stack         QSIG multi-TF stack
  quantum_matrix_text({TF:df}) -> str         confluence heat grid
SIGNAL
  l2_route(ctx) -> {signals,bias,...}         15-strategy router
  l2_record(name, r) / l2_leaderboard()       stats + weights + parking
  quantum_signal(tf_dfs, ctx, ...) -> Ticket  full pipeline to entry ticket
  quantum_fuse(strat, side, reg, bar)         dedupe + cooldown + quota
  quantum_killzone(sym, sess) -> gate         learned session gate
EXITS
  quantum_exits(class, atr, side)             conformal SL/TP/time
  quantum_exits_record(class, mfe, mae, n)    feed the exit learner
  quantum_trail(ticket, px, ...)              adaptive ratchet / STOPPED
  quantum_ladder(class) -> [{at_r,frac}]      scale-out ladder
EXECUTION
  quantum_execute(ticket, ctx, broker_fn)     guarded fill pipeline
  quantum_quote_guard(bmid, ref)              stale-quote halt
  quantum_deadline(ticket, ttl) / _sweep()    pending TTL management
  quantum_fillq_add(...) / _report()          slippage attribution
FORENSICS
  quantum_attribute(feats, score_fn)          Shapley-lite drivers
  quantum_global_importance()                 what moves the needle overall
  quantum_autopsy2_report()                   loser-cluster verdict
REPORTS / OPS
  quantum_backtest_csv(path, sym)             CSV -> HTML tearsheet
  quantum_backtest_report(trades, eq, path)   tearsheet builder
  quantum_live_status_report(path)            live snapshot page
  quantum_cli(argv) / QUANTUM_CLI_HELP        operator console
  quantum_selftest_text() / _status_text()    M diagnostics
  quantum_version() / _architecture()         version + map + runbook
  quantum_help(topic)                         this knowledge base
  quantum_spec(symbol) -> SymbolSpec          contract facts + gates
All quantum_* calls are total: they never raise; worst case they return a
safe fallback (0, pass-True, or {'status':'error'} + reason).
""",
"audit": """THE SHAKE-UP LEDGER — legacy logic vs adaptive replacement
=============================================================
LEGACY (v12.1, preserved below the quantum line)   ->  QUANTUM
----------------------------------------------------------------
ema9/ema21 + adx>25 (TrendFollowing l.12098)       -> trend_rider:
  breathing EMAs (efficiency), ADX rolling quantile, calibrated conf
high_20/low_20 + 3xSL/6xTP (Breakout l.12301)      -> breakout_hunter:
  breathing lookback, structure SL, learned-R TP, adaptive trap fade
fixed z mean-reversion (V18 l.11476/18718)         -> swing_catcher:
  breathing window, quantile bands, HTF veto vs strong drift
fixed 38.2/50/61.8 fibs (Pullback l.12436)        -> fib_sniper:
  reaction-validated levels, dead levels pruned by touch stats
every-wick SMC sweeps (SMC l.12602)                -> sweep_fader:
  displacement-quantile filter, reclaim-required, else treated as break
1.001/0.999 micro bands (Scalp l.18881)            -> scalp_sniper:
  spread-normalized targets, killzone gate, imbalance trigger, AE kill
single-indicator divergence (Div l.18829)          -> divergence_sniper:
  THREE witnesses required (div + RSI-quantile + swing break)
fixed blackout minutes (News l.5402/12740)         -> news_sentinel:
  per-event-class realized-vol blackouts, expected-move straddles
staged martingale-adjacent sizing (Recov l.16613)  -> recovery_pilot:
  edge-gated scaling — no positive live edge, no scale-up. Ever.
fixed-drawdown hedge lots (BattleBot l.22190)      -> hedge_guardian:
  correlation-gated, beta-sized, targets net-zero delta
static ensemble votes (Ensemble l.11365)           -> L2Suite weights:
  expectancy x sqrt(n); dead strategies auto-parked after 20 trades
fixed 1:2 exits everywhere                          -> G2 conformal exits:
  MFE/MAE quantiles per setup-class with coverage guarantees
scattergun session trading                          -> killzones + fuse:
  learned per-symbol session stats; cooldown + regime quotas
WHAT WAS KEPT: every guardrail, kill-switch, telemetry column, news filter,
risk manager, journal format, and adapter in v12.1 — the L section grooms
9 legacy strategies as consult-only advisers (parked by default).
""",
"strategies": """THE 15 L2 SYSTEMS — when each trades
============================================
TREND (ride it)                    REGIMES              NEEDS
  trend_rider ................... TREND_*, VOLATILE ... ADX top-40%, EMA touch
  breakout_hunter ............... RANGE, VOLATILE ..... squeeze + volume + no trap
  session_break ................. RANGE, QUIET ........ session open range + expansion
  vol_squeeze ................... QUIET, RANGE ........ compression pct<0.2 + release
RANGE (fade it)
  swing_catcher ................. RANGE, QUIET ........ z beyond quantile band
  fib_sniper .................... RANGE, TREND_* ...... armed level + wick reaction
  sweep_fader ................... RANGE, VOLATILE ..... top-quartile sweep + reclaim
  gap_filler .................... RANGE, QUIET ........ gap/FVG + no acceptance beyond
  grid_weaver ................... RANGE, QUIET ........ low heat + quantum bias align
FAST (snipe it)
  scalp_sniper .................. QUIET, RANGE ........ killzone + imbalance + lean
  divergence_sniper ............. RANGE, TREND_*, VOL  3 witnesses (div/RSI/swing)
SLOW (grind it)
  carry_drift ................... QUIET, RANGE ........ drift SNR 0.04..0.5, tiny size
PROTECT (survive it)
  news_sentinel ................. ALL ................. event within adaptive window
  hedge_guardian ................ ALL ................. exposure + pain + correlation
  recovery_pilot ................ not CHAOS/NEWS ...... drawdown + LIVE edge > 0.02R
ROUTING: l2_route() runs only regime-suitable systems, weights votes by
learned weight, vetoes on news blackout, and parks losers automatically.
""",
"regimes": """THE 9 REGIMES — permission map
=================================
  TREND_UP / TREND_DOWN ... directional, efficient. Riders + hunters + snipers.
  RANGE ................... bounded chop. Catchers, fibs, sweeps, grids.
  QUIET ................... dead/low-vol. Drift, scalps (killzone permitting).
  VOLATILE ................ wide but tradeable. Hunters, sweeps, divergence.
  SESSION ................. session-open energy. Session breaks, ignition.
  MEAN_REVERT ............. stretched rubber. Catchers only + HTF gate.
  CHAOS ................... untradeable noise. FLAT — only hedge_guardian.
  NEWS .................... event window. FLAT except news_sentinel straddle.
Regime comes from H (HMM + change-points + Hurst + MTFA vote). Every ticket
carries its regime; every stat table splits by it. If you disagree with a
regime call, the journal + matrix show exactly why it was called.
""",
"exits": """EXITS — where the money is kept
==================================
1. CONFORMAL (G2): per-setup-class MFE/MAE quantiles. SL = adverse quantile
   (1-alpha), TP = favorable quantile (0.35), time-stop = duration q0.8.
   Coverage guarantee printed on every exit set. Needs 25 samples/class;
   before that, safe 2.0/3.0/48 defaults.
2. TRAIL (TrailSmith): ratchets to max(chandelier 2.2a, swing +/- 0.3a,
   breakeven+0.2a after +1R). Never loosens. Returns STOPPED at the line.
3. LADDER (PartialBanker): scale-out fractions at the MFE q0.3/0.55/0.75 —
   bank where price historically stalls for THIS setup.
4. TIME: conformal duration stop. Dead money is risk.
5. STRUCTURE: L2 strategies set SL beyond the level that proves them wrong
   (slow EMA, broken level, extreme, gap origin) — never a round number.
Record every closed trade via quantum_exits_record(class, mfe_r, mae_r,
bars) or the exit learner starves. The backtester does this automatically.
""",
"env": """ENVIRONMENT + CREDENTIALS
===========================
Standard build (GitHub-safe — never hardcode):
  MT5_LOGIN / MT5_PASSWORD / MT5_SERVER ... broker login
  MT5_PATH (optional) ...................... terminal path
  TG_BOT_TOKEN / TG_CHAT_ID ................ alerts
  GMAIL_USER / GMAIL_APP_PASSWORD .......... email reports
  GEMINI_API_KEY ........................... narrative LLM (optional)
  NEWS_API_KEY / NEWS_CALENDAR_URL ......... event feed
  QUANTUM_MODE=live|paper|off (default live). paper = tickets logged, no fills.
Moonlight build (private file, NEVER pushed to git):
  Same keys, hardcoded in the MOONLIGHT block. The file lives outside the
  repo; git history on GitHub stays scrubbed. Rotate the broker password the
  day Moonlight is generated — the old password is burned into main history.
""",
"backtest": """BACKTEST GUIDE
================
CSV FORMAT: header time,open,high,low,close[,tickvol]. Any timeframe; name
the file SYMBOL_TF.csv (e.g. XAUUSDm_M15.csv) for auto-symbol.
RUN:  python sentinel_bot.py backtest XAUUSDm_M15.csv XAUUSDm
  (or quantum_backtest_csv(path, symbol) from code)
RULES THE ENGINE ENFORCES: decisions use bars strictly before entry;
fills at next-bar open; SL checked before TP intrabar (conservative);
spread cost subtracted in R; first 25% of bars are warmup (no trades).
READING THE TEARSHEET: Net R + expectancy first; profit factor > 1.3 with
100+ trades is interesting; per-regime table shows WHERE the edge lives;
calibration + walk-forward sections show whether to believe it; L2 board
shows WHO earned it. Green equity with red calibration = luck; size small.
PARITY: the same quantum_signal() + quantum_exits() code runs live and in
backtest — there is no separate backtest strategy to drift out of sync.
""",
"live": """GO-LIVE CHECKLIST
===================
1. selftest PASS (13/13) and status shows no missing deps.
2. Paper-trade 500+ bars; run 'calibrate'; TAC < 0.08 per regime.
3. Backtest tearsheet: PF > 1.2, expectancy > 0.05R, 100+ trades.
4. Meta-verdict HEALTHY (or DEGRADED with a known, accepted reason).
5. Kill switches verified: daily -4R halt, DD governor veto, quote guard.
6. News feed live (check news_sentinel sees the next event).
7. Snapshot store writable (quantum_store/ persists learning).
8. Alerts live (send a test Telegram/email).
HARVEST (monthly): SPA gate promotes challengers; parked strategies need
20+ paper trades at expectancy > 0 to return. Never hand-edit weights —
record results and let the ledger do it, or the audit trail lies.
""",
"faq": """OPERATOR FAQ
==============
Q: Why did it skip my perfect setup?
A: Read the ticket chain (journal): mtf -> regime -> killzone -> early ->
   L2 -> permission -> fuse -> calibration -> exits. The veto is named.
Q: Why is size so small?
A: Stacked governors: lot_mult x vol-governor x drift-factor x DD-governor.
   'status' prints each factor. Small size in unfamiliar regimes is the
   system working, not broken.
Q: It traded against the H1 trend!
A: Only swing_catcher with conf > 0.7 may. Everything else needs HTF
   permission. Check the matrix: permission row shows the HTF vote.
Q: Can I force a trade?
A: No manual override exists by design. Paper account + 'calibrate' is the
   override: prove the edge and the system adopts it.
Q: How is this different from the old bot?
A: Old: fixed numbers, static votes, 1:2 exits, martingale-adjacent
   recovery. New: everything learned or quantile-based, exits with
   guarantees, edge-gated recovery, losers parked automatically.
Q: What breaks it?
A: Stale quotes (guarded), dead news feed (check weekly), broker
   slippage regime change (fillq report), trading CHAOS (vetoed), and
   operator edits to learned weights (don't).
""",
"troubleshoot": """RED-WEEK PLAYBOOK (in order)
===============================
1. quantum_meta_verdict() — which watchdog is red?
2. DRIFT_DOWN? Halve risk (auto), read the last 20 journal rows: same
   regime? same strategy? same session?
3. Autopsy report: which driver-pair leads the losers? If one pair owns
   > 40% of red R, consider parking its strategy to paper.
4. Attribution importance shifted? A top-3 driver falling out means the
   market changed character — recalibrate, don't override.
5. Fill quality: avg_slip < -0.1R means execution, not signal. Check
   broker health, spread logs, session mix.
6. Calibration per regime: TAC > 0.15 anywhere with n > 30 means the
   probabilities lie — run 'calibrate' on fresh paper data.
7. Walk-forward: last window negative while older windows green =
   edge decay. Demote the system to paper until two green windows.
8. If EVERYTHING is red incl. paper: market is CHAOS/NEWS dominated.
   The correct trade is flat; the system already knows. Let it sit.
""",
"glossary": """GLOSSARY
==========
  R ............ one unit of initial risk. +2R = won twice what was risked.
  Expectancy ... mean R per trade. > 0.05R with 100+ trades = real edge.
  TAC .......... top-label absolute calibration error. < 0.08 = honest probs.
  SPA .......... superior predictive ability: is the champion really better?
  Conformal .... exits/intervals with finite-sample coverage guarantees.
  Killzone ..... session bucket; cold ones (score < 0.3) veto entries.
  Fuse ......... dedupe + cooldown + regime quota on repeated signals.
  MFE/MAE ...... max favorable/adverse excursion of a trade, in R.
  Pinball ...... quantile loss: scores interval forecasts honestly.
  Deflated SR .. Sharpe corrected for multiple-testing luck.
  Attribution .. which input moved the needle (Shapley-lite leave-one-out).
  Harvest ..... monthly promotion/demotion of strategies by SPA gate.
  Moonlight ... private build with hardcoded creds. Never pushed to git.
""",
}


def quantum_help(topic=None):
    try:
        if not topic:
            return QUANTUM_DOCS["index"]
        t = str(topic).lower().strip()
        if t in QUANTUM_DOCS:
            return QUANTUM_DOCS[t]
        hits = [k for k in QUANTUM_DOCS if t in k]
        if hits:
            return QUANTUM_DOCS[hits[0]]
        return "unknown topic. " + QUANTUM_DOCS["index"]
    except Exception:
        return "help unavailable"


def quantum_doc_topics():
    try:
        return sorted(QUANTUM_DOCS.keys())
    except Exception:
        return []


SECTION_DOC_OK = True
