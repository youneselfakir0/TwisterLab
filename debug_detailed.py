#!/usr/bin/env python3
"""
TwisterLab API Debug Script - Detailed Error Analysis
"""

import os
import sys
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test all imports step by step"""
    print("🔍 Testing imports...")

    try:
        print("  📦 Testing FastAPI...")
        from fastapi import FastAPI

        print("    ✅ FastAPI imported")

        print("  📦 Testing database config...")
        from agents.database.config import engine, get_db

        print("    ✅ Database config imported")

        print("  📦 Testing monitoring...")
        from agents.api.monitoring import MetricsMiddleware, setup_logging

        print("    ✅ Monitoring imported")

        print("  📦 Testing security...")
        from agents.api.security import setup_security_middleware

        print("    ✅ Security imported")

        print("  📦 Testing routes...")
        from agents.api.routes_agents import router as agents_router
        from agents.api.routes_orchestrator import router as orchestrator_router
        from agents.api.routes_sops import router as sops_router
        from agents.api.routes_tickets import router as tickets_router

        print("    ✅ All routes imported")

        print("  📦 Testing main app...")
        from agents.api.main import app

        print("    ✅ Main app imported")

        return True

    except Exception as e:
        print(f"    ❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")

    try:
        import asyncio

        from agents.database.config import async_session

        async def test_db():
            async with async_session() as session:
                from sqlalchemy import text

                result = await session.execute(text("SELECT 1"))
                return result.scalar()

        result = asyncio.run(test_db())
        print(f"  ✅ Database connection successful: {result}")
        return True

    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        traceback.print_exc()
        return False


def test_app_creation():
    """Test FastAPI app creation step by step"""
    print("\n🔍 Testing app creation...")

    try:
        from fastapi import FastAPI

        from agents.api.monitoring import MetricsMiddleware, setup_logging
        from agents.api.routes_agents import router as agents_router
        from agents.api.routes_orchestrator import router as orchestrator_router
        from agents.api.routes_sops import router as sops_router
        from agents.api.routes_tickets import router as tickets_router
        from agents.api.security import setup_security_middleware

        # Configure logging
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE", "logs/twisterlab.log")
        logger = setup_logging(log_level=log_level, log_file=log_file)

        print("  📦 Creating FastAPI app...")
        app = FastAPI(
            title="TwisterLab API",
            description="AI-powered IT Helpdesk automation platform",
            version="1.0.0-alpha.1",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
        )
        print("    ✅ FastAPI app created")

        print("  📦 Adding monitoring middleware...")
        app.add_middleware(MetricsMiddleware, logger=logger)
        print("    ✅ Monitoring middleware added")

        print("  📦 Adding security middleware...")
        setup_security_middleware(app)
        print("    ✅ Security middleware added")

        print("  📦 Including routers...")
        app.include_router(tickets_router, prefix="/api/v1/tickets", tags=["tickets"])
        app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
        app.include_router(sops_router, prefix="/api/v1/sops", tags=["sops"])
        app.include_router(
            orchestrator_router, prefix="/api/v1/orchestrator", tags=["orchestrator"]
        )
        print("    ✅ All routers included")

        return app

    except Exception as e:
        print(f"  ❌ App creation error: {e}")
        traceback.print_exc()
        return None


def main():
    """Main debug function"""
    print("🚀 TwisterLab API Debug Script")
    print("=" * 50)

    # Test environment
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Cannot continue.")
        return 1

    # Test database
    if not test_database_connection():
        print("\n❌ Database tests failed. Cannot continue.")
        return 1

    # Test app creation
    app = test_app_creation()
    if app is None:
        print("\n❌ App creation failed. Cannot continue.")
        return 1

    print("\n✅ All tests passed! App created successfully.")
    print("🌐 Attempting to start server...")

    # Try to start server
    try:
        import uvicorn

        print("📡 Starting uvicorn server on http://127.0.0.1:8004...")

        # Run server (this will block)
        uvicorn.run(app, host="127.0.0.1", port=8004, log_level="info")

    except Exception as e:
        print(f"❌ Server startup error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
