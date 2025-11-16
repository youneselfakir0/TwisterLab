"""
Test Configuration Continue IDE v1.0.1
Vérifie que tous les composants sont opérationnels
"""
import subprocess
import sys
import json
from pathlib import Path

def test_yaml_config():
    """Test validité config.yaml"""
    print("🔍 Test 1: Validation config.yaml...")
    try:
        import yaml
        with open('.continue/config.yaml', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        assert 'name' in config, "name manquant"
        assert 'version' in config, "version manquante"
        assert 'schema' in config, "schema manquant"
        assert 'models' in config, "models manquant"
        # MCP est optionnel (peut être commenté)

        print(f"   ✅ YAML valide")
        print(f"   ✅ {len(config['models'])} modèles configurés")
        if 'mcpServers' in config:
            print(f"   ✅ {len(config['mcpServers'])} MCP server configuré")
        else:
            print(f"   ℹ️  MCP désactivé (optionnel)")
        print(f"   ✅ {len(config.get('rules', []))} rules configurées")
        print(f"   ✅ {len(config.get('context', []))} context providers")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_ollama_models():
    """Test présence modèles Ollama"""
    print("\n🔍 Test 2: Modèles Ollama installés...")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header

        expected_models = [
            'llama3.2:1b',
            'llama3:latest',
            'deepseek-r1:latest',
            'codellama:latest',
            'qwen3:8b',
            'gpt-oss:120b-cloud'
        ]

        installed = [line.split()[0] for line in lines if line.strip()]

        for model in expected_models:
            if model in installed:
                print(f"   ✅ {model}")
            else:
                print(f"   ⚠️  {model} - NON INSTALLÉ (ollama pull {model})")

        return len([m for m in expected_models if m in installed]) >= 4
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_ollama_api():
    """Test API Ollama locale"""
    print("\n🔍 Test 3: API Ollama locale...")
    try:
        import urllib.request
        with urllib.request.urlopen('http://localhost:11434/api/version') as response:
            data = json.loads(response.read())
            print(f"   ✅ Ollama v{data['version']}")
            return True
    except Exception as e:
        print(f"   ❌ API Ollama inaccessible: {e}")
        print(f"      Démarrer: ollama serve")
        return False

def test_mcp_script():
    """Test script MCP existe"""
    print("\n🔍 Test 4: Script MCP TwisterLab...")
    mcp_path = Path('agents/mcp/mcp_server_continue_sync.py')
    if mcp_path.exists():
        print(f"   ✅ {mcp_path} existe")
        print(f"   ✅ Taille: {mcp_path.stat().st_size} bytes")
        return True
    else:
        print(f"   ❌ {mcp_path} introuvable")
        return False

def test_twisterlab_api():
    """Test API TwisterLab production"""
    print("\n🔍 Test 5: API TwisterLab (production)...")
    try:
        import urllib.request
        with urllib.request.urlopen('http://192.168.0.30:8000/health', timeout=5) as response:
            data = json.loads(response.read())
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Version: {data['version']}")
            return True
    except Exception as e:
        print(f"   ⚠️  API inaccessible: {e}")
        print(f"      Normal si edgeserver éteint")
        return False

def test_api_metrics():
    """Test Prometheus metrics endpoint on TwisterLab API"""
    print("\n🔍 Test 6: Metrics endpoint on TwisterLab API...")
    try:
        import urllib.request
        with urllib.request.urlopen('http://localhost:8000/metrics', timeout=5) as response:
            if response.status == 200:
                print(f"   ✅ /metrics accessible (HTTP 200)")
                return True
            else:
                print(f"   ⚠️ /metrics returned HTTP {response.status}")
                return False
    except Exception as e:
        print(f"   ⚠️ /metrics inaccessible: {e}")
        return False

def test_continue_files():
    """Test fichiers Continue présents"""
    print("\n🔍 Test 6: Fichiers Continue...")
    files = [
        '.continue/config.yaml',
        '.continue/SETUP_GUIDE_v1.0.1.md',
        '.continue/README_MCP_TROUBLESHOOTING.md'
    ]

    all_ok = True
    for filepath in files:
        if Path(filepath).exists():
            print(f"   ✅ {filepath}")
        else:
            print(f"   ❌ {filepath} manquant")
            all_ok = False

    return all_ok

def main():
    """Execute tous les tests"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TEST CONFIGURATION CONTINUE v1.0.1                     ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    results = []
    results.append(("YAML Config", test_yaml_config()))
    results.append(("Modèles Ollama", test_ollama_models()))
    results.append(("API Ollama", test_ollama_api()))
    results.append(("Script MCP", test_mcp_script()))
    results.append(("API TwisterLab", test_twisterlab_api()))
    results.append(("API Metrics", test_api_metrics()))
    results.append(("Fichiers Continue", test_continue_files()))

    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║                        RÉSULTAT                            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name:20} {status}")

    passed_count = sum(1 for _, p in results if p)
    total = len(results)

    print(f"\n   Total: {passed_count}/{total} tests réussis")

    if passed_count >= 4:
        print("\n✅ Configuration OPÉRATIONNELLE")
        print("   Redémarrer VS Code: Ctrl+Shift+P → 'Reload Window'")
        print("   Tester Continue: Ctrl+L")
        return 0
    else:
        print("\n⚠️  Configuration PARTIELLE")
        print("   Voir erreurs ci-dessus")
        return 1

if __name__ == '__main__':
    sys.exit(main())
