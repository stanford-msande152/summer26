# coding: utf-8
"""
Hindsight validation. Everything in this file uses knowledge of how the 2026
tournament actually finished, and none of it feeds back into the model. It
exists to answer two questions a reader is entitled to ask.

  1. Was the forecast any good?  Brier score of the pre-tournament conditional
     advancement probabilities against what happened, for Spain, for Norway,
     and across all 108 (team, round) transitions of the tournament. Scored
     the way the course's Brier tool scores a probability forecast:
     https://stanford-msande152.github.io/summer26/sw/brier/

  2. Was the recommended policy any good?  What each fixed strategy would in
     fact have cost or returned along the two bracket paths, against what the
     model recommended before any ball was kicked.

Actual results: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage
"""
import csv, json, sys
import os as _os, sys as _sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
_sys.path.insert(0, _HERE)
def _here(name): return _os.path.join(_HERE, name)

class _Tee:
    """Mirror stdout to hindsight_output.txt, so the transcript the README names is produced."""
    def __init__(self, path):
        self._fh = open(path, "w", encoding="utf-8")
        import atexit; atexit.register(self.close)
    def write(self, s):
        _sys.__stdout__.write(s)
        if not self._fh.closed: self._fh.write(s)
    def flush(self):
        _sys.__stdout__.flush()
        if not self._fh.closed: self._fh.flush()
    def close(self):
        try:
            if not self._fh.closed: self._fh.flush(); self._fh.close()
        except Exception: pass
    def __getattr__(self, k): return getattr(_sys.__stdout__, k)

_sys.stdout = _Tee(_here("hindsight_output.txt"))

import inputs

ROWS = json.load(open(_here("model_results.json")))
SENS, SPEC = inputs.FORECAST_SENS, inputs.FORECAST_SPEC
V = inputs.V

# ------------------------------------------------------------------ outcomes
# k: 1 group stage, 2 R32, 3 R16, 4 QF, 5 SF, 6 final.  True = the team played
# that round.  Spain won the tournament; Norway lost the quarter-final 1-2
# after extra time to England on 11 July.
REACHED = {
    "Spain":  {1: True, 2: True, 3: True, 4: True, 5: True,  6: True},
    "Norway": {1: True, 2: True, 3: True, 4: True, 5: False, 6: False},
}

STAGE = {1: "Group stage", 2: "Round of 32", 3: "Round of 16",
         4: "Quarter-final", 5: "Semi-final", 6: "Final"}


def brier(pairs):
    """Mean squared error of a probability forecast. pairs = [(p, outcome)]."""
    return sum((p - (1.0 if o else 0.0)) ** 2 for p, o in pairs) / len(pairs)


print("=" * 74)
print("1. WAS THE FORECAST ANY GOOD?")
print("=" * 74)
print("\n   (a) the two bracket paths in the report, round by round")
print("   %-7s %-3s %-14s %8s %10s %10s" %
      ("team", "k", "stage", "p", "happened", "sq error"))
path_pairs = {}
for team in ("Spain", "Norway"):
    a = inputs.advancement(team)
    pairs = []
    for k in range(2, 7):                      # k=1 is certain, not a forecast
        if not REACHED[team][k - 1]:
            break                              # nothing left to forecast
        o = REACHED[team][k]
        pairs.append((a[k], o))
        print("   %-7s %-3d %-14s %8.4f %10s %10.4f"
              % (team, k, STAGE[k], a[k], "yes" if o else "no",
                 (a[k] - (1.0 if o else 0.0)) ** 2))
    path_pairs[team] = pairs
    print("   %-7s %s Brier = %.4f over %d live rounds\n"
          % (team, " " * 34, brier(pairs), len(pairs)))

both = path_pairs["Spain"] + path_pairs["Norway"]
print("   both paths together: Brier = %.4f over %d rounds" % (brier(both), len(both)))

# ------------------------------------------------------- the whole tournament
rows = list(csv.DictReader(open(_here("advance_data_audit.csv"))))
allp = [(float(r["p_advance_conditional"]), r["advanced"] == "yes") for r in rows]
base = sum(1 for _, o in allp if o) / len(allp)
bs = brier(allp)
bs_ref = brier([(base, o) for _, o in allp])
bs_coin = brier([(0.5, o) for _, o in allp])
print("\n   (b) every knockout transition in the tournament, all 48 teams")
print("       %-46s %8s" % ("forecast", "Brier"))
print("       %-46s %8.4f" % ("Groll/Zeileis conditional probability", bs))
print("       %-46s %8.4f" % ("base rate alone (%.4f every time)" % base, bs_ref))
print("       %-46s %8.4f" % ("a coin (0.5000 every time)", bs_coin))
print("       skill score against the base rate  = %.4f" % (1 - bs / bs_ref))
print("       skill score against a coin         = %.4f" % (1 - bs / bs_coin))
print("       n = %d transitions, %d of which the team survived" %
      (len(allp), sum(1 for _, o in allp if o)))

# ------------------------------------------------------------------ 2. policy
print("\n" + "=" * 74)
print("2. WAS THE RECOMMENDED POLICY ANY GOOD?")
print("=" * 74)
print("\n   Money is what the fan actually pays or receives, at the base value of")
print("   the trip, v = $%s, and the scheduled city for each round." % format(V, ",.0f"))
print("   The wait arm is shown at its expected value, because whether a late")
print("   ticket was still on sale is not recoverable after the fact.")


def realised(d, arm, reached):
    """What arm `arm` actually pays in round k, given what happened."""
    if arm == "Stay home":
        return 0.0
    if arm == "Book non-refundable":
        return (V - d["Bnr"]) if reached else -(1 - d["r"]) * d["Bnr"]
    if arm == "Book refundable":
        return (V - d["Brf"]) if reached else -d["f"]
    # wait: buy late only if the team qualifies and something is left
    return (1 - d["q"]) * max(V - d["Blate"], 0.0) if reached else 0.0


def posterior(prior, signal):
    ly = SENS if signal == "Says_advance" else 1 - SENS
    ln = (1 - SPEC) if signal == "Says_advance" else SPEC
    return prior * ly / (prior * ly + (1 - prior) * ln)


ARMS = ["Book non-refundable", "Book refundable", "Wait", "Stay home"]
summary = {}
for team in ("Spain", "Norway"):
    a = inputs.advancement(team)
    print("\n   %s" % team.upper())
    print("   %-3s %-14s %-13s %-13s %-22s %11s" %
          ("k", "stage", "city", "forecast", "model recommends", "realised $"))
    tot = dict((x, 0.0) for x in ARMS)
    tot["model policy"] = 0.0
    alive = True
    for k in range(1, 7):
        d = [x for x in ROWS if x["team"] == team and x["k"] == k][0]
        if not alive:
            print("   %-3d %-14s %-13s %-13s %-22s %11s"
                  % (k, STAGE[k], d["city"], "-", "already eliminated", "0.00"))
            continue
        sig = "Says_advance" if a[k] > 0.5 else "Says_out"
        p = posterior(a[k], sig)
        ev = {}
        for arm in ARMS:
            if arm == "Book non-refundable":
                ev[arm] = p * (V - d["Bnr"]) + (1 - p) * (-(1 - d["r"]) * d["Bnr"])
            elif arm == "Book refundable":
                ev[arm] = (p * (V - d["Brf"]) + (1 - p) * (-d["f"])
                           if d["Brf"] > d["Bnr"] else float("-inf"))
            elif arm == "Wait":
                ev[arm] = p * (1 - d["q"]) * max(V - d["Blate"], 0.0)
            else:
                ev[arm] = 0.0
        best = max(ARMS, key=lambda x: ev[x])
        got = realised(d, best, REACHED[team][k])
        tot["model policy"] += got
        for arm in ARMS:
            tot[arm] += realised(d, arm, REACHED[team][k])
        print("   %-3d %-14s %-13s %-13s %-22s %11.2f"
              % (k, STAGE[k], d["city"],
                 "advance" if sig == "Says_advance" else "out", best, got))
        alive = REACHED[team][k]
    print("   %-3s %-14s %-13s %-13s %-22s %11s"
          % ("", "", "", "", "-" * 22, "-" * 11))
    order = ["model policy"] + ARMS
    for arm in order:
        print("   %-3s %-14s %-13s %-13s %-22s %11.2f"
              % ("", "", "", "", arm + " (whole run)", tot[arm]))
    summary[team] = dict(tot)

print("\n" + "=" * 74)
print("3. SUMMARY")
print("=" * 74)
print("   %-24s %14s %14s" % ("strategy", "Spain path", "Norway path"))
for arm in ["model policy"] + ARMS:
    print("   %-24s %14.2f %14.2f"
          % (arm, summary["Spain"][arm], summary["Norway"][arm]))

json.dump({"brier_all": bs, "brier_base": bs_ref, "brier_coin": bs_coin,
           "base_rate": base, "n": len(allp),
           "brier_spain": brier(path_pairs["Spain"]),
           "brier_norway": brier(path_pairs["Norway"]),
           "realised": summary},
          open(_here("hindsight_results.json"), "w"), indent=2)
print("\nwrote", _here("hindsight_results.json"))
