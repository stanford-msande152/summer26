#!/usr/bin/env python3
"""
step3_trace_to_svg.py
Created: 2026-07-08 by Cline (Anthropic Claude)
Convert each extracted figure PNG to an editable SVG using vtracer Python API.
Produces clean <path>-based vector output optimized for line art.
Processes Figures 1-1 through 6-13.
"""

from pathlib import Path
from vtracer import convert_image_to_svg_py

INPUT_DIR = Path('/Users/jma/repos/summer26/figures')
OUTPUT_DIR = Path('/Users/jma/repos/summer26/figures')

FIGURES = [
    # Section 1
    "Figure1-01", "Figure1-02", "Figure1-03", "Figure1-04",
    "Figure1-05", "Figure1-06", "Figure1-07", "Figure1-08",
    "Figure1-09", "Figure1-10", "Figure1-11", "Figure1-12",
    "Figure1-13", "Figure1-14", "Figure1-15", "Figure1-16",
    "Figure1-17", "Figure1-18", "Figure1-19", "Figure1-20",
    "Figure1-21", "Figure1-22", "Figure1-23", "Figure1-24",
    "Figure1-25", "Figure1-26", "Figure1-27", "Figure1-28",
    "Figure1-29", "Figure1-30", "Figure1-31", "Figure1-32",
    "Figure1-33", "Figure1-34", "Figure1-35", "Figure1-36",
    "Figure1-37",
    # Section 2
    "Figure2-01",
    # Section 3
    "Figure3-01", "Figure3-02", "Figure3-03", "Figure3-04",
    "Figure3-05", "Figure3-06", "Figure3-07", "Figure3-08",
    "Figure3-09", "Figure3-10", "Figure3-11", "Figure3-12",
    "Figure3-13", "Figure3-14", "Figure3-15", "Figure3-16",
    "Figure3-17", "Figure3-18", "Figure3-19", "Figure3-20",
    "Figure3-21", "Figure3-22", "Figure3-23", "Figure3-24",
    "Figure3-25",
    # Section 4
    "Figure4-01", "Figure4-02", "Figure4-03", "Figure4-04",
    "Figure4-05",
    # Section 5
    "Figure5-01", "Figure5-02", "Figure5-03", "Figure5-04",
    "Figure5-05", "Figure5-06", "Figure5-07", "Figure5-08",
    # Section 6
    "Figure6-01", "Figure6-02", "Figure6-03", "Figure6-04",
    "Figure6-05", "Figure6-06", "Figure6-07", "Figure6-08",
    "Figure6-09", "Figure6-10", "Figure6-11", "Figure6-12",
    "Figure6-13",
]


def main():
    success = 0
    skipped = 0
    for fig_name in FIGURES:
        png_path = INPUT_DIR / f"{fig_name}.png"
        svg_path = OUTPUT_DIR / f"{fig_name}.svg"

        if not png_path.exists():
            print(f"  SKIP {fig_name}: PNG not found")
            skipped += 1
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

    print(f"\nDone. {success}/{len(FIGURES)} SVGs created, {skipped} skipped")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()