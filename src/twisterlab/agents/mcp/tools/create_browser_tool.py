import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from twisterlang.codec import build_message, validate_message

router = APIRouter()


class CreateBrowserToolRequest(BaseModel):
    tool_name: str
    target_url: str
    llm_backend: str


class CreateBrowserToolResponse(BaseModel):
    status: str
    tool_name: str
    page_loaded: bool
    snapshots: list
    llm_summary: dict
    logs_key: str


@router.post("/create_browser_tool", response_model=CreateBrowserToolResponse)
async def create_browser_tool(request: CreateBrowserToolRequest):
    correlation_id = str(uuid.uuid4())

    # Build the message to send to the BrowserAgent
    message = build_message(
        tool_name=request.tool_name,
        target_url=request.target_url,
        llm_backend=request.llm_backend,
        correlation_id=correlation_id,
    )

    # Validate the message
    if not validate_message(message):
        raise HTTPException(status_code=400, detail="Invalid message format")

    # Simulate the tool creation process (replace with actual logic)
    response = {
        "status": "success",
        "tool_name": request.tool_name,
        "page_loaded": True,
        "snapshots": [
            {"timestamp": "2025-01-01T00:00:00Z", "content_summary": "Sample summary"}
        ],
        "llm_summary": {
            "model": request.llm_backend,
            "temperature": 0.5,
            "summary": "Sample summary",
        },
        "logs_key": f"redis:agent:{request.tool_name}:logs:{correlation_id}",
    }

    return response
