import json
import sys

# Read the dashboard JSON
with open(
    "monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json",
    "r",
    encoding="utf-8",
) as f:
    dashboard_data = json.load(f)


# Update all panels to use the correct datasource format
def update_datasource(obj):
    if isinstance(obj, dict):
        if "datasource" in obj and obj["datasource"] == "Prometheus":
            obj["datasource"] = {"type": "prometheus", "uid": "df3qqymva25tsb"}
        for key, value in obj.items():
            update_datasource(value)
    elif isinstance(obj, list):
        for item in obj:
            update_datasource(item)


# Update the dashboard
update_datasource(dashboard_data)

# Save the updated dashboard
with open(
    "monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(dashboard_data, f, indent=2)

print("✅ Dashboard updated with correct datasource format")
print("   Datasource: { type: 'prometheus', uid: 'df3qqymva25tsb' }")
