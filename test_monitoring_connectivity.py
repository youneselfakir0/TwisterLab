#!/usr/bin/env python3
"""
Test script for monitoring services connectivity
"""

import asyncio
import os
import sys

# Add agents to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.real.real_monitoring_agent import RealMonitoringAgent


async def test_monitoring_agent():
    """Test the RealMonitoringAgent port checking functionality"""
    print("🧪 Testing RealMonitoringAgent port connectivity...")

    agent = RealMonitoringAgent()

    # Test port checking
    result = await agent._check_ports()

    print(f"Status: {result['status']}")
    print(f"Total ports checked: {result['total_ports']}")
    print(f"Open ports: {result['open_ports']}")
    print(f"Closed ports: {result['closed_ports']}")

    print("\nPort details:")
    for port, info in result["ports"].items():
        status = "✅" if info["accessible"] else "❌"
        host = info.get("host", "unknown")
        print(f"  {port} ({info['service']}) on {host}: {status} {info['status']}")

    # Test Docker services check
    print("\n🐳 Testing Docker services...")
    docker_result = await agent._check_docker_services()
    print(f"Docker status: {docker_result['status']}")
    print(
        f"Running services: {docker_result['running_services']}/{docker_result['total_services']}"
    )

    return result


if __name__ == "__main__":
    asyncio.run(test_monitoring_agent())
