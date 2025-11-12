#!/usr/bin/env python3
import subprocess
import sys
import time

# Start API
api_process = subprocess.Popen(
    [
        sys.executable,
        "-c",
        'import uvicorn; from agents.api.main import app; uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")',
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

time.sleep(3)

try:
    # Test execute endpoint
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:8000/api/v1/autonomous/agents/monitoring/execute",
            "-H",
            "Content-Type: application/json",
            "-d",
            '{"operation": "check_system_health", "params": {}}',
        ],
        capture_output=True,
        text=True,
    )
    print("Execute endpoint response:", repr(result.stdout.strip()))

finally:
    api_process.terminate()
    api_process.wait()
