#!/usr/bin/env python3
"""
step2_extract_figures.py
Extract Figures 1-1 through 1-18 from the Howard manuscript PDF.
Renders each figure region as a high-res PNG (excludes the caption).
"""

import fitz
import os
from pathlib import Path

PDF_PATH = '/Users/jma/Library/CloudStorage/OneDrive-Personal/teaching/Stanford/stanford_DA/MSnE152_DA/Ron_coursenotes/MS&E152_coursenotes copy.pdf'
OUTPUT_DIR = Path('/Users/jma/repos/summer26/figures')
DPI = 300
SCALE = DPI / 72.0

# (filename, page_1indexed, y_top, y_bottom, x_left, x_right)
# y_top = top of figure region, y_bottom = where caption starts
FIGURES = [
    ("Figure1-01", 7,  398, 530, 80, 530),
    ("Figure1-02", 8,  105, 232, 80, 530),
    ("Figure1-03", 8,  415, 680, 80, 530),
    ("Figure1-04", 10, 170, 405, 80, 530),
    ("Figure1-05", 11, 70,  285, 80, 530),
    ("Figure1-06", 12, 70,  362, 80, 530),
    ("Figure1-07", 13, 198, 308, 80, 530),
    ("Figure1-08", 13, 498, 610, 80, 530),
    ("Figure1-09", 14, 143, 475, 80, 530),
    ("Figure1-10", 15, 235, 502, 80, 530),
    ("Figure1-11", 16, 330, 692, 80, 530),
    ("Figure1-12", 19, 68,  197, 80, 530),
    ("Figure1-13", 19, 468, 597, 80, 530),
    ("Figure1-14", 20, 125, 240, 80, 530),
    ("Figure1-15", 20, 365, 476, 80, 530),
    ("Figure1-16", 21, 68,  333, 80, 530),
    ("Figure1-17", 23, 68,  331, 80, 530),
    ("Figure1-18", 25, 183, 411, 80, 530),
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    print(f"Opened: {PDF_PATH} ({doc.page_count} pages)")

    for fig_name, page_num, y_top, y_bottom, x_left, x_right in FIGURES:
        page = doc[page_num - 1]
        clip = fitz.Rect(x_left, y_top, x_right, y_bottom)
        mat = fitz.Matrix(SCALE, SCALE)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        out_path = OUTPUT_DIR / f"{fig_name}.png"
        pix.save(str(out_path))
        print(f"  {fig_name}.png  {pix.width}x{pix.height} px")

    doc.close()
    print(f"\nDone. {len(FIGURES)} PNGs saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()