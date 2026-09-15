# coding: utf-8
"""
The knockout run as a Causal Decision Network, drawn the way Week 4 Lecture 2
prescribes.

Differences from BookNowOrWait_sequence.xdsl, all of them driven by the lecture:

  1. Conventional formatting. Uncertainties yellow, the observable predictor
     cyan, decisions pink, value nodes green. The old file had this inverted.
  2. The value sub-model is split into Benefits and Costs, as in the general
     form. Benefit_k + Cost_k reproduces the old Value_k exactly.
  3. A "test then act" backbone. Forecast_k is an imperfect predictor of
     Reaches_k, caused by it and observed before the ticket is bought. This is
     the Weather / Detector structure of the party problem: the arc runs from
     the uncertainty to the observable, and the fan has to invert it.
  4. Attend_k now sees LateAvail_k. The fan knows whether anything is left
     before he decides to fly. In the old file he decided blind.
  5. No forgetting inside the round: everything observed before Ticket_k is
     also a parent of Attend_k, including the forecast.

Per round k:
    Venue_k       chance    which city the round lands in         (uncertainty)
    Price_k       chance    price band within that venue          (uncertainty)
    Reaches_k     chance    does the team play round k at all     (uncertainty)
    Forecast_k    chance    imperfect predictor of Reaches_k      (OBSERVABLE)
    Ticket_k      DECISION  book now / refundable / wait / none
    LateAvail_k   chance    is anything left if you book late     (uncertainty)
    Attend_k      DECISION  taken once the round is resolved
    Benefit_k     value     what being at the game is worth
    Cost_k        value     money out

Global:
    Trip_worth    chance    what attending is worth to this fan

Every price and probability is read from model_results.json, which analyse.py
writes out of the A3_Inputs tab. Nothing is retyped.
"""
import itertools, json, xml.etree.ElementTree as ET
import os as _os, sys as _sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
_sys.path.insert(0, _HERE)
def _here(name): return _os.path.join(_HERE, name)

import inputs

ROWS = json.load(open(_here("model_results.json")))
TEAM = inputs.TEAM                   # the bracket path the report follows

# Every number below is sourced in inputs.py. Nothing here is a placeholder.
A = inputs.advancement(TEAM)         # conditional advancement, Groll/Zeileis
WORTH_VAL = inputs.WORTH_VAL         # value of attending, TickPick resale
P_WORTH = inputs.P_WORTH             # McNamee and Celona 0.25/0.50/0.25
PRICE_MULT = inputs.PRICE_MULT       # host-city match-day hotel premium
P_PRICE = inputs.P_PRICE

# How good the forecast is, measured with the course's naive_bayes.py over all
# 108 (team, round) transitions of the tournament. Asymmetric, because a
# forecast that says a team will go through is not as trustworthy as one that
# says it will not: it is right 82% of the time on teams that do advance and
# 66% of the time on teams that do not.
SENS = inputs.FORECAST_SENS
SPEC = inputs.FORECAST_SPEC

WORTH = inputs.WORTH
PRICE = inputs.PRICE
TICK  = ["Nonrefundable", "Refundable", "Wait", "No_ticket"]
ATT   = ["Go", "Stay"]
YN    = ["Yes", "No"]
LATE  = ["Available", "Sold_out"]
SIG   = ["Says_advance", "Says_out"]

FIELDS = ("Bnr", "Brf", "f", "Blate", "q", "r")


def slug(city):
    return str(city).replace(" ", "_").replace("-", "_")


# Candidate venues for each round: the distinct cities the workbook shows for
# that round across both bracket paths. Where both paths share a city there is
# no venue uncertainty and the node is omitted.
VEN, STAGE, HOME = {}, {}, {}
for k in range(1, 7):
    rs = [d for d in ROWS if d["k"] == k]
    STAGE[k] = rs[0]["stage"]
    HOME[k] = slug([d for d in rs if d["team"] == TEAM][0]["city"])
    seen = {}
    for d in rs:
        seen.setdefault(slug(d["city"]), {f: d[f] for f in FIELDS})
    VEN[k] = seen


def venues(k):
    return list(VEN[k].keys())


def has_venue_node(k):
    return len(VEN[k]) > 1


def prev(k):
    return "Reaches_%d" % (k - 1) if k >= 2 else None


# ------------------------------------------------- the two value sub-models
def benefit(tick, att, reaches, worth, late, alive=True):
    """What being at the game is worth. Nothing else lives in here."""
    if not alive or reaches != "Yes" or att != "Go" or tick == "No_ticket":
        return 0.0
    if tick == "Wait" and late != "Available":
        return 0.0            # he tried to buy late and there was nothing left
    return WORTH_VAL[worth]


def cost(k, ven, price, tick, att, reaches, late, alive=True):
    """Money out. Negative, so that benefits and costs simply add."""
    if not alive or tick == "No_ticket":
        return 0.0
    d = VEN[k][ven]
    m = PRICE_MULT[price]
    B, Brf, Blate, fee = d["Bnr"] * m, d["Brf"] * m, d["Blate"] * m, d["f"] * m
    if tick == "Nonrefundable":
        return -B if att == "Go" else -(1 - d["r"]) * B
    if tick == "Refundable":
        return -Brf if att == "Go" else -fee
    if reaches == "Yes" and att == "Go" and late == "Available":
        return -Blate
    return 0.0                # waiting commits nothing


# ------------------------------------------------------------------ xdsl
def fmt(xs):
    return " ".join(("%.6f" % x).rstrip("0").rstrip(".") for x in xs)


def add_states(el, names):
    for n in names:
        ET.SubElement(el, "state", id=n)


def cpt(nodes, nid, sts, parents, probs):
    e = ET.SubElement(nodes, "cpt", id=nid)
    add_states(e, sts)
    if parents:
        ET.SubElement(e, "parents").text = " ".join(parents)
    ET.SubElement(e, "probabilities").text = fmt(probs)


def domain(nid, k):
    if nid.startswith("Reaches"):
        return YN
    if nid.startswith("Venue"):
        return venues(k)
    if nid.startswith("Price"):
        return PRICE
    if nid.startswith("Ticket"):
        return TICK
    if nid.startswith("Attend"):
        return ATT
    if nid.startswith("Forecast"):
        return SIG
    if nid == "Trip_worth":
        return WORTH
    return LATE


def utility(nodes, nid, parents, k, fn):
    vals = []
    for combo in itertools.product(*[domain(p, k) for p in parents]):
        a = dict(zip(parents, combo))
        vals.append(fn(a))
    e = ET.SubElement(nodes, "utility", id=nid)
    ET.SubElement(e, "parents").text = " ".join(parents)
    ET.SubElement(e, "utilities").text = fmt(vals)
    return len(vals)


smile = ET.Element("smile", version="1.0", id="BookNowOrWait_CDN",
                   numsamples="10000", discsamples="10000")
nodes = ET.SubElement(smile, "nodes")

cpt(nodes, "Trip_worth", WORTH, [], P_WORTH)

cells = 0
for k in range(1, 7):
    vn = "Venue_%d" % k
    if has_venue_node(k):
        vs = venues(k)
        cpt(nodes, vn, vs, [], [1.0 / len(vs)] * len(vs))

    vpar = [vn] if has_venue_node(k) else []
    nv = len(venues(k)) if has_venue_node(k) else 1

    cpt(nodes, "Price_%d" % k, PRICE, vpar, P_PRICE * nv)

    cpt(nodes, "LateAvail_%d" % k, LATE, vpar,
        [x for v in (venues(k) if has_venue_node(k) else [HOME[k]])
         for x in (1 - VEN[k][v]["q"], VEN[k][v]["q"])])

    # qualification chain: once out, out for good
    if prev(k):
        cpt(nodes, "Reaches_%d" % k, YN, [prev(k)], [A[k], 1 - A[k], 0.0, 1.0])
    else:
        cpt(nodes, "Reaches_%d" % k, YN, [], [A[k], 1 - A[k]])

    # The observable. The arrow runs from the uncertainty to the predictor,
    # exactly as Weather -> Detector in the party problem; the fan sees the
    # forecast and has to invert the arrow to get a posterior on Reaches_k.
    # Row 1 is Reaches = Yes, row 2 is Reaches = No, so the diagonal holds the
    # sensitivity and the specificity respectively.
    cpt(nodes, "Forecast_%d" % k, SIG, ["Reaches_%d" % k],
        [SENS, 1 - SENS, 1 - SPEC, SPEC])

    # everything the fan has seen by the time he books
    base = ([prev(k)] if prev(k) else []) + vpar + ["Price_%d" % k]
    seen_at_ticket = base + ["Trip_worth", "Forecast_%d" % k]

    e = ET.SubElement(nodes, "decision", id="Ticket_%d" % k)
    add_states(e, TICK)
    ET.SubElement(e, "parents").text = " ".join(seen_at_ticket)

    # no forgetting: the attend decision remembers all of it, plus the ticket
    # it holds, whether the team qualified, and whether anything is left late
    seen_at_attend = seen_at_ticket + ["Ticket_%d" % k, "Reaches_%d" % k,
                                       "LateAvail_%d" % k]
    e = ET.SubElement(nodes, "decision", id="Attend_%d" % k)
    add_states(e, ATT)
    ET.SubElement(e, "parents").text = " ".join(seen_at_attend)

    bpar = ([prev(k)] if prev(k) else []) + [
        "Ticket_%d" % k, "Attend_%d" % k, "Reaches_%d" % k, "Trip_worth",
        "LateAvail_%d" % k]
    cells += utility(nodes, "Benefit_%d" % k, bpar, k, lambda a, k=k: benefit(
        a["Ticket_%d" % k], a["Attend_%d" % k], a["Reaches_%d" % k],
        a["Trip_worth"], a["LateAvail_%d" % k],
        alive=(a.get(prev(k), "Yes") == "Yes")))

    cpar = base + ["Ticket_%d" % k, "Attend_%d" % k, "Reaches_%d" % k,
                   "LateAvail_%d" % k]
    cells += utility(nodes, "Cost_%d" % k, cpar, k, lambda a, k=k: cost(
        k, a.get("Venue_%d" % k, HOME[k]), a["Price_%d" % k],
        a["Ticket_%d" % k], a["Attend_%d" % k], a["Reaches_%d" % k],
        a["LateAvail_%d" % k],
        alive=(a.get(prev(k), "Yes") == "Yes")))

# ------------------------------------------------------------- cosmetics
# The lecture's palette: uncertainties yellow, the observable cyan, decisions
# pink, value nodes green.
UNCERT, OBSERV, DECIDE, VALUE = "ffffcc", "ccffff", "ffccff", "ccffcc"

YPOS = {"Venue": 15, "Price": 95, "Reaches": 175, "Forecast": 255,
        "Ticket": 340, "LateAvail": 425, "Attend": 510, "Benefit": 595,
        "Cost": 665}
FILL = {"Venue": UNCERT, "Price": UNCERT, "Reaches": UNCERT,
        "LateAvail": UNCERT, "Forecast": OBSERV, "Ticket": DECIDE,
        "Attend": DECIDE, "Benefit": VALUE, "Cost": VALUE}
NICE = {"Venue": "Game location", "Price": "Price band",
        "Reaches": "Will they qualify", "Forecast": "Forecast (imperfect)",
        "Ticket": "Ticket choice", "LateAvail": "Late availability",
        "Attend": "Attend", "Benefit": "Benefit", "Cost": "Cost"}

ext = ET.SubElement(smile, "extensions")
g = ET.SubElement(ext, "genie", version="1.0", app="GeNIe 5.0",
                  name="Book Now or Wait - causal decision network (%s)" % TEAM)


def place(nid, label, x, y, fill):
    e = ET.SubElement(g, "node", id=nid)
    ET.SubElement(e, "name").text = label
    ET.SubElement(e, "interior", color=fill)
    ET.SubElement(e, "outline", color="000080")
    ET.SubElement(e, "font", color="000000", name="Arial", size="8")
    ET.SubElement(e, "position").text = "%d %d %d %d" % (x, y, x + 165, y + 50)


place("Trip_worth", "What the trip is worth", 620, 760, UNCERT)
for k in range(1, 7):
    x = 40 + 230 * (k - 1)
    for kind, y in YPOS.items():
        if kind == "Venue" and not has_venue_node(k):
            continue
        place("%s_%d" % (kind, k), "%s  (R%d %s)" % (NICE[kind], k, STAGE[k]),
              x, y, FILL[kind])

ET.indent(smile, space="\t")
out = _here("BookNowOrWait_CDN.xdsl")
with open(out, "w", encoding="utf-8") as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fh.write(ET.tostring(smile, encoding="unicode"))

print("wrote", out)
print("nodes: %d | value cells: %d" % (len(list(nodes)), cells))
print("forecast sensitivity %.4f | specificity %.4f" % (SENS, SPEC))
print("trip worth %s p=%s" % (WORTH_VAL, P_WORTH))
print("price band %s" % {k: round(v, 4) for k, v in PRICE_MULT.items()})
print("advancement a_k %s" % {k: round(v, 5) for k, v in A.items()})
for k in range(1, 7):
    print("  R%d %-14s a=%.4f venues=%-28s q=%s" %
          (k, STAGE[k], A[k], ",".join(venues(k)),
           ",".join("%.2f" % VEN[k][v]["q"] for v in venues(k))))
