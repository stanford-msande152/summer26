# coding: utf-8
"""
Independent check of BookNowOrWait_CDN.xdsl.

Nothing here trusts the generator. The file is parsed back off disk and every
number below is read out of the XML.

  1. Structure. Parents exist, the graph is acyclic, every CPT column sums to
     one, every table is exactly the length its parent set implies, and the
     palette follows the lecture's convention.
  2. Per-round agreement with analyse.py, with Benefit_k + Cost_k standing in
     for the old single value node.
  3. The three information regimes of the party problem, computed the same way
     the lecture computes them: no forecast, the imperfect forecast, and the
     clairvoyant. The gap between the first two is the value of the forecast.
  4. Two independent recomputations: an exact joint enumeration of the last
     three rounds, and a Monte Carlo run of the whole tournament.
"""
import itertools, json, random, sys
import xml.etree.ElementTree as ET
import os as _os, sys as _sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
_sys.path.insert(0, _HERE)
def _here(name): return _os.path.join(_HERE, name)

class _Tee:
    """Mirror stdout to verifier_output.txt, so the transcript the README names is produced."""
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

_sys.stdout = _Tee(_here("verifier_output.txt"))

import inputs

XDSL = _here("BookNowOrWait_CDN.xdsl")
root = ET.parse(XDSL).getroot()

S, PAR, TAB, KIND, ORDER = {}, {}, {}, {}, []
for n in root.find("nodes"):
    i = n.get("id")
    ORDER.append(i)
    KIND[i] = n.tag
    S[i] = [s.get("id") for s in n.findall("state")]
    p = n.find("parents")
    PAR[i] = p.text.split() if p is not None else []
    v = n.find("probabilities")
    if v is None:
        v = n.find("utilities")
    if v is not None:
        TAB[i] = [float(x) for x in v.text.split()]

COLOUR = {}
for n in root.find("extensions").find("genie"):
    COLOUR[n.get("id")] = n.find("interior").get("color")

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


# ------------------------------------------------------------ 1. structure
print("1. STRUCTURE")
seen = set()
for nid in ORDER:
    for p in PAR[nid]:
        check(p in S, "%s has unknown parent %s" % (nid, p))
        check(p in seen, "%s cites %s before it is declared (cycle?)" % (nid, p))
    seen.add(nid)

for nid in ORDER:
    rows = 1
    for p in PAR[nid]:
        rows *= len(S[p])
    if KIND[nid] == "cpt":
        w = len(S[nid])
        check(len(TAB[nid]) == rows * w,
              "%s table is %d cells, expected %d" % (nid, len(TAB[nid]), rows * w))
        for r in range(rows):
            tot = sum(TAB[nid][r * w:(r + 1) * w])
            check(abs(tot - 1.0) < 1e-9, "%s row %d sums to %.9f" % (nid, r, tot))
    elif KIND[nid] == "utility":
        check(len(TAB[nid]) == rows,
              "%s table is %d cells, expected %d" % (nid, len(TAB[nid]), rows))

UNCERT, OBSERV, DECIDE, VALUE = "ffffcc", "ccffff", "ffccff", "ccffcc"
for nid in ORDER:
    if KIND[nid] == "decision":
        want = DECIDE
    elif KIND[nid] == "utility":
        want = VALUE
    elif nid.startswith("Forecast"):
        want = OBSERV
    else:
        want = UNCERT
    check(COLOUR.get(nid) == want,
          "%s is %s, the lecture's convention wants %s" % (nid, COLOUR.get(nid), want))

ndec = sum(1 for k in KIND.values() if k == "decision")
nutil = sum(1 for k in KIND.values() if k == "utility")
ncpt = sum(1 for k in KIND.values() if k == "cpt")
print("   %d nodes: %d chance, %d decision, %d value" % (len(ORDER), ncpt, ndec, nutil))
print("   %d value cells in total" %
      sum(len(TAB[n]) for n in ORDER if KIND[n] == "utility"))
print("   parents resolve, graph is acyclic, columns sum to 1, palette follows")
print("   the lecture's convention: %s" % ("yes" if not fails else "NO"))


# ------------------------------------------------------------ helpers
def look(nid, assign, own=None):
    idx = 0
    for p in PAR[nid]:
        idx = idx * len(S[p]) + S[p].index(assign[p])
    if own is None:
        return TAB[nid][idx]
    return TAB[nid][idx * len(S[nid]) + S[nid].index(own)]


WORTH, PRICE = S["Trip_worth"], S["Price_1"]
WB = WORTH[1]                       # the base state of the trip's worth
TICK, ATT, LATE, YN, SIG = S["Ticket_1"], S["Attend_1"], S["LateAvail_1"], \
    S["Reaches_1"], S["Forecast_1"]
ROUNDS = range(1, 7)


def ven_node(k):
    return "Venue_%d" % k if "Venue_%d" % k in S else None


def venues(k):
    v = ven_node(k)
    return S[v] if v else [None]


def base_assign(k, ven, price, alive=True):
    a = {"Price_%d" % k: price}
    if ven_node(k):
        a[ven_node(k)] = ven
    if k >= 2:
        a["Reaches_%d" % (k - 1)] = "Yes" if alive else "No"
    return a


def val(k, a):
    return look("Benefit_%d" % k, a) + look("Cost_%d" % k, a)


def arms(k, ven, price, worth, pyes, alive=True):
    """Expected round-k payoff for each ticket arm, given whatever belief the
    fan holds about Reaches_k at the moment he books. The attend decision is
    taken later, once qualification and late availability are both known."""
    out, pol = {}, {}
    for tk in TICK:
        tot = 0.0
        for rc in YN:
            pr = pyes if rc == "Yes" else 1 - pyes
            for la in LATE:
                a = base_assign(k, ven, price, alive)
                pl = look("LateAvail_%d" % k, a, la)
                if pl == 0.0:
                    continue
                u = dict(a)
                u.update({"Ticket_%d" % k: tk, "Reaches_%d" % k: rc,
                          "Trip_worth": worth, "LateAvail_%d" % k: la})
                best = None
                for at in reversed(ATT):          # ties resolve to Stay
                    u["Attend_%d" % k] = at
                    v = val(k, u)
                    if best is None or v > best[0]:
                        best = (v, at)
                pol[tk, rc, la] = best[1]
                if pr:
                    tot += pr * pl * best[0]
        out[tk] = tot
    return out, pol


def pick(a):
    return max(TICK, key=lambda t: (round(a[t], 6), t == "No_ticket"))


# --------------------------------- 2. per-round agreement with analyse.py
print("\n2. PER-ROUND AGREEMENT WITH analyse.py  (benefit + cost)")
ROWS = json.load(open(_here("model_results.json")))
TEAM, V = inputs.TEAM, inputs.V
A = inputs.advancement(TEAM)

print("   venue held at the workbook's scheduled city, price Base, v = $%s"
      % format(V, ",.0f"))
print("   %-3s %-14s %-13s %10s %10s   %10s %10s   %10s %10s"
      % ("R", "stage", "city", "nr file", "nr model", "rf file", "rf model",
         "wait file", "wait model"))
for k in ROUNDS:
    d = [x for x in ROWS if x["team"] == TEAM and x["k"] == k][0]
    ven = d["city"].replace(" ", "_").replace("-", "_")
    P = A[k]
    nr = P * (V - d["Bnr"]) + (1 - P) * (-(1 - d["r"]) * d["Bnr"])
    rf = P * (V - d["Brf"]) + (1 - P) * (-d["f"])
    wt = P * ((1 - d["q"]) * (V - d["Blate"]) + d["q"] * 0) + (1 - P) * 0
    wt_fixed = P * (1 - d["q"]) * max(V - d["Blate"], 0.0)
    a, _ = arms(k, ven if ven_node(k) else None, "Base", WB, P)
    ok = [abs(a["Nonrefundable"] - nr) < 0.01, abs(a["Refundable"] - rf) < 0.01,
          abs(a["Wait"] - wt_fixed) < 0.01, abs(a["No_ticket"]) < 1e-9]
    for flag, name in zip(ok, ["nonrefundable", "refundable", "wait", "no-ticket"]):
        check(flag, "round %d %s arm disagrees" % (k, name))
    print("   %-3d %-14s %-13s %10.2f %10.2f %s %10.2f %10.2f %s %10.2f %10.2f %s"
          % (k, d["stage"], d["city"], a["Nonrefundable"], nr, "ok" if ok[0] else "XX",
             a["Refundable"], rf, "ok" if ok[1] else "XX",
             a["Wait"], wt, "ok" if ok[2] else "XX"))
print("   the wait column is expected to differ from the model: the model treats")
print("   waiting as a commitment to buy late, the diagram lets the fan decline.")


# ------------------------------------------ 3. the three information regimes
print("\n3. THE THREE INFORMATION REGIMES")


def solve(regime):
    """regime: 'none' (book on the prior), 'forecast' (book on the posterior
    given the imperfect predictor), 'clairvoyant' (book knowing Reaches_k)."""
    POL, W = {}, {7: dict((wo, 0.0) for wo in WORTH)}
    M = {}
    for k in reversed(list(ROUNDS)):
        W[k] = {}
        prior = look("Reaches_%d" % k,
                     {"Reaches_%d" % (k - 1): "Yes"} if k >= 2 else {}, "Yes")
        for wo in WORTH:
            tot = 0.0
            for ven in venues(k):
                pv = look(ven_node(k), {}, ven) if ven_node(k) else 1.0
                for price in PRICE:
                    pp = look("Price_%d" % k, base_assign(k, ven, price), price)
                    if pv * pp == 0.0:
                        continue
                    if regime == "none":
                        a, pol = arms(k, ven, price, wo, prior)
                        b = pick(a)
                        POL[k, ven, price, wo] = (b, pol)
                        tot += pv * pp * a[b]
                    elif regime == "forecast":
                        for s in SIG:
                            ly = look("Forecast_%d" % k, {"Reaches_%d" % k: "Yes"}, s)
                            ln = look("Forecast_%d" % k, {"Reaches_%d" % k: "No"}, s)
                            ps = prior * ly + (1 - prior) * ln
                            if ps == 0.0:
                                continue
                            post = prior * ly / ps
                            a, pol = arms(k, ven, price, wo, post)
                            b = pick(a)
                            POL[k, ven, price, wo, s] = (b, pol)
                            tot += pv * pp * ps * a[b]
                    else:
                        for rc in YN:
                            pr = prior if rc == "Yes" else 1 - prior
                            if pr == 0.0:
                                continue
                            a, pol = arms(k, ven, price, wo, 1.0 if rc == "Yes" else 0.0)
                            b = pick(a)
                            POL[k, ven, price, wo, rc] = (b, pol)
                            tot += pv * pp * pr * a[b]
            M[k, wo] = tot
            W[k][wo] = tot + prior * W[k + 1][wo]
    eu = sum(look("Trip_worth", {}, wo) * W[1][wo] for wo in WORTH)
    return eu, W, M, POL


EU0, W0, M0, _ = solve("none")
EU1, W1, M1, POL1 = solve("forecast")
EU2, W2, M2, _ = solve("clairvoyant")

print("   %-42s %12s" % ("book on the prior, no forecast", "$%.2f" % EU0))
print("   %-42s %12s" % ("book on the imperfect forecast", "$%.2f" % EU1))
print("   %-42s %12s" % ("book knowing the result, the clairvoyant", "$%.2f" % EU2))
print("   value of the imperfect forecast   $%.2f - $%.2f = $%.2f"
      % (EU1, EU0, EU1 - EU0))
print("   value of clairvoyance (EVPI)      $%.2f - $%.2f = $%.2f"
      % (EU2, EU0, EU2 - EU0))
check(EU1 >= EU0 - 1e-6, "the forecast is worth less than nothing")
check(EU2 >= EU1 - 1e-6, "the clairvoyant is worth less than the forecast")

# Regression guard. This is the no-forecast value of the calibrated model, and
# it is the number the report quotes as the base case. If an edit anywhere in
# the pipeline moves it, this check says so rather than letting the report and
# the file drift apart.  (The pre-calibration placeholder model gave 31576.29,
# on v = $12,000 and a symmetric 0.80 forecast.)
OLD = 36209.41
check(abs(EU0 - OLD) < 0.02,
      "the no-forecast value is %.2f, the recorded baseline is %.2f" % (EU0, OLD))
print("   no-forecast value against the recorded baseline $%.2f: %s"
      % (OLD, "matches" if abs(EU0 - OLD) < 0.02 else "MOVED"))

print("\n   where the forecast earns its keep (v = base)")
print("   %-3s %-14s %11s %11s %11s %10s"
      % ("R", "stage", "no forecast", "forecast", "clairvoyant", "gain"))
for k in ROUNDS:
    st = [x for x in ROWS if x["team"] == TEAM and x["k"] == k][0]["stage"]
    print("   %-3d %-14s %11.2f %11.2f %11.2f %10.2f"
          % (k, st, M0[k, WB], M1[k, WB], M2[k, WB],
             M1[k, WB] - M0[k, WB]))

SHORT = {"Nonrefundable": "book nr", "Refundable": "book rf",
         "Wait": "wait", "No_ticket": "stay home"}
print("\n   what the forecast changes, v = base, price Base")
print("   %-3s %-14s %-14s %-14s" % ("R", "venue", "says advance", "says out"))
for k in ROUNDS:
    for ven in venues(k):
        row = [SHORT[POL1[k, ven, "Base", WB, s][0]] for s in SIG]
        flag = "   <- differs" if row[0] != row[1] else ""
        print("   %-3d %-14s %-14s %-14s%s"
              % (k, ven if ven else "fixed", row[0], row[1], flag))


# ---------------------------- 4. two independent recomputations
print("\n4. INDEPENDENT RECOMPUTATION OF THE FORECAST-REGIME VALUE")


def joint(k0, wo):
    """Every chance combination of rounds k0..6 totalled under the extracted
    policy, with no dynamic programming anywhere."""
    total = 0.0
    ks = list(range(k0, 7))
    doms = [[(v, p, l, r, s) for v in venues(k) for p in PRICE for l in LATE
             for r in YN for s in SIG] for k in ks]
    for combo in itertools.product(*doms):
        w, alive, acc = 1.0, True, 0.0
        for k, (ven, price, la, rc, sg) in zip(ks, combo):
            a = base_assign(k, ven, price, alive)
            pv = look(ven_node(k), {}, ven) if ven_node(k) else 1.0
            pp = look("Price_%d" % k, a, price)
            pl = look("LateAvail_%d" % k, a, la)
            pa = {"Reaches_%d" % (k - 1): "Yes" if alive else "No"} if k >= 2 else {}
            pr = look("Reaches_%d" % k, pa, rc)
            ps = look("Forecast_%d" % k, {"Reaches_%d" % k: rc}, sg)
            w *= pv * pp * pl * pr * ps
            if w == 0.0:
                break
            if alive:
                tk, pol = POL1[k, ven, price, wo, sg]
                at = pol[tk, rc, la]
            else:
                tk, at = "No_ticket", "Stay"
            u = dict(a)
            u.update({"Ticket_%d" % k: tk, "Attend_%d" % k: at,
                      "Reaches_%d" % k: rc, "Trip_worth": wo,
                      "LateAvail_%d" % k: la})
            acc += val(k, u)
            alive = (rc == "Yes")
        total += w * acc
    return total


ex, dp = joint(4, WB), W1[4][WB]
check(abs(ex - dp) < 1e-6, "joint %.6f vs DP %.6f" % (ex, dp))
print("   (a) exact joint enumeration of rounds 4-6, v = base")
print("       enumerated $%.4f   rolled back $%.4f   %s"
      % (ex, dp, "agree" if abs(ex - dp) < 1e-6 else "DISAGREE"))


def draw(rng, nid, assign):
    u, acc = rng.random(), 0.0
    for st in S[nid]:
        acc += look(nid, assign, st)
        if u <= acc:
            return st
    return S[nid][-1]


rng = random.Random(20260802)
N = 400000
tot = tot2 = 0.0
for _ in range(N):
    wo = draw(rng, "Trip_worth", {})
    alive, acc = True, 0.0
    for k in ROUNDS:
        ven = draw(rng, ven_node(k), {}) if ven_node(k) else None
        a = base_assign(k, ven, PRICE[0], alive)
        price = draw(rng, "Price_%d" % k, a)
        a = base_assign(k, ven, price, alive)
        la = draw(rng, "LateAvail_%d" % k, a)
        pa = {"Reaches_%d" % (k - 1): "Yes" if alive else "No"} if k >= 2 else {}
        rc = draw(rng, "Reaches_%d" % k, pa)
        sg = draw(rng, "Forecast_%d" % k, {"Reaches_%d" % k: rc})
        if alive:
            tk, pol = POL1[k, ven, price, wo, sg]
            at = pol[tk, rc, la]
        else:
            tk, at = "No_ticket", "Stay"
        u = dict(a)
        u.update({"Ticket_%d" % k: tk, "Attend_%d" % k: at,
                  "Reaches_%d" % k: rc, "Trip_worth": wo,
                  "LateAvail_%d" % k: la})
        acc += val(k, u)
        alive = (rc == "Yes")
    tot += acc
    tot2 += acc * acc
mean = tot / N
se = ((tot2 / N - mean * mean) / N) ** 0.5
z = abs(mean - EU1) / se
check(z < 4.0, "Monte Carlo %.2f is %.1f standard errors from %.2f" % (mean, z, EU1))
print("   (b) %d simulated tournaments through the extracted policy" % N)
print("       mean $%.2f, standard error $%.2f, rolled-back $%.2f, %.2f "
      "standard errors apart" % (mean, se, EU1, z))

print("\nRESULT")
if fails:
    print("  %d CHECK(S) FAILED" % len(fails))
    for f in fails:
        print("   -", f)
    sys.exit(1)
print("  all checks passed")
