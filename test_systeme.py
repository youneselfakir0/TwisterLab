#!/usr/bin/env python3
"""Test système TwisterLab - Validation rapide"""

import asyncio
import sys

import aiohttp

API_URL = "http://localhost:8000"


async def test_api():
    """Test 1/4: API active"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/health", timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    print("✅ API: OK")
                    return True
    except Exception as e:
        print(f"❌ API: ERREUR ({e})")
        return False


async def test_agents():
    """Test 2/4: Agents disponibles"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/v1/autonomous/agents",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    count = data.get("total", 0)
                    print(f"✅ Agents: {count}/7 actifs")
                    return count >= 7
    except Exception as e:
        print(f"❌ Agents: ERREUR ({e})")
        return False


async def test_monitoring():
    """Test 3/4: Agent monitoring"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"operation": "health_check"}
            async with session.post(
                f"{API_URL}/api/v1/autonomous/agents/MonitoringAgent/execute",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    print("✅ Monitoring: OK")
                    return True
    except Exception as e:
        print(f"❌ Monitoring: ERREUR ({e})")
        return False


async def test_maestro():
    """Test 4/4: Orchestration Maestro"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"operation": "assess_situation"}
            async with session.post(
                f"{API_URL}/api/v1/autonomous/agents/MaestroOrchestratorAgent/execute",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    print("✅ Maestro: OK")
                    return True
    except Exception as e:
        print(f"❌ Maestro: ERREUR ({e})")
        return False


async def main():
    print(f"\n{'=' * 50}")
    print("🚀 TWISTERLAB - TEST SYSTÈME RAPIDE")
    print(f"{'=' * 50}\n")

    results = []
    results.append(await test_api())
    results.append(await test_agents())
    results.append(await test_monitoring())
    results.append(await test_maestro())

    success = sum(results)
    total = len(results)

    print(f"\n{'=' * 50}")
    print(f"📊 RÉSULTAT: {success}/{total} tests réussis")
    print(f"{'=' * 50}\n")

    if success == total:
        print("🎉 SYSTÈME 100% OPÉRATIONNEL\n")
        sys.exit(0)
    elif success >= 2:
        print("⚠️  SYSTÈME PARTIELLEMENT OPÉRATIONNEL\n")
        sys.exit(1)
    else:
        print("❌ SYSTÈME NON OPÉRATIONNEL\n")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
