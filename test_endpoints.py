#!/usr/bin/env python3
import subprocess
import sys
import time

# Start API
api_process = subprocess.Popen(
    [
        sys.executable,
        "-c",
        'import uvicorn; from agents.api.main import app; uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")',
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

time.sleep(5)  # Give more time for startup

# Read startup logs
if api_process.poll() is None:  # Process still running
    print("API started successfully")
else:
    stdout, stderr = api_process.communicate()
    print("API failed to start:")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    sys.exit(1)

try:
    # Test basic health
    result1 = subprocess.run(
        ["curl", "-s", "http://localhost:8000/health"], capture_output=True, text=True
    )
    print("Basic /health:", repr(result1.stdout.strip()))

    # Test API health
    result2 = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/v1/autonomous/health"],
        capture_output=True,
        text=True,
    )
    print("API /api/v1/autonomous/health:", repr(result2.stdout.strip()))

    # Test agents endpoint
    result4 = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/v1/autonomous/agents"],
        capture_output=True,
        text=True,
    )
    print("Agents endpoint:", repr(result4.stdout.strip()))

finally:
    api_process.terminate()
    api_process.wait()
