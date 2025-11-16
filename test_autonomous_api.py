#!/usr/bin/env python3
"""
Quick test for autonomous API endpoints
"""

import asyncio
import threading

import aiohttp
import uvicorn


async def test_api():
    """Test autonomous API endpoints."""

    # Start API in background thread
    def start_api():
        uvicorn.run("agents.api.main:app", host="127.0.0.1", port=8001, log_level="error")

    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # Wait for API to start
    await asyncio.sleep(3)

    try:
        async with aiohttp.ClientSession() as session:
            # Test status endpoint
            async with session.get("http://127.0.0.1:8001/api/v1/autonomous/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Autonomous API is responding")
                    print(f"Status: {data.get('status')}")
                    print(f"Agent count: {data.get('agents_count')}")
                    print(f"Scheduled tasks: {data.get('scheduled_tasks_count')}")
                else:
                    print(f"❌ Status endpoint returned {response.status}")

            # Test agents endpoint
            async with session.get("http://127.0.0.1:8001/api/v1/autonomous/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Agents endpoint working")
                    print(f"Found {len(data.get('agents', []))} agents")
                else:
                    print(f"❌ Agents endpoint returned {response.status}")

    except Exception as e:
        print(f"❌ API test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_api())
