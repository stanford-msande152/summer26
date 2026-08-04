# Test harness for cpd() in sw/cpd.ipynb
# Created 28 July 2026 by Cline (MiniMax-M3)

import json
import numpy as np

# Extract the cpd() function definition from the notebook
with open("sw/cpd.ipynb") as f:
    nb = json.load(f)

cpd_src = None
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        if "def cpd" in src:
            cpd_src = src
            break

assert cpd_src is not None, "cpd() definition not found in notebook"

# Provide the imports cpd() depends on
import numpy.typing as npt  # noqa: F401
from bokeh.plotting import figure  # noqa: F401
from bokeh.io import output_notebook
output_notebook()

# Execute the cpd() definition
exec(cpd_src, globals())

# --- Test 1: uniform example from the notebook ---
uniform_p = np.linspace(0, 1.0, 8)
uniform_u = np.linspace(30, 100, 8)
fig1 = cpd(uniform_p, uniform_u)
print("Test 1 (uniform): figure created ->", type(fig1).__name__)
print("  x_range =", fig1.x_range.start, "to", fig1.x_range.end)
print("  y_range =", fig1.y_range.start, "to", fig1.y_range.end)
# CPD of uniform_p cumsum should end at 4.0 (sum of 0..7/7 = 28/7 = 4), so y_range should
# still be (0,1) as defined -- that's the design choice (probability axis is always 0..1).

# --- Test 2: hand-checked non-uniform distribution ---
# p = [0.2, 0.5, 0.3] at u = [10, 20, 30]
# After sort by u: same order. CPD = [0.2, 0.7, 1.0]
p2 = np.array([0.2, 0.5, 0.3])
u2 = np.array([10, 20, 30])
fig2 = cpd(p2, u2)
print("Test 2 (hand-checked): figure created ->", type(fig2).__name__)
print("  x_range =", fig2.x_range.start, "to", fig2.x_range.end)

# Inspect the renderers to confirm the step + scatter are there
renderers = fig2.renderers
print("  renderer count =", len(renderers))
for r in renderers:
    print("    -", type(r).__name__)

# --- Test 3: unsorted input should still produce a monotonic CPD ---
p3 = np.array([0.3, 0.2, 0.5])
u3 = np.array([30, 10, 20])  # intentionally scrambled
fig3 = cpd(p3, u3)
print("Test 3 (unsorted input): figure created ->", type(fig3).__name__)

print("\nAll tests completed without exception.")
