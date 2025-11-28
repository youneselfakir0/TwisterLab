#!/usr/bin/env python3
"""Simple secret scan helper: detect-secrets (if installed) and gitleaks via Docker.
Writes reports to reports/ in the project root.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def run_detect_secrets() -> dict:
    try:
        subprocess.run(["detect-secrets", "--version"], check=True, capture_output=True)
    except Exception:
        return {"detect_secrets": "not_installed"}
    baseline = REPORTS_DIR / ".secrets.baseline"
    try:
        # Older/newer CLI differs; capture stdout to baseline file
        with open(baseline, "w", encoding="utf-8") as fh:
            subprocess.run(["detect-secrets", "scan"], cwd=ROOT, stdout=fh, check=True)
        return {"detect_secrets": str(baseline)}
    except Exception as e:
        return {"detect_secrets": f"failed: {e}"}


def run_gitleaks() -> dict:
    report = REPORTS_DIR / "gitleaks-report.json"
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/repo",
        "zricethezav/gitleaks:latest",
        "detect",
        "--source",
        "/repo",
        "--report-format",
        "json",
        "--report-path",
        f"/repo/{report.name}",
    ]
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except Exception:
        return {"gitleaks": "docker_missing"}
    try:
        subprocess.run(cmd, check=True)
        return {"gitleaks": str(report)}
    except Exception as e:
        return {"gitleaks": f"failed: {e}"}


def main() -> None:
    out = {"detect_secrets": None, "gitleaks": None}
    out.update(run_detect_secrets())
    out.update(run_gitleaks())
    summary_file = REPORTS_DIR / "secrets-scan-summary.json"
    summary_file.write_text(json.dumps(out, indent=2))
    print("Secret scan completed. Reports written to:", REPORTS_DIR)


if __name__ == "__main__":
    main()
