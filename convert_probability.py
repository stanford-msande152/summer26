#!/usr/bin/env python3
"""
convert_probability.py — Transform Howard manuscript probability notation to LaTeX.

Performs three passes (in order) on all { ... } brace expressions:
  1. X'  →  X^c   (complement notation, within braces only)
  2. { X | Y & }  →  $\\textsf{P}( X \\, |\\, Y, \\mathcal{E})$
  3. { X | & }    →  $\\textsf{P}( X \\, |\\, \\mathcal{E})$

Processes the file line by line and prints each substitution to stderr with
the line number and the old/new text.

Usage:  python convert_probability.py input.md [output.md]
        If output.md is omitted, the result is written to stdout.
        Substitution log is written to stderr.
"""

import re
import sys


# ---------------------------------------------------------------------------
# 1.  Prime → complement  (applied inside every brace group)
# ---------------------------------------------------------------------------
# A variable is a letter optionally followed by subscript characters.
# Unicode blocks used in the manuscript:
#   U+2080–U+2089   subscript digits          ₀₁₂₃₄₅₆₇₈₉
#   U+1D62–U+1D6A   subscript Latin letters   ᵢᵣᵤᵥᵦᵧᵨᵩᵪ
#   U+2C7C          subscript j                ⱼ
_SUBSCRIPTS = r"\u2080-\u2089\u1D62-\u1D6A\u2C7C"
_PRIME_RE = re.compile(rf"([A-Za-z](?:[{_SUBSCRIPTS}])?)'")


def _prime_to_complement(text: str) -> str:
    """Replace X' with X^c for every variable inside *text*."""
    return _PRIME_RE.sub(r"\1^c", text)


# ---------------------------------------------------------------------------
# 2.  Wrap brace expressions
# ---------------------------------------------------------------------------
_BRACE_RE = re.compile(r"\{([^}]*)\}")


def _wrap_brace(match: re.Match) -> str:
    inner = match.group(1)

    # ---- Pass 1: complement ----
    inner = _prime_to_complement(inner)

    # Must contain a |
    if "|" not in inner:
        return match.group(0)

    before, after = inner.split("|", 1)
    before = before.strip()
    after = after.strip()

    if after.startswith("&"):
        # ---- Pass 3:  { X | & }  ----
        return f"$\\textsf{{P}}({before} \\, |\\, \\mathcal{{E}})$"
    else:
        # ---- Pass 2:  { X | Y & }  ----
        amp = after.find("&")
        if amp >= 0:
            y_part = after[:amp].strip()
            return f"$\\textsf{{P}}({before} \\, |\\, {y_part}, \\mathcal{{E}})$"
        else:
            # No & — leave unchanged
            return match.group(0)


# ---------------------------------------------------------------------------
# 3.  Find and log each local replacement within a single line
# ---------------------------------------------------------------------------
_SPLIT_RE = re.compile(r"(\{[^}]*\})")


def _process_line(line: str, lineno: int, out_lines: list) -> None:
    """Process one line, logging changes to stderr, appending result to out_lines."""
    parts = _SPLIT_RE.split(line)          # split while keeping delimiters
    new_parts = []
    changed = False
    for i, part in enumerate(parts):
        if part.startswith("{"):
            m = _BRACE_RE.fullmatch(part)
            if m:
                replacement = _wrap_brace(m)
                if replacement != part:
                    print(f"[line {lineno}] {part} → {replacement}", file=sys.stderr)
                    part = replacement
                    changed = True
        new_parts.append(part)
    out_lines.append("".join(new_parts))


def convert_lines(lines: list) -> list:
    """Return transformed lines, logging changes to stderr."""
    out = []
    for i, line in enumerate(lines, start=1):
        _process_line(line.rstrip("\n"), i, out)
    return out


# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_file> [output_file]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    with open(input_path, encoding="utf-8") as fh:
        original_lines = fh.readlines()

    converted_lines = convert_lines(original_lines)
    converted_text = "\n".join(converted_lines) + "\n"

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(converted_text)
        print(f"Converted → {output_path}", file=sys.stderr)
    else:
        sys.stdout.write(converted_text)


if __name__ == "__main__":
    main()