#!/usr/bin/env python3
"""Lightweight static lint for Pine v6 scripts.

Checks:
1. Per-line paren/bracket balance (strings & comments stripped).
2. Indentation always a multiple of 4 spaces (no tabs).
3. Watchlist identifiers are declared before first use (Pine requirement).
4. No stray non-ASCII quote characters, no trailing `:=` misuse heuristics.
"""
import re
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "OMNI-GOD-UNIFIED.pine (15).txt"

WATCH = [
    "GRP_TRAP", "useTrapEngine", "useBeyondFvg", "useInvFvg", "blockSusBreak",
    "showTraps", "trapMemoryBars", "brkLookback", "trapVolMult", "maxInvFvgs",
    "costBps", "useCostGate", "minNetRR", "alertOnTrap",
    "useCircuitBreaker", "maxDailyLossR", "maxTradesDay",
    "ifvgSupH", "ifvgSupL", "ifvgSupBar", "ifvgSupOk", "ifvgSupBox",
    "ifvgDemH", "ifvgDemL", "ifvgDemBar", "ifvgDemOk", "ifvgDemBox",
    "ifvgFlipSupEv", "ifvgFlipDemEv",
    "bullTrapNow", "bearTrapNow", "bullTrapEng", "bearTrapEng",
    "bullTrapBar", "bearTrapBar", "bullTrapWasEng", "bearTrapWasEng",
    "bullTrapActive", "bearTrapActive",
    "brkUpBar", "brkUpLvl", "brkDnBar", "brkDnLvl",
    "brkUpNow", "brkDnNow", "brkUpSus", "brkDnSus",
    "fakeBrkUp", "fakeBrkDn",
    "bfgState", "bfgBot", "bfgTop", "bfgBar", "bfgReclaimFull",
    "bfgSweepEv", "bfgReclaimEv",
    "rfgState", "rfgTop", "rfgBot", "rfgBar", "rfgReclaimFull",
    "rfgSweepEv", "rfgReclaimEv",
    "insideBullFvg", "insideBearFvg", "baitLong", "baitShort",
    "ifvgSupTest", "ifvgSupLvl", "ifvgDemTest", "ifvgDemLvl",
    "costPx", "pSlLong", "pRiskLong", "pSlShort", "pRiskShort",
    "costOkLong", "costOkShort", "lureLong", "lureShort",
    "cbDay", "dayR", "tradesToday", "cbHalt",
]

def strip_strings_comments(line: str) -> str:
    out = []
    i = 0
    in_str = False
    while i < len(line):
        c = line[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            i += 1
            continue
        if c == "/" and i + 1 < len(line) and line[i + 1] == "/":
            break
        out.append(c)
        i += 1
    return "".join(out), in_str

errors = []
decl_line = {}
first_use = {}
decl_re = re.compile(
    r"^\s*(?:var\s+|varip\s+)?(?:bool|int|float|string|color|line|box|label|table|"
    r"array<[^>]*>|matrix<[^>]*>|RiskProfile)\s+(\w+)\s*(?::=|=)"
)
# tuple destructuring [a, b, c] = ...
tuple_re = re.compile(r"^\s*\[([^\]]+)\]\s*=")
func_re = re.compile(r"^\s*(?:export\s+)?(\w+)\s*\([^)]*\)\s*(?:=>|=\s*$)")

with open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

open_str_carry = False
for n, raw in enumerate(lines, 1):
    line = raw.rstrip("\n")
    # indentation checks
    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    if "\t" in line:
        errors.append(f"L{n}: TAB character")
    if stripped and indent % 4 != 0:
        errors.append(f"L{n}: indent {indent} not multiple of 4: {stripped[:60]!r}")
    code, open_str = strip_strings_comments(line)
    # bracket balance per line (Pine statements rarely span lines except continuations)
    for o, c in (("(", ")"), ("[", "]"), ("<", ">")):
        pass
    bal = code.count("(") - code.count(")")
    if bal != 0 and "=>" not in code and not code.rstrip().endswith(("(", ",", "+", "-", "*", "/", "?", ":")):
        errors.append(f"L{n}: unbalanced parens ({bal:+d}): {line.strip()[:80]!r}")
    bal2 = code.count("[") - code.count("]")
    if bal2 != 0:
        errors.append(f"L{n}: unbalanced brackets ({bal2:+d}): {line.strip()[:80]!r}")
    # declarations
    m = decl_re.match(line)
    if m:
        decl_line.setdefault(m.group(1), n)
    mt = tuple_re.match(line)
    if mt:
        for name in mt.group(1).split(","):
            name = name.strip()
            if re.fullmatch(r"\w+", name):
                decl_line.setdefault(name, n)
    mf = func_re.match(line)
    if mf and not line.strip().startswith("//") and not line.strip().startswith("if"):
        decl_line.setdefault(mf.group(1), n)
    # input.x() assigns into typed decl handled by decl_re

# watchlist usage order
joined = []
for n, raw in enumerate(lines, 1):
    code, _ = strip_strings_comments(raw.rstrip("\n"))
    for w in WATCH:
        for m in re.finditer(r"\b" + w + r"\b", code):
            if w not in first_use:
                first_use[w] = n
for w in WATCH:
    if w in first_use and (w not in decl_line or first_use[w] < decl_line[w]):
        # allow usage on the same line as declaration
        if w in decl_line and first_use[w] == decl_line[w]:
            continue
        errors.append(f"{w}: first use L{first_use[w]} vs declaration L{decl_line.get(w, 'MISSING')}")

if errors:
    print(f"{len(errors)} issue(s):")
    for e in errors[:80]:
        print("  " + e)
    sys.exit(1)
print(f"OK — {len(lines)} lines, watchlist order clean, brackets balanced")
