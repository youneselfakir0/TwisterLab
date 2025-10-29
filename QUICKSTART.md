# TwisterLab v1.0 - Guide de Démarrage Rapide

**Démarrez TwisterLab en 5 minutes** ⏱️

---

## 📋 Prérequis

- ✅ Docker Desktop installé et en cours d'exécution
- ✅ Python 3.12+ installé
- ✅ Git installé

---

## 🚀 Démarrage Rapide (5 étapes)

### 1. Cloner le projet (si pas déjà fait)

```bash
cd C:\TwisterLab
```

### 2. Créer et activer l'environnement virtuel

```bash
# Créer l'environnement
python -m venv .venv_new

# Activer (Windows PowerShell)
.\.venv_new\Scripts\Activate.ps1

# Ou (Windows CMD)
.\.venv_new\Scripts\activate.bat

# Ou (Git Bash/Linux)
source .venv_new/bin/activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic python-dotenv requests typer rich
```

### 4. Démarrer PostgreSQL

```bash
docker-compose up -d postgres

# Vérifier que ça tourne
docker ps
# Vous devriez voir: twisterlab-postgres (healthy)
```

### 5. Démarrer l'API

```bash
uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ Vérifier que tout fonctionne

### Option 1: Test avec le script Python (Recommandé)

**Ouvrir un nouveau terminal** et lancer:

```bash
cd C:\TwisterLab
.\.venv_new\Scripts\Activate.ps1
python test_sops_api.py
```

**Résultat attendu**: 7 tests passent avec succès ✅

### Option 2: Test manuel avec curl

```bash
# Health check
curl http://localhost:8000/api/v1/sops/hello

# Créer une SOP
curl -X POST http://localhost:8000/api/v1/sops/ ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Test SOP\",\"description\":\"Test\",\"category\":\"password\",\"steps\":[\"Step 1\"],\"applicable_issues\":[\"test\"]}"

# Lister les SOPs
curl http://localhost:8000/api/v1/sops/
```

### Option 3: Test dans le navigateur

Ouvrez votre navigateur et allez sur:

- **Documentation API interactive**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/api/v1/sops/hello

---

## 📚 Accès aux services

| Service | URL | Credentials |
|---------|-----|-------------|
| **API FastAPI** | http://localhost:8000 | - |
| **API Docs (Swagger)** | http://localhost:8000/docs | - |
| **PostgreSQL** | localhost:5432 | User: twisterlab, DB: twisterlab_db |

---

## 🔍 Vérifier PostgreSQL directement (Optionnel)

```bash
# Se connecter à PostgreSQL
docker exec -it twisterlab-postgres psql -U twisterlab -d twisterlab_db

# Dans psql:
# Lister les tables
\dt

# Voir les SOPs créées
SELECT * FROM sops;

# Quitter
\q
```

---

## 🛠️ Commandes utiles

### Arrêter/Redémarrer

```bash
# Arrêter l'API
# Ctrl+C dans le terminal de uvicorn

# Arrêter PostgreSQL
docker-compose stop postgres

# Redémarrer PostgreSQL
docker-compose start postgres

# Tout arrêter
docker-compose down
```

### Voir les logs

```bash
# Logs PostgreSQL
docker logs twisterlab-postgres

# Logs API
# Les logs s'affichent directement dans le terminal uvicorn
```

### Réinitialiser la base de données

```bash
# Supprimer les données (⚠️ ATTENTION: supprime toutes les données)
docker-compose down -v

# Recréer
docker-compose up -d postgres

# Réappliquer les migrations
alembic upgrade head
```

---

## 🧪 Tester avec Postman/Insomnia

Importez cette collection:

**Endpoint**: `http://localhost:8000/api/v1/sops/`

**Exemple POST (Créer SOP)**:
```json
{
  "title": "Software Installation",
  "description": "Standard procedure for installing software",
  "category": "software",
  "steps": [
    "1. Download installer",
    "2. Run as administrator",
    "3. Follow installation wizard",
    "4. Restart computer"
  ],
  "applicable_issues": ["software_install", "new_software"],
  "estimated_time": 10,
  "success_rate": 0.95,
  "tags": ["software", "installation"]
}
```

---

## 📖 Documentation Complète

- **Documentation master**: `.github/copilot-instructions.md`
- **État du projet**: `STATUS.md`
- **Schémas agents**: `docs/AGENT_SCHEMA.md`
- **Scripts automation**: `deployment/scripts/`

---

## 🆘 Dépannage

### Problème: "Cannot connect to API"

**Solution**:
1. Vérifiez que uvicorn est lancé: `uvicorn agents.api.main:app --reload`
2. Vérifiez le port 8000: `netstat -ano | findstr :8000`
3. Essayez un autre port: `uvicorn agents.api.main:app --port 8001 --reload`

### Problème: "Connection refused to PostgreSQL"

**Solution**:
1. Vérifiez que Docker tourne: `docker ps`
2. Vérifiez le conteneur: `docker ps | findstr postgres`
3. Redémarrez: `docker-compose restart postgres`
4. Vérifiez les logs: `docker logs twisterlab-postgres`

### Problème: "Module not found"

**Solution**:
1. Vérifiez l'environnement virtuel est activé: `where python` (doit pointer vers .venv_new)
2. Réinstallez les dépendances: `pip install -r requirements.txt`
3. Vérifiez Python 3.12+: `python --version`

### Problème: "Alembic migration error"

**Solution**:
1. Vérifiez la connexion DB: `alembic current`
2. Réappliquez: `alembic downgrade base` puis `alembic upgrade head`
3. Vérifiez alembic.ini pointe vers la bonne DB

---

## 🎯 Prochaines étapes

Une fois que tout fonctionne, vous pouvez:

1. **Option A**: Implémenter l'authentification JWT/OAuth2
2. **Option B**: Intégrer les agents MCP + orchestration
3. **Option C**: Créer un frontend React/Vue
4. **Option D**: Ajouter tests automatisés (pytest)
5. **Option E**: Préparer le déploiement production

**Voir**: `STATUS.md` pour détails sur chaque option

---

## ✨ Commandes CLI TwisterLab

```bash
# Lister les agents disponibles
python cli/twisterlab.py list-agents

# Exporter un agent au format Microsoft
python cli/twisterlab.py export-agent helpdesk-resolver

# Exporter vers un fichier
python cli/twisterlab.py export-agent classifier --output agent.json

# Voir détails d'un agent
python cli/twisterlab.py show-agent desktop-commander

# Valider un schéma
python cli/twisterlab.py validate-schema config/agent_schemas/helpdesk_resolver.json

# Voir les formats supportés
python cli/twisterlab.py formats
```

---

## 🎉 Félicitations !

Vous avez maintenant TwisterLab v1.0 opérationnel avec:

- ✅ PostgreSQL + SQLAlchemy
- ✅ API FastAPI avec CRUD complet
- ✅ Migrations Alembic
- ✅ Scripts de test
- ✅ CLI riche
- ✅ Documentation complète

**Prêt pour la production !** 🚀

---

**Besoin d'aide ?** Consultez:
- `STATUS.md` - État du projet et prochaines étapes
- `.github/copilot-instructions.md` - Documentation complète
- `docs/AGENT_SCHEMA.md` - Guide des schémas agents
