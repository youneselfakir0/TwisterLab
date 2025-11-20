#!/usr/bin/env python3
"""
Minimal FastAPI test
"""

import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    logger.info("Starting minimal FastAPI server with built-in server...")
    import uvicorn

    uvicorn.run("test_minimal:app", host="127.0.0.1", port=8001, log_level="info")
