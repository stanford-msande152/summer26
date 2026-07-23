# naive_bayes.py
# Created: 2026-07-22 by AI model Cline (MiniMax-M3)
#
# Estimate a multinomial naive Bayes classifier from a "rectangular" CSV dataset
# without using any Python machine learning library for the math.
#
# Algorithm
#   - Initialize each CPT to uniform counts using DEFAULT_COUNT (Laplace-style
#     smoothing).
#   - Compute a pivot table of counts for each (feature x target) pair and add
#     it into the CPT.
#   - Compute the marginal counts for the target variable.
#   - If NORMALIZE_COUNTS is true, convert each matrix so its columns sum to 1.
#
# Output
#   - A printed visual report of each CPT, with its entropy and its mutual
#     information with the target.
#   - A python file of the CPTs that can be imported into another script.

import math
import os
import sys

import pandas as pd


# ---------------------------------------------------------------------------
# Options and parameters (mirror the values set in the notebook)
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "test_data.csv")
TARGET_COLUMN = "target"
DEFAULT_COUNT = 5
NORMALIZE_COUNTS = True
OUTPUT_MODULE = os.path.join(os.path.dirname(__file__), "cpts.py")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data(path):
    """Read the CSV file and return the dataframe and the list of feature
    columns (every column except the target)."""
    df = pd.read_csv(path)
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found in {list(df.columns)}"
        )
    feature_cols = [c for c in df.columns if c != TARGET_COLUMN]
    return df, feature_cols


# ---------------------------------------------------------------------------
# Math utilities (hand-written; no scipy)
# ---------------------------------------------------------------------------
def normalize_columns(matrix):
    """Normalize a 2D matrix to a probability table.

    - If the matrix has more than one row, each column is divided by its sum
      (so columns are conditional distributions, e.g. P(x | y)).
    - If the matrix has exactly one row, that single row is divided by its
      sum (so the row is a marginal distribution, e.g. P(y)).
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    out = [[0.0 for _ in range(cols)] for _ in range(rows)]
    if rows == 1:
        # marginal: the single row should sum to 1
        row_sum = sum(matrix[0])
        if row_sum == 0:
            return out
        for c in range(cols):
            out[0][c] = matrix[0][c] / row_sum
        return out
    # conditional: each column sums to 1
    for c in range(cols):
        col_sum = sum(matrix[r][c] for r in range(rows))
        if col_sum == 0:
            continue
        for r in range(rows):
            out[r][c] = matrix[r][c] / col_sum
    return out


def entropy(probs):
    """Shannon entropy in nats: H(p) = -sum p * log(p), with 0*log(0) := 0.
    `probs` is an iterable that sums to 1."""
    h = 0.0
    for p in probs:
        if p > 0.0:
            h -= p * math.log(p)
    return h


def mutual_information(joint):
    """Mutual information I(X;Y) = sum_{x,y} P(x,y) * log(P(x,y) / (P(x)P(y)))
    in nats. `joint` is a 2D list (rows = X states, cols = Y states) of joint
    probabilities (rows x cols must sum to 1)."""
    rows = len(joint)
    cols = len(joint[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0.0
    # marginals
    px = [sum(joint[r][c] for c in range(cols)) for r in range(rows)]
    py = [sum(joint[r][c] for r in range(rows)) for c in range(cols)]
    mi = 0.0
    for r in range(rows):
        for c in range(cols):
            pxy = joint[r][c]
            if pxy > 0.0 and px[r] > 0.0 and py[c] > 0.0:
                mi += pxy * math.log(pxy / (px[r] * py[c]))
    return mi


# ---------------------------------------------------------------------------
# CPT construction
# ---------------------------------------------------------------------------
def build_cpt(df, feature, target, default_count, normalize):
    """Build a single conditional probability table for `feature` given
    `target`.  Returns (feature_states, target_states, matrix).

    Steps:
      1. Discover the sorted list of states for both variables.
      2. Build a (feature_states x target_states) matrix of uniform
         `default_count` values (Laplace smoothing).
      3. Add the observed counts from a pivot table to the matrix.
      4. Optionally normalize each column so it sums to 1.
    """
    feature_states = sorted(df[feature].unique().tolist())
    target_states = sorted(df[target].unique().tolist())

    f_index = {s: i for i, s in enumerate(feature_states)}
    t_index = {s: i for i, s in enumerate(target_states)}

    # 1. Initialize uniform counts
    matrix = [
        [float(default_count) for _ in range(len(target_states))]
        for _ in range(len(feature_states))
    ]

    # 2. Add observed counts via a pandas pivot table (rows=feature, cols=target)
    pivot = pd.pivot_table(
        df,
        index=feature,
        columns=target,
        aggfunc="size",
        fill_value=0,
    )
    # make sure every state is present even if missing in the data
    pivot = pivot.reindex(index=feature_states, columns=target_states, fill_value=0)
    for fs in feature_states:
        for ts in target_states:
            matrix[f_index[fs]][t_index[ts]] += float(pivot.at[fs, ts])  # type: ignore[arg-type]

    # 3. Optional normalization
    if normalize:
        matrix = normalize_columns(matrix)

    return feature_states, target_states, matrix


def build_target_prior(df, target, default_count, normalize):
    """Build the marginal CPT (prior) for the target variable.  Returns
    (target_states, matrix) where matrix is a (1 x |target|) row."""
    target_states = sorted(df[target].unique().tolist())
    counts = pd.Series(df[target]).value_counts().to_dict()
    matrix = [[float(default_count) + float(counts.get(s, 0)) for s in target_states]]
    if normalize:
        matrix = normalize_columns(matrix)
    return target_states, matrix


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def format_matrix(row_labels, col_labels, matrix):
    """Pretty-print a 2D matrix with labeled rows and columns."""
    # column width = max label length
    width = max(8, max(len(s) for s in col_labels) + 2)
    row_label_width = max(len(s) for s in row_labels) + 2

    header = " " * row_label_width + "".join(
        f"{c:>{width}}" for c in col_labels
    )
    lines = [header, "-" * len(header)]
    for r_label, row in zip(row_labels, matrix):
        line = f"{r_label:<{row_label_width}}" + "".join(
            f"{v:>{width}.4f}" for v in row
        )
        lines.append(line)
    return "\n".join(lines)


def report_cpts(cpts, target_prior):
    """Print a visual report of each feature CPT plus the target prior.

    For each feature CPT we show the matrix, the entropy of each conditional
    distribution (column), and the mutual information between the feature and
    the target.
    """
    target_states, prior_matrix = target_prior
    print("=" * 72)
    print("TARGET PRIOR  P(target)")
    print("=" * 72)
    print(format_matrix(["P"], target_states, prior_matrix))
    prior_entropy = entropy(prior_matrix[0])
    print(f"Entropy of target:  {prior_entropy:.4f} nats")
    print()

    for feature, (f_states, t_states, matrix) in cpts.items():
        print("=" * 72)
        print(f"CPT:  P({feature} | target)")
        print("=" * 72)
        print(format_matrix(f_states, t_states, matrix))
        # entropy of each conditional column
        col_ents = []
        for c in range(len(t_states)):
            col = [matrix[r][c] for r in range(len(f_states))]
            col_ents.append(entropy(col))
        print(
            "Conditional entropies H(" + feature + " | target):  "
            + ", ".join(
                f"{t}={col_ents[i]:.4f}" for i, t in enumerate(t_states)
            )
        )
        # joint = P(feature, target) for mutual information.
        # if the matrix is already column-normalized, reconstruct joint as
        # P(x|y) * P(y).
        total = sum(sum(row) for row in matrix)
        if total > 0 and abs(total - 1.0) < 1e-9:
            # already joint probabilities (un-normalized CPT that sums to 1)
            joint = matrix
        else:
            # matrix is P(x|y) and prior_matrix is P(y)
            joint = [
                [matrix[r][c] * prior_matrix[0][c] for c in range(len(t_states))]
                for r in range(len(f_states))
            ]
        mi = mutual_information(joint)
        print(f"Mutual information I({feature}; target):  {mi:.4f} nats")
        print()


# ---------------------------------------------------------------------------
# Module writer
# ---------------------------------------------------------------------------
def write_cpt_module(cpts, target_prior, out_path):
    """Write a python file containing the CPTs as plain python literals so it
    can be `import`-ed by another script."""
    target_states, prior_matrix = target_prior
    lines = []
    lines.append("# Auto-generated CPT module -- do not edit by hand.")
    lines.append("# Created by naive_bayes.py on 2026-07-22.")
    lines.append("")
    lines.append("TARGET_COLUMN = " + repr(TARGET_COLUMN))
    lines.append("TARGET_STATES = " + repr(target_states))
    lines.append("TARGET_PRIOR = " + repr(prior_matrix))
    lines.append("")
    lines.append("FEATURES = {")
    for feature, (f_states, t_states, matrix) in cpts.items():
        lines.append(f"    {feature!r}: {{")
        lines.append(f"        'states': {f_states!r},")
        lines.append(f"        'matrix': {matrix!r},")
        lines.append("    },")
    lines.append("}")
    lines.append("")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote CPT module to {out_path}")


# ---------------------------------------------------------------------------
# Prediction (illustrative, uses the CPTs directly)
# ---------------------------------------------------------------------------
def predict(cpts, target_prior, evidence):
    """Return argmax_y P(y) * prod_x P(x|y) over the target states.  `evidence`
    is a dict mapping feature name -> observed state.  Missing states fall
    back to a tiny epsilon probability to avoid multiplying by zero."""
    target_states, prior_matrix = target_prior
    eps = 1e-9
    scores = []
    for c, t in enumerate(target_states):
        log_p = math.log(max(prior_matrix[0][c], eps))
        for feature, value in evidence.items():
            if feature not in cpts:
                continue
            f_states, t_states, matrix = cpts[feature]
            if value in f_states and t in t_states:
                r = f_states.index(value)
                ci = t_states.index(t)
                p = matrix[r][ci]
            else:
                p = eps
            log_p += math.log(max(p, eps))
        scores.append((t, log_p))
    # softmax to turn log scores into a proper distribution for display
    m = max(s for _, s in scores)
    exps = [(t, math.exp(s - m)) for t, s in scores]
    z = sum(e for _, e in exps)
    return [(t, e / z) for t, e in exps]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Loading data from {DATA_PATH}")
    df, feature_cols = load_data(DATA_PATH)
    print(f"Read {len(df)} rows, {len(feature_cols)} features: {feature_cols}")
    print(f"Columns: {list(df.columns)}")
    print()

    # build the target prior
    target_prior = build_target_prior(df, TARGET_COLUMN, DEFAULT_COUNT, NORMALIZE_COUNTS)

    # build a CPT for every feature
    cpts = {}
    for feature in feature_cols:
        cpts[feature] = build_cpt(
            df, feature, TARGET_COLUMN, DEFAULT_COUNT, NORMALIZE_COUNTS
        )

    # visual report
    report_cpts(cpts, target_prior)

    # write the importable module
    write_cpt_module(cpts, target_prior, OUTPUT_MODULE)

    # simple demo prediction
    print()
    print("=" * 72)
    print("Demo prediction")
    print("=" * 72)
    test_evidence = {"outlook": "sunny", "temp": "cool", "humidity": "high", "wind": "strong"}
    print(f"Evidence: {test_evidence}")
    posteriors = predict(cpts, target_prior, test_evidence)
    for t, p in posteriors:
        print(f"  P(target={t!r} | evidence) = {p:.4f}")
    print()

    return cpts, target_prior


if __name__ == "__main__":
    main()
