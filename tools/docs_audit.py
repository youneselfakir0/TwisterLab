"""
Docs audit script for TwisterLab
- Scans the repository for .md and .txt files
- Computes H1/title, SHA256 hash, file size
- Outputs JSON and CSV reports in tools/reports/

Usage:
  python tools/docs_audit.py
"""

import os
import re
import json
import hashlib
import csv
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "tools" / "reports"
PATTERNS = ("*.md", "*.txt")
IGNORE_DIRS = ("docs/archive", ".git", "__pycache__", "node_modules", "venv", "dist")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def extract_title(path: Path) -> str:
    first_lines = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for _ in range(8):
                line = fh.readline()
                if not line:
                    break
                first_lines.append(line.rstrip("\n"))
    except Exception:
        return ""

    # match markdown H1/H2 or first non-empty line
    for l in first_lines:
        m = re.match(r'^\s*#\s+(.*)', l)
        if m:
            return m.group(1).strip()
    for l in first_lines:
        if l.strip():
            return l.strip()
    return ""


def scan_repo(root: Path) -> List[Dict[str, Any]]:
    results = []
    for pattern in PATTERNS:
        for path in root.rglob(pattern):
            # ignore some directories
            if any(ig in str(path) for ig in IGNORE_DIRS):
                continue
            try:
                h = file_hash(path)
                title = extract_title(path)
                relpath = path.relative_to(root)
                results.append({
                    "path": str(relpath).replace("\\", "/"),
                    "size": path.stat().st_size,
                    "hash": h,
                    "title": title,
                })
            except Exception as e:
                results.append({
                    "path": str(path),
                    "error": str(e)
                })
    return results


def build_report(entries: List[Dict[str, Any]]):
    if not OUT_DIR.exists():
        OUT_DIR.mkdir(parents=True, exist_ok=True)
    rep_json = OUT_DIR / "docs_inventory.json"
    with rep_json.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2, ensure_ascii=False)
    # duplicates
    hash_map = {}
    for e in entries:
        if "hash" not in e:
            continue
        hash_map.setdefault(e["hash"], []).append(e)
    duplicates = [v for v in hash_map.values() if len(v) > 1]
    csv_path = OUT_DIR / "duplicate_docs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["hash", "count", "paths", "title", "total_size"])
        for group in duplicates:
            paths = [g["path"] for g in group]
            size = sum(g.get("size", 0) for g in group)
            title = group[0].get("title", "")
            writer.writerow([group[0]["hash"], len(group), ";".join(paths), title, size])
    print(f"Report written to {rep_json} and {csv_path}")


def main():
    print(f"Scanning repo: {REPO_ROOT}")
    entries = scan_repo(REPO_ROOT)
    build_report(entries)
    print("Done.")


if __name__ == "__main__":
    main()
