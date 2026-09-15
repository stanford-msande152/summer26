#!/usr/bin/env python3
"""
Runs the course tornado generator against the Book Now or Wait model.

    python3 run_tornado.py

Reads fifa_tornado_inputs.csv, calls build_utility_table() and plot_tornado()
out of the professor's tornado.py without modifying either, and writes:

    tornado_ce.html      certain equivalent of the Final-round policy
    tornado_margin.html  refundable minus non-refundable, the decision margin
    fig_tornado_ce.png   the same table drawn statically, for the report
    tornado_tables.txt   both utility tables as printed numbers

The only thing this file does that tornado.py's own command line cannot is
supply our utility function instead of the built-in test_utility, and save
the html rather than trying to open a browser, which a headless machine
has none of.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from bokeh.io import output_file, save

import fifa_utility as F
from tornado import build_utility_table, plot_tornado

from pathlib import Path

_HERE = Path(__file__).resolve().parent

CSV = "fifa_tornado_inputs.csv"

# The report's palette, so the figure sits beside the others without clashing.
INK, GREY, BLUE, ORANGE, RED = "#1A2233", "#5A6472", "#2B6CB0", "#C05621", "#9B2C2C"

LABEL = {
    "worth": "What the trip is worth  (v)",
    "play_prob": "Chance the team plays  (P)",
    "price_mult": "Bundle price multiplier  (m)",
    "recovery": "Resale recovery fraction  (r)",
    "cancel_fee": "Cancellation fee  (f)",
    "flex_premium": "Refundable premium",
    "sellout": "Late market sells out  (q)",
    "risk_tol": "Risk tolerance  (ρ)",
}


def load(the_path):
    df = pd.read_csv(the_path /  CSV)
    df.set_index(df.columns[0], inplace=True)
    return df


def swing_png(table, path, title, subtitle, xlabel, flat_note, zero_line=False):
    """A static twin of the bokeh chart, for dropping into the report.

    Two colours, because in a tornado the two halves of a bar mean different
    things: which end of the input's range produced that end of the output.
    Both are labelled, so identity never rests on colour alone.
    """
    t = table.iloc[::-1].reset_index(drop=True)      # largest swing on top
    base = float(table["U_base"].iloc[0])
    names = [LABEL.get(v, v) for v in t["Variable"]]
    y = range(len(t))

    ends = list(t["U_P10"]) + list(t["U_P90"]) + [base] + ([0.0] if zero_line else [])
    lo_x, hi_x = min(ends), max(ends)
    span = (hi_x - lo_x) or 1.0
    pad = 0.14 * span
    off = 0.012 * span

    fig, ax = plt.subplots(figsize=(9.6, 0.62 * len(t) + 1.9), dpi=200)
    fig.patch.set_facecolor("white")

    for i, row in t.iterrows():
        flat = abs(float(row["Range"])) < 0.005
        if flat:
            ax.text(base + off, i, flat_note,
                    va="center", ha="left", fontsize=7.6, color=GREY,
                    style="italic", zorder=4)
            continue
        for u, colour in ((row["U_P10"], ORANGE), (row["U_P90"], BLUE)):
            a, b = sorted((base, u))
            ax.barh(i, b - a, left=a, height=0.54,
                    color=colour, alpha=0.85, edgecolor="white", linewidth=1.2,
                    zorder=3)
        for u, colour in ((row["U_P10"], ORANGE), (row["U_P90"], BLUE)):
            right = u >= base
            ax.text(u + (off if right else -off), i, f"{u:,.0f}", va="center",
                    ha="left" if right else "right",
                    fontsize=7.6, color=colour, zorder=4)

    ax.axvline(base, color=RED, linestyle="--", linewidth=1.4, zorder=5)
    if zero_line:
        ax.axvline(0, color=INK, linewidth=1.2, zorder=5)
        ax.annotate("zero: the two arms tie", xy=(0, len(t) - 0.45),
                    xytext=(5, 0), textcoords="offset points",
                    fontsize=7.6, color=INK, va="center")
    ax.set_xlim(lo_x - pad, hi_x + pad)
    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=9, color=INK)
    ax.set_xlabel(xlabel, fontsize=8.6, color=GREY)
    ax.set_ylim(-0.7, len(t) - 0.3)
    ax.tick_params(axis="x", labelsize=8, colors=GREY)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#D8DEE7")
    ax.grid(axis="x", color="#E6EBF2", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)

    ax.annotate(f"base {base:,.0f}", xy=(base, len(t) - 0.45),
                xytext=(5, 0), textcoords="offset points",
                fontsize=7.6, color=RED, va="center")

    handles = [plt.Rectangle((0, 0), 1, 1, color=ORANGE, alpha=0.85),
               plt.Rectangle((0, 0), 1, 1, color=BLUE, alpha=0.85)]
    ax.legend(handles, ["input at its P10", "input at its P90"],
              loc="lower right", frameon=False, fontsize=8,
              labelcolor=GREY, ncol=2, bbox_to_anchor=(1.0, -0.16 / len(t) - 0.10))

    ax.set_title(title, fontsize=11.5, color=INK, loc="left", pad=16, fontweight="bold")
    ax.text(0, 1.015, subtitle, transform=ax.transAxes,
            fontsize=8.4, color=GREY, va="bottom")

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def bokeh_html(table, path, title):
    "The professor's own plot function, saved rather than shown."
    p = plot_tornado(table)
    p.title.text = title
    p.xaxis.axis_label = "Certain equivalent, dollars"
    output_file(filename=path, title=title)
    save(p)


def flips(vars_df):
    "Which inputs change the recommended arm between their P10 and their P90."
    base = {n: float(vars_df.loc[n, "P50"]) for n in vars_df.index}
    out = []
    for n in vars_df.index:
        picks = []
        for col in ("P10", "P50", "P90"):
            kw = dict(base)
            kw[n] = float(vars_df.loc[n, col])
            picks.append(F.best_alternative(**kw))
        if len(set(picks)) > 1:
            out.append((n, picks))
    return out


def main():
    vars_df = load()

    ce = build_utility_table(vars_df, F.utility)
    mg = build_utility_table(vars_df, F.utility_margin)

    bokeh_html(ce, "tornado_ce.html",
               "Book Now or Wait? Sensitivity of the Final-round certain equivalent")
    bokeh_html(mg, "tornado_margin.html",
               "Book Now or Wait? What could flip the recommendation")

    swing_png(ce, "fig_tornado_ce.png",
              "What the Final-round answer is most sensitive to",
              "Certain equivalent of the best arm at ρ = $10,000, "
              "one input at a time, all others at their median.",
              "Certain equivalent of the Final-round policy, dollars",
              "no effect: this input only moves alternatives the fan does not pick")
    swing_png(mg, "fig_tornado_margin.png",
              "What would have to move to change the recommendation",
              "Refundable minus non-refundable. A bar reaching zero is an "
              "input that can flip the choice.",
              "Refundable minus non-refundable, dollars",
              "no effect: this input moves both arms by the same amount",
              zero_line=True)

    cols = ["Variable", "P10", "P50", "P90", "U_P10", "U_base", "U_P90", "Range"]
    with open("tornado_tables.txt", "w") as fh:
        for name, tbl in (("CERTAIN EQUIVALENT OF THE FINAL-ROUND POLICY", ce),
                          ("MARGIN: REFUNDABLE MINUS NON-REFUNDABLE", mg)):
            fh.write(name + "\n")
            fh.write(tbl[cols].to_string(index=False,
                     float_format=lambda x: f"{x:,.4f}") + "\n\n")
        fh.write("INPUTS THAT CHANGE THE RECOMMENDED ARM ACROSS THEIR OWN RANGE\n")
        f = flips(vars_df)
        fh.write("none\n" if not f else
                 "".join(f"  {n:14s} P10 {a} -> P50 {b} -> P90 {c}\n"
                         for n, (a, b, c) in f))

    print(open("tornado_tables.txt").read())
    print("wrote tornado_ce.html, tornado_margin.html, "
          "fig_tornado_ce.png, fig_tornado_margin.png, tornado_tables.txt")


if __name__ == "__main__":
    main()
