# ICT / SMC Trading Logic — Deep Mining
*Researched 2026-10-11. Practitioner knowledge base, not academic finance. Every concept includes: what it is, why it should work (the mechanism), precise entry rules where they exist, what kills it, and honest verification status.*

**Method:** Summarized from ICT's public teachings, SMC trader communities, open-source TradingView/Pine implementations, and GitHub backtest projects. No pirated mentorship content. Quotes kept minimal.

**Core thesis of ICT/SMC:** Price is not random. Institutional algorithms deliver price to specific levels at specific times, hunting liquidity (retail stop-losses and pending orders) before making directional moves. The retail trader's job is to identify where liquidity sits, wait for it to be taken, then enter in the direction of the real move.

**Honest framing:** This is a *narrative framework* for reading price action. Some components are precisely definable and backtestable (FVGs, killzones, OTE zones). Others are interpretive (reading "intent"). The backtest evidence is thin and mostly informal — flagged throughout.

---

## 1. Market Structure — BOS, ChoCH, MSS

### What it is
The skeleton of all ICT/SMC analysis. Price moves in swings: higher highs (HH), higher lows (HL) = uptrend; lower highs (LH), lower lows (LL) = downtrend.

- **BOS (Break of Structure):** Price breaks a swing in the *direction of the trend*. In an uptrend, price takes out the previous swing high = bullish BOS = trend continuation.
- **ChoCH (Change of Character):** Price breaks a swing *against* the trend. In an uptrend, price takes out the previous swing low = bearish ChoCH = potential reversal starting.
- **MSS (Market Structure Shift):** The ICT 2022 term for ChoCH — same thing, rebranded. A shift signals the first crack in the current trend.

### The logic
Trend continuation vs reversal is the oldest question in trading. BOS/ChoCH gives it a mechanical definition: no opinions, just "did price take out the last swing high or low?" The mechanism is order flow — a BOS means buyers absorbed all selling at the old high; a ChoCH means sellers overwhelmed buyers at the old low.

### Entry rules (as precise as they get)
1. Identify the last two swings on your timeframe.
2. Wait for a candle *body close* beyond the swing (wicks don't count for most practitioners).
3. BOS = continue trading with trend. ChoCH/MSS = start looking for reversal entries on lower timeframe.

### What kills it
- Choppy/ranging markets: every tiny swing gets labeled BOS/ChoCH, generating noise. (Common beginner mistake: over-labeling.)
- No universally agreed swing definition — different traders mark different swings, so "structure" is partly subjective.

### Verification status
**Backtestable in principle** (swing detection is algorithmic), but results depend heavily on the swing-detection parameters. No large-scale independent verification found. The concepts are sound as *definitions* — whether they have edge as *signals* is unproven.

---

## 2. Liquidity — BSL, SSL, Sweeps, Turtle Soup

### What it is
The central ICT concept. Everything else orbits it.

- **Buy-Side Liquidity (BSL):** Resting buy-stops sitting *above* old highs, equal highs, trendlines. When price rallies into them,short-sellers' stop-losses trigger as market buy orders. Also: breakout traders' buy-stops.
- **Sell-Side Liquidity (SSL):** Resting sell-stops sitting *below* old lows, equal lows. Longs' stop-losses + breakdown sellers' sell-stops.
- **Liquidity sweep / raid:** Price spikes beyond a swing high/low, triggering those stops, then reverses. The wick that takes out the high/low but closes back inside is the footprint.
- **Turtle Soup:** ICT's name for the sweep-and-reverse pattern (borrowed from Linda Raschke's "Turtle Soup" — fading false breakouts). Specifically: price takes out the prior day's high/low (or Asian range high/low), then reverses.
- **Equal highs/lows (EQH/EQL):** Two or more swing points at the same price. These are the most obvious liquidity pools — every retail trader sees them, places stops just beyond. ICT teaches these get raided *first*.

### The logic (why it should work)
This is the strongest mechanistic claim in ICT. It doesn't require believing in "smart money" as a conspiracy — it's market microstructure:

1. Stop-loss orders are *real* resting liquidity. A cluster of stops above old highs is actual buy-market-orders waiting to trigger.
2. Large players *need* liquidity to fill size without slippage. They cannot buy 10,000 contracts into thin air — they need sellers.
3. Triggering retail stops *creates* that liquidity. The sweep fills institutional orders at good prices.
4. After the sweep, the original reason for the stops is gone (the breakout failed), so price reverses with less opposition.

This is not unique to ICT — it's the same logic behind "stop hunts" in every prop trading book. ICT just built a full framework around it.

### Entry rules
1. Mark obvious liquidity pools: prior day high/low, Asian range high/low, equal highs/lows, weekly highs/lows.
2. Wait for price to wick beyond the pool AND close back inside (the sweep).
3. Enter in the reversal direction on lower-timeframe confirmation (MSS/ChoCH, or directly on the close back inside for aggressive entries).
4. Stop: beyond the sweep extreme (the wick high/low).
5. Target: the opposite liquidity pool.

### What kills it
- **Sweep-and-go:** Sometimes the sweep *is* the real breakout. Price takes out the high and keeps going. Entering the reversal gets run over.
- **Deep sweeps:** In volatile markets (news, crypto), the sweep wick can be enormous, making stops very wide and R:R unworkable.
- **No sweep:** On strong trend days, price never sweeps — it just goes. Waiting for a sweep means missing the move entirely.

### Verification status
**Partially verified.** The existence of stop-hunting is well-documented in market microstructure literature. One open-source SMC backtest (CISD model on BTC/ETH/SOL) reported profit factor 1.38–1.51 using sweep → retest logic. But the *specific* ICT claim — that sweeps reliably precede reversals at a tradeable frequency — has no large-scale independent verification. The bytwork.com breaker-block backtest (100 setups, 43% win rate, +47% at 1:2 R:R) is the most specific public test found, but it's from a commercial site selling the methodology.

---

## 3. Order Blocks (OB)

### What it is
The last opposing candle before a strong displacement move. In precise terms:

- **Bullish OB:** The last *bearish* candle before price displaces upward (breaks structure to the upside). The zone = that candle's high to low (some use open-to-low, or wick-to-wick — see variations below).
- **Bearish OB:** The last *bullish* candle before price displaces downward.

The claim: this candle marks where institutional orders were placed. When price returns to the zone, those institutions defend it (adding to positions) or take profit, causing a reaction.

### Variations (the "block family")
- **Breaker Block:** A failed order block. Price was supposed to hold at a bullish OB, but swept through it (took out its low). The broken OB *flips polarity* — the old bullish OB becomes a bearish breaker block (resistance). Entry: short the retest of the breaker.
- **Mitigation Block:** An order block that price has partially entered but not fully broken. The "mitigation" is price filling the remaining institutional orders before reversing. Weaker signal than a fresh OB.
- **Rejection Block:** A single candle with a long wick rejecting a level — a more aggressive, less confirmed version of an OB.
- **Propulsion Block:** A strong continuation candle *after* the OB holds — confirms institutional interest, used as an add-on entry.

### The logic
If large players really do accumulate positions at specific levels, revisiting those levels should show a reaction — either defense (adding) or profit-taking (causing a bounce). This is plausible but *untestable* as stated: you can't see institutional orders on a retail chart. The OB is an *inference* from price action, not a direct observation.

### Entry rules (bullish OB)
1. Identify displacement: a strong move that breaks market structure (BOS).
2. Mark the last bearish candle before the displacement leg started.
3. Zone = candle's low to high (conservative) or open to low (aggressive/refined).
4. Wait for price to retrace into the zone.
5. Enter long on touch (aggressive) or on lower-timeframe confirmation (conservative: bullish MSS/ChoCH inside the zone).
6. Stop: below the OB low (plus buffer for spread).
7. Target: opposing liquidity (next swing high, BSL pool).

### What kills it
- **OB violation without reversal:** Price slices through the OB and keeps going. The "institutional defense" doesn't materialize. This is extremely common in strong trends — every pullback OB gets violated.
- **Too many OBs:** Every displacement creates an OB. On lower timeframes, charts become wallpapered with overlapping zones. Practitioners filter by: only the *most recent* OB, only OBs in premium/discount, only OBs with FVG confluence.
- **Subjectivity:** Which candle is "the last opposing candle"? If there are three bearish candles before displacement, is it the last one? The one with the biggest range? Different answers = different zones.

### Verification status
**Weak.** The FvgGold EA (open-source, MIT) backtested FVG + OB on XAUUSD M15: 45% win rate, +48.7% over 6 months, 64 trades. That's a real number but a small sample. No large-scale independent verification of OBs as standalone entries. The concept is *reasonable* as a refined support/resistance zone, but the "institutional footprint" narrative is unprovable.

---

## 4. Fair Value Gaps (FVG) — Imbalances

### What it is
A 3-candle pattern where price moves so fast that a gap is left:
- **Bullish FVG:** Candle 1 high < Candle 3 low. The zone between them is the gap — price traded *through* it without filling all orders.
- **Bearish FVG:** Candle 1 low > Candle 3 high.

The claim: the market is "inefficient" here and will return to "rebalance" — fill the gap — before continuing.

### Precise identification
1. Three consecutive candles.
2. Middle candle is a displacement candle (large range, strong close).
3. The wick of candle 1 and the wick of candle 3 do not overlap.
4. The non-overlapping zone = the FVG.

Some practitioners require the middle candle's *body* to fully clear the zone (stronger signal). Others accept any non-overlap.

**Consequent Encroachment (CE):** The 50% midpoint of the FVG. ICT teaches this as the highest-probability fill level — price often taps CE and reverses without filling the entire gap.

### The logic
In auction market theory, single prints (gaps) are areas where one side was completely dominant. The market *tends* to revisit these areas because: (a) resting limit orders were left unfilled, and (b) the move was emotional — mean reversion pulls price back. This is more defensible than the OB narrative because it's about *observable* order-book mechanics, not inferred institutional intent.

### Entry rules (bullish FVG)
1. Displacement creates a bullish FVG.
2. Wait for price to retrace into the FVG zone (aggressive: full zone; refined: CE / 50% level).
3. Enter long.
4. Stop: below the FVG low.
5. Target: opposing liquidity or 1:2+ R:R.

### IFVG — Inversion Fair Value Gap ("the inverted blah blah")
When price *fails* to respect an FVG and closes through it, the gap inverts:
- A **bullish FVG** that price closes *below* becomes a **bearish IFVG** (resistance).
- A **bearish FVG** that price closes *above* becomes a **bullish IFVG** (support).

**The rule:** It must be a *candle body close* through the FVG, not just a wick pierce. The wick piercing and returning = the FVG held. The body closing through = inversion.

**Entry:** Trade the retest of the inverted zone in the new direction. This is one of ICT's highest-conviction patterns because it represents a *failed* expectation — everyone who entered on the original FVG is now trapped, and their exits fuel the new move.

**Why it matters for the user's question:** The IFVG is the "inverted" concept they mentioned. It's the pattern of a pattern failing — meta-level price action.

### What kills FVGs
- **FVGs in strong trends don't fill:** In a rip-your-face-off trend, price leaves FVGs behind and never looks back. Waiting for a fill means missing the move.
- **FVG stacking:** Multiple overlapping FVGs create wide zones with no precise entry.
- **Time decay:** An FVG from 3 days ago is less relevant than one from 3 hours ago. Most practitioners only trade *fresh* FVGs.

### Verification status
**Best-verified ICT concept.** The FvgGold EA: 45% WR, +48.7%, 64 trades on XAUUSD. The SMC Pro BTC indicator (TradingView): 45.56% WR, profit factor 1.95, +14.36% over 5 years on BTC. Multiple open-source implementations exist. Still small samples, but FVGs are the most *mechanically precise* ICT concept — the definition is algorithmic, not interpretive.

---

## 5. Premium / Discount & Dealing Ranges

### What it is
A framework for *where* in a range to trade:
1. Mark the dealing range: swing high to swing low (of the relevant HTF leg).
2. **Equilibrium (EQ)** = 50% midpoint.
3. **Premium** = upper half (above EQ). **Discount** = lower half (below EQ).
4. Rule: *Buy in discount, sell in premium.* Never buy in premium, never sell in discount.

### The logic
This is just disciplined mean-reversion framing: don't chase. If you're bullish, wait for price to come to *you* (discount) rather than buying the top (premium). It prevents the most common retail mistake — buying highs and selling lows.

### Entry rules
Combine with any other ICT entry (OB, FVG, OTE): only take longs when price is in discount, only shorts when in premium. If price is at equilibrium, wait.

### What kills it
- In a strong trend, price can stay in premium (uptrend) or discount (downtrend) for a long time. Waiting for discount in a moonshot means never entering.

### Verification status
**Unverifiable as a standalone edge** — it's a filter, not a signal. But as a discipline tool (don't chase), it's sound.

---

## 6. OTE — Optimal Trade Entry

### What it is
ICT's canonical entry zone: the **0.62–0.79 Fibonacci retracement** of a clean impulse leg, with **0.705 as the optimal midpoint**.

Note: these are *not* standard Fib levels. ICT uses 0.62 (not 0.618), 0.705 (not a standard level at all — it's the midpoint of the OTE zone), and 0.79 (not 0.786). The projection levels are -1.5, -2.0, -2.5, -4.0.

### Precise rules
1. Identify a clean impulse leg (displacement that broke structure).
2. Draw Fib from leg start to leg end.
3. OTE zone = 0.62 to 0.79 retracement.
4. Look for PD-array confluence (FVG, OB) *within* the OTE zone.
5. Enter at 0.705 (optimal) or 0.62 (shallow, wider stop) or 0.79 (deep, tighter stop).
6. **Invalidation:** Beyond 0.79. If price retraces deeper than 79%, the OTE has failed — the leg wasn't an impulse, it was something else.
7. Targets: -1.5, -2.0 for conservative; -2.5, -4.0 for runners.

### The logic
Deeper retracements offer better R:R (tighter stop relative to target) but lower fill probability. The 0.62–0.79 zone is the sweet spot where you're getting meaningful discount without betting on a full reversal. The 0.705 midpoint balances fill rate vs R:R.

### What kills it
- **Shallow pullbacks:** In strong trends, price retraces 30–40% and goes. OTE never fills.
- **Deep pullbacks past 0.79:** The setup is invalidated, but price often reverses *right after* stopping out OTE traders. This is itself a liquidity event.

### Verification status
**Backtestable** (pure math — no subjectivity in the zone calculation). No large-scale independent backtest found in research. The *zone* is precise; whether entries *within* the zone have edge depends on the confluence filter.

---

## 7. Power of 3 — Accumulation, Manipulation, Distribution (AMD)

### What it is
ICT's daily template. Every trading day has three phases:
1. **Accumulation:** Ranging market (often Asian session). Builds liquidity on both sides — longs and shorts both enter, placing stops above/below the range.
2. **Manipulation:** A false move in one direction (often London open). Takes out one side's stops. This is NOT the real direction — it's the liquidity grab. Also called the **Judas Swing**.
3. **Distribution:** The real move in the opposite direction of the manipulation (often New York session). Distributes price to the true objective.

### The logic
This is the Power of 3 applied to the daily cycle: range → stop-hunt → trend. The mechanism is the same as the liquidity sweep (Section 2), just framed as a daily rhythm. Asian range builds the liquidity pools; London takes one side; New York delivers to the other side.

**Why sessions matter (not just "when"):** Different participants dominate different sessions. Asian session = lower volume, algorithmic ranging. London open = European bank desks coming online, real order flow begins. New York open = US institutional flow + London overlap = maximum liquidity. The *reason* manipulation happens at London open is that's when enough volume exists to absorb the sweep.

### Entry rules (two approaches)
**Aggressive (manipulation fade):**
1. Mark Asian range high/low.
2. Wait for London to spike beyond one side and close back inside.
3. Enter in the opposite direction immediately on the close back inside (or on LTF ChoCH).
4. Stop: beyond the manipulation wick.

**Conservative (distribution entry):**
1. Wait for manipulation to complete AND distribution to begin (MSS on LTF confirming new direction).
2. Enter on pullback to OB/FVG in the distribution direction.
3. Target: opposite side liquidity.

### What kills it
- **Trend days:** Some days skip manipulation entirely — price just trends from Asian open. The AMD template doesn't apply.
- **Double manipulation:** Price sweeps *both* sides (takes out Asian high AND low) before choosing a direction. Both aggressive entries get stopped.
- **News days:** NFP, FOMC, CPI — the "manipulation" is actually the real move on news repricing.

### Verification status
**Lore-heavy, thin verification.** The pattern is recognizable on charts (every trader has seen it), but no rigorous statistical test of "how often does London sweep Asian range then reverse to the other side" was found. The proea.app source documented a precise AMD detection rule but noted "we haven't tested this as a trading rule." This is the highest-conviction *narrative* in ICT with the least *evidence*.

---

## 8. Killzones — Time Windows

### What it is
Specific hours when ICT teaches that institutional activity concentrates:

| Killzone | NY Time (ET) | UTC | Character |
|---|---|---|---|
| Asian KZ | 7:00–9:00 PM | 00:00–02:00 | Range-building, liquidity accumulation |
| London KZ | 2:00–5:00 AM | 07:00–10:00 | European desks online, manipulation common |
| NY AM KZ | 7:00–10:00 AM | 12:00–15:00 | London-NY overlap, highest volume |
| London Close KZ | 11:00 AM–1:00 PM | 15:00–17:00 | Position squaring, reversals |

**Macros** (finer subdivision): 20-minute windows within killzones of peak algorithmic activity — e.g., 8:20–8:30, 9:50–10:10, 10:50–11:10 AM EST.

### The logic
This is the most *empirically grounded* ICT concept. It's not mystical — it's just market microstructure:
- Volume is U-shaped intraday (high at open, low midday, high at close).
- FX volume peaks at London-NY overlap (verified by BIS triennial surveys).
- Scheduled economic releases cluster at specific times (8:30 AM EST for US data).
- Institutional execution algorithms (VWAP, TWAP) concentrate at opens.

Trading during killzones = trading when volume exists to support your thesis. Trading outside them = thin markets, wider spreads, more noise.

### Entry rules
Not a standalone signal — a *filter*. Only take ICT setups (sweeps, FVGs, OTEs) that trigger inside killzone hours. Skip everything else.

### What kills it
- Nothing — it's a filter, not a prediction. But over-restricting to killzones means fewer trades, which can hurt if your edge needs frequency.

### Verification status
**Strongest empirical support of any ICT concept.** Intraday volume patterns are among the most replicated findings in market microstructure. The *specific* ICT killzone hours align with known volume peaks. Whether restricting entries to killzones improves ICT setups specifically is untested, but the volume logic is sound.

---

## 9. Silver Bullet — The Time-Window Model

### What it is
ICT's flagship "trade one hour a day" model. Three specific 1-hour windows:

| Window | NY Time | Focus |
|---|---|---|
| London SB | 3:00–4:00 AM | European sweep |
| NY AM SB | 10:00–11:00 AM | Highest probability (London-NY overlap + NYSE open) |
| NY PM SB | 2:00–3:00 PM | Afternoon continuation |

### Precise entry sequence
1. **Window opens** (e.g., 10:00 AM EST).
2. **Liquidity sweep:** Price wicks beyond a recent swing high/low and closes back inside.
3. **Displacement:** Strong directional candle (body > 50% of ATR on some implementations).
4. **FVG forms** on the displacement leg.
5. **MSS/ChoCH** on 1–3 minute timeframe confirms the shift.
6. **Enter** on retracement into the FVG.
7. **Stop:** Beyond the FVG extreme (or beyond the sweep wick).
8. **Target:** Opposing liquidity pool. Minimum 1:2 R:R. Some versions use fixed targets (5 handles on indices, 20–30 pips on FX).
9. **Time stop:** Close all positions at 11:15 AM EST regardless.

### The logic
Combines everything: killzone timing (peak volume) + liquidity sweep (fuel) + displacement (institutional commitment) + FVG (precise entry). The time restriction is the key insight — by only trading one hour, you eliminate 90% of chop and only play when conditions are best.

### Claimed performance
ICT and followers claim 70–81% win rates for the NY AM window. **Treat with extreme skepticism** — no independently audited track record exists. One open-source implementation (auto-ict on GitHub) codes the full sequence with causal ordering checks (sweep → ChoCH → FVG must occur in sequence).

### What kills it
- **No setup in the window:** Many days produce no valid sequence in the 1-hour window. Discipline means taking zero trades.
- **Sweep-and-go:** The sweep becomes the real move, no FVG retracement offered.
- **Overfitting to the window:** The 10:00–11:00 AM specificity may be curve-fit to historical data.

### Verification status
**Unverified claims, verifiable rules.** The entry sequence is precise enough to code and backtest (several GitHub projects have done so). The 70%+ win rate claims are *not* independently verified. This is the most *testable* ICT model — and the most important one to actually backtest before trusting.

---

## 10. ICT 2022 Model — The Full Framework

### What it is
The comprehensive model from ICT's 2022 mentorship, combining all concepts into one sequence:

1. **HTF bias:** Daily/4H market structure → bullish or bearish.
2. **Draw on liquidity (DOL):** Identify where price is *going* (the target liquidity pool).
3. **Liquidity raid:** Wait for price to sweep the near-side liquidity (opposite to DOL direction).
4. **Displacement + MSS:** Strong move + market structure shift on LTF.
5. **FVG entry:** Enter on retracement into the FVG.
6. **Stop:** Beyond the sweep extreme.
7. **Target:** The DOL (draw on liquidity).

### The logic
This is the "everything" model — it chains liquidity → sweep → displacement → FVG → entry into one causal narrative. The key addition over Silver Bullet is the **DOL concept**: always know where price is going *before* you enter. You're not just buying a bounce — you're buying a bounce that's *going somewhere specific*.

### Verification status
**Lore.** The sequence is logical and each component is individually definable, but the full 7-step model as a *system* has no published backtest. The auto-ict GitHub project implements it (`ict_2022.py`) with minimum 1:3 R:R.

---

## 11. Risk Management — How ICT Traders Actually Size

Unlike the academic literature (Kelly criterion, etc.), ICT risk management is practitioner-simple:

1. **Fixed fractional risk:** 1–2% per trade is standard. Some aggressive traders go to 3%. No Kelly, no dynamic sizing based on edge — just fixed %.
2. **Daily loss limit:** 2–3% max daily loss, then *stop trading*. This is the most important rule — it prevents revenge trading.
3. **Partial profits:** Common approach: take 50% at 1:2 R:R, move stop to breakeven, let the rest run to opposing liquidity. This creates the "never lose" psychology (breakeven stops) but *mathematically* reduces expectancy if winners are cut short.
4. **No averaging down:** Adding to losers is forbidden. Adding to winners (scaling in on pullbacks) is allowed.
5. **Session limits:** Some traders limit to 1–2 trades per killzone. If stopped twice, done for the session.

### Honest assessment
This is *sound* but *generic*. There's nothing ICT-specific about 2% risk and daily loss limits — it's standard professional practice. The valuable ICT-specific insight is the **time stop** (close everything at end of killzone) and the **invalidation-based stops** (stop beyond the sweep extreme = the thesis is wrong, not an arbitrary distance).

---

## 12. Backtest Evidence — Honest Summary

| Source | What was tested | Result | Sample | Credibility |
|---|---|---|---|---|
| FvgGold EA (open-source, MIT) | FVG + OB on XAUUSD M15 | 45% WR, +48.7%, 64 trades, 6 months | Small | Medium — real code, real backtest, small sample |
| SMC Pro BTC (TradingView) | OB + FVG + sweep on BTC | 45.56% WR, PF 1.95, +14.36%, 5 years, 90 trades | Medium | Medium — includes costs, but commercial product |
| CISD model (m0nx73r/backtest) | Sweep → retest on BTC/ETH/SOL | PF 1.38–1.51, ~42% WR, 800+ trades each | Large | Medium-high — open source, multi-asset |
| Breaker blocks (bytwork.com) | 100 BB setups, 1H, 1:2 R:R | 43% WR, +47%, max DD -10% | Small | Low-medium — commercial site |
| Micro-futures analyzer | ICT signals on MNQ/MES | 61–75% WR, PF 1.36–3.8 | Small-medium | Low-medium — developer's own project |
| Silver Bullet 70%+ WR claims | NY AM window | 70–81% claimed | Unknown | **Low — no audited track record** |

### The pattern
Win rates cluster around **42–46%** with profit factors of **1.4–2.0**. This is the *realistic* ICT performance envelope — not the 70–80% claimed by marketers. At 45% WR and 1:2 R:R, expectancy is positive but modest: (0.45 × 2) − (0.55 × 1) = +0.35R per trade. That's tradeable but not life-changing, and it's *before* accounting for the discipline required to execute perfectly.

### What's NOT verified
- The 70–81% Silver Bullet win rates (no audited data)
- Power of 3 as a *predictive* daily template (recognizable in hindsight, untested as a forecast)
- The "smart money" narrative itself (untestable by definition)
- Any ICT concept on timeframes below M5 (spread kills it)

---

## 13. What's Real vs What's Lore

### Real (mechanically sound, definable, testable)
- **FVGs** — precise 3-candle definition, backtested, most credible concept
- **Liquidity sweeps** — grounded in market microstructure, stop-hunting is real
- **Killzones** — volume patterns are empirically verified
- **OTE zones** — pure math, precise levels
- **Premium/discount** — sound discipline framework
- **Risk management** — standard professional practice

### Plausible but unproven
- **Order blocks** — reasonable as refined S/R, "institutional footprint" narrative unprovable
- **IFVG** — logical (failed pattern = trapped traders), but thin backtest data
- **Breaker blocks** — same as OBs, one small backtest
- **Silver Bullet** — precise enough to test, win rate claims unverified

### Lore (narrative without evidence)
- **Power of 3 as prediction** — great story, no statistical test
- **"Smart money" as identifiable actors** — untestable; use "order flow" instead
- **70%+ win rates** — marketing, not data
- **Specific macro windows** (8:20–8:30 etc.) — likely overfit

---

## Bottom Line for Building

If building ICT/SMC logic into a trading system:

1. **Start with FVGs** — most precise, most backtested, least subjective.
2. **Add liquidity sweep filter** — only take FVGs that form after a sweep.
3. **Add killzone filter** — only trade during London/NY hours.
4. **Use OTE for entry refinement** — enter at 0.705 within FVG, not at the edge.
5. **Size with invalidation stops** — stop beyond the sweep extreme, not arbitrary ATR multiples.
6. **Don't trust the narrative** — code the mechanics, ignore the "smart money" story. The patterns either have statistical edge or they don't; the story doesn't matter.

The 120 Sentinel strategies failed because they were parameter variations of generic templates. ICT/SMC concepts are *different* — they're specific microstructural patterns. Whether they have edge is an empirical question that can actually be tested, because the definitions are precise enough to code.
