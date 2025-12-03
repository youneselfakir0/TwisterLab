#!/usr/bin/env python3
"""
Simple script to detect duplicate assignments to `pytestmark` in Python test files.
Exit with a non-zero status if any file contains more than one assignment.
"""

import argparse
import re
import sys
from pathlib import Path


def find_python_files(paths):
    for p in paths:
        path = Path(p)
        if str(path) == "tests\\unit\\test_check_pytestmark_duplicates.py":
            continue
        if path.is_file() and path.suffix == ".py":
            yield path
        elif path.is_dir():
            for f in path.rglob("*.py"):
                if str(f) == "tests\\unit\\test_check_pytestmark_duplicates.py":
                    continue
                yield f


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["tests"], help="Paths to search")
    parser.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="Auto-fix duplicate pytestmark assignments by merging into a single list",
    )
    parser.add_argument(
        "--pattern",
        default=r"^\s*pytestmark\s*=\s*(.*)$",
        help="Regex to detect pytestmark assignment lines (capture RHS in group 1)",
    )
    parsed = parser.parse_args(args=args)

    pattern = re.compile(parsed.pattern, flags=re.MULTILINE)

    failures = []
    for p in find_python_files(parsed.paths):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        matches = list(pattern.finditer(text))
        if len(matches) > 1:
            failures.append((p, len(matches), matches))

    if failures:
        print("Duplicate pytestmark assignments found:\n")
        for fname, count, _ in failures:
            print(f"  {fname} has {count} pytestmark assignments")
        print(
            "\nPlease ensure each test module defines pytestmark at most once (use a list of pytestmarks if needed)."
        )
        if parsed.fix:
            # Attempt to fix each file by merging assignments into a single list expression
            for fname, count, matches in failures:
                print(f"Attempting to fix {fname}...", end=" ")
                path = Path(fname)
                text = path.read_text(encoding="utf-8")
                # Collect existing RHS expressions
                items = []
                for m in matches:
                    rhs = m.group(1).strip()
                    # If it's already a list, strip brackets
                    if rhs.startswith("[") and rhs.endswith("]"):
                        inner = rhs[1:-1].strip()
                        if inner:
                            items.append(inner)
                    else:
                        items.append(rhs)
                combined = ", ".join(items)
                replacement = f"pytestmark = [{combined}]"
                # Replace the first match line with combined, and remove other assignment lines
                # We'll iterate over match positions and remove lines except first
                new_text_lines = []
                current_pos = 0
                for idx, m in enumerate(matches):
                    sline_start = text.rfind("\n", 0, m.start()) + 1
                    sline_end = text.find("\n", m.end())
                    if sline_end == -1:
                        sline_end = len(text)
                    # append segment from current_pos to start of this match's line
                    new_text_lines.append(text[current_pos:sline_start])
                    if idx == 0:
                        new_text_lines.append(replacement)
                    # Advance current_pos past this line
                    current_pos = sline_end + 1
                new_text_lines.append(text[current_pos:])
                new_text = "".join(new_text_lines)
                path.write_text(new_text, encoding="utf-8")
                print("fixed")
            return 0
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
