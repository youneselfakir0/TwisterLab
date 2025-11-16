# Test API startup issues
import sys
import traceback

try:
    print("Testing API import...")
    from agents.api.main import app

    print("✅ API import successful")

    print("Testing CORS...")
    from fastapi.middleware.cors import CORSMiddleware

    print("✅ CORS import successful")

    print("Testing routes...")
    from agents.api.routes_tickets import router as tickets_router

    print("✅ Tickets router import successful")

    print("Testing app creation...")
    # Test basic app creation without middleware
    from fastapi import FastAPI

    test_app = FastAPI()
    print("✅ Basic FastAPI app creation successful")

    print("All imports successful!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
