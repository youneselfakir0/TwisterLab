#!/usr/bin/env python3
"""
Import updated Grafana dashboard with agent metrics.
"""
import json
import sys
import requests
from pathlib import Path

GRAFANA_URL = "http://192.168.0.30:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"

def import_dashboard(dashboard_path: str) -> bool:
    """Import dashboard JSON to Grafana."""

    # Read dashboard JSON
    with open(dashboard_path, 'r') as f:
        dashboard_json = json.load(f)

    # Prepare API request
    url = f"{GRAFANA_URL}/api/dashboards/db"
    headers = {"Content-Type": "application/json"}
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)

    print(f"📊 Importing dashboard: {dashboard_json['dashboard']['title']}")
    print(f"🌐 Grafana URL: {url}")

    try:
        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            json=dashboard_json,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard imported successfully!")
            print(f"   - ID: {result.get('id')}")
            print(f"   - UID: {result.get('uid')}")
            print(f"   - URL: {result.get('url')}")
            print(f"   - Version: {result.get('version')}")
            return True
        else:
            print(f"❌ Failed to import dashboard")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Grafana at {GRAFANA_URL}")
        print(f"   - Check if Grafana is running")
        print(f"   - Verify URL and network connectivity")
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
