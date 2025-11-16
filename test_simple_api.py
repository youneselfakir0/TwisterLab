#!/usr/bin/env python3
"""
Simple API Test - Minimal FastAPI app
"""

from fastapi import FastAPI

app = FastAPI(title="Test API", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Hello World", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
