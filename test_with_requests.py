import threading
import time

import httpx
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8008, log_level="error")


def test_request():
    time.sleep(1)  # Wait for server to start
    try:
        with httpx.Client() as client:
            response = client.get("http://127.0.0.1:8008/")
            print(f"Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Test the request
    test_request()

    print("Test completed")
