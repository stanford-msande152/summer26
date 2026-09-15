# coding: utf-8
"""
Sensitivity of the recommendation to the flat value of attending.

The model carries a single v and applies it at every round, so a group-stage
match and the Final are worth the same to the fan if he is in the stadium.
Section 4 of the report calls that the largest simplification in the value
function, and says what it would take to matter was tested rather than assumed.
This is that test.

Five schemes for how the worth of attending round k might vary with k:

    flat          v_k = v                      the model as submitted
    price         v_k = v * B_nr(k) / B_nr(6)  an early round is worth what an
                                               early trip costs
    linear        v_k = v * (k/6)
    squared       v_k = v * (k/6)^2            values a group-stage match at $315
    cubed         v_k = v * (k/6)^3

For each scheme every one of the twelve team-rounds is re-solved and the
recommended alternative compared against the flat baseline. Writes
sensitivity_output.txt.

Run after analyse.py, from this folder:  python3 sensitivity_v_scaling.py
"""
import os as _os, sys as _sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
_sys.path.insert(0, _HERE)
def _here(name): return _os.path.join(_HERE, name)

import json
import inputs

ROWS = json.load(open(_here("model_results.json")))
V = inputs.V
BNR_FINAL = 5511.01          # the Final bundle, the reference the price scheme scales to


# ---------------------------------------------------------------- the schemes
SCHEMES = [
    ("flat",     lambda d: V),
    ("price",    lambda d: V * d["Bnr"] / BNR_FINAL),
    ("linear",   lambda d: V * (d["k"] / 6.0)),
    ("squared",  lambda d: V * (d["k"] / 6.0) ** 2),
    ("cubed",    lambda d: V * (d["k"] / 6.0) ** 3),
]


def solve(d, v):
    """The four alternatives at one team-round, at a given worth of attending.

    Identical arithmetic to analyse.py; only v varies. The refundable arm is
    dropped where no refundable product exists, which is where B_rf equals B_nr.
    """
    P = d["P"]
    nr = P * (v - d["Bnr"]) + (1 - P) * (-(1 - d["r"]) * d["Bnr"])
    rf = P * (v - d["Brf"]) + (1 - P) * (-d["f"])
    wt = P * ((1 - d["q"]) * (v - d["Blate"]))
    alts = [("Book non-refundable", nr),
            ("Book refundable", rf if d["Brf"] > d["Bnr"] else None),
            ("Wait", wt),
            ("Stay home", 0.0)]
    alts = [(n, x) for n, x in alts if x is not None]
    alts.sort(key=lambda t: -t[1])
    return alts[0][0], alts[0][1], alts[0][1] - alts[1][1]


# ---------------------------------------------------------------- the report
lines = []
def say(s=""):
    print(s)
    lines.append(s)


say("SENSITIVITY OF THE RECOMMENDATION TO A ROUND-VARYING VALUE OF ATTENDING")
say()
say(f"Base value of attending, v = ${V:,.0f}, applied flat at every round in the")
say("submitted model. Each scheme below replaces that with a v_k that grows")
say("with the round, then re-solves all twelve team-rounds.")
say()

base = {}
for name, f in SCHEMES:
    say(f"--- {name} " + "-" * (66 - len(name)))
    say(f"  {'team':7}{'k':>2}  {'stage':15}{'v_k':>11}  {'recommended':22}{'margin':>10}   change")
    changed = stayhome = 0
    for d in ROWS:
        v = f(d)
        best, bv, margin = solve(d, v)
        if name == "flat":
            base[(d["team"], d["k"])] = best
            flag = ""
        else:
            flag = "" if best == base[(d["team"], d["k"])] else "CHANGED"
            if flag:
                changed += 1
                if best == "Stay home":
                    stayhome += 1
        say(f"  {d['team']:7}{d['k']:>2}  {d['stage'][:14]:15}{v:>11,.2f}  {best:22}{margin:>10.2f}   {flag}")
    if name == "flat":
        say("  baseline")
    else:
        say(f"  {changed} of 12 rounds change recommendation; "
            f"{stayhome} of those become Stay home")
    say()

say("=" * 74)
say("READING")
say()
say("Scaling v in proportion to the round's own bundle price changes nothing:")
say("all twelve rounds keep the recommendation the flat model gives. Linear")
say("scaling is also harmless. The recommendation only starts to move when the")
say("early rounds are discounted very steeply. At (k/6)^2, which values a")
say("group-stage match at $315, three rounds become Stay home; at (k/6)^3, four")
say("do. One further round changes at (k/6)^2, Norway's Round of 16, and it")
say("changes to Wait by $4.33, which is a tie rather than a finding.")
say()
say("So the flat v is safe unless the fan values an early-round trip at a small")
say("fraction of a Final, and if he does, the consequence is that he should not")
say("travel to those rounds at all rather than that he should book them")
say("differently. No scheme moves the Final, which is the round the report's")
say("headline figures are drawn from.")

open(_here("sensitivity_output.txt"), "w").write("\n".join(lines) + "\n")
print("\nwrote", _here("sensitivity_output.txt"))
