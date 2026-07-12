#!/usr/bin/env python3
"""
step2_extract_figures.py
Extract Figures 1-1 through 1-18 from the Howard manuscript PDF.
Renders each figure region as a high-res PNG (excludes the caption).

Also extracts a small set of Section 3 figures at FULL PAGE WIDTH
(saving to <name>ex.png) per the request to re-extract 3-04, 3-05,
3-06, 3-07, 3-08, 3-12, 3-14, 3-15, 3-18, 3-21, 3-22, 3-23, 3-25
with surrounding layout.
"""

import fitz
import os
from pathlib import Path

PDF_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lit", "manuscript", "MSnE152_coursenotes.pdf")
)
OUTPUT_DIR = Path(os.path.join(os.path.dirname(__file__), "..", "..", "figures")).resolve()
DPI = 300
SCALE = DPI / 72.0

# Full page-content horizontal bounds (US Letter, ~1-inch margins).
# 60 pt left, 552 pt right -> 492 pt wide -> ~2050 px at 300 DPI.
FULL_WIDTH_X = (60, 552)

# (filename, page_1indexed, y_top, y_bottom, x_left, x_right)
# y_top = top of figure region, y_bottom = where caption starts
# Original Figures 1-1 through 1-18 (manually measured)
# New Figures 1-19 through 6-13 (auto-discovered by step1_discover_figures.py)
FIGURES = [
    # ---- Section 1: Possibilities and Probabilities ----
    ("Figure1-01", 7, 398, 530, 80, 530),
    ("Figure1-02", 8, 105, 232, 80, 530),
    ("Figure1-03", 8, 415, 680, 80, 530),
    ("Figure1-04", 10, 170, 405, 80, 530),
    ("Figure1-05", 11, 70, 285, 80, 530),
    ("Figure1-06", 12, 70, 362, 80, 530),
    ("Figure1-07", 13, 198, 308, 80, 530),
    ("Figure1-08", 13, 498, 610, 80, 530),
    ("Figure1-09", 14, 143, 475, 80, 530),
    ("Figure1-10", 15, 235, 502, 80, 530),
    ("Figure1-11", 16, 330, 692, 80, 530),
    ("Figure1-12", 19, 68, 197, 80, 530),
    ("Figure1-13", 19, 468, 597, 80, 530),
    ("Figure1-14", 20, 125, 240, 80, 530),
    ("Figure1-15", 20, 365, 476, 80, 530),
    ("Figure1-16", 21, 68, 333, 80, 530),
    ("Figure1-17", 23, 68, 331, 80, 530),
    ("Figure1-18", 25, 183, 411, 80, 530),
    # ---- Section 1 (continued): auto-discovered ----
    ("Figure1-19", 27, 245, 384, 80, 530),
    ("Figure1-20", 28, 47, 127, 81, 532),
    ("Figure1-21", 28, 67, 660, 80, 532),
    ("Figure1-22", 30, 219, 603, 80, 492),
    ("Figure1-23", 32, 84, 355, 82, 423),
    ("Figure1-24", 34, 426, 513, 129, 484),
    ("Figure1-25", 35, 76, 596, 80, 530),
    ("Figure1-26", 36, 76, 429, 80, 428),
    ("Figure1-27", 39, 84, 399, 135, 379),
    ("Figure1-28", 40, 83, 174, 238, 375),
    ("Figure1-29", 40, 83, 623, 80, 375),
    ("Figure1-30", 42, 82, 433, 117, 502),
    ("Figure1-31", 43, 70, 420, 117, 502),
    ("Figure1-32", 44, 147, 498, 117, 502),
    ("Figure1-33", 45, 115, 500, 80, 303),
    ("Figure1-34", 46, 71, 334, 178, 450),
    ("Figure1-35", 47, 66, 356, 81, 537),
    ("Figure1-36", 48, 178, 430, 133, 377),
    ("Figure1-37", 49, 76, 470, 80, 504),
    # ---- Section 2: Rules of Actional Thought ----
    ("Figure2-01", 55, 124, 222, 119, 474),
    # ---- Section 3: The Party Problem: Basic Form ----
    ("Figure3-01", 60, 501, 713, 377, 532),
    ("Figure3-02", 61, 338, 561, 373, 534),
    ("Figure3-03", 62, 89, 633, 98, 413),
    ("Figure3-04", 63, 298, 499, 341, 531),
    ("Figure3-05", 64, 71, 387, 166, 408),
    ("Figure3-06", 65, 71, 279, 193, 384),
    ("Figure3-07", 66, 91, 294, 177, 432),
    ("Figure3-08", 68, 76, 307, 98, 379),
    ("Figure3-09", 68, 76, 595, 98, 379),
    ("Figure3-10", 69, 71, 678, 80, 514),
    ("Figure3-11", 70, 79, 313, 128, 530),
    ("Figure3-12", 71, 76, 385, 98, 403),
    ("Figure3-13", 72, 73, 302, 141, 505),
    ("Figure3-14", 73, 112, 299, 150, 340),
    ("Figure3-15", 75, 95, 699, 80, 414),
    ("Figure3-16", 78, 71, 323, 141, 505),
    ("Figure3-17", 79, 390, 604, 277, 534),
    ("Figure3-18", 80, 66, 332, 223, 534),
    ("Figure3-19", 81, 119, 279, 80, 539),
    ("Figure3-20", 81, 398, 650, 141, 506),
    ("Figure3-21", 82, 146, 243, 117, 417),
    ("Figure3-22", 83, 109, 317, 144, 334),
    ("Figure3-23", 85, 96, 691, 116, 451),
    ("Figure3-24", 86, 336, 673, 98, 145),
    ("Figure3-25", 88, 99, 694, 116, 451),
    # ---- Section 4: The Party Problem: Risk Attitude ----
    ("Figure4-01", 92, 297, 544, 136, 498),
    ("Figure4-02", 94, 486, 586, 136, 476),
    ("Figure4-03", 95, 219, 589, 80, 459),
    ("Figure4-04", 98, 215, 295, 270, 358),
    ("Figure4-05", 99, 104, 396, 80, 376),
    # ---- Section 5: The Party Problem: Sensitivity Analysis ----
    ("Figure5-01", 105, 97, 305, 156, 343),
    ("Figure5-02", 106, 86, 489, 108, 494),
    ("Figure5-03", 108, 88, 474, 133, 501),
    ("Figure5-04", 109, 103, 301, 124, 488),
    ("Figure5-05", 110, 97, 304, 192, 379),
    ("Figure5-06", 111, 91, 508, 119, 505),
    ("Figure5-07", 112, 220, 424, 110, 506),
    ("Figure5-08", 113, 288, 488, 121, 486),
    # ---- Section 6: The Party Problem: Basic Information Gathering ----
    ("Figure6-01", 116, 273, 485, 241, 534),
    ("Figure6-02", 118, 102, 301, 208, 534),
    ("Figure6-03", 118, 102, 692, 208, 534),
    ("Figure6-04", 119, 66, 327, 208, 534),
    ("Figure6-05", 119, 66, 692, 208, 534),
    ("Figure6-06", 120, 154, 704, 80, 369),
    ("Figure6-07", 123, 101, 405, 80, 447),
    ("Figure6-08", 123, 101, 661, 80, 491),
    ("Figure6-09", 124, 312, 416, 127, 487),
    ("Figure6-10", 125, 67, 187, 81, 532),
    ("Figure6-11", 125, 67, 459, 80, 532),
    ("Figure6-12", 126, 89, 300, 80, 533),
    ("Figure6-13", 127, 67, 282, 81, 533),
]


# Section 3 figures re-extracted at full page width (saves as <name>ex.png).
# y_top/y_bottom are reused from FIGURES (figure region above the caption);
# x_left/x_right are overridden with FULL_WIDTH_X.
FIGURES_FULLWIDTH = [
    ("Figure3-04", 63, 298, 499),
    ("Figure3-05", 64, 71, 387),
    ("Figure3-06", 65, 71, 279),
    ("Figure3-07", 66, 91, 294),
    ("Figure3-08", 68, 76, 307),
    ("Figure3-12", 71, 76, 385),
    ("Figure3-14", 73, 112, 299),
    ("Figure3-15", 75, 95, 699),
    ("Figure3-18", 80, 66, 332),
    ("Figure3-21", 82, 146, 243),
    ("Figure3-22", 83, 109, 317),
    ("Figure3-23", 85, 96, 691),
    ("Figure3-25", 88, 99, 694),
]



def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    print(f"Opened: {PDF_PATH} ({doc.page_count} pages)")
    print(f"Output: {OUTPUT_DIR}\n")

    success = 0
    print("== Standard (tight-crop) extractions ==")
    for fig_name, page_num, y_top, y_bottom, x_left, x_right in FIGURES:
        page = doc[page_num - 1]
        height = max(y_bottom - y_top, 1)
        if height < 20:
            print(f"  SKIP {fig_name}: height too small ({height:.0f}pt)")
            continue
        clip = fitz.Rect(x_left, y_top, x_right, y_bottom)
        mat = fitz.Matrix(SCALE, SCALE)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        out_path = OUTPUT_DIR / f"{fig_name}.png"
        pix.save(str(out_path))
        print(f"  {fig_name}.png  {pix.width}x{pix.height} px  (page {page_num}, {height:.0f}pt tall)")
        success += 1

    # Full-width re-extractions: appended "ex" suffix.
    fw_success = 0
    print("\n== Full-width re-extractions (*ex.png) ==")
    x_left, x_right = FULL_WIDTH_X
    for fig_name, page_num, y_top, y_bottom in FIGURES_FULLWIDTH:
        page = doc[page_num - 1]
        height = max(y_bottom - y_top, 1)
        if height < 20:
            print(f"  SKIP {fig_name}ex: height too small ({height:.0f}pt)")
            continue
        clip = fitz.Rect(x_left, y_top, x_right, y_bottom)
        mat = fitz.Matrix(SCALE, SCALE)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        out_path = OUTPUT_DIR / f"{fig_name}ex.png"
        pix.save(str(out_path))
        print(f"  {fig_name}ex.png  {pix.width}x{pix.height} px  (page {page_num}, {height:.0f}pt tall)")
        fw_success += 1

    doc.close()
    print(
        f"\nDone. {success}/{len(FIGURES)} standard PNGs and "
        f"{fw_success}/{len(FIGURES_FULLWIDTH)} full-width PNGs saved to {OUTPUT_DIR}"
    )



if __name__ == "__main__":
    main()
