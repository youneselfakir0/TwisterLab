import asyncio
import json
import sys

import aiohttp
import yaml


async def validate_setup():
    results = {}
    
    # 1. Valider config YAML
    try:
        with open('.continue/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        results['yaml_config'] = 'Valide'
        results['models_count'] = len(config.get('models', []))
        results['mcp_servers'] = len(config.get('mcpServers', []))
        results['rules_count'] = len(config.get('rules', []))
    except Exception as e:
        results['yaml_config'] = f'Erreur: {e}'
    
    # 2. Tester API TwisterLab
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://192.168.0.30:8000/health') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results['api_health'] = f'{data.get(\"status\", \"unknown\")}'
                else:
                    results['api_health'] = f'Status {resp.status}'
    except Exception as e:
        results['api_health'] = f'Erreur: {e}'
    
    # 3. Tester Ollama
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://192.168.0.20:11434/api/tags') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m['name'] for m in data.get('models', [])]
                    results['ollama_models'] = f'{len(models)} modèles'
                    configured = ['qwen3:8b', 'deepseek-r1:latest', 'codellama:latest']
                    missing = [m for m in configured if m not in models]
                    if missing:
                        results['ollama_missing'] = f'Manquants: {missing}'
                    else:
                        results['ollama_missing'] = 'Tous présents'
                else:
                    results['ollama_models'] = f'Status {resp.status}'
    except Exception as e:
        results['ollama_models'] = f'Erreur: {e}'
    
    # Afficher résultats
    print('=== VALIDATION CONFIGURATION CONTINUE IDE ===')
    for key, value in results.items():
        print(f'{key}: {value}')
    
    # Résumé
    errors = [k for k, v in results.items() if 'Erreur' in v or 'Status' in v and not v.startswith('healthy')]
    if errors:
        print(f'\n{len(errors)} erreurs détectées')
        return False
    else:
        print(f'\nConfiguration valide - {results.get(\"models_count\", 0)} modèles, {results.get(\"mcp_servers\", 0)} MCP servers')
        return True

if __name__ == '__main__':
    success = asyncio.run(validate_setup())
    sys.exit(0 if success else 1)
