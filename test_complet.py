#!/usr/bin/env python3
"""Test complet TwisterLab - Dashboards, WebUI, Ollama, MCPs"""

import asyncio
import sys

import aiohttp

# Configuration
ENDPOINTS = {
    "api": "http://localhost:8000",
    "grafana": "http://edgeserver.twisterlab.local:3000",
    "prometheus": "http://edgeserver.twisterlab.local:9090",
    "openwebui": "http://edgeserver.twisterlab.local:8083",
    "ollama": "http://localhost:11434",
}


async def test_endpoint(name, url, path="/", expected_status=200):
    """Test générique d'endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{url}{path}",
                timeout=aiohttp.ClientTimeout(total=10),
                allow_redirects=True,
            ) as resp:
                if resp.status == expected_status or resp.status == 200:
                    print(f"✅ {name}: OK (status {resp.status})")
                    return True
                else:
                    print(f"⚠️  {name}: Status {resp.status} (attendu {expected_status})")
                    return False
    except asyncio.TimeoutError:
        print(f"❌ {name}: TIMEOUT (>10s)")
        return False
    except aiohttp.ClientConnectorError:
        print(f"❌ {name}: CONNEXION REFUSÉE")
        return False
    except Exception as e:
        print(f"❌ {name}: {type(e).__name__}")
        return False


async def test_ollama_models():
    """Test Ollama + modèles disponibles"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ENDPOINTS['ollama']}/api/tags",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get("models", [])
                    if models:
                        model_names = [m.get("name", "?") for m in models]
                        print(f"✅ Ollama: {len(models)} modèle(s) - {', '.join(model_names[:3])}")
                        return True
                    else:
                        print("⚠️  Ollama: Aucun modèle installé")
                        return False
    except Exception as e:
        print(f"❌ Ollama models: {type(e).__name__}")
        return False


async def test_mcp_isolation():
    """Test isolation MCPs (endpoints de test)"""
    mcp_tests = []

    # Test que les MCPs ne sont PAS accessibles publiquement (sécurité)
    mcp_ports = [
        9001,
        9002,
        9003,
        9004,
        9005,
    ]  # LinkedIn, Twitter, Email, GitHub, Notion

    accessible_count = 0
    for port in mcp_ports:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://localhost:{port}", timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    accessible_count += 1
        except Exception:
            pass  # Normal - MCPs doivent être isolés

    if accessible_count == 0:
        print(f"✅ MCPs: Isolation OK (0/{len(mcp_ports)} accessibles publiquement)")
        return True
    else:
        print(f"⚠️  MCPs: {accessible_count}/{len(mcp_ports)} accessibles (risque sécurité)")
        return False


async def test_api_advanced():
    """Tests API avancés"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test agents endpoint
            async with session.get(
                f"{ENDPOINTS['api']}/api/v1/autonomous/agents",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    agents = data.get("agents", [])
                    print(f"✅ API Agents: {len(agents)}/7 disponibles")
                    return len(agents) >= 7
    except Exception as e:
        print(f"❌ API Agents: {type(e).__name__}")
        return False


async def main():
    print(f"\n{'=' * 60}")
    print("🔬 TWISTERLAB - TEST COMPLET SYSTÈME")
    print(f"{'=' * 60}\n")

    results = {}

    # Section 1: Services principaux
    print("📡 SERVICES PRINCIPAUX")
    print("-" * 60)
    results["api"] = await test_endpoint("API TwisterLab", ENDPOINTS["api"], "/health")
    results["api_agents"] = await test_api_advanced()
    print()

    # Section 2: Monitoring & Dashboards
    print("📊 MONITORING & DASHBOARDS")
    print("-" * 60)
    results["grafana"] = await test_endpoint("Grafana", ENDPOINTS["grafana"], "/api/health", 200)
    results["prometheus"] = await test_endpoint(
        "Prometheus", ENDPOINTS["prometheus"], "/-/healthy", 200
    )
    print()

    # Section 3: IA & Modèles
    print("🤖 INTELLIGENCE ARTIFICIELLE")
    print("-" * 60)
    results["openwebui"] = await test_endpoint("OpenWebUI", ENDPOINTS["openwebui"], "/", 200)
    results["ollama"] = await test_endpoint("Ollama API", ENDPOINTS["ollama"], "/", 200)
    results["ollama_models"] = await test_ollama_models()
    print()

    # Section 4: Sécurité MCPs
    print("🔒 SÉCURITÉ MCPs")
    print("-" * 60)
    results["mcp_isolation"] = await test_mcp_isolation()
    print()

    # Résumé
    success = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (success / total * 100) if total > 0 else 0

    print(f"{'=' * 60}")
    print(f"📊 RÉSULTAT GLOBAL: {success}/{total} ({percentage:.0f}%)")
    print(f"{'=' * 60}\n")

    if percentage == 100:
        print("🎉 SYSTÈME 100% OPÉRATIONNEL - PRODUCTION READY\n")
        sys.exit(0)
    elif percentage >= 80:
        print("✅ SYSTÈME OPÉRATIONNEL - Quelques services optionnels manquants\n")
        sys.exit(0)
    elif percentage >= 50:
        print("⚠️  SYSTÈME PARTIELLEMENT OPÉRATIONNEL\n")
        sys.exit(1)
    else:
        print("❌ SYSTÈME NON OPÉRATIONNEL - Vérifier la configuration\n")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
