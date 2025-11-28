from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ExecuteRequest(BaseModel):
    tool_name: str
    args: dict | None = None


@router.post("/execute")
async def execute_tool(req: ExecuteRequest):
    # Minimal stub for MCP execution used in tests / dev environment.
    try:
        # Simulate execution response
        return {
            "status": "success",
            "result": {"executed_tool": req.tool_name, "args": req.args},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    return {"status": "MCP server is running"}
