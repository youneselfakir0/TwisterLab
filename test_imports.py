# test_imports.py - Script pour tester les imports Python
import sys
import importlib

modules_to_test = ["fastapi", "uvicorn", "sqlalchemy", "alembic", "pytest", "asyncpg"]

success_count = 0
for module in modules_to_test:
    try:
        importlib.import_module(module)
        print(f"OK - {module}")
        success_count += 1
    except ImportError as e:
        print(f"ECHEC - {module}: {e}")
    except Exception as e:
        print(f"ERREUR - {module}: {e}")

if success_count == len(modules_to_test):
    sys.exit(0)
else:
    sys.exit(1)