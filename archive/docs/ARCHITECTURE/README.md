# =============================================================================
# TWISTERLAB INFRASTRUCTURE - README
# Version: 1.0.0
# Date: 2025-11-10
# =============================================================================

## STRUCTURE

```
infrastructure/
├── docker/
│   └── docker-compose.unified.yml    # UN SEUL fichier Docker Compose
├── dockerfiles/
│   └── Dockerfile.api                # Image de l'API
├── configs/
│   ├── .env.staging                  # Configuration staging
│   ├── .env.production               # Configuration production
│   └── daemon.json                   # Configuration Docker daemon
└── scripts/
    └── deploy.ps1                    # Script de déploiement unifié
```

## DÉPLOIEMENT RAPIDE

### Production
```powershell
.\infrastructure\scripts\deploy.ps1 -Environment production
```

### Staging
```powershell
.\infrastructure\scripts\deploy.ps1 -Environment staging
```

## DÉPLOIEMENT MANUEL (si script bloqué)

### 1. Copier fichiers sur edgeserver
```powershell
scp infrastructure/docker/docker-compose.unified.yml twister@edgeserver.twisterlab.local:/home/twister/docker-compose.yml
scp infrastructure/configs/.env.production twister@edgeserver.twisterlab.local:/home/twister/.env
```

### 2. Déployer la stack
```powershell
ssh twister@edgeserver.twisterlab.local @"
cd /home/twister
export `$(cat .env | xargs)
docker stack deploy -c docker-compose.yml twisterlab
"@
```

### 3. Vérifier l'état
```powershell
ssh twister@edgeserver.twisterlab.local "docker service ls"
```

### 4. Tester l'API
```powershell
curl http://192.168.0.30:8000/health
```

## COMMANDES UTILES

### Lister les services
```bash
docker service ls
```

### Voir les logs d'un service
```bash
docker service logs twisterlab_api
docker service logs twisterlab_api --follow
```

### Mettre à jour un service
```bash
docker service update --force twisterlab_api
```

### Redémarrer un service
```bash
docker service scale twisterlab_api=0
docker service scale twisterlab_api=1
```

### Supprimer la stack complète
```bash
docker stack rm twisterlab
```

### Voir l'état détaillé d'un service
```bash
docker service ps twisterlab_api --no-trunc
```

## TROUBLESHOOTING

### Services à 0/1 (ne démarrent pas)

**Vérifier les logs** :
```bash
docker service logs twisterlab_api --tail 50
```

**Vérifier les contraintes** :
```bash
docker service inspect twisterlab_api --pretty
```

**Forcer mise à jour** :
```bash
docker service update --force twisterlab_api
```

### API ne répond pas

**Vérifier le container** :
```bash
docker service ps twisterlab_api
```

**Vérifier les healthchecks** :
```bash
docker service inspect twisterlab_api | grep -A 10 Healthcheck
```

**Tester depuis edgeserver** :
```bash
ssh twister@edgeserver.twisterlab.local "curl http://localhost:8000/health"
```

### Problèmes de volumes/données

**Vérifier que les répertoires existent** :
```bash
ssh twister@edgeserver.twisterlab.local "ls -la /twisterlab/ai-storage/data/"
```

**Créer répertoires manquants** :
```bash
ssh twister@edgeserver.twisterlab.local "sudo mkdir -p /twisterlab/ai-storage/data/{postgres,redis,ollama,webui}"
ssh twister@edgeserver.twisterlab.local "sudo chown -R 1000:1000 /twisterlab/ai-storage/data/"
```

### Services dupliqués (ancienne stack existe)

**Lister toutes les stacks** :
```bash
docker stack ls
```

**Supprimer ancienne stack** :
```bash
docker stack rm twisterlab_prod
docker stack rm twisterlab-prod
```

## ARCHITECTURE

### Réseau

```
┌─────────────────────────────────────┐
│  Traefik (Load Balancer)            │
│  Port: 80, 443, 8080                │
└───────────┬─────────────────────────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼────┐     ┌───▼────┐
│  API   │     │ WebUI  │
│  :8000 │     │ :8083  │
└───┬────┘     └───┬────┘
    │              │
┌───▼──────────────▼────┐
│  Backend Network      │
│  ┌────────┐ ┌──────┐ │
│  │Postgres│ │Redis │ │
│  └────────┘ └──────┘ │
│  ┌────────┐           │
│  │ Ollama │           │
│  └────────┘           │
└───────────────────────┘
```

### Volumes

- **postgres_data** : `/twisterlab/ai-storage/data/postgres`
- **redis_data** : `/twisterlab/ai-storage/data/redis`
- **ollama_data** : `/twisterlab/ai-storage/data/ollama`
- **webui_data** : `/twisterlab/ai-storage/data/webui`

### Réseaux

- **backend** : Communication entre services (encrypted)
- **traefik-public** : Exposition publique via Traefik

## ENDPOINTS

| Service | URL | Description |
|---------|-----|-------------|
| API Health | http://192.168.0.30:8000/health | Santé de l'API |
| API Docs | http://192.168.0.30:8000/docs | Documentation interactive |
| Traefik Dashboard | http://192.168.0.30:8080 | Tableau de bord Traefik |
| WebUI | http://192.168.0.30:8083 | Interface utilisateur |

## CONFIGURATION

### Variables d'environnement (.env.production)

```bash
ENVIRONMENT=production
DOMAIN=twisterlab.local
API_REPLICAS=2
VERSION=latest

POSTGRES_DB=twisterlab_prod
POSTGRES_USER=twisterlab
POSTGRES_PASSWORD=<STRONG_PASSWORD>

REDIS_PASSWORD=<STRONG_PASSWORD>

SECRET_KEY=<STRONG_SECRET_32_CHARS>
WEBUI_SECRET_KEY=<STRONG_SECRET>

DATA_PATH=/twisterlab/ai-storage/data
LOG_LEVEL=INFO
WEBUI_PORT=8083

ENABLE_METRICS=true
ENABLE_TRACING=true
ENABLE_DEBUG=false
```

### Générer secrets forts

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## SÉCURITÉ

### Fichiers à NE JAMAIS commiter

- `infrastructure/configs/.env.production` (contient mots de passe)
- `infrastructure/configs/.env.staging` (contient secrets)

### Bonnes pratiques

1. ✅ Utiliser des secrets forts (32+ caractères)
2. ✅ Ne jamais exposer ports internes (postgres, redis)
3. ✅ Utiliser Traefik pour toutes les expositions HTTP
4. ✅ Activer les healthchecks sur tous les services
5. ✅ Configurer TLS/HTTPS en production
6. ✅ Limiter ressources (memory, CPU) pour chaque service
7. ✅ Utiliser réseaux Docker encrypted

## MAINTENANCE

### Sauvegardes

**PostgreSQL** :
```bash
ssh twister@edgeserver.twisterlab.local "docker exec \$(docker ps -qf name=twisterlab_postgres) pg_dump -U twisterlab twisterlab_prod > backup_$(date +%Y%m%d).sql"
```

**Volumes complets** :
```bash
ssh twister@edgeserver.twisterlab.local "sudo tar -czf backup_volumes_$(date +%Y%m%d).tar.gz /twisterlab/ai-storage/data/"
```

### Mises à jour

**Rebuilder image API** :
```bash
cd /path/to/TwisterLab
docker build -t twisterlab/api:latest -f infrastructure/dockerfiles/Dockerfile.api .
docker push twisterlab/api:latest  # Si registry distant
```

**Déployer nouvelle version** :
```bash
docker service update --image twisterlab/api:latest twisterlab_api
```

## SUPPORT

Pour toute question ou problème :
1. Vérifier les logs : `docker service logs <service>`
2. Consulter ce README
3. Vérifier `/docs/TROUBLESHOOTING.md`
4. Ouvrir une issue GitHub

---

**Version** : 1.0.0
**Dernière mise à jour** : 2025-11-10
**Mainteneur** : TwisterLab Team
