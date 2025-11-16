# TwisterLab - Guide de Déploiement Production

## Vue d'ensemble

TwisterLab est un système d'automatisation de helpdesk IT multi-agent utilisant FastAPI, PostgreSQL, Redis et l'architecture MCP. Ce guide couvre le déploiement en production du système complet.

## Prérequis

### Système
- **OS**: Linux (Ubuntu 20.04+ recommandé), Windows Server, ou macOS
- **CPU**: 2+ cœurs
- **RAM**: 4GB+ minimum, 8GB+ recommandé
- **Stockage**: 20GB+ pour base de données et logs

### Logiciels
- **Docker**: 24.0+
- **Docker Compose**: 2.0+
- **Python**: 3.12+
- **PostgreSQL**: 15+
- **Redis**: 7+

### Réseau
- **Ports ouverts**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis)
- **Domaines**: Configuration SSL recommandée

## Architecture de Déploiement

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway    │    │  Web Frontend   │
│   (nginx/traefik)│    │   (FastAPI)      │    │  (OpenWebUI)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────────┐
                    │   TwisterLab    │
                    │   Core System   │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │  Maestro    │ │
                    │ │Orchestrator │ │
                    │ └─────────────┘ │
                    │        │        │
                    │ ┌──────┼──────┐ │
                    │ │      │      │ │
                    │ │ ┌────▼────┐ │ │
                    │ │ │Classifier│ │ │
                    │ │ └─────────┘ │ │
                    │ │             │ │
                    │ │ ┌─────────┐ │ │
                    │ │ │ Resolver │ │ │
                    │ │ └─────────┘ │ │
                    │ │             │ │
                    │ │ ┌─────────┐ │ │
                    │ │ │Desktop   │ │ │
                    │ │ │Commander │ │ │
                    │ │ └─────────┘ │ │
                    │ └─────────────┘ │
                    └─────────────────┘
                             │
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │   + Redis       │
                    └─────────────────┘
```

## 1. Configuration de l'Environnement

### Variables d'environnement

Créez un fichier `.env.production` :

```bash
# Base de données
DATABASE_URL=postgresql+asyncpg://twisterlab:secure_password@localhost:5432/twisterlab_prod
REDIS_URL=redis://localhost:6379/0

# Sécurité
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
API_KEY=your-api-key-for-external-access

# Modèle IA
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-r1

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/twisterlab/twisterlab.log

# Serveur
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### Permissions et Utilisateurs

```bash
# Créer l'utilisateur système
sudo useradd -r -s /bin/false twisterlab

# Créer les répertoires
sudo mkdir -p /opt/twisterlab
sudo mkdir -p /var/log/twisterlab
sudo mkdir -p /var/lib/twisterlab

# Définir les permissions
sudo chown -R twisterlab:twisterlab /opt/twisterlab
sudo chown -R twisterlab:twisterlab /var/log/twisterlab
sudo chown -R twisterlab:twisterlab /var/lib/twisterlab
```

## 2. Déploiement avec Docker

### Docker Compose Production

Créez `docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  # Base de données PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: twisterlab-postgres
    environment:
      POSTGRES_DB: twisterlab_prod
      POSTGRES_USER: twisterlab
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/docker/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - twisterlab-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U twisterlab"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Cache Redis
  redis:
    image: redis:7-alpine
    container_name: twisterlab-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - twisterlab-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Serveur Ollama (pour les modèles IA)
  ollama:
    image: ollama/ollama:latest
    container_name: twisterlab-ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - twisterlab-network
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=0.0.0.0

  # Application TwisterLab
  twisterlab:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.prod
    container_name: twisterlab-app
    env_file:
      - .env.production
    volumes:
      - ./logs:/var/log/twisterlab
      - ./config:/opt/twisterlab/config
    ports:
      - "8000:8000"
    networks:
      - twisterlab-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      ollama:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Interface Web (OpenWebUI)
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: twisterlab-webui
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
    volumes:
      - openwebui_data:/app/backend/data
    ports:
      - "3000:8080"
    networks:
      - twisterlab-network
    depends_on:
      - ollama
    restart: unless-stopped

  # Proxy inverse (nginx)
  nginx:
    image: nginx:alpine
    container_name: twisterlab-nginx
    volumes:
      - ./deployment/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deployment/nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    networks:
      - twisterlab-network
    depends_on:
      - twisterlab
      - openwebui
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  ollama_data:
  openwebui_data:

networks:
  twisterlab-network:
    driver: bridge
```

### Dockerfile de Production

Créez `deployment/docker/Dockerfile.prod` :

```dockerfile
FROM python:3.12-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer l'utilisateur
RUN useradd --create-home --shell /bin/bash twisterlab

# Définir le répertoire de travail
WORKDIR /opt/twisterlab

# Copier les fichiers de dépendances
COPY pyproject.toml requirements.txt ./

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /var/log/twisterlab && \
    chown -R twisterlab:twisterlab /var/log/twisterlab

# Changer d'utilisateur
USER twisterlab

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage
CMD ["python", "-m", "uvicorn", "agents.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 3. Configuration de la Base de Données

### Script d'initialisation

Créez `deployment/docker/init.sql` :

```sql
-- Créer la base de données et l'utilisateur
CREATE DATABASE twisterlab_prod;
CREATE USER twisterlab WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE twisterlab_prod TO twisterlab;

-- Se connecter à la base de données
\c twisterlab_prod;

-- Donner les permissions complètes à l'utilisateur
GRANT ALL ON SCHEMA public TO twisterlab;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO twisterlab;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO twisterlab;

-- Configuration pour les nouvelles tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO twisterlab;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO twisterlab;
```

### Migrations Alembic

```bash
# Appliquer les migrations
docker-compose -f docker-compose.prod.yml exec twisterlab alembic upgrade head

# Vérifier l'état
docker-compose -f docker-compose.prod.yml exec twisterlab alembic current
```

## 4. Configuration Nginx

Créez `deployment/nginx/nginx.conf` :

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=webui:10m rate=30r/s;

    upstream twisterlab_api {
        server twisterlab:8000;
    }

    upstream openwebui {
        server openwebui:8080;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://twisterlab_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # CORS headers
            add_header 'Access-Control-Allow-Origin' 'https://yourdomain.com' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, X-API-Key' always;

            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Web UI
        location / {
            limit_req zone=webui burst=50 nodelay;

            proxy_pass http://openwebui;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 5. Déploiement

### Commandes de déploiement

```bash
# 1. Cloner le repository
git clone https://github.com/yourorg/twisterlab.git
cd twisterlab

# 2. Configurer l'environnement
cp .env.example .env.production
# Éditer .env.production avec vos valeurs

# 3. Démarrer les services
docker-compose -f docker-compose.prod.yml up -d

# 4. Vérifier le déploiement
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs

# 5. Appliquer les migrations
docker-compose -f docker-compose.prod.yml exec twisterlab alembic upgrade head

# 6. Tester l'API
curl https://yourdomain.com/api/health
curl https://yourdomain.com/health
```

### Configuration SSL

```bash
# Utiliser Let's Encrypt
sudo certbot certonly --nginx -d yourdomain.com

# Ou copier les certificats manuellement
sudo mkdir -p deployment/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/nginx/ssl/
```

## 6. Tests de Production

### Tests d'intégration

```bash
# Tests de santé
curl -f https://yourdomain.com/health
curl -f https://yourdomain.com/api/health

# Tests fonctionnels
curl -X POST https://yourdomain.com/api/tickets/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"subject": "Test Ticket", "description": "Test description"}'

# Tests de charge
ab -n 1000 -c 10 https://yourdomain.com/api/health
```

### Monitoring

```bash
# Logs des conteneurs
docker-compose -f docker-compose.prod.yml logs -f twisterlab

# Métriques système
docker stats

# Logs nginx
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log
```

## 7. Maintenance

### Sauvegardes

```bash
# Sauvegarde PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U twisterlab twisterlab_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde des volumes
docker run --rm -v twisterlab_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

### Mises à jour

```bash
# Arrêter les services
docker-compose -f docker-compose.prod.yml down

# Mettre à jour le code
git pull origin main

# Reconstruire et redémarrer
docker-compose -f docker-compose.prod.yml up -d --build

# Appliquer les migrations si nécessaire
docker-compose -f docker-compose.prod.yml exec twisterlab alembic upgrade head
```

### Monitoring continu

- **Logs**: Centraliser avec ELK stack ou Loki
- **Métriques**: Prometheus + Grafana
- **Alertes**: Alertmanager pour les notifications
- **Health checks**: Monitoring automatique des endpoints

## 8. Sécurité

### Configuration de sécurité

```bash
# Firewall
sudo ufw enable
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow ssh

# Fail2Ban pour la protection SSH
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Mises à jour automatiques
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### Audit de sécurité

- Changer tous les mots de passe par défaut
- Utiliser des certificats SSL valides
- Configurer CORS correctement
- Activer les logs d'audit
- Régulièrement scanner les vulnérabilités

## 9. Dépannage

### Problèmes courants

**API ne démarre pas**:
```bash
docker-compose -f docker-compose.prod.yml logs twisterlab
# Vérifier les variables d'environnement et la connectivité DB
```

**Base de données inaccessible**:
```bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U twisterlab -d twisterlab_prod
# Vérifier les credentials et les permissions
```

**Performance lente**:
```bash
# Vérifier les ressources système
docker stats
# Augmenter les workers dans docker-compose.prod.yml
# Optimiser la configuration PostgreSQL
```

## 9. Automatisation du Déploiement

### Script de Déploiement Automatisé

Utilisez le script `deploy.sh` pour automatiser le déploiement complet:

```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Déploiement en production
./deploy.sh prod

# Déploiement en staging
./deploy.sh staging
```

Le script effectue automatiquement:
- ✅ Vérification des prérequis
- ✅ Génération des mots de passe sécurisés
- ✅ Construction des images Docker
- ✅ Démarrage des services
- ✅ Exécution des migrations de base de données
- ✅ Configuration SSL (si domaine configuré)
- ✅ Tests de santé des endpoints

### Script de Monitoring

Le script `monitor.sh` vérifie régulièrement la santé du système:

```bash
# Rendre exécutable et exécuter
chmod +x monitor.sh
./monitor.sh prod

# Planifier avec cron pour monitoring continu
echo "*/5 * * * * /path/to/twisterlab/monitor.sh prod" | crontab -
```

Le monitoring vérifie:
- 🏥 Santé de tous les services Docker
- 💾 Utilisation des ressources (CPU, mémoire, disque)
- 🔗 Connectivité des bases de données
- 🌐 Accessibilité des endpoints API/WebUI

### Variables d'Environnement

Copiez et configurez le fichier d'environnement:

```bash
cp .env.prod.example .env.prod
nano .env.prod  # Éditez avec vos valeurs
```

Variables essentielles à configurer:
- `DOMAIN_NAME`: Votre nom de domaine
- `ADMIN_EMAIL`: Email pour les certificats SSL
- `SECRET_KEY`: Clé secrète pour les sessions
- Mots de passe des bases de données (générés automatiquement par le script)

## 10. Support et Documentation

- **Documentation développeur**: `/docs/` dans le repository
- **API Documentation**: `https://yourdomain.com/docs`
- **Logs système**: `/var/log/twisterlab/`
- **Configuration**: `/opt/twisterlab/config/`

---

**Version**: 1.0.0
**Date**: 2025-10-29
**Auteur**: TwisterLab Team</content>
<parameter name="filePath">DEPLOYMENT.md