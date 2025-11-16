# TwisterLab v2 - Guide de Démarrage

Bienvenue sur TwisterLab v2, un écosystème d'agents IA autonomes pour l'automatisation des services informatiques. Ce guide vous expliquera comment déployer et interagir avec le système.

---

## 1. Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés et configurés :

- **Docker & Docker Swarm :** La dernière version de Docker Desktop est recommandée. Assurez-vous que le mode Swarm est activé (`docker swarm init`).
- **Git :** Pour cloner le référentiel.
- **Client SSH :** Pour vous connecter aux serveurs distants si nécessaire.
- **Python 3.12+ :** (Optionnel) Pour le développement local et l'exécution de scripts.

---

## 2. Configuration Initiale

Clonez le référentiel et configurez les variables d'environnement de production.

```bash
# 1. Clonez le référentiel
git clone https://github.com/youneselfakir0/TwisterLab.git
cd TwisterLab

# 2. Créez le fichier d'environnement de production à partir de l'exemple
# (Sous Windows, utilisez 'copy' au lieu de 'cp')
cp .env.prod.example .env.prod

# 3. MODIFIEZ .env.prod
# Ouvrez le fichier .env.prod et remplacez les valeurs par défaut 
# par vos propres secrets et configurations (clés API, mots de passe, etc.).
```
**IMPORTANT :** Ne commitez jamais votre fichier `.env.prod`.

---

## 3. Déploiement de la Stack avec Docker Swarm

Le script `deploy.ps1` est le moyen recommandé pour déployer l'ensemble de la stack TwisterLab, y compris l'API, la base de données, et les services de monitoring.

```powershell
# Exécutez le script de déploiement pour l'environnement de production
./deploy_production_simple.ps1

# Une fois le déploiement terminé, vérifiez le statut des services
docker service ls
```

Vous devriez voir tous les services (`twisterlab_api`, `twisterlab_postgres`, `twisterlab_grafana`, etc.) avec `1/1` dans la colonne `REPLICAS`, indiquant qu'ils sont en cours d'exécution.

---

## 4. Accès et Vérification du Système

Une fois la stack déployée, vous pouvez accéder aux différents services via les adresses IP de votre nœud Docker Swarm (par exemple, `192.168.0.30`).

- **API Principale :** `http://<DOCKER_HOST_IP>:8000`
- **Documentation API (SwaggerUI) :** `http://<DOCKER_HOST_IP>:8000/docs`
- **Tableaux de Bord (Grafana) :** `http://<DOCKER_HOST_IP>:3000`

### Test de Santé de l'API

Utilisez `curl` ou votre navigateur pour vérifier que l'API est en ligne :

```bash
curl http://<DOCKER_HOST_IP>:8000/health
```

La réponse attendue est : `{"status":"healthy","version":"2.0.0", ...}`.

### Test d'Exécution d'un Agent

Pour tester l'exécution d'un agent, vous devez d'abord obtenir un token d'authentification.

```bash
# 1. Obtenir un token (remplacez 'testuser' et 'testpassword')
$response = curl -X POST "http://<DOCKER_HOST_IP>:8000/token" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=testuser&password=testpassword"

# Extrayez le token de la réponse
$token = ($response | ConvertFrom-Json).access_token

# 2. Exécuter le MonitoringAgent avec le token
curl -X POST "http://<DOCKER_HOST_IP>:8000/api/v1/autonomous/agents/MonitoringAgent/execute" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"operation": "health_check", "context": {}}'
```

---

## 5. Développement Local (Optionnel)

Si vous souhaitez développer localement sans tout déployer via Docker, vous pouvez lancer l'API directement.

```bash
# 1. Créez et activez un environnement virtuel Python
python -m venv .venv
# Sous Windows:
.\.venv\Scripts\Activate.ps1
# Sous Linux/macOS:
# source .venv/bin/activate

# 2. Installez les dépendances requises
pip install -r requirements.txt

# 3. Assurez-vous que la base de données est accessible
# (Vous pouvez lancer uniquement la base de données avec Docker)
docker stack deploy -c docker-compose.yml twisterlab

# 4. Lancez le serveur API avec Uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Prochaines Étapes

Maintenant que le système est en place, vous pouvez explorer la documentation plus détaillée :

- **Architecture du Système :** `docs/ARCHITECTURE.md`
- **Guide de Déploiement Avancé :** `docs/DEPLOYMENT.md`
- **Référence de l'API :** `docs/API.md`
- **Guide de Dépannage :** `docs/TROUBLESHOOTING.md`
- **Configuration de l'IDE (VS Code & Continue) :** `docs/IDE_SETUP.md` (à venir)
- **Guide de Contribution :** `CONTRIBUTING.md` (à venir)
