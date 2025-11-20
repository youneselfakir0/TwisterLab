#!/usr/bin/env python3
"""
TwisterLab API Server Startup Script
"""

import os
import subprocess
import sys
import time


def start_api_server() -> None:
    """Start the FastAPI server"""
    print("🚀 Starting TwisterLab API Server...")

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = "c:\\TwisterLab"

    try:
        # Start the server
        cmd = 'from agents.api.main import app; import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)'
        process = subprocess.Popen(
            [sys.executable, "-c", cmd],
            cwd="c:\\TwisterLab",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        print("✅ Server process started")
        print(f"   PID: {process.pid}")
        print("   URL: http://localhost:8000")
        print("   Health: http://localhost:8000/health")
        print("   API Docs: http://localhost:8000/docs")
        print()

        # Wait a bit for server to start
        time.sleep(3)

        # Check if server is still running
        if process.poll() is None:
            print("✅ Server appears to be running successfully!")
            print("Press Ctrl+C to stop the server")

            try:
                # Keep the process running
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")
        else:
            # Server crashed
            stdout, stderr = process.communicate()
            print("❌ Server failed to start:")
            if stdout:
                print("STDOUT:", stdout)
            if stderr:
                print("STDERR:", stderr)

    except Exception as e:
        print(f"❌ Failed to start server: {e}")


if __name__ == "__main__":
    start_api_server()
