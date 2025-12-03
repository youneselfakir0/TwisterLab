from fastapi import FastAPI

from twisterlab.api.routes import agents, mcp, system

app = FastAPI(title="TwisterLab API", version="1.0")

app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])


@app.get("/")
async def root():
    return {"message": "Welcome to the TwisterLab API!"}
