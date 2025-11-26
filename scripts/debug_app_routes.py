from fastapi.testclient import TestClient

from twisterlab.api.main import app

client = TestClient(app)
print("ROUTES:")
for route in app.router.routes:
    try:
        print(route.path)
    except Exception:
        print("--- route with no path", route)

print("\nMounted mounts:")
for route in app.router.routes:
    if hasattr(route, "name") and "static" in route.name.lower():
        print("Static route", route.path)
