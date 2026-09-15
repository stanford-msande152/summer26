"""
Build the naive-Bayes training set that estimates how good a pre-tournament
model forecast actually is at calling one knockout round.

One record per (team, round transition) for every team alive at the start of
that transition:  48 group->R32, 32 R32->R16, 16 R16->QF, 8 QF->SF,
4 SF->Final  =  108 records.

Columns
  signal     Says_advance / Says_out.  The pre-tournament forecast's call for
             this team at this transition: Says_advance iff the Groll/Zeileis
             conditional probability P(reach next stage | reached this stage)
             exceeds 0.5.
  rank_band  the team's band in the FIFA/Coca-Cola ranking released 11 Jun 2026
  stage      which transition this is
  advanced   the target: did the team in fact reach the next stage

Sources
  Groll, Hanekov, Hvattum, Michels, Schauberger, Sukhanova, Witte, Zeileis
    hybrid random forest, 100,000 simulations, published 2-3 June 2026
    https://www.zeileis.org/assets/posts/2026-06-03-fifa2026/p_surv.html
  FIFA/Coca-Cola Men's World Ranking, release of 11 June 2026
    https://inside.fifa.com/fifa-world-ranking/men
  Results: 2026 FIFA World Cup round of 32 / knockout stage, Wikipedia
"""
import csv, os
import os as _os, sys as _sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
_sys.path.insert(0, _HERE)
def _here(name): return _os.path.join(_HERE, name)


# ---------------------------------------------------------------- reach probs
# Probability (%) of REACHING each stage, Groll/Zeileis, 100k sims.
# order: R32, R16, QF, SF, Final, Win
REACH = {
    "Spain":        [96.83, 70.54, 49.82, 36.13, 22.77, 14.46],
    "England":      [96.48, 70.42, 49.80, 33.12, 21.08, 12.43],
    "France":       [94.66, 68.68, 45.41, 30.84, 19.77, 12.37],
    "Germany":      [95.39, 70.46, 44.10, 29.96, 18.78, 11.25],
    "Portugal":     [93.89, 65.32, 44.14, 28.53, 16.34,  8.91],
    "Argentina":    [95.95, 62.82, 44.62, 28.67, 15.62,  8.24],
    "Netherlands":  [89.41, 56.28, 37.33, 20.16, 11.02,  5.58],
    "Brazil":       [92.55, 56.15, 33.90, 18.14,  9.80,  4.72],
    "Belgium":      [95.31, 65.40, 38.65, 16.61,  7.45,  2.99],
    "Norway":       [80.63, 47.65, 25.70, 13.18,  6.19,  2.60],
    "Switzerland":  [93.60, 61.82, 29.05, 13.10,  5.49,  2.08],
    "Croatia":      [85.72, 44.56, 21.57, 10.08,  3.89,  1.37],
    "Colombia":     [85.01, 43.99, 20.48,  9.48,  3.72,  1.30],
    "Japan":        [76.11, 35.75, 18.76,  8.14,  3.38,  1.27],
    "Morocco":      [76.54, 34.22, 17.16,  6.86,  2.79,  0.99],
    "United States":[78.01, 44.14, 19.76,  7.83,  2.83,  0.95],
    "Senegal":      [76.75, 38.37, 17.27,  7.50,  2.89,  0.95],
    "Uruguay":      [84.46, 35.92, 18.17,  7.84,  2.92,  0.95],
    "Sweden":       [69.66, 30.85, 15.20,  6.14,  2.46,  0.89],
    "Ecuador":      [73.49, 34.96, 14.45,  6.08,  2.38,  0.75],
    "Austria":      [81.23, 34.54, 16.70,  7.20,  2.34,  0.66],
    "Turkey":       [75.74, 41.27, 17.79,  6.65,  2.18,  0.65],
    "Canada":       [85.36, 47.47, 18.50,  6.16,  2.07,  0.62],
    "Mexico":       [83.96, 42.66, 16.27,  5.46,  1.88,  0.60],
    "South Korea":  [83.67, 41.30, 15.34,  4.83,  1.60,  0.48],
    "Ivory Coast":  [67.99, 28.84,  9.96,  3.43,  1.14,  0.28],
    "Algeria":      [68.09, 24.92, 10.03,  3.46,  0.99,  0.25],
    "Australia":    [59.99, 27.26,  9.67,  3.15,  0.88,  0.22],
    "Czech Republic":[72.53,31.91, 10.70,  2.93,  0.86,  0.21],
    "Scotland":     [63.40, 21.36,  7.98,  2.49,  0.78,  0.21],
    "Paraguay":     [58.05, 25.37,  8.47,  2.59,  0.65,  0.14],
    "Egypt":        [66.87, 25.16,  7.56,  2.08,  0.52,  0.12],
    "Bosnia and Herzegovina":[63.17,25.05,7.76, 2.06,  0.52,  0.11],
    "DR Congo":     [47.38, 13.93,  4.31,  1.22,  0.31,  0.07],
    "Ghana":        [45.68, 14.17,  4.42,  1.30,  0.32,  0.07],
    "Tunisia":      [34.22,  9.97,  3.23,  0.93,  0.27,  0.06],
    "Iran":         [55.07, 17.99,  4.61,  1.07,  0.21,  0.04],
    "Cape Verde":   [40.62, 10.99,  2.96,  0.67,  0.16,  0.03],
    "Uzbekistan":   [37.71,  9.76,  2.65,  0.65,  0.14,  0.03],
    "Panama":       [32.99,  8.21,  2.07,  0.50,  0.11,  0.03],
    "Haiti":        [34.69,  8.14,  2.18,  0.52,  0.12,  0.02],
    "New Zealand":  [46.98, 12.79,  3.06,  0.66,  0.11,  0.02],
    "Saudi Arabia": [38.03,  8.71,  2.05,  0.41,  0.09,  0.012],
    "Curacao":      [28.90,  7.03,  1.54,  0.34,  0.06,  0.011],
    "South Africa": [31.73,  8.87,  1.94,  0.33,  0.06,  0.007],
    "Iraq":         [18.88,  4.27,  0.95,  0.20,  0.05,  0.006],
    "Qatar":        [25.01,  5.35,  1.00,  0.15,  0.02,  0.002],
    "Jordan":       [21.61,  4.40,  0.96,  0.18,  0.03,  0.001],
}

# ---------------------------------------------------------------- FIFA ranks
RANK = {
    "Argentina":1, "Spain":2, "France":3, "England":4, "Portugal":5, "Brazil":6,
    "Morocco":7, "Netherlands":8, "Belgium":9, "Germany":10, "Croatia":11,
    "Colombia":13, "Mexico":14, "Senegal":15, "Uruguay":16, "United States":17,
    "Japan":18, "Switzerland":19, "Iran":20, "Turkey":22, "Ecuador":23,
    "Austria":24, "South Korea":25, "Australia":27, "Algeria":28, "Egypt":29,
    "Canada":30, "Norway":31, "Ivory Coast":33, "Panama":34, "Sweden":38,
    "Czech Republic":40, "Paraguay":41, "Scotland":42, "Tunisia":45,
    "DR Congo":46, "Uzbekistan":50, "Qatar":56, "Iraq":57, "South Africa":60,
    "Saudi Arabia":61, "Jordan":63, "Bosnia and Herzegovina":64,
    "Cape Verde":67, "Ghana":73, "Curacao":82, "Haiti":83, "New Zealand":85,
}

def band(team):
    r = RANK[team]
    if r <= 10:  return "Top10"
    if r <= 25:  return "R11_25"
    if r <= 50:  return "R26_50"
    return "R51_plus"

# ---------------------------------------------------------------- results
# The 32 teams that came out of the group stage (they are exactly the teams
# that appear in the round of 32).
R32_FIELD = [
    "South Africa","Canada","Brazil","Japan","Germany","Paraguay",
    "Netherlands","Morocco","Ivory Coast","Norway","France","Sweden",
    "Mexico","Ecuador","England","DR Congo","Belgium","Senegal",
    "United States","Bosnia and Herzegovina","Spain","Austria","Portugal",
    "Croatia","Switzerland","Algeria","Australia","Egypt","Argentina",
    "Cape Verde","Colombia","Ghana",
]
R16_FIELD = ["Canada","Morocco","Paraguay","France","Brazil","Norway","Mexico",
             "England","Portugal","Spain","United States","Belgium",
             "Argentina","Egypt","Switzerland","Colombia"]
QF_FIELD  = ["Morocco","France","Norway","England","Spain","Belgium",
             "Argentina","Switzerland"]
SF_FIELD  = ["France","Spain","England","Argentina"]
FINALISTS = ["Spain","Argentina"]

TRANSITIONS = [
    # label,          field alive now,      who reached the next stage, index of
    #                                                              next-stage prob
    ("Group_to_R32",  sorted(REACH),        set(R32_FIELD),  0),
    ("R32_to_R16",    R32_FIELD,            set(R16_FIELD),  1),
    ("R16_to_QF",     R16_FIELD,            set(QF_FIELD),   2),
    ("QF_to_SF",      QF_FIELD,             set(SF_FIELD),   3),
    ("SF_to_Final",   SF_FIELD,             set(FINALISTS),  4),
]

def conditional(team, i):
    """P(reach stage i+1 | reached stage i), Groll/Zeileis."""
    p = REACH[team]
    return p[i] / 100.0 if i == 0 else p[i] / p[i - 1]

rows = []
for label, field, made_it, idx in TRANSITIONS:
    for team in field:
        c = conditional(team, idx)
        rows.append({
            "signal":   "Says_advance" if c > 0.5 else "Says_out",
            "rank_band": band(team),
            "stage":    label,
            "advanced": "yes" if team in made_it else "no",
            "_team":    team,
            "_p":       round(c, 5),
        })

assert len(rows) == 108, len(rows)

OUT = _here("advance_data.csv")
with open(OUT, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["signal", "rank_band", "stage", "advanced"])
    for r in rows:
        w.writerow([r["signal"], r["rank_band"], r["stage"], r["advanced"]])

# a fully documented copy, with the team and the probability that produced the
# signal, so every row of the training set can be traced back to its source
AUD = _here("advance_data_audit.csv")
with open(AUD, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["stage", "team", "fifa_rank", "rank_band",
                "p_advance_conditional", "signal", "advanced"])
    for r in rows:
        w.writerow([r["stage"], r["_team"], RANK[r["_team"]], r["rank_band"],
                    r["_p"], r["signal"], r["advanced"]])

# ---------------------------------------------------------------- quick view
from collections import Counter
print("rows:", len(rows), "->", OUT)
tab = Counter((r["signal"], r["advanced"]) for r in rows)
print("\n2x2 confusion of the pre-tournament forecast against what happened")
print(f"{'':16}{'advanced=yes':>14}{'advanced=no':>13}")
for s in ("Says_advance", "Says_out"):
    print(f"{s:16}{tab[(s,'yes')]:>14}{tab[(s,'no')]:>13}")
ny = sum(1 for r in rows if r["advanced"] == "yes")
nn = len(rows) - ny
print(f"\nP(Says_advance | advanced)   = {tab[('Says_advance','yes')]}/{ny}"
      f" = {tab[('Says_advance','yes')]/ny:.4f}")
print(f"P(Says_out     | not adv.)   = {tab[('Says_out','no')]}/{nn}"
      f" = {tab[('Says_out','no')]/nn:.4f}")
print(f"overall hit rate             = "
      f"{(tab[('Says_advance','yes')]+tab[('Says_out','no')])/len(rows):.4f}")
print("\nby stage")
for label, field, made_it, idx in TRANSITIONS:
    sub = [r for r in rows if r["stage"] == label]
    hit = sum(1 for r in sub if (r["signal"] == "Says_advance") ==
              (r["advanced"] == "yes"))
    print(f"  {label:14} {hit:>3}/{len(sub):<3} = {hit/len(sub):.3f}")
