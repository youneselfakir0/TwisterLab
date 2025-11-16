# 🚀 TwisterLab - Guide de Démarrage Rapide

## Bienvenue dans TwisterLab !

**TwisterLab** est un système d'automatisation IT Helpdesk multi-agent utilisant FastAPI, PostgreSQL et le protocole MCP.

---

## ⚡ Démarrage en 5 Minutes

### 1. Vérifier l'Environnement
```bash
# Vérifier Python 3.12+
python --version

# Vérifier que vous êtes dans le bon répertoire
pwd  # Doit afficher le chemin vers TwisterLab
```

### 2. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer les Tests Automatisés
```bash
# Utiliser le script d'automatisation (recommandé)
.\run_all_tests.ps1

# Ou manuellement
pytest tests/unit/ -v
pytest test_maestro_integration.py -v
```

### 4. Démarrer l'API
```bash
# 🚀 SOLUTION RECOMMANDÉE : Utiliser Docker
docker-compose up api -d

# Vérifier que l'API fonctionne
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

**⚠️ Note**: Si Docker n'est pas disponible, l'API peut avoir des problèmes de démarrage dans certains environnements Windows/PowerShell. Docker garantit un environnement isolé et stable.

### 5. Créer un Ticket de Test
```bash
# Avec curl
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test ticket",
    "description": "Test de l'\''orchestrateur Maestro",
    "requestor_email": "test@example.com"
  }'

# Avec PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/tickets/" `
  -Method POST -ContentType "application/json" `
  -Body '{"subject": "Test ticket", "description": "Test de l''orchestrateur Maestro", "requestor_email": "test@example.com"}'
```

---

## 🏗️ Architecture du Système

### Composants Principaux
```
TwisterLab/
├── agents/                          # Agents AI spécialisés
│   ├── base.py                     # Classe de base TwisterAgent
│   ├── orchestrator/maestro.py     # Orchestrateur principal
│   └── helpdesk/                   # Agents métier
│       ├── classifier.py           # Classification des tickets
│       ├── auto_resolver.py        # Résolution automatique
│       └── desktop_commander.py    # Commandes à distance
├── agents/api/                     # API REST FastAPI
│   ├── main.py                     # Application principale
│   └── routes_*.py                 # Endpoints API
├── agents/database/                # Persistance des données
│   ├── models.py                   # Modèles SQLAlchemy
│   ├── config.py                   # Configuration PostgreSQL
│   └── services.py                 # Services CRUD
├── tests/                          # Tests automatisés
│   ├── unit/                       # Tests unitaires (19 tests)
│   └── integration/                # Tests d'intégration (6 tests)
└── deployment/                     # Déploiement production
    ├── docker/                     # Conteneurs Docker
    └── scripts/                    # Scripts PowerShell Azure
```

### Flux de Traitement des Tickets
1. **Réception** → Ticket soumis via API
2. **Classification** → Agent Classifier évalue priorité/complexité
3. **Routage** → Maestro Orchestrator décide du chemin
4. **Traitement** → Agent spécialisé traite le ticket
5. **Résolution** → Réponse finale au demandeur

---

## 📋 Endpoints API Disponibles

### Tickets
```http
POST   /api/v1/tickets/          # Créer un ticket
GET    /api/v1/tickets/          # Lister les tickets
GET    /api/v1/tickets/{id}      # Détails d'un ticket
PUT    /api/v1/tickets/{id}      # Mettre à jour un ticket
DELETE /api/v1/tickets/{id}      # Supprimer un ticket
```

### Agents
```http
GET    /api/v1/agents/           # Liste des agents
GET    /api/v1/agents/{name}     # Détails d'un agent
POST   /api/v1/agents/{name}/execute  # Exécuter un agent
```

### Orchestrateur
```http
POST   /api/v1/orchestrator/route # Router un ticket
GET    /api/v1/orchestrator/status # Status des agents
POST   /api/v1/orchestrator/rebalance # Rééquilibrer la charge
```

### Système
```http
GET    /health                   # Health check
GET    /metrics                  # Métriques système
GET    /docs                     # Documentation Swagger UI
```

---

## 🧪 Tests Disponibles

### Tests Unitaires (19 tests)
- `test_maestro.py` - Orchestrateur Maestro
  - Routage des tickets
  - Gestion des agents
  - Métriques de performance
  - Rebalancing de charge

### Tests d'Intégration (6 tests)
- `test_maestro_integration.py` - Flux complet
  - Création → Classification → Routage → Résolution
  - Gestion d'erreurs
  - Performance sous charge

### Exécution des Tests
```bash
# Tous les tests
pytest

# Tests unitaires seulement
pytest tests/unit/

# Tests d'intégration seulement
pytest test_maestro_integration.py

# Avec coverage
pytest --cov=agents --cov-report=html
```

---

## 🔧 Dépannage

### Erreur: ModuleNotFoundError
```bash
# Installer les dépendances manquantes
pip install -r requirements.txt

# Vérifier l'installation
python -c "import fastapi, uvicorn, sqlalchemy, asyncpg"
```

### Erreur: Port 8000 déjà utilisé
```bash
# Tuer les processus sur le port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Ou utiliser un autre port
uvicorn agents.api.main:app --port 8001
```

### Erreur: Base de données PostgreSQL
```bash
# Vérifier Docker
docker ps

# Redémarrer les services
docker-compose down
docker-compose up -d

# Attendre 10 secondes puis vérifier
alembic current
```

### Erreur: Tests échouent
```bash
# Vérifier la structure des répertoires
ls -la tests/

# Recréer l'environnement virtuel si nécessaire
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 📊 Métriques et Monitoring

### Métriques Clés
- **Coverage Tests**: > 80%
- **Temps de Réponse API**: < 500ms
- **Taux de Résolution Auto**: > 70%
- **Disponibilité**: 99.9%

### Commandes de Monitoring
```bash
# Métriques API
curl http://localhost:8000/metrics

# Status des agents
curl http://localhost:8000/api/v1/agents/status

# Health check
curl http://localhost:8000/health

# Logs en temps réel
tail -f logs/twisterlab.log
```

---

## 🚀 Prochaines Étapes

Après ce guide de démarrage rapide :

1. **Phase 2** (En cours)
   - ✅ Installation dépendances
   - 🔄 Exécution des tests
   - ⏳ Test API REST
   - ⏳ Documentation technique
   - ⏳ Implémentation Desktop Commander

2. **Phase 3**: Interfaces utilisateur
3. **Phase 4**: Déploiement production
4. **Phase 5**: Optimisation et scaling

### Utiliser GitHub Copilot
Pour continuer le développement :
```bash
# Ouvrir le prompt détaillé
code .github/copilot-prompt-next-steps.md

# Copier le contenu dans Copilot Chat
# Suivre les instructions étape par étape
```

---

## 📞 Support

- **Documentation**: `.github/copilot-prompt-next-steps.md`
- **Tests**: `run_all_tests.ps1`
- **API**: `http://localhost:8000/docs`
- **Logs**: `logs/twisterlab.log`

**Version**: 1.0.0-alpha.1
**Date**: 28 octobre 2025
```

**Tests d'intégration**:
```bash
python test_maestro_integration.py
```

#### 4. Démarrer l'API

```bash
uvicorn agents.api.main:app --reload --port 8000
```

Ouvrir dans le navigateur: http://localhost:8000/docs

---

## 📚 Documentation

### Fichiers Importants

| Fichier | Description |
|---------|-------------|
| [.github/copilot-prompt-next-steps.md](.github/copilot-prompt-next-steps.md) | **PROMPT COMPLET pour GitHub Copilot** avec les 5 prochaines étapes à implémenter |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Instructions complètes du projet (1200+ lignes) |
| [test_maestro_integration.py](test_maestro_integration.py) | Tests d'intégration (6 tests) |
| [tests/unit/test_maestro.py](tests/unit/test_maestro.py) | Tests unitaires pytest (19 tests) |
| [requirements.txt](requirements.txt) | Dépendances Python |

### Architecture du Projet

```
TwisterLab/
├── agents/
│   ├── base.py                          # Classe de base TwisterAgent
│   ├── orchestrator/
│   │   └── maestro.py                   # ⭐ Orchestrateur principal (CORRIGÉ)
│   ├── helpdesk/
│   │   ├── classifier.py                # Classification des tickets
│   │   ├── auto_resolver.py             # Résolution automatique
│   │   └── desktop_commander.py         # Gestion postes à distance
│   ├── api/
│   │   ├── main.py                      # Application FastAPI
│   │   └── routes_orchestrator.py       # Routes API orchestrateur
│   └── database/
│       ├── config.py                    # Config PostgreSQL
│       ├── models.py                    # Modèles SQLAlchemy
│       └── services.py                  # Services CRUD
├── tests/
│   └── unit/
│       └── test_maestro.py              # ⭐ 19 tests unitaires
├── test_maestro_integration.py          # ⭐ 6 tests d'intégration
├── run_all_tests.ps1                    # ⭐ Script PowerShell auto
├── requirements.txt                     # Dépendances Python
└── .github/
    ├── copilot-instructions.md          # Instructions complètes
    └── copilot-prompt-next-steps.md     # ⭐ PROMPT pour Copilot
```

---

## 🎯 État Actuel du Projet

### ✅ Complété

- [x] Base de données PostgreSQL + SQLAlchemy + Alembic
- [x] API FastAPI avec endpoints REST
- [x] Agent Maestro Orchestrator (corrections des 9 erreurs)
- [x] Agent Classifier (classification des tickets)
- [x] Agent Helpdesk Resolver (résolution automatique)
- [x] Agent Desktop Commander (gestion postes à distance)
- [x] Tests d'intégration (6 tests)
- [x] Tests unitaires pytest (19 tests)
- [x] Routes API orchestrateur (4 endpoints)

### 📋 Prochaines Étapes

Voir le fichier **[.github/copilot-prompt-next-steps.md](.github/copilot-prompt-next-steps.md)** pour le prompt complet GitHub Copilot.

**Résumé des 5 étapes**:
1. ✅ Installer dépendances (`pip install asyncpg pytest pytest-asyncio`)
2. ✅ Exécuter tests pytest (`pytest tests/unit/test_maestro.py -v`)
3. 🔄 Tester API REST (démarrer avec `uvicorn`)
4. 📝 Créer documentation technique (3 fichiers MD)
5. 🔌 Implémenter intégration MCP pour Desktop Commander

---

## 🧪 Tests Disponibles

### Tests Unitaires (pytest)

**Fichier**: `tests/unit/test_maestro.py`

**19 tests couvrant**:
- Initialisation de Maestro
- Routing de tickets (urgent, password, software)
- Statut des agents
- Rééquilibrage de charge
- Métriques de performance
- Gestion d'erreurs
- Enums TicketPriority et TicketComplexity

**Exécuter**:
```bash
pytest tests/unit/test_maestro.py -v
```

**Avec couverture de code**:
```bash
pytest tests/unit/test_maestro.py --cov=agents.orchestrator.maestro --cov-report=html
```

### Tests d'Intégration

**Fichier**: `test_maestro_integration.py`

**6 tests end-to-end**:
1. Password Reset (classification + routing)
2. Urgent Ticket (escalade immédiate)
3. Software Installation
4. Access Request
5. Agent Status (avec health metrics)
6. Load Balancing

**Exécuter**:
```bash
python test_maestro_integration.py
```

---

## 🌐 API Endpoints

### Orchestrateur (/api/v1/orchestrator)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/process-ticket` | Traiter un ticket complet (classify → route → resolve) |
| GET | `/results/{ticket_id}` | Obtenir les résultats pour un ticket |
| GET | `/results` | Lister tous les résultats |
| GET | `/agents/status` | Statut de tous les agents |
| GET | `/metrics` | Métriques de performance |
| POST | `/rebalance` | Rééquilibrer la charge |

**Exemple d'utilisation**:

```bash
# Démarrer l'API
uvicorn agents.api.main:app --reload --port 8000

# Tester un endpoint
curl http://localhost:8000/api/v1/orchestrator/metrics
```

**Documentation interactive**: http://localhost:8000/docs

---

## 🐛 Dépannage

### Erreur: "No module named 'asyncpg'"

**Solution**:
```bash
pip install asyncpg
```

### PostgreSQL n'est pas démarré

**Solution**:
```bash
docker-compose up -d postgres
```

### Tests pytest échouent

**Solutions**:
1. Vérifier que toutes les dépendances sont installées:
   ```bash
   pip install -r requirements.txt
   ```

2. Vérifier que PostgreSQL fonctionne:
   ```bash
   docker ps | grep postgres
   ```

3. Vérifier les imports:
   ```bash
   python -c "from agents.orchestrator.maestro import MaestroOrchestratorAgent"
   ```

### API ne démarre pas (port 8000 occupé)

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Utiliser un autre port:
```bash
uvicorn agents.api.main:app --reload --port 8001
```

---

## 📞 Aide et Support

- **Documentation complète**: `.github/copilot-instructions.md`
- **Prochaines étapes**: `.github/copilot-prompt-next-steps.md`
- **Tests unitaires**: `tests/unit/test_maestro.py`
- **Tests d'intégration**: `test_maestro_integration.py`

---

## ✅ Checklist de Vérification

Avant de passer aux étapes suivantes, vérifier que:

- [ ] Python 3.12+ est installé
- [ ] Toutes les dépendances sont installées (`pip install -r requirements.txt`)
- [ ] PostgreSQL fonctionne (docker ps)
- [ ] Les 19 tests unitaires passent (pytest)
- [ ] Les 6 tests d'intégration passent
- [ ] L'API démarre sans erreur (uvicorn)
- [ ] La page Swagger est accessible (http://localhost:8000/docs)

**Si tout est ✅, vous êtes prêt pour les prochaines étapes!**

Voir: [.github/copilot-prompt-next-steps.md](.github/copilot-prompt-next-steps.md)

---

**Bon développement! 🚀**
