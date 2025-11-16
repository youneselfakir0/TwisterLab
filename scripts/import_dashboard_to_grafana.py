#!/usr/bin/env python3
"""
Import updated Grafana dashboard with agent metrics.
"""

import json
import os
import sys
from pathlib import Path

import requests

GRAFANA_URL = "http://192.168.0.30:3000"
GRAFANA_USER = "admin"


def get_grafana_password() -> str:
    secret_path = "/run/secrets/grafana_admin_password"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    password = os.getenv("GRAFANA_ADMIN_PASSWORD")
    if password:
        return password
    # Do not fallback to insecure default - require a secret be present
    raise RuntimeError(
        "Grafana admin password not set; set GRAFANA_ADMIN_PASSWORD or "
        "create Docker secret 'grafana_admin_password'."
    )


def import_dashboard(dashboard_path: str) -> bool:
    """Import dashboard JSON to Grafana."""

    # Read dashboard JSON
    with open(dashboard_path, "r") as f:
        dashboard_json = json.load(f)

    # Prepare API request
    url = f"{GRAFANA_URL}/api/dashboards/db"
    headers = {"Content-Type": "application/json"}
    # Resolve Grafana password at runtime to avoid import-time errors
    grafana_password = get_grafana_password()
    auth = (GRAFANA_USER, grafana_password)

    dashboard_title = dashboard_json["dashboard"]["title"]
    print("📊 Importing dashboard: {}".format(dashboard_title))
    print("🌐 Grafana URL: {}".format(url))

    try:
        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            json=dashboard_json,
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Dashboard imported successfully!")
            print(f"   - ID: {result.get('id')}")
            print(f"   - UID: {result.get('uid')}")
            print(f"   - URL: {result.get('url')}")
            print(f"   - Version: {result.get('version')}")
            return True
        else:
            print("❌ Failed to import dashboard")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Grafana at {}".format(GRAFANA_URL))
        print("   - Check if Grafana is running")
        print("   - Verify URL and network connectivity")
        return False

    except Exception as e:
        print(f"❌ Error importing dashboard: {e}")
        return False


if __name__ == "__main__":
    dashboard_path = "monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json"

    if not Path(dashboard_path).exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        sys.exit(1)

    success = import_dashboard(dashboard_path)
    sys.exit(0 if success else 1)
