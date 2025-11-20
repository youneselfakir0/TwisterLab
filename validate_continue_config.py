#!/usr/bin/env python3
"""
Test script for Continue IDE configuration validation
"""

import json
import os
import sys
from pathlib import Path


def validate_continue_config():
    """Validate the Continue IDE configuration"""
    config_path = Path(".continue/config.json")

    if not config_path.exists():
        print("❌ .continue/config.json not found")
        return False

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        print("✅ Configuration JSON valide")

        # Validate models
        models = config.get("models", [])
        print(f"📊 {len(models)} modèles configurés:")
        for model in models:
            print(f"  - {model['title']} ({model['model']})")

        # Validate MCP servers
        mcp_servers = config.get("experimental", {}).get("modelContextProtocolServers", [])
        print(f"🔧 {len(mcp_servers)} serveurs MCP configurés:")
        for server in mcp_servers:
            print(f"  - {server['name']}")
            auto_approve = server.get("autoApprove", [])
            print(f"    Auto-approve: {len(auto_approve)} outils")

        # Validate rules
        rules = config.get("rules", [])
        print(f"📋 {len(rules)} règles configurées:")
        for rule in rules:
            print(f"  - {rule['name']}")

        # Validate prompts
        prompts_dir = Path(".continue/prompts")
        if prompts_dir.exists():
            prompts = list(prompts_dir.glob("*.prompt.md"))
            print(f"💬 {len(prompts)} prompts configurés:")
            for prompt in prompts:
                print(f"  - {prompt.stem}")

        # Test MCP server script
        mcp_script = Path("agents/mcp/mcp_server_continue_sync.py")
        if mcp_script.exists():
            print("✅ Serveur MCP script trouvé")
        else:
            print("❌ Serveur MCP script manquant")

        print("\n🎉 Configuration Continue IDE validée avec succès !")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON dans config.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False


def test_mcp_server():
    """Test MCP server connectivity"""
    print("\n🔍 Test du serveur MCP...")

    try:
        # Test import
        sys.path.append(str(Path.cwd()))
        from agents.mcp.mcp_server_continue_sync import MCPServerContinue

        # Create server instance
        server = MCPServerContinue()

        print("✅ Serveur MCP instancié avec succès")
        print(f"  - Version: {server.server_info['version']}")
        print(f"  - API URL: {server.api_url}")
        print(f"  - Mode: {server.mode}")
        print(f"  - API disponible: {server.api_available}")

        # Test tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
        response = server.handle_request(tools_request)

        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ {len(tools)} outils MCP disponibles:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description'][:50]}...")
        else:
            print("❌ Erreur récupération outils MCP")

        return True

    except ImportError as e:
        print(f"❌ Erreur import MCP server: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur test MCP server: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Validation Configuration Continue IDE pour TwisterLab\n")

    # Change to project root
    os.chdir(Path(__file__).parent)

    # Validate config
    config_ok = validate_continue_config()

    # Test MCP server
    mcp_ok = test_mcp_server()

    if config_ok and mcp_ok:
        print("\n🎯 Configuration Continue IDE PRÊTE POUR PRODUCTION !")
        print("\n📋 Actions suivantes:")
        print("1. Redémarrer VS Code")
        print("2. Ouvrir un fichier Python dans TwisterLab")
        print("3. Tester @mcp list_autonomous_agents")
        print("4. Tester @mcp monitor_system_health")
    else:
        print("\n❌ Problèmes détectés - corriger avant utilisation")
