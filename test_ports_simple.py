#!/usr/bin/env python3
"""
Simple test for monitoring agent port connectivity
"""

import asyncio
import os
import socket
import sys

# Add agents to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Simple test without importing the full agent
async def test_port_connectivity():
    """Test port connectivity logic directly"""
    print("🧪 Testing port connectivity logic...")

    # Expected ports and hosts (like in the updated agent)
    expected_ports = {
        "8000": "API",
        "5432": "PostgreSQL",
        "6379": "Redis",
        "9090": "Prometheus",
        "3000": "Grafana",
        "11434": "Ollama",
    }

    # Service hosts (Docker service names)
    service_hosts = {
        "8000": "api",
        "5432": "postgres",
        "6379": "redis",
        "9090": "prometheus",
        "3000": "grafana",
        "11434": "ollama",
    }

    ports_status = {}

    for port, service_name in expected_ports.items():
        host = service_hosts.get(port, "127.0.0.1")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        try:
            result = sock.connect_ex((host, int(port)))
            is_open = result == 0
            ports_status[port] = {
                "service": service_name,
                "host": host,
                "status": "open" if is_open else "closed",
                "accessible": is_open,
            }
        except Exception as e:
            ports_status[port] = {
                "service": service_name,
                "host": host,
                "status": "error",
                "accessible": False,
                "error": str(e),
            }
        finally:
            sock.close()

    open_ports = [p for p, s in ports_status.items() if s["accessible"]]
    closed_ports = [p for p, s in ports_status.items() if not s["accessible"]]

    print(f"Status: {'healthy' if len(closed_ports) == 0 else 'degraded'}")
    print(f"Total ports checked: {len(ports_status)}")
    print(f"Open ports: {len(open_ports)}")
    print(f"Closed ports: {len(closed_ports)}")

    print("\nPort details:")
    for port, info in ports_status.items():
        status = "✅" if info["accessible"] else "❌"
        host = info.get("host", "unknown")
        print(f"  {port} ({info['service']}) on {host}: {status} {info['status']}")

    return ports_status


if __name__ == "__main__":
    asyncio.run(test_port_connectivity())
