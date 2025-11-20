import json
import sys

print("🔧 Fixing dashboard panels for missing exporters...")

# Read the dashboard JSON
with open(
    "monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json",
    "r",
    encoding="utf-8",
) as f:
    dashboard_data = json.load(f)

panels = dashboard_data["dashboard"]["panels"]

# Fix Panel 3 - Redis Status
for panel in panels:
    if panel.get("id") == 3 and panel.get("title") == "Redis Status":
        print("  ✅ Fixing Redis Status panel...")
        # Change to show service count instead of exporter metric
        panel["targets"][0]["expr"] = 'count(up{job=~".*redis.*"}) OR on() vector(0)'
        panel["fieldConfig"]["defaults"]["mappings"] = [
            {"type": "value", "value": 0, "text": "NO EXPORTER"},
            {"type": "value", "value": 1, "text": "MONITORED"},
        ]
        panel["fieldConfig"]["defaults"]["thresholds"]["steps"] = [
            {"value": 0, "color": "orange"},
            {"value": 1, "color": "green"},
        ]
        panel["fieldConfig"]["defaults"]["noValue"] = "No Redis Exporter Configured"

    # Fix Panel 4 - PostgreSQL Status
    elif panel.get("id") == 4 and panel.get("title") == "PostgreSQL Status":
        print("  ✅ Fixing PostgreSQL Status panel...")
        # Change to show service count instead of exporter metric
        panel["targets"][0]["expr"] = 'count(up{job=~".*postgres.*"}) OR on() vector(0)'
        panel["fieldConfig"]["defaults"]["mappings"] = [
            {"type": "value", "value": 0, "text": "NO EXPORTER"},
            {"type": "value", "value": 1, "text": "MONITORED"},
        ]
        panel["fieldConfig"]["defaults"]["thresholds"]["steps"] = [
            {"value": 0, "color": "orange"},
            {"value": 1, "color": "green"},
        ]
        panel["fieldConfig"]["defaults"]["noValue"] = "No PostgreSQL Exporter Configured"

    # Fix Panel 5 - API Request Rate
    elif panel.get("id") == 5 and panel.get("title") == "API Request Rate (req/s)":
        print("  ✅ Fixing API Request Rate panel...")
        # Ensure correct query with proper labels
        panel["targets"][0][
            "expr"
        ] = 'sum(rate(http_requests_total{job="twisterlab-api"}[1m])) by (method, endpoint)'
        panel["targets"][0]["legendFormat"] = "{{method}} {{endpoint}}"
        # Add fallback for no data
        if "fieldConfig" not in panel:
            panel["fieldConfig"] = {"defaults": {}}
        if "defaults" not in panel["fieldConfig"]:
            panel["fieldConfig"]["defaults"] = {}
        panel["fieldConfig"]["defaults"]["noValue"] = "No HTTP Traffic"

# Increment version
dashboard_data["dashboard"]["version"] = 5

# Save the updated dashboard
with open(
    "monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(dashboard_data, f, indent=2)

print("\n✅ Dashboard fixed successfully!")
print("   - Redis Status: Shows 'NO EXPORTER' in orange")
print("   - PostgreSQL Status: Shows 'NO EXPORTER' in orange")
print("   - API Request Rate: Fixed query with fallback")
print("   - Version: 5")
