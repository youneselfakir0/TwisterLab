import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define request and response models
class JsonRpcRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: Any


class JsonRpcResponse(BaseModel):
    jsonrpc: str
    result: Any
    id: Any


class JsonRpcError(BaseModel):
    jsonrpc: str
    error: Dict[str, Any]
    id: Any


# JSON-RPC endpoint
@app.post("/api/v1/mcp/execute")
async def execute_method(request: JsonRpcRequest):
    logger.info("Received request: %s", request.model_dump())

    # Example of handling different methods
    if request.method == "example_method":
        result = {"message": "This is an example response."}
        return JsonRpcResponse(jsonrpc="2.0", result=result, id=request.id)

    # Handle unknown method
    error_response = JsonRpcError(
        jsonrpc="2.0",
        error={"code": -32601, "message": "Method not found"},
        id=request.id,
    )
    logger.error(f"Method not found: {request.method}")
    raise HTTPException(status_code=404, detail=error_response.model_dump())


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
