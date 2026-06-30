#!/usr/bin/env python3
"""
step3_trace_to_svg.py
Convert each extracted figure PNG to an editable SVG using vtracer Python API.
Produces clean <path>-based vector output optimized for line art.
"""

from pathlib import Path
from vtracer import convert_image_to_svg_py

INPUT_DIR = Path('/Users/jma/repos/summer26/figures')
OUTPUT_DIR = Path('/Users/jma/repos/summer26/figures')

FIGURES = [
    "Figure1-01", "Figure1-02", "Figure1-03", "Figure1-04",
    "Figure1-05", "Figure1-06", "Figure1-07", "Figure1-08",
    "Figure1-09", "Figure1-10", "Figure1-11", "Figure1-12",
    "Figure1-13", "Figure1-14", "Figure1-15", "Figure1-16",
    "Figure1-17", "Figure1-18",
]


def main():
    success = 0
    for fig_name in FIGURES:
        png_path = INPUT_DIR / f"{fig_name}.png"
        svg_path = OUTPUT_DIR / f"{fig_name}.svg"

        if not png_path.exists():
            print(f"  SKIP {fig_name}: PNG not found")
            continue

        print(f"  Tracing {fig_name}...", end=" ", flush=True)
        try:
            convert_image_to_svg_py(
                str(png_path),
                str(svg_path),
                colormode="binary",
                hierarchical="stacked",
                mode="polygon",
                filter_speckle=4,
                color_precision=1,
                corner_threshold=60,
                length_threshold=3.0,
                splice_threshold=45,
                path_precision=3,
            )
            size = svg_path.stat().st_size
            print(f"OK ({size:,} bytes)")
            success += 1
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nDone. {success}/{len(FIGURES)} SVGs created in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()