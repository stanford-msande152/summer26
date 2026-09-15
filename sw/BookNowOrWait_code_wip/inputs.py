# coding: utf-8
"""
Every calibrated input the model uses, in one place, with its source.

Before this file existed, `analyse.py`, `build_genie_cdn.py` and
`check_genie_cdn.py` each carried their own copy of the advancement chain and
the value of the trip, and the three had to be edited in lockstep. They now all
import from here, so there is exactly one place a number can be wrong.

Information state: everything below was public on or before 11 June 2026, the
day the fan in the case makes his first booking decision. Nothing in this file
uses knowledge of how the tournament actually turned out. The one exception is
FORECAST_SENS / FORECAST_SPEC, which are a backward-looking measurement of how
good this class of forecast is; see the note on that block.
"""

# --------------------------------------------------------------------------
# 1. Advancement, a_k = P(reach round k | reached round k-1)
# --------------------------------------------------------------------------
# Groll, Hanekov, Hvattum, Michels, Schauberger, Sukhanova, Witte and Zeileis,
# hybrid random forest (24-bookmaker consensus odds, Transfermarkt market
# values, plus-minus player ratings, FIFA and Elo ratings), 100,000 simulated
# tournaments, published 2-3 June 2026.
#   https://www.zeileis.org/assets/posts/2026-06-03-fifa2026/p_surv.html
#
# The published figures are probabilities of REACHING each stage, unconditional
# at the start of the tournament. The model needs the conditional step, so each
# a_k below is the ratio of consecutive published values. Round 1 is the group
# stage, which the team is in by construction, so a_1 = 1.
#
#   order of REACH: R32, R16, QF, SF, Final, Win   (percentages)
REACH = {
    "Spain":  [96.83, 70.54, 49.82, 36.13, 22.77, 14.46],
    "Norway": [80.63, 47.65, 25.70, 13.18,  6.19,  2.60],
}


def advancement(team):
    """a_1..a_6 for the six rounds the fan might travel to.

    k = 1 group stage, 2 round of 32, 3 round of 16, 4 quarter-final,
    5 semi-final, 6 final.
    """
    p = REACH[team]
    a = {1: 1.0, 2: p[0] / 100.0}
    for k in range(3, 7):
        a[k] = p[k - 2] / p[k - 3]
    return a


# --------------------------------------------------------------------------
# 2. What attending is worth, v
# --------------------------------------------------------------------------
# Anchored on what fans actually paid on the secondary market for the 2026
# final, since that is the one number that reveals willingness to pay rather
# than stating it. TickPick resale data for the 19 July final: get-in (cheapest
# available) $6,943, average price paid $11,327. The base case is the average
# paid; the low case is the get-in price; the high case is the reflection of
# the low case about the base, so the three-point distribution is symmetric in
# dollars and the mean equals the base.
WORTH_VAL = {"Low_6943": 6943.0, "Base_11327": 11327.0, "High_15711": 15711.0}
WORTH = ["Low_6943", "Base_11327", "High_15711"]
BASE_WORTH_STATE = "Base_11327"
V = WORTH_VAL[BASE_WORTH_STATE]

# McNamee and Celona's standard three-point discretisation of a continuous
# quantity: 0.25 / 0.50 / 0.25 on the 10th, 50th and 90th percentiles.
P_WORTH = [0.25, 0.50, 0.25]

# --------------------------------------------------------------------------
# 3. Price band multiplier
# --------------------------------------------------------------------------
# The high band is the observed match-day hotel premium across all host cities
# during the tournament, +31.44% against the same cities' non-match-day rates.
# The low band is its reciprocal, so the band is symmetric in log price and the
# three states bracket the workbook's quoted rate rather than sitting above it.
PRICE_MULT = {"Low": 1.0 / 1.3144, "Base": 1.00, "High": 1.3144}
PRICE = ["Low", "Base", "High"]
P_PRICE = [0.25, 0.50, 0.25]

# --------------------------------------------------------------------------
# 4. How good the forecast is
# --------------------------------------------------------------------------
# Estimated with the course's own naive_bayes.py, run on a 108-row training set
# built by build_nb_data.py: one record for every (team, round transition) in
# the 2026 tournament, 48 group->R32 + 32 + 16 + 8 + 4. The signal is
# "Says_advance" when the Groll/Zeileis conditional probability of surviving
# that particular round exceeds one half, and the target is whether the team in
# fact survived it.
#
# Raw 2x2, 108 records:
#                     advanced=yes   advanced=no
#     Says_advance             54            14
#     Says_out                  8            32
#
# With the tool's shipped Laplace-style smoothing (DEFAULT_COUNT = 5,
# NORMALIZE_COUNTS = True):
#     sensitivity  P(Says_advance | advanced)     = 59/72 = 0.8194
#     specificity  P(Says_out     | not advanced) = 37/56 = 0.6607
# Unsmoothed the same table gives 0.8710 and 0.6957. We use the smoothed pair,
# which is the tool's default setting and the more conservative of the two: it
# credits the forecast with less skill and therefore values information lower.
#
# This is a measurement made after the fact, and it is the only backward-
# looking input in the model. It is used the way a diagnostic test's published
# sensitivity and specificity would be used by a doctor at the bedside: it
# characterises the instrument, not this particular tournament. The fan in
# June 2026 would have had the equivalent figure from previous World Cups.
FORECAST_SENS = 59.0 / 72.0      # P(Says_advance | the team does advance)
FORECAST_SPEC = 37.0 / 56.0      # P(Says_out     | the team does not)

# --------------------------------------------------------------------------
# 5. Not calibrated here
# --------------------------------------------------------------------------
# q_k, the chance that nothing is left if the fan waits, and the cost block
# (B_nr, B_rf, f, B_late, r) come from the group's workbook; the cost block is
# built from published airfares, Lighthouse hotel rates and the FIFA ticket
# ladder, and q_k is the one genuinely elicited judgement in the model. Both
# are read out of A3_Inputs and are not restated here.
TEAM = "Spain"
