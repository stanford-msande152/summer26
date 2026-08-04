# Render the cpd() output to an HTML file for visual inspection.
# Created 28 July 2026 by Cline (MiniMax-M3)

import json
import numpy as np
from bokeh.io import output_file, save
from bokeh.plotting import show  # noqa: F401
import numpy.typing as npt  # noqa: F401
from bokeh.plotting import figure  # noqa: F401

# Extract cpd() from the notebook
with open("sw/cpd.ipynb") as f:
    nb = json.load(f)
cpd_src = next(
    "".join(c["source"]) for c in nb["cells"]
    if c["cell_type"] == "code" and "def cpd" in "".join(c["source"])
)
exec(cpd_src, globals())

# --- Plot 1: uniform distribution (the example already in the notebook) ---
uniform_p = np.linspace(0, 1.0, 8)
uniform_u = np.linspace(30, 100, 8)
fig = cpd(uniform_p, uniform_u)

output_file("sw/cpd_uniform.html", title="CPD — uniform")
save(fig, filename="sw/cpd_uniform.html", title="CPD — uniform")
print("Wrote sw/cpd_uniform.html")

# --- Plot 2: a hand-checked non-uniform distribution ---
p2 = np.array([0.2, 0.5, 0.3])
u2 = np.array([10, 20, 30])
fig2 = cpd(p2, u2)
save(fig2, filename="sw/cpd_handchecked.html", title="CPD — hand-checked")
print("Wrote sw/cpd_handchecked.html")
