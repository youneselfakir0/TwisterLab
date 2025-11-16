#!/usr/bin/env python3
"""
Sanitize or scan archive and log files for hardcoded secrets.

This script helps find potential secrets in `archive/`, `debug_*.txt`, and other logs
and optionally writes a sanitized copy with secrets redacted.

Usage:
    python scripts/sanitize_archives.py --dry-run
    python scripts/sanitize_archives.py --apply --backup-dir sanitized_archives/

The script looks for common patterns such as PASSWORD=, GF_SECURITY_ADMIN_PASSWORD,
DATABASE_URL that includes password, and other token-like strings.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Iterable, List, Pattern, Tuple


def find_files(root: Path, patterns: Iterable[str]) -> List[Path]:
    matches: List[Path] = []
    for pattern in patterns:
        for p in root.rglob(pattern):
            if p.is_file():
                matches.append(p)
    return matches


SENSITIVE_PATTERNS: List[Tuple[Pattern, str]] = [
    (re.compile(r"POSTGRES_PASSWORD=[^\s\n\r]+", re.IGNORECASE), "POSTGRES_PASSWORD=<REDACTED>"),
    (re.compile(r"REDIS_PASSWORD=[^\s\n\r]+", re.IGNORECASE), "REDIS_PASSWORD=<REDACTED>"),
    (
        re.compile(r"GF_SECURITY_ADMIN_PASSWORD[^=]*=[^\s\n\r]+", re.IGNORECASE),
        "GF_SECURITY_ADMIN_PASSWORD=<REDACTED>",
    ),
    (
        re.compile(r"DATABASE_URL=postgresql://[^:]+:[^@]+@", re.IGNORECASE),
        "DATABASE_URL=postgresql://<REDACTED>:@",
    ),
    (
        re.compile(r"(password\s*[:=]\s*['\"]?)[^'\"\n\r]{6,}(['\"]?)", re.IGNORECASE),
        "\1<REDACTED>\2",
    ),
]


def scan_file(path: Path) -> List[Tuple[int, str, str]]:
    """Scan a file and return a list of tuples: (line_number, original_line, sanitized_line)

    If a line doesn't match any sensitive pattern, it's not returned.
    """
    matches = []
    raw = path.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(raw.splitlines(), start=1):
        sanitized = line
        matched = False
        for pattern, replacement in SENSITIVE_PATTERNS:
            if pattern.search(sanitized):
                sanitized = pattern.sub(replacement, sanitized)
                matched = True
        if matched:
            matches.append((i, line.rstrip("\n\r"), sanitized))
    return matches


def redact_file(path: Path, backup_dir: Path) -> int:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    sanitized = raw
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    if sanitized == raw:
        return 0

    # Write to backup dir preserving relative path
    rel = path.relative_to(Path.cwd())
    dest = backup_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(sanitized, encoding="utf-8")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan and optionally sanitize archives for hardcoded secrets"
    )
    ap.add_argument("--root", default=".", help="Root path to scan (default: project root)")
    ap.add_argument(
        "--patterns",
        nargs="*",
        default=["archive/**", "debug_*", "**/*.log", "**/*.txt"],
        help="Glob patterns to search for files",
    )
    ap.add_argument(
        "--apply", action="store_true", help="Write sanitized copies to the backup directory"
    )
    ap.add_argument(
        "--backup-dir",
        default="sanitized_archives",
        help="Directory to write sanitized copies into when --apply is set",
    )
    ap.add_argument("--quiet", action="store_true", help="Suppress summary output")

    args = ap.parse_args()
    root = Path(args.root).resolve()
    patterns = args.patterns

    files = find_files(root, patterns)
    total_matches = 0
    files_with_matches: List[Path] = []

    for f in files:
        matches = scan_file(f)
        if matches:
            total_matches += len(matches)
            files_with_matches.append(f)
            if not args.quiet:
                print(f"File: {f}")
                for ln, original, sanitized in matches:
                    print(f"  Line {ln}: {original}")
                    print(f"  => sanitized: {sanitized}")
    if args.apply:
        backup_dir = Path(args.backup_dir).resolve()
        counters = 0
        for f in files_with_matches:
            counters += redact_file(f, backup_dir)
        if not args.quiet:
            print(f"Sanitized {counters} files, results in {backup_dir}")

    if not args.quiet:
        print(
            f"Scanned {len(files)} files, found {total_matches} sensitive occurrences in {len(files_with_matches)} files"
        )
    return 0 if total_matches == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
