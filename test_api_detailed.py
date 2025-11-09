# Detailed API startup test
import sys
import traceback
import time

def test_step(description, func):
    print(f"Testing: {description}...")
    try:
        result = func()
        print(f"✅ {description}: SUCCESS")
        return result
    except Exception as e:
        print(f"❌ {description}: FAILED - {e}")
        traceback.print_exc()
        return None

def test_imports():
    # Test all imports
    import os
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    from agents.api.routes_tickets import router as tickets_router
    from agents.api.routes_agents import router as agents_router
    from agents.api.routes_sops import router as sops_router
    from agents.api.routes_orchestrator import router as orchestrator_router
    from agents.monitoring import setup_logging, MetricsMiddleware, create_health_endpoint
    from agents.security import setup_security_middleware

def test_app_creation():
    from fastapi import FastAPI
    app = FastAPI(title="Test API", version="1.0.0")
    return app

def test_middleware_addition():
    from fastapi import FastAPI
    from agents.monitoring import MetricsMiddleware
    from agents.security import setup_security_middleware

    app = FastAPI()
    app.add_middleware(MetricsMiddleware, logger=None)
    setup_security_middleware(app)
    return app

def test_router_inclusion():
    from fastapi import FastAPI
    from agents.api.routes_tickets import router as tickets_router

    app = FastAPI()
    app.include_router(tickets_router, prefix="/api/v1/tickets", tags=["tickets"])
    return app

def test_full_app():
    from agents.api.main import app
    return app

if __name__ == "__main__":
    print("🔍 DETAILED API STARTUP DIAGNOSTIC")
    print("=" * 50)

    # Run all tests
    test_step("Basic imports", test_imports)
    test_step("FastAPI app creation", test_app_creation)
    test_step("Middleware addition", test_middleware_addition)
    test_step("Router inclusion", test_router_inclusion)
    test_step("Full app creation", test_full_app)

    print("\n🏁 Diagnostic complete!")