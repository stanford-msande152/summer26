#!/usr/bin/env python3
"""
Value and utility functions for "Book Now or Wait?", written to the interface
the course tornado generator expects.

MS&E 152 summer 2026. Benjamin Solomon, Dias, Eugenio, Hamilton Sharpe.

The course script tornado.py calls

    build_utility_table(vars_df, utility)

and evaluates utility(**kwargs) where the keyword names are the row labels of
the csv. So every function here takes its arguments by keyword, named exactly
as the rows of fifa_tornado_inputs.csv:

    worth         v, what attending the Final is worth to the fan, dollars
    play_prob     P, the chance the team actually plays the Final
    price_mult    m, the multiplier on the whole bundle price
    recovery      r, the fraction of a stranded non-refundable bundle recovered
    cancel_fee    f, the cost of cancelling a refundable bundle
    flex_premium  the dollars the refundable bundle costs over the non-refundable one
    sellout       q, the chance no comparable seat is left on the late market
    risk_tol      rho, the fan's risk tolerance in an exponential utility

At every argument's P50 this module reproduces the Final-round figures in the
report to the cent: EV 2599.86 / 3111.11 / -853.37, margin 511.25, CE 2635.65.
Run `python3 fifa_utility.py` to check that.

Sources for the base values are in inputs.py and in section 5 of the report.
"""

import math

# --- base bundle, Spain, the Final, New York NJ, before any multiplier ---
BNR_BASE = 5511.01     # non-refundable bundle: airfare 1553.51 + hotel 749.00 + ticket 3208.50
BLATE_BASE = 13788.94  # the same trip bought after qualification is known


# ---------------------------------------------------------------- the prospects
def prospects(alternative, worth, play_prob, price_mult, recovery,
              cancel_fee, flex_premium, sellout):
    """Return [(probability, dollars), ...] for one alternative.

    This is the value function of the report, stated as a lottery rather than
    as an expectation, so that a utility can be applied to each prospect
    separately rather than to the average of them.
    """
    v = float(worth)
    P = float(play_prob)
    m = float(price_mult)
    Bnr = BNR_BASE * m
    Brf = (BNR_BASE + float(flex_premium)) * m
    Blate = BLATE_BASE * m
    q = float(sellout)

    if alternative == "nr":
        # Books outright. Goes if the team plays; otherwise resells at a loss.
        return [(P, v - Bnr), (1 - P, -(1 - float(recovery)) * Bnr)]

    if alternative == "rf":
        # Books flexibly. Goes if the team plays; otherwise cancels for a fee.
        return [(P, v - Brf), (1 - P, -float(cancel_fee))]

    if alternative == "wait":
        # Commits to buying late if the team plays and a seat is left.
        return [(P * (1 - q), v - Blate), (P * q, 0.0), (1 - P, 0.0)]

    if alternative == "stay":
        return [(1.0, 0.0)]

    raise ValueError(alternative)


ALTERNATIVES = ("nr", "rf", "wait", "stay")


# ---------------------------------------------------------------- preferences
def ev(pairs):
    "Expected value in dollars. The risk-neutral measure."
    return sum(p * x for p, x in pairs)


def certain_equivalent(pairs, risk_tol):
    """Certain equivalent under an exponential utility.

    u(x) = 1 - exp(-x / rho), so the utility is increasing and concave, and
    u is inverted to put the answer back in dollars:  v_c = u^-1(E[u]).
    This is the course formula from week 7, lecture 2.
    """
    rho = float(risk_tol)
    eu = sum(p * (1 - math.exp(-x / rho)) for p, x in pairs)
    return -rho * math.log(1 - eu) if eu < 1 else float("inf")


def _available(alternative, flex_premium):
    "The refundable arm does not exist where the trip is a drive. Not so at the Final."
    return not (alternative == "rf" and float(flex_premium) <= 0.0)


# ---------------------------------------------------------------- entry points
def utility(worth, play_prob, price_mult, recovery, cancel_fee,
            flex_premium, sellout, risk_tol):
    """The fan's certain equivalent for the Final round, in dollars.

    This is the function the tornado diagram is drawn against. It picks the
    best of the four alternatives under the fan's risk attitude and returns
    what that policy is worth to him with certainty. Higher is better.
    """
    kw = dict(worth=worth, play_prob=play_prob, price_mult=price_mult,
              recovery=recovery, cancel_fee=cancel_fee,
              flex_premium=flex_premium, sellout=sellout)
    return max(certain_equivalent(prospects(a, **kw), risk_tol)
               for a in ALTERNATIVES if _available(a, flex_premium))


def utility_ev(worth, play_prob, price_mult, recovery, cancel_fee,
               flex_premium, sellout, risk_tol):
    "The same policy valued risk neutrally, so the risk premium can be read off."
    kw = dict(worth=worth, play_prob=play_prob, price_mult=price_mult,
              recovery=recovery, cancel_fee=cancel_fee,
              flex_premium=flex_premium, sellout=sellout)
    return max(ev(prospects(a, **kw))
               for a in ALTERNATIVES if _available(a, flex_premium))


def utility_margin(worth, play_prob, price_mult, recovery, cancel_fee,
                   flex_premium, sellout, risk_tol):
    """How much booking refundable beats booking outright by, in dollars.

    A tornado on this answers a different question from a tornado on the
    policy value: not how uncertain the answer is, but what would have to
    move before the recommendation itself changed. A bar that crosses zero
    is an input that can flip the decision.
    """
    kw = dict(worth=worth, play_prob=play_prob, price_mult=price_mult,
              recovery=recovery, cancel_fee=cancel_fee,
              flex_premium=flex_premium, sellout=sellout)
    return ev(prospects("rf", **kw)) - ev(prospects("nr", **kw))


def best_alternative(worth, play_prob, price_mult, recovery, cancel_fee,
                     flex_premium, sellout, risk_tol):
    "Which arm wins, as a string. Used to check that a swing changes the choice."
    kw = dict(worth=worth, play_prob=play_prob, price_mult=price_mult,
              recovery=recovery, cancel_fee=cancel_fee,
              flex_premium=flex_premium, sellout=sellout)
    scored = [(certain_equivalent(prospects(a, **kw), risk_tol), a)
              for a in ALTERNATIVES if _available(a, flex_premium)]
    return max(scored)[1]


BASE = dict(worth=11327.0, play_prob=0.6302241904234708, price_mult=1.0,
            recovery=0.47713577, cancel_fee=837.0, flex_premium=388.3765,
            sellout=0.45, risk_tol=10000.0)


# ---------------------------------------------------------------- self-check
if __name__ == "__main__":
    kw = {k: v for k, v in BASE.items() if k != "risk_tol"}
    expect = [("nr", 2599.86), ("rf", 3111.11), ("wait", -853.37), ("stay", 0.0)]
    print("Final round at every input's P50, against the report:\n")
    print(f"  {'arm':6}{'EV, model':>13}{'EV, report':>13}{'CE at rho=10k':>16}")
    ok = True
    for arm, target in expect:
        pr = prospects(arm, **kw)
        e = ev(pr)
        c = certain_equivalent(pr, BASE["risk_tol"])
        ok &= abs(e - target) < 0.005
        print(f"  {arm:6}{e:13.2f}{target:13.2f}{c:16.2f}")
    m = utility_margin(**BASE)
    u = utility(**BASE)
    print(f"\n  margin, refundable over non-refundable  {m:10.2f}   report 511.25")
    print(f"  certain equivalent of the best arm     {u:10.2f}   report 2635.65")
    print(f"  expected value of the best arm         {utility_ev(**BASE):10.2f}   report 3111.11")
    print(f"  risk premium                           {utility_ev(**BASE) - u:10.2f}   report 475.46")
    print(f"  best arm                               {best_alternative(**BASE):>10}")
    ok &= abs(m - 511.2461) < 0.01 and abs(u - 2635.65) < 0.01
    print("\n  " + ("all figures reproduce the report" if ok else "MISMATCH"))
