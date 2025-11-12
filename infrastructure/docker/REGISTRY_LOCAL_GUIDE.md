# Docker Registry Locale - TwisterLab

**Souveraineté numérique - Zéro dépendance à Docker Hub**

## 🎯 Objectif

Déployer une registry Docker locale pour :
- ✅ **Éviter les rate limits** Docker Hub (429 Too Many Requests)
- ✅ **Souveraineté complète** sur les images
- ✅ **Performance optimale** (réseau local)
- ✅ **Disponibilité garantie** (pas de dépendance externe)
- ✅ **Contrôle total** des versions

---

## 📦 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TwisterLab Registry                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  Docker Registry │◄────────┤  Registry UI     │        │
│  │  (Port 5000)     │         │  (Port 5001)     │        │
│  └────────┬─────────┘         └──────────────────┘        │
│           │                                                 │
│           │ Stockage: /var/lib/registry                    │
│           ▼                                                 │
│  ┌──────────────────────────────────────────┐             │
│  │  Volume Docker: registry_data            │             │
│  │  - Images Python (3.11, 3.12)            │             │
│  │  - PostgreSQL 16                         │             │
│  │  - Redis 7                               │             │
│  │  - Traefik, Prometheus, Grafana          │             │
│  │  - TwisterLab API (builds locaux)        │             │
│  └──────────────────────────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Déploiement Complet

### Option 1: Déploiement automatique (PowerShell)

```powershell
cd C:\TwisterLab
.\infrastructure\scripts\deploy_local_registry.ps1 -Action all
```

**Étapes exécutées automatiquement** :
1. Copie des fichiers de configuration
2. Déploiement de la registry (port 5000) + UI (port 5001)
3. Migration des images Docker Hub → Registry locale
4. Build et push de l'API TwisterLab
5. Mise à jour du service Docker Swarm
6. Tests de validation

### Option 2: Déploiement manuel (étape par étape)

#### 1. Déployer la registry

```bash
ssh twister@192.168.0.30
cd /home/twister/TwisterLab
./infrastructure/scripts/deploy_registry.sh
```

#### 2. Migrer les images

```bash
./infrastructure/scripts/migrate_images_to_registry.sh
```

#### 3. Builder l'API

```bash
./infrastructure/scripts/build_api_local_registry.sh
```

---

## 🌐 Accès

| Service | URL | Description |
|---------|-----|-------------|
| **Registry API** | http://192.168.0.30:5000 | API Docker Registry v2 |
| **Registry UI** | http://192.168.0.30:5001 | Interface web de gestion |
| **Catalog** | http://192.168.0.30:5000/v2/_catalog | Liste des images |

---

## 📝 Utilisation

### Lister les images disponibles

```bash
curl -s http://192.168.0.30:5000/v2/_catalog | jq
```

**Résultat attendu** :
```json
{
  "repositories": [
    "python",
    "postgres",
    "redis",
    "traefik",
    "prometheus",
    "grafana",
    "twisterlab-api"
  ]
}
```

### Lister les tags d'une image

```bash
curl -s http://192.168.0.30:5000/v2/twisterlab-api/tags/list | jq
```

### Tag et push d'une nouvelle image

```bash
# Tag
docker tag mon-image:latest 192.168.0.30:5000/mon-image:v1.0

# Push
docker push 192.168.0.30:5000/mon-image:v1.0
```

### Pull depuis la registry locale

```bash
docker pull 192.168.0.30:5000/twisterlab-api:latest
```

---

## 🔧 Configuration Docker Daemon

**Important** : Tous les nœuds Docker doivent déclarer la registry comme "insecure" (HTTP au lieu de HTTPS).

### Sur edgeserver (Linux)

Fichier : `/etc/docker/daemon.json`

```json
{
  "insecure-registries": ["192.168.0.30:5000"],
  "registry-mirrors": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Redémarrer Docker :
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Sur CoreRTX (Windows)

1. **Docker Desktop** → Settings → Docker Engine
2. Ajouter à la configuration JSON :
```json
{
  "insecure-registries": [
    "192.168.0.30:5000"
  ]
}
```
3. **Apply & Restart**

---

## 📊 Images Migrées

| Image Source (Docker Hub) | Image Locale | Taille | Usage |
|---------------------------|--------------|--------|-------|
| `python:3.11-slim` | `192.168.0.30:5000/python:3.11-slim` | ~120 MB | Base API |
| `python:3.12-slim` | `192.168.0.30:5000/python:3.12-slim` | ~125 MB | Base API future |
| `postgres:16-alpine` | `192.168.0.30:5000/postgres:16-alpine` | ~75 MB | Base de données |
| `redis:7-alpine` | `192.168.0.30:5000/redis:7-alpine` | ~11 MB | Cache |
| `traefik:v2.10` | `192.168.0.30:5000/traefik:v2.10` | ~35 MB | Load balancer |
| `prom/prometheus:latest` | `192.168.0.30:5000/prometheus:latest` | ~80 MB | Monitoring |
| `grafana/grafana:latest` | `192.168.0.30:5000/grafana:latest` | ~100 MB | Dashboards |

---

## 🛠️ Maintenance

### Nettoyer les images non utilisées

```bash
# Via l'UI (port 5001) - bouton "Delete" sur chaque tag

# Ou via API
curl -X DELETE http://192.168.0.30:5000/v2/<image>/manifests/<digest>
```

### Sauvegarder la registry

```bash
# Backup du volume
docker run --rm -v registry_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/registry_backup_$(date +%Y%m%d).tar.gz /data

# Backup sur NAS
scp registry_backup_*.tar.gz user@nas:/backups/
```

### Restaurer la registry

```bash
# Restaurer depuis backup
docker run --rm -v registry_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/registry_backup_20251112.tar.gz -C /
```

### Redémarrer la registry

```bash
cd /home/twister/TwisterLab
docker-compose -f infrastructure/docker/docker-compose.registry.yml restart
```

---

## 🔐 Sécurité

### Configuration actuelle

- ✅ **HTTP uniquement** (pas d'authentification)
- ✅ **Réseau privé** (192.168.0.x)
- ✅ **Firewall** (accès limité au LAN)

### Sécurisation future (optionnelle)

#### Option 1: Basic Auth

```bash
# Créer htpasswd
docker run --rm --entrypoint htpasswd httpd:2 -Bbn admin password > auth/htpasswd

# Ajouter au docker-compose.yml
environment:
  REGISTRY_AUTH: htpasswd
  REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
```

#### Option 2: TLS/HTTPS

```bash
# Générer certificat auto-signé
openssl req -newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key \
  -x509 -days 365 -out certs/domain.crt

# Ajouter au docker-compose.yml
environment:
  REGISTRY_HTTP_TLS_CERTIFICATE: /certs/domain.crt
  REGISTRY_HTTP_TLS_KEY: /certs/domain.key
```

---

## 📈 Performance

### Statistiques attendues

| Métrique | Valeur |
|----------|--------|
| **Pull time** (API 20MB) | ~2s (vs 30s Docker Hub) |
| **Push time** (API 20MB) | ~3s (vs 45s Docker Hub) |
| **Latence réseau** | <1ms (LAN) vs 50-100ms (Internet) |
| **Bande passante** | Gigabit local illimité |

### Monitoring

```bash
# Logs de la registry
docker logs twisterlab_registry -f --tail 100

# Métriques Prometheus (si intégré)
curl -s http://192.168.0.30:5000/metrics
```

---

## 🐛 Troubleshooting

### Registry ne démarre pas

```bash
# Vérifier les logs
docker logs twisterlab_registry

# Vérifier le volume
docker volume inspect registry_data

# Redémarrer
docker-compose -f infrastructure/docker/docker-compose.registry.yml restart
```

### Push échoue (HTTP 400)

```bash
# Vérifier que daemon.json contient insecure-registries
cat /etc/docker/daemon.json

# Redémarrer Docker
sudo systemctl restart docker
```

### Image non trouvée après push

```bash
# Vérifier le catalogue
curl http://192.168.0.30:5000/v2/_catalog

# Vérifier les tags
curl http://192.168.0.30:5000/v2/<image>/tags/list
```

### Rate limit Docker Hub persiste

**Solution** : Toutes les images doivent être taguées avec `192.168.0.30:5000/` prefix.

**Mauvais** :
```bash
docker pull python:3.11-slim  # ❌ Va sur Docker Hub
```

**Correct** :
```bash
docker pull 192.168.0.30:5000/python:3.11-slim  # ✅ Registry locale
```

---

## 📚 Références

- **Docker Registry v2**: https://docs.docker.com/registry/
- **Registry API**: https://docs.docker.com/registry/spec/api/
- **Docker insecure registries**: https://docs.docker.com/registry/insecure/

---

## ✅ Checklist de déploiement

- [ ] Registry déployée (port 5000)
- [ ] UI accessible (port 5001)
- [ ] daemon.json configuré sur tous les nœuds
- [ ] Images de base migrées (Python, PostgreSQL, Redis)
- [ ] API TwisterLab buildée et pushée
- [ ] Service Docker Swarm mis à jour
- [ ] Tests de validation OK
- [ ] Backup configuré (volume registry_data)

---

**Status** : ✅ Production Ready  
**Dernière mise à jour** : 2025-11-12  
**Mainteneur** : TwisterLab Infrastructure Team
