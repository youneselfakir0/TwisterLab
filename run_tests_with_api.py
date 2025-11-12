#!/usr/bin/env python3
"""
Temporary script to run autonomous agents tests with API
"""

import subprocess
import sys
import time


def main():
    # Start API in background
    api_process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            'import uvicorn; from agents.api.main import app; uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for API to start
    time.sleep(3)

    try:
        # Run tests
        result = subprocess.run(
            [sys.executable, "test_autonomous_agents.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # Run tests
        result = subprocess.run(
            [sys.executable, "test_autonomous_agents.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print("Return code:", result.returncode)

        # Print detailed results
        print("\n=== DETAILED ERROR ANALYSIS ===")
        # Let's run a simple curl test to see if API is responding
        try:
            import subprocess as sp

            health_result = sp.run(
                ["curl", "-s", "http://localhost:8000/api/v1/health"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            print(f"Health endpoint response: {health_result.stdout[:500]}...")
            if health_result.stderr:
                print(f"Health endpoint error: {health_result.stderr}")
        except Exception as e:
            print(f"Could not test health endpoint: {e}")
    finally:
        # Stop API
        api_process.terminate()
        api_process.wait()


if __name__ == "__main__":
    main()
