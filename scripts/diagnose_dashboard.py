#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger les queries Grafana du dashboard TwisterLab
Vérifie chaque panel et suggère des corrections
"""

import json
import sys

def analyze_dashboard(dashboard_path):
    """Analyse le dashboard et identifie les problèmes"""

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dashboard = data.get('dashboard', {})
    panels = dashboard.get('panels', [])

    print("\n" + "="*70)
    print("ANALYSE DU DASHBOARD GRAFANA")
    print("="*70)
    print(f"\nDashboard: {dashboard.get('title')}")
    print(f"Version: {dashboard.get('version')}")
    print(f"Total panels: {len(panels)}")
    print("\n" + "-"*70)

    problems = []

    for panel in panels:
        panel_id = panel.get('id')
        panel_title = panel.get('title')
        panel_type = panel.get('type')
        targets = panel.get('targets', [])

        print(f"\nPanel #{panel_id}: {panel_title} ({panel_type})")

        if not targets:
            print("  ⚠️  Pas de targets définies")
            problems.append({
                'panel_id': panel_id,
                'title': panel_title,
                'issue': 'No targets'
            })
            continue

        for idx, target in enumerate(targets):
            expr = target.get('expr', '')
            legend = target.get('legendFormat', '')

            print(f"  Query #{idx+1}: {expr[:80]}")

            # Vérifier les queries problématiques
            if not expr:
                print("    ❌ Query vide")
                problems.append({
                    'panel_id': panel_id,
                    'title': panel_title,
                    'issue': 'Empty query'
                })
            elif 'api_health' in expr:
                print("    ❌ Métrique 'api_health' n'existe pas")
                print("    💡 Suggestion: Utiliser 'up{job=\"twisterlab-api\"}'")
                problems.append({
                    'panel_id': panel_id,
                    'title': panel_title,
                    'issue': 'Invalid metric: api_health',
                    'suggestion': 'up{job="twisterlab-api"}'
                })
            elif 'redis_status' in expr or 'pg_status' in expr:
                print("    ❌ Métrique status n'existe pas")
                print("    💡 Suggestion: Utiliser 'redis_up' ou 'pg_up'")
                problems.append({
                    'panel_id': panel_id,
                    'title': panel_title,
                    'issue': 'Invalid status metric',
                    'suggestion': 'Use redis_up or pg_up'
                })
            elif 'container_cpu' in expr and 'cadvisor' not in expr:
                print("    ⚠️  Métrique container_cpu sans source cadvisor")
                problems.append({
                    'panel_id': panel_id,
                    'title': panel_title,
                    'issue': 'Missing cadvisor metrics',
                    'suggestion': 'Verify cadvisor is running'
                })
            else:
                print("    ✅ Query semble valide")

    print("\n" + "="*70)
    print(f"RÉSUMÉ: {len(problems)} problèmes détectés")
    print("="*70)

    if problems:
        print("\nDÉTAILS DES PROBLÈMES:")
        for i, problem in enumerate(problems, 1):
            print(f"\n{i}. Panel #{problem['panel_id']}: {problem['title']}")
            print(f"   Issue: {problem['issue']}")
            if 'suggestion' in problem:
                print(f"   Suggestion: {problem['suggestion']}")

    return problems

def suggest_fixes():
    """Suggestions de corrections basées sur les métriques disponibles"""
    print("\n" + "="*70)
    print("MÉTRIQUES DISPONIBLES ACTUELLEMENT")
    print("="*70)
    print("""
✅ MÉTRIQUES API (http://192.168.0.30:8000/metrics):
   - http_requests_total{endpoint, method, status}
   - agent_operations_total{agent, operation, status}
   - process_cpu_seconds_total
   - process_resident_memory_bytes
   - up (via Prometheus)

✅ MÉTRIQUES REDIS EXPORTER (http://192.168.0.30:9121/metrics):
   - redis_up
   - redis_connected_clients
   - redis_uptime_in_seconds
   - redis_memory_used_bytes
   - redis_commands_processed_total

⚠️  MÉTRIQUES POSTGRESQL EXPORTER (http://192.168.0.30:9187/metrics):
   - pg_up (actuellement = 0, problème d'auth)
   - pg_stat_database_* (non disponibles tant que pg_up=0)

❌ MÉTRIQUES MANQUANTES (à ajouter):
   - cadvisor metrics (CPU, mémoire conteneurs)
   - node_exporter metrics (disk, network I/O)
   - API response time (besoin d'ajouter histogram dans l'API)

QUERIES À CORRIGER:
1. API Health: Utiliser 'up{job="twisterlab-api"}' au lieu de 'api_health'
2. Redis Status: Utiliser 'redis_up OR on() vector(0)' avec fallback
3. PostgreSQL Status: Utiliser 'pg_up OR on() vector(0)' avec fallback
4. Container CPU: Vérifier que cadvisor exporte bien les métriques
5. API Response Time: Ajouter des histograms dans l'API FastAPI
""")

if __name__ == '__main__':
    dashboard_file = 'monitoring/grafana/provisioning/dashboards/twisterlab-agents-realtime.json'

    try:
        problems = analyze_dashboard(dashboard_file)
        suggest_fixes()

        if problems:
            print("\n" + "="*70)
            print("PROCHAINES ACTIONS RECOMMANDÉES:")
            print("="*70)
            print("""
1. Corriger les queries du dashboard (utiliser script fix_dashboard_queries.py)
2. Vérifier que cadvisor exporte bien les métriques
3. Résoudre l'authentification PostgreSQL (pg_up=0)
4. Ajouter des métriques de response time dans l'API
5. Réimporter le dashboard dans Grafana
""")
            sys.exit(1)
        else:
            print("\n✅ Aucun problème détecté!")
            sys.exit(0)

    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {dashboard_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
