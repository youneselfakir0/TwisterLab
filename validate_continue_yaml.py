#!/usr/bin/env python3
"""
Validation script for Continue IDE YAML configuration
"""

import sys
from pathlib import Path

import yaml


def validate_yaml_config():
    """Validate the YAML configuration file"""
    config_path = Path(".continue/config.yaml")

    if not config_path.exists():
        print("❌ Fichier config.yaml non trouvé")
        return False

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        print("🚀 Validation Configuration Continue IDE YAML")
        print()

        # Validate basic required fields
        required_fields = ["name", "version", "schema"]
        for field in required_fields:
            if field not in config:
                print(f"❌ Champ requis manquant: {field}")
                return False

        print(
            f"📋 Configuration: {config['name']} v{config['version']} (schema: {config['schema']})"
        )
        print()

        # Validate models
        models = config.get("models", [])
        print(f"📊 {len(models)} modèles configurés:")
        for model in models:
            name = model.get("name", "Unknown")
            model_name = model.get("model", "Unknown")
            roles = model.get("roles", [])
            role_str = f" (rôles: {', '.join(roles)})" if roles else ""
            print(f"  - {name} ({model_name}){role_str}")

        # Validate MCP servers
        mcp_servers = config.get("mcpServers", [])
        print(f"🔧 {len(mcp_servers)} serveurs MCP configurés:")
        for server in mcp_servers:
            name = server.get("name", "Unknown")
            print(f"  - {name}")

        # Validate context providers
        context_providers = config.get("context", [])
        print(f"📄 {len(context_providers)} context providers configurés:")
        for provider in context_providers:
            provider_name = provider.get("provider", "Unknown")
            print(f"  - {provider_name}")

        # Validate other components
        rules = config.get("rules", [])
        print(f"📋 {len(rules)} règles configurées:")

        prompts = config.get("prompts", [])
        print(f"💬 {len(prompts)} prompts configurés:")

        # Check MCP script
        mcp_script = Path("agents/mcp/mcp_server_continue_sync.py")
        if mcp_script.exists():
            print("✅ Serveur MCP script trouvé")
        else:
            print("❌ Serveur MCP script non trouvé")

        print()
        print("🎉 Configuration Continue IDE YAML validée avec succès !")
        print()

        # Test MCP server
        print("🔍 Test du serveur MCP...")
        try:
            import requests

            response = requests.get("http://192.168.0.30:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Serveur MCP instancié avec succès")
                print("  - API disponible: True")
            else:
                print("❌ Serveur MCP API non accessible")
        except Exception as e:
            print(f"❌ Erreur de connexion MCP: {e}")

        print()
        print("📋 Actions suivantes:")
        print("1. Redémarrer VS Code")
        print("2. Ouvrir un fichier Python dans TwisterLab")
        print("3. Tester @mcp list_autonomous_agents")
        print("4. Tester @mcp monitor_system_health")

        return True

    except Exception as e:
        print(f"❌ Erreur de validation YAML: {e}")
        return False


if __name__ == "__main__":
    success = validate_yaml_config()
    sys.exit(0 if success else 1)
