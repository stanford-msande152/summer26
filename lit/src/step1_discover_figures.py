#!/usr/bin/env python3
"""
step1_discover_figures.py
Created: 2026-07-08 by Cline (Anthropic Claude)
Discover figure locations in the Howard manuscript PDF for Figures 1-19 through 6-13.
Outputs coordinate tuples ready to paste into step2_extract_figures.py.
Uses visual content (drawings, images) to find figure regions robustly.
"""

import fitz
import re
import os
from pathlib import Path

PDF_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "manuscript", "MSnE152_coursenotes.pdf")
)
PAGE_W = 612.0  # US Letter width in points
MIN_FIGURE_HEIGHT = 80  # minimum figure height in points


def get_visual_bounds(page, y_min, y_max, x_min, x_max):
    """Find the bounding box of visual content (drawings + images) in a region."""
    drawings = page.get_drawings()
    images = page.get_images(full=True)

    vy0, vy1 = y_max, y_min  # start reversed
    vx0, vx1 = x_max, x_min

    for d in drawings:
        rx0, ry0, rx1, ry1 = d["rect"]
        # Check if drawing overlaps our region
        if ry0 <= y_max and ry1 >= y_min and rx0 <= x_max and rx1 >= x_min:
            vy0 = min(vy0, ry0)
            vy1 = max(vy1, ry1)
            vx0 = min(vx0, rx0)
            vx1 = max(vx1, rx1)

    for img in images:
        bbox_list = page.get_image_bbox(img)
        if bbox_list:
            rx0, ry0, rx1, ry1 = bbox_list
            if ry0 <= y_max and ry1 >= y_min and rx0 <= x_max and rx1 >= x_min:
                vy0 = min(vy0, ry0)
                vy1 = max(vy1, ry1)
                vx0 = min(vx0, rx0)
                vx1 = max(vx1, rx1)

    if vy0 < vy1:
        return (vx0, vy0, vx1, vy1)
    return None


def get_text_paragraphs_below(page, y_max):
    """Get the y0 of the first body-text paragraph below y_max (used as fallback y_top)."""
    blocks = page.get_text("dict")["blocks"]
    body_bottoms = []
    for b in blocks:
        if b["type"] != 0:
            continue
        tx0, ty0, tx1, ty1 = b["bbox"]
        if ty1 < y_max:
            full_text = " ".join(
                span["text"].strip()
                for line in b.get("lines", [])
                for span in line["spans"]
            )
            # Skip figure captions and short lines
            if "Figure " in full_text[:80]:
                continue
            if len(full_text.strip()) > 20:
                body_bottoms.append(ty1)

    if body_bottoms:
        return max(body_bottoms) + 6
    return None


def main():
    doc = fitz.open(PDF_PATH)
    print(f"Opened: {PDF_PATH} ({doc.page_count} pages)\n")

    # Collect figure captures: (fig_name, page_1idx, y_top, y_bottom, x_left, x_right)
    results = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_height = page.rect.height
        text_blocks = [b for b in page.get_text("dict")["blocks"] if b["type"] == 0]

        # Find all text blocks with figure captions on this page
        page_figs = {}
        for tb in text_blocks:
            full_text = " ".join(
                span["text"].strip()
                for line in tb.get("lines", [])
                for span in line["spans"]
            )
            m = re.search(r"Figure\s+(\d+)-(\d+)", full_text)
            if not m:
                continue
            section_num = int(m.group(1))
            fig_num = int(m.group(2))
            if section_num > 6:
                continue
            if section_num == 1 and fig_num < 19:
                continue

            # Check if this is an actual caption (not just an in-text reference)
            text_start = full_text.strip()[:60]
            is_caption = text_start.startswith(f"Figure {section_num}-{fig_num}")
            # Also catch captions that start with the figure label after a short prefix
            # (e.g., "   Figure 3-8. Dollar Value...")
            fig_label = f"Figure {section_num}-{fig_num}"
            early_pos = full_text[:200].find(fig_label)
            if early_pos >= 0 and early_pos < 40:
                is_caption = True

            if not is_caption:
                continue

            fig_key = (section_num, fig_num)
            cap_x0, cap_y0, cap_x1, cap_y1 = tb["bbox"]

            # x range: use caption width with padding
            x_left = max(60, cap_x0 - 10)
            x_right = min(PAGE_W - 60, cap_x1 + 20)

            # y_bottom: just above the caption text
            y_bottom = cap_y0 - 4

            # y_top: try visual content first, then fall back to text gaps
            # Look for visual content (drawings, images) in the region above the caption
            visual = get_visual_bounds(
                page, y_min=60, y_max=y_bottom + 5, x_min=x_left - 20, x_max=x_right + 20
            )

            if visual:
                vx0, vy0, vx1, vy1 = visual
                y_top = vy0 - 6
                # Use visual x-bounds if they're reasonable
                if vx0 > 50 and vx1 < PAGE_W - 40:
                    x_left = max(60, vx0 - 10)
                    x_right = min(PAGE_W - 60, vx1 + 10)
            else:
                # Fall back to text-based detection
                para_bottom = get_text_paragraphs_below(page, y_bottom)
                if para_bottom:
                    y_top = para_bottom
                else:
                    y_top = max(60, y_bottom - 250)

            # Ensure minimum figure height
            if y_bottom - y_top < MIN_FIGURE_HEIGHT:
                y_top = y_bottom - MIN_FIGURE_HEIGHT

            page_figs[fig_key] = (page_num + 1, y_top, y_bottom, x_left, x_right)

        for (section_num, fig_num), entry in page_figs.items():
            fig_name = f"Figure{section_num}-{fig_num:02d}"
            results.append((fig_name,) + entry)

    doc.close()

    # If a figure appears on multiple pages (from cross-references), keep the earlier page
    deduped = {}
    for entry in results:
        name = entry[0]
        page = entry[1]
        if name not in deduped or page < deduped[name][1]:
            deduped[name] = entry

    # Sort by section, then figure number
    def sort_key(item):
        name = item[0]
        parts = name.replace("Figure", "").split("-")
        return (int(parts[0]), int(parts[1]))

    sorted_results = sorted(deduped.values(), key=sort_key)

    # Verify coverage
    by_section = {}
    for entry in sorted_results:
        name = entry[0]
        parts = name.replace("Figure", "").split("-")
        sec = int(parts[0])
        num = int(parts[1])
        by_section.setdefault(sec, []).append(num)

    print("Figures found per section:")
    all_missing = {}
    for sec in sorted(by_section):
        nums = by_section[sec]
        expected = list(range(min(nums), max(nums) + 1))
        missing = set(expected) - set(nums)
        print(f"  Section {sec}: {len(nums)} figures ({min(nums)}-{max(nums)})", end="")
        if missing:
            mlist = sorted(missing)
            print(f"  MISSING: {mlist}")
            all_missing[sec] = mlist
        else:
            print()

    print(f"\nTotal unique figures: {len(sorted_results)}")

    # If there are missing figures, search for them more broadly
    if all_missing:
        print("\n--- Searching for missing figures with broader criteria ---\n")
        doc2 = fitz.open(PDF_PATH)
        for sec, missing_nums in all_missing.items():
            for fig_num in missing_nums:
                fig_label = f"Figure {sec}-{fig_num}"
                found = False
                for page_num in range(len(doc2)):
                    page = doc2[page_num]
                    text = page.get_text()
                    if fig_label in text:
                        # Find the mention and surrounding context
                        idx = text.find(fig_label)
                        context = text[max(0, idx - 50):idx + 200].replace("\n", " ")
                        print(f"  {fig_label} mentioned on page {page_num + 1}: ...{context}...")
                        found = True
                if not found:
                    print(f"  {fig_label}: NOT FOUND in any page text")
        doc2.close()

    # Print the list for step2
    print(f"\n# Paste this list into step2_extract_figures.py's FIGURES list:\n")
    print("FIGURES_EXTRA = [")
    for fig_name, page_num, y_top, y_bottom, x_left, x_right in sorted_results:
        print(
            f'    ("{fig_name}", {page_num:3d}, {y_top:6.0f}, {y_bottom:6.0f}, '
            f"{x_left:5.0f}, {x_right:5.0f}),"
        )
    print("]")


if __name__ == "__main__":
    main()