# 🧪 Guide des Tests de Charge TwisterLab

## Vue d'ensemble

Ce guide explique comment exécuter des tests de charge sur l'API TwisterLab pour valider ses performances sous stress.

## Prérequis

### Installation des dépendances

```bash
# Installation automatique des dépendances
python install_load_test_deps.py

# Ou installation manuelle
pip install locust requests matplotlib pandas
```

## Structure des tests

### Fichiers créés

- **`load_test.py`** : Définition des scénarios de test (utilisateurs simulés)
- **`run_load_test.py`** : Script d'exécution automatique des tests
- **`install_load_test_deps.py`** : Installation des dépendances

### Scénarios de test

1. **Test léger** : 5 utilisateurs, montée progressive
2. **Test moyen** : 20 utilisateurs, montée modérée
3. **Test intensif** : 50 utilisateurs, montée rapide

## Exécution des tests

### Test automatique complet

```bash
# Démarrer l'API d'abord
python start_api_simple.py

# Dans un autre terminal, lancer les tests
python run_load_test.py
```

### Test manuel avec Locust

```bash
# Interface web interactive
locust --locustfile load_test.py --host http://127.0.0.1:8000

# Puis ouvrir http://localhost:8089 dans le navigateur
```

### Test spécifique

```bash
# Test avec paramètres personnalisés
locust --locustfile load_test.py \
       --host http://127.0.0.1:8000 \
       --users 10 \
       --spawn-rate 2 \
       --run-time 30s \
       --headless
```

## Métriques surveillées

### Performances

- **Temps de réponse moyen** : < 500ms pour les endpoints critiques
- **Taux d'erreur** : < 1% acceptable
- **Débit (RPS)** : Mesuré pour différents niveaux de charge

### Endpoints testés

- `GET /health` - Santé du système
- `GET /docs` - Documentation API
- `GET /openapi.json` - Spécification OpenAPI
- `GET /api/v1/tickets/` - Liste des tickets
- `GET /api/v1/agents/` - Liste des agents
- `GET /api/v1/sops/` - Liste des SOPs
- `GET /api/v1/orchestrator/status` - Statut orchestrateur

## Résultats

### Fichiers générés

- **`logs/load_test.log`** : Log détaillé des tests
- **`logs/load_test_results_stats.csv`** : Statistiques détaillées
- **`logs/load_test_results_failures.csv`** : Échecs enregistrés

### Interprétation

#### ✅ Test réussi

- Temps de réponse < 1000ms en moyenne
- Taux d'erreur < 5%
- Pas de crash du serveur

#### ⚠️ A optimiser

- Temps de réponse > 2000ms
- Taux d'erreur > 10%
- Mémoire/CPU excessive

#### ❌ Test échoué

- Erreurs 5xx fréquentes
- Crash du serveur
- Timeouts systématiques

## Optimisations recommandées

### Si performances insuffisantes

1. **Base de données**

   ```sql
   -- Ajouter des index
   CREATE INDEX CONCURRENTLY idx_tickets_status ON tickets(status);
   CREATE INDEX CONCURRENTLY idx_tickets_priority ON tickets(priority);
   ```

2. **Cache Redis**

   ```python
   # Implémenter le cache pour les données fréquemment lues
   @app.get("/api/v1/tickets/")
   @cache(expire=300)  # Cache 5 minutes
   async def list_tickets():
       pass
   ```

3. **Configuration serveur**

   ```bash
   # Augmenter les workers uvicorn
   uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

## Intégration CI/CD

### GitHub Actions

```yaml
name: Load Testing
on: [push, pull_request]

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust requests
      - name: Run load tests
        run: python run_load_test.py
```

## Dépannage

### Problèmes courants

1. **Erreur de connexion**

   ```
   ConnectionError: Connection refused
   ```

   → Vérifier que l'API est démarrée

2. **Timeout**

   ```
   TimeoutError: Request timed out
   ```

   → Augmenter les timeouts ou optimiser les requêtes

3. **Mémoire insuffisante**

   ```
   MemoryError: Out of memory
   ```

   → Réduire le nombre d'utilisateurs simultanés

### Debug

```bash
# Test avec logs détaillés
locust --locustfile load_test.py --host http://127.0.0.1:8000 --loglevel DEBUG

# Test d'un endpoint spécifique
curl -w "@curl-format.txt" -o /dev/null -s http://127.0.0.1:8000/health
```

## Métriques de production

Une fois en production, surveiller :

- **Response Time** : P95 < 1000ms
- **Error Rate** : < 0.1%
- **Throughput** : Capacité maximale connue
- **Resource Usage** : CPU < 80%, RAM < 85%

---

**Résultats attendus** : ✅ Tests réussis avant déploiement en production