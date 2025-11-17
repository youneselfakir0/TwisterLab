#!/usr/bin/env python3
"""
Simple CI secret scanner that fails when inline secrets are detected.

This file is intended to be used alongside an external secret scanner (for
example, the gitleaks action), or as a fallback when the external action
cannot be reliably executed in the runner environment (tag resolution or
mirror problems). The scanner looks for common password patterns in YAML,
env and PowerShell files and uses exclusion rules for secret-backed files
and known patterns (e.g., *_FILE entries that point to Docker secrets).

It returns a non-zero exit status when a potential hard-coded secret is
identified and prints contextual lines to help triage the finding.

Usage:
    python scripts/ci_secret_scan.py

In CI workflows, consider running the external action first and this script
as a double-check to avoid false negatives.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"archive", "backups", ".venv", "venv", "node_modules", ".github"}
EXCLUDE_FILES = {
    "infrastructure/scripts/security.ps1",
    "infrastructure/scripts/security_audit.ps1",
    "deploy-monitoring-full.ps1",
}

PATTERNS = {
    "POSTGRES_PASSWORD": re.compile(r"POSTGRES_PASSWORD\s*[=:]\s*[^\n\r]+", re.IGNORECASE),
    "REDIS_PASSWORD": re.compile(r"REDIS_PASSWORD\s*[=:]\s*[^\n\r]+", re.IGNORECASE),
    "GF_ADMIN": re.compile(r"GF_SECURITY_ADMIN_PASSWORD\s*[=:]\s*[^\n\r]+", re.IGNORECASE),
    "DATABASE_URL_PW": re.compile(r"DATABASE_URL=postgresql://[^:]+:[^@]+@", re.IGNORECASE),
}
IGNORE_PATTERNS = [
    re.compile(r"_FILE", re.IGNORECASE),
    re.compile(r"/run/secrets", re.IGNORECASE),
    re.compile(r"\$\(cat /run/secrets", re.IGNORECASE),
    re.compile(r"\${{\s*secrets\.", re.IGNORECASE),
    re.compile(r"\$\{?GRAFANA_PASSWORD\}?", re.IGNORECASE),
    re.compile(r"\$\{?POSTGRES_PASSWORD\}?", re.IGNORECASE),
    re.compile(r"\$\(|\$\{", re.IGNORECASE),
]


def scan_file(path: Path) -> list[tuple[int, str]]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    results = []
    lines = content.splitlines()
    for i, line in enumerate(lines, start=1):
        for key, p in PATTERNS.items():
            if p.search(line):
                # Ignore _FILE references
                if "_FILE" in line:
                    continue
                results.append((i, line.strip()))
    return results


def main() -> int:
    files_to_scan = (
        list(ROOT.rglob("*.yml"))
        + list(ROOT.rglob("*.yaml"))
        + list(ROOT.rglob("*.env"))
        + list(ROOT.rglob("*.ps1"))
    )
    # Exclude archives, backups and virtualenvs
    files_to_scan = [
        f
        for f in files_to_scan
        if not any(part in EXCLUDE_DIRS for part in f.parts)
        and str(f.relative_to(ROOT)).replace("\\", "/") not in EXCLUDE_FILES
    ]
    hits = 0
    for f in files_to_scan:
        try:
            matches = scan_file(f)
        except Exception:
            continue
        if matches:
            # Filter out those lines that match ignore patterns (file-backed or GH secrets)
            filtered = [m for m in matches if not any(p.search(m[1]) for p in IGNORE_PATTERNS)]
            if not filtered:
                continue
            print(f"Potential secrets in: {f}")
            for ln, line in filtered:
                print(f"  {ln}: {line}")
            matches = filtered
            hits += len(matches)

    if hits > 0:
        print(f"Found {hits} potential hard-coded secrets. Failing CI.")
        return 2

    print("No inline secrets detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
