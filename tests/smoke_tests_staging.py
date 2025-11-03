#!/usr/bin/env python3
"""
TwisterLab Staging Smoke Tests
================================

Quick validation tests to verify staging environment is operational.

Tests:
- PostgreSQL connectivity (port 5433)
- Redis connectivity (port 6380)
- API health endpoint (port 8001)
- Ollama LLM service (port 11435)
- Prometheus metrics (port 9092)
- Grafana UI (port 3001)

Usage:
    python tests/smoke_tests_staging.py
    pytest tests/smoke_tests_staging.py -v
"""

import asyncio
import asyncpg
import redis.asyncio as redis
import pytest
import aiohttp
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


# Staging service endpoints
SERVICES = {
    "postgres": {"host": "localhost", "port": 5433, "db": "twisterlab"},
    "redis": {"host": "localhost", "port": 6380},
    "api": {"url": "http://localhost:8001"},
    "ollama": {"url": "http://localhost:11435"},
    "prometheus": {"url": "http://localhost:9092"},
    "grafana": {"url": "http://localhost:3001"},
}


@pytest.mark.asyncio
async def test_postgres_connectivity():
    """Test PostgreSQL database connectivity"""
    print(f"\n{Colors.BOLD}Testing PostgreSQL (port 5433)...{Colors.ENDC}")
    
    try:
        conn = await asyncpg.connect(
            host=SERVICES["postgres"]["host"],
            port=SERVICES["postgres"]["port"],
            database=SERVICES["postgres"]["db"],
            user="twisterlab",
            password="twisterlab_staging_password",
            timeout=10
        )
        
        # Test query
        result = await conn.fetchval("SELECT version()")
        assert result is not None
        
        # Check tables exist
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        )
        table_names = [t["tablename"] for t in tables]
        
        await conn.close()
        
        print(f"{Colors.OKGREEN}✅ PostgreSQL: Connected successfully")
        print(f"   Database: {SERVICES['postgres']['db']}")
        print(f"   Tables: {len(table_names)}")
        print(f"   Version: {result[:50]}...{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ PostgreSQL: Connection failed - {e}{Colors.ENDC}")
        pytest.fail(f"PostgreSQL connectivity failed: {e}")


@pytest.mark.asyncio
async def test_redis_connectivity():
    """Test Redis connectivity"""
    print(f"\n{Colors.BOLD}Testing Redis (port 6380)...{Colors.ENDC}")
    
    try:
        r = redis.Redis(
            host=SERVICES["redis"]["host"],
            port=SERVICES["redis"]["port"],
            password="twisterlab_redis_password",
            decode_responses=True,
            socket_timeout=10
        )
        
        # Test ping
        pong = await r.ping()
        assert pong is True
        
        # Test set/get
        await r.set("smoke_test_key", "smoke_test_value", ex=60)
        value = await r.get("smoke_test_key")
        assert value == "smoke_test_value"
        
        # Get server info
        info = await r.info()
        
        await r.close()
        
        print(f"{Colors.OKGREEN}✅ Redis: Connected successfully")
        print(f"   Version: {info.get('redis_version', 'unknown')}")
        print(f"   Uptime: {info.get('uptime_in_seconds', 0)}s")
        print(f"   Connected clients: {info.get('connected_clients', 0)}{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Redis: Connection failed - {e}{Colors.ENDC}")
        pytest.fail(f"Redis connectivity failed: {e}")


@pytest.mark.asyncio
async def test_api_health():
    """Test TwisterLab API health endpoint"""
    print(f"\n{Colors.BOLD}Testing API (port 8001)...{Colors.ENDC}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Health check
            async with session.get(
                f"{SERVICES['api']['url']}/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                assert response.status == 200
                health = await response.json()
                
                print(f"{Colors.OKGREEN}✅ API: Health check passed")
                print(f"   Status: {health.get('status', 'unknown')}")
                print(f"   Version: {health.get('version', 'unknown')}")
                print(f"   Uptime: {health.get('uptime', 0)}s{Colors.ENDC}")
                
            # Test API docs
            async with session.get(
                f"{SERVICES['api']['url']}/docs",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                assert response.status == 200
                print(f"{Colors.OKGREEN}   API docs: Accessible{Colors.ENDC}")
                
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ API: Health check failed - {e}{Colors.ENDC}")
        pytest.fail(f"API health check failed: {e}")


@pytest.mark.asyncio
async def test_ollama_service():
    """Test Ollama LLM service"""
    print(f"\n{Colors.BOLD}Testing Ollama (port 11435)...{Colors.ENDC}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check service is running
            async with session.get(
                f"{SERVICES['ollama']['url']}/api/tags",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                assert response.status == 200
                data = await response.json()
                models = data.get("models", [])
                
                print(f"{Colors.OKGREEN}✅ Ollama: Service running")
                print(f"   Models loaded: {len(models)}{Colors.ENDC}")
                
                if models:
                    for model in models[:3]:  # Show first 3 models
                        print(f"   - {model.get('name', 'unknown')}")
                else:
                    print(f"{Colors.WARNING}   ⚠️  No models loaded yet")
                    print(f"   Run: docker exec twisterlab-ollama-staging "
                          f"ollama pull deepseek-r1{Colors.ENDC}")
                
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Ollama: Service check failed - {e}{Colors.ENDC}")
        pytest.fail(f"Ollama service check failed: {e}")


@pytest.mark.asyncio
async def test_prometheus_metrics():
    """Test Prometheus metrics endpoint"""
    print(f"\n{Colors.BOLD}Testing Prometheus (port 9092)...{Colors.ENDC}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Health check
            async with session.get(
                f"{SERVICES['prometheus']['url']}/-/healthy",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                assert response.status == 200
                
            # Check metrics endpoint
            async with session.get(
                f"{SERVICES['prometheus']['url']}/api/v1/targets",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                assert response.status == 200
                data = await response.json()
                targets = data.get("data", {}).get("activeTargets", [])
                
                print(f"{Colors.OKGREEN}✅ Prometheus: Service running")
                print(f"   Active targets: {len(targets)}{Colors.ENDC}")
                
                # Show target status
                for target in targets:
                    health = target.get("health", "unknown")
                    job = target.get("labels", {}).get("job", "unknown")
                    emoji = "✅" if health == "up" else "❌"
                    color = Colors.OKGREEN if health == "up" else Colors.FAIL
                    print(f"{color}   {emoji} {job}: {health}{Colors.ENDC}")
                
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Prometheus: Service check failed - {e}{Colors.ENDC}")
        pytest.fail(f"Prometheus service check failed: {e}")


@pytest.mark.asyncio
async def test_grafana_ui():
    """Test Grafana web UI"""
    print(f"\n{Colors.BOLD}Testing Grafana (port 3001)...{Colors.ENDC}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check UI is accessible
            async with session.get(
                f"{SERVICES['grafana']['url']}/api/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                assert response.status == 200
                health = await response.json()
                
                print(f"{Colors.OKGREEN}✅ Grafana: UI accessible")
                print(f"   Status: {health.get('database', 'unknown')}")
                print(f"   Version: {health.get('version', 'unknown')}")
                print(f"   URL: http://localhost:3001")
                print(f"   Login: admin/staging_grafana_password{Colors.ENDC}")
                
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Grafana: UI check failed - {e}{Colors.ENDC}")
        pytest.fail(f"Grafana UI check failed: {e}")


@pytest.mark.asyncio
async def test_full_stack():
    """Test complete stack integration"""
    print(f"\n{Colors.BOLD}Testing Full Stack Integration...{Colors.ENDC}")
    
    try:
        # Run all tests in sequence
        await test_postgres_connectivity()
        await test_redis_connectivity()
        await test_api_health()
        await test_ollama_service()
        await test_prometheus_metrics()
        await test_grafana_ui()
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ ALL SMOKE TESTS PASSED!")
        print(f"{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
        
        return True
        
    except Exception as e:
        print(f"\n{Colors.FAIL}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}❌ SMOKE TESTS FAILED: {e}")
        print(f"{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
        raise


if __name__ == "__main__":
    """Run all smoke tests"""
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'TWISTERLAB STAGING SMOKE TESTS'.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    
    asyncio.run(test_full_stack())
