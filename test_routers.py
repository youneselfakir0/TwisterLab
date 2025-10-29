#!/usr/bin/env python3
"""
Test individual router imports
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_router_import(router_name, import_path):
    """Test importing a specific router"""
    try:
        print(f"📦 Testing {router_name}...")
        __import__(import_path)
        print(f"    ✅ {router_name} imported successfully")
        return True
    except Exception as e:
        print(f"    ❌ {router_name} import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all routers"""
    print("🔍 Testing router imports...")

    routers = [
        ("Tickets Router", "agents.api.routes_tickets"),
        ("Agents Router", "agents.api.routes_agents"),
        ("SOPs Router", "agents.api.routes_sops"),
        ("Orchestrator Router", "agents.api.routes_orchestrator"),
    ]

    all_good = True
    for name, path in routers:
        if not test_router_import(name, path):
            all_good = False

    if all_good:
        print("\n✅ All routers imported successfully")
    else:
        print("\n❌ Some routers failed to import")

if __name__ == "__main__":
    main()