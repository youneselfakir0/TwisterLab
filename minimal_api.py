#!/usr/bin/env python3
"""
Minimal API test - Just uvicorn with a simple app
"""

from fastapi import FastAPI

app = FastAPI(title="Minimal Test API")

@app.get("/")
async def root():
    return {"message": "Minimal API is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting minimal API on port 8003...")
    uvicorn.run(app, host="127.0.0.1", port=8003, log_level="info")