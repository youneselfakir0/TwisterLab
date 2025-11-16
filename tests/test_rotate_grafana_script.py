import os
import shlex
import shutil
import subprocess
import sys

import pytest

PW = os.environ.get("POWERSHELL_EXE", None)
if not PW:
    PW = shutil.which("pwsh") or shutil.which("powershell")
    if not PW:
        raise RuntimeError("PowerShell (pwsh or powershell) is required to run tests")


def run_ps_script(args):
    cmd = [PW, "-NoLogo", "-NoProfile", "-File"] + args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    return proc


def test_use_service_name_override():
    proc = run_ps_script(
        [
            "scripts/rotate_grafana_secret.ps1",
            "-DryRun",
            "-ServiceName",
            "grafana_test",
            "-RestartService",
        ]
    )
    assert proc.returncode == 0
    assert "Using provided service name: grafana_test" in proc.stdout


def test_autodetect_single_candidate():
    proc = run_ps_script(
        [
            "scripts/rotate_grafana_secret.ps1",
            "-DryRun",
            "-TestServiceList",
            "grafana",
            "-RestartService",
        ]
    )
    assert proc.returncode == 0
    assert "Auto-detected Grafana service name: grafana" in proc.stdout


def test_autodetect_prefers_port_3000():
    # Provide two candidates and indicate that grafanaB exposes port 3000
    proc = run_ps_script(
        [
            "scripts/rotate_grafana_secret.ps1",
            "-DryRun",
            "-TestServiceList",
            "grafanaA,grafanaB",
            "-TestServicePortMap",
            "grafanaB:3000",
            "-RestartService",
        ]
    )
    assert proc.returncode == 0
    assert "Auto-detected Grafana service name: grafanaB" in proc.stdout
