from pathlib import Path

from fastapi import FastAPI
from fastapi import Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from ..tracing import configure_tracer
from .routes import agents, browser, mcp, system

configure_tracer("twisterlab-api")

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(browser.router, prefix="/api/v1/browser", tags=["browser"])


@app.get("/")
async def root():
    return {"message": "Welcome to TwisterLab API"}


# Mount the simple UI (if present). Support both the package-relative path (src/twisterlab/ui/browser)
# and a more generic src/ui/browser path used in other environments.
pkg_ui = Path(__file__).resolve().parents[1] / "ui" / "browser"
generic_ui = Path(__file__).resolve().parents[2] / "ui" / "browser"
STATIC_UI = pkg_ui if pkg_ui.exists() else generic_ui
if STATIC_UI.exists():
    app.mount("/ui", StaticFiles(directory=str(STATIC_UI), html=True), name="ui")


# Ensure /metrics exists even if optional prometheus instrumentator is not installed.
# This is a lightweight runtime handler that attempts to use prometheus_client if available
# but otherwise returns a simple text body. Adding the route at module import time makes it
# available during TestClient initialization and in the container runtime prior to startup.
def _metrics_view():
    try:
        from prometheus_client import CONTENT_TYPE_LATEST  # type: ignore
        from prometheus_client import generate_latest

        payload = generate_latest()
        return FastAPIResponse(content=payload, media_type=CONTENT_TYPE_LATEST)
    except Exception:
        # Fallback minimal text for tests/CI when prometheus_client isn't present
        return FastAPIResponse(
            content=b"# metrics unavailable\n", media_type="text/plain"
        )


if not any(getattr(route, "path", None) == "/metrics" for route in app.router.routes):
    app.add_api_route("/metrics", _metrics_view, methods=["GET"])


@app.on_event("startup")
async def startup():
    # Create DB tables if they are not present.
    # Import models module to ensure ORM models are registered with Base
    import twisterlab.database.models.agent  # noqa: F401
    from twisterlab.database.session import Base, engine

    Base.metadata.create_all(bind=engine)
    # Register monitoring metrics in a guarded way
    try:
        from twisterlab.monitoring import register_with_app

        register_with_app(app)
    except Exception:
        pass
    # Integrate Prometheus Instrumentator in a guarded manner
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        if not getattr(app.state, "_instrumentator_attached", False):
            instr = Instrumentator()
            instr.instrument(app)
            app.state._instrumentator_attached = True
    except Exception:
        # Instrumentator is optional; ignore if not installed
        pass
    # If instrumentator is not available, fall back to exposing /metrics using prometheus_client.
    try:
        from fastapi import Response as FastAPIResponse
        from prometheus_client import CONTENT_TYPE_LATEST  # type: ignore
        from prometheus_client import generate_latest

        if not any(
            getattr(route, "path", None) == "/metrics" for route in app.router.routes
        ):

            def _metrics_view():
                payload = generate_latest()
                return FastAPIResponse(content=payload, media_type=CONTENT_TYPE_LATEST)

            app.add_api_route("/metrics", _metrics_view, methods=["GET"])
    except Exception:
        pass
