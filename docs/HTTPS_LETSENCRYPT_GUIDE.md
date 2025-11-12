# Guide: Activer HTTPS avec Let's Encrypt sur TwisterLab
**Date**: 2025-11-10
**Version**: 1.0

---

## 🔒 CONTEXTE

**Situation actuelle:**
- Traefik utilise un **certificat auto-signé** (self-signed)
- Les services internes communiquent en **HTTP** (pas affectés)
- HTTPS externe affiche avertissement navigateur

**Objectif:**
Activer HTTPS valide avec certificats Let's Encrypt auto-renouvelés

---

## ✅ PRÉREQUIS

### 1. Domaine Public
```bash
# Vous avez besoin d'un nom de domaine pointant vers votre serveur
# Exemples:
#   - twisterlab.example.com → 192.168.0.30
#   - *.twisterlab.example.com (wildcard)

# Vérifier DNS:
nslookup twisterlab.example.com
# Doit retourner: 192.168.0.30 (IP publique si derrière NAT)
```

### 2. Port 80 et 443 Accessibles
```bash
# Depuis Internet, ces ports doivent atteindre edgeserver
# Configurer NAT/Port forwarding sur routeur si nécessaire:
#   Port 80 (HTTP) → 192.168.0.30:80
#   Port 443 (HTTPS) → 192.168.0.30:443

# Test depuis externe:
curl http://twisterlab.example.com
curl https://twisterlab.example.com
```

### 3. Email pour Let's Encrypt
```bash
# Email requis pour notifications de renouvellement
EMAIL="admin@example.com"
```

---

## 🔧 CONFIGURATION TRAEFIK ACME

### Étape 1: Créer Fichier acme.json

```bash
# Sur edgeserver
ssh twister@192.168.0.30

# Créer fichier pour stocker certificats
sudo mkdir -p /opt/twisterlab/traefik/acme
sudo touch /opt/twisterlab/traefik/acme/acme.json
sudo chmod 600 /opt/twisterlab/traefik/acme/acme.json
```

### Étape 2: Configuration Traefik

**Fichier**: `infrastructure/traefik/traefik.yml`

```yaml
global:
  checkNewVersion: true
  sendAnonymousUsage: false

api:
  dashboard: true
  insecure: false  # Désactiver accès insecure au dashboard

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt
        domains:
          - main: "twisterlab.example.com"
            sans:
              - "*.twisterlab.example.com"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@example.com"  # ← MODIFIER
      storage: /acme/acme.json
      httpChallenge:
        entryPoint: web
      # Ou pour wildcard (requiert DNS challenge):
      # dnsChallenge:
      #   provider: cloudflare  # ou autre provider DNS
      #   delayBeforeCheck: 30

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: twisterlab_traefik-public
    swarmMode: true

log:
  level: INFO

accessLog:
  filePath: "/var/log/traefik/access.log"
```

### Étape 3: Mettre à Jour Docker Compose

**Fichier**: `infrastructure/docker/docker-compose.unified.yml`

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--configFile=/etc/traefik/traefik.yml"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard (protégé par auth)
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./infrastructure/traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - /opt/twisterlab/traefik/acme:/acme
    networks:
      - twisterlab_traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager
      labels:
        # Dashboard avec authentification
        - "traefik.enable=true"
        - "traefik.http.routers.traefik.rule=Host(`traefik.twisterlab.example.com`)"
        - "traefik.http.routers.traefik.entrypoints=websecure"
        - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
        - "traefik.http.routers.traefik.service=api@internal"
        - "traefik.http.routers.traefik.middlewares=auth"
        - "traefik.http.middlewares.auth.basicauth.users=admin:$$apr1$$..."  # htpasswd

  # Grafana avec HTTPS
  grafana:
    # ... config existante ...
    deploy:
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.grafana.rule=Host(`grafana.twisterlab.example.com`)"
        - "traefik.http.routers.grafana.entrypoints=websecure"
        - "traefik.http.routers.grafana.tls.certresolver=letsencrypt"
        - "traefik.http.services.grafana.loadbalancer.server.port=3000"

  # Prometheus avec HTTPS
  prometheus:
    # ... config existante ...
    deploy:
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.prometheus.rule=Host(`prometheus.twisterlab.example.com`)"
        - "traefik.http.routers.prometheus.entrypoints=websecure"
        - "traefik.http.routers.prometheus.tls.certresolver=letsencrypt"
        - "traefik.http.services.prometheus.loadbalancer.server.port=9090"
        - "traefik.http.routers.prometheus.middlewares=auth"  # Protéger avec auth
```

---

## 🚀 DÉPLOIEMENT

### 1. Générer htpasswd pour Auth

```bash
# Générer password pour Traefik dashboard
sudo apt-get install -y apache2-utils
htpasswd -n admin
# Copier le résultat (doubler les $ pour Docker)
# admin:$apr1$xyz...
```

### 2. Déployer Configuration

```bash
# Copier fichiers sur edgeserver
scp infrastructure/traefik/traefik.yml twister@192.168.0.30:/tmp/
scp infrastructure/docker/docker-compose.unified.yml twister@192.168.0.30:/tmp/

# SSH vers edgeserver
ssh twister@192.168.0.30

# Déplacer config
sudo cp /tmp/traefik.yml /opt/twisterlab/traefik/
sudo cp /tmp/docker-compose.unified.yml /opt/twisterlab/

# Redéployer stack
cd /opt/twisterlab
docker stack deploy -c docker-compose.unified.yml twisterlab
```

### 3. Vérifier Certificats

```bash
# Attendre 30-60 secondes pour obtention certificat

# Vérifier logs Traefik
docker service logs twisterlab_traefik | grep -i acme

# Devrait afficher:
# "Obtaining certificate for domain twisterlab.example.com"
# "Certificate obtained successfully"

# Vérifier fichier acme.json
sudo cat /opt/twisterlab/traefik/acme/acme.json
# Devrait contenir les certificats JSON
```

### 4. Tester HTTPS

```bash
# Depuis navigateur ou curl
curl https://grafana.twisterlab.example.com
curl https://prometheus.twisterlab.example.com
curl https://traefik.twisterlab.example.com

# Vérifier certificat valide:
openssl s_client -connect grafana.twisterlab.example.com:443 -servername grafana.twisterlab.example.com < /dev/null 2>/dev/null | grep -A2 "Verify"
# Devrait afficher: Verify return code: 0 (ok)
```

---

## 🔄 RENOUVELLEMENT AUTOMATIQUE

Let's Encrypt certificats expirent après **90 jours**.
Traefik les renouvelle **automatiquement** 30 jours avant expiration.

**Vérifier renouvellement:**
```bash
# Logs Traefik montreront:
docker service logs twisterlab_traefik | grep renew

# Ou forcer renouvellement manuel:
# 1. Supprimer acme.json
sudo rm /opt/twisterlab/traefik/acme/acme.json
sudo touch /opt/twisterlab/traefik/acme/acme.json
sudo chmod 600 /opt/twisterlab/traefik/acme/acme.json

# 2. Redémarrer Traefik
docker service update --force twisterlab_traefik
```

---

## 🛡️ SÉCURITÉ ADDITIONNELLE

### 1. Bloquer Accès Direct aux Ports

```bash
# Firewall: Autoriser SEULEMENT 80, 443 depuis Internet
# Bloquer 3000, 8000, 9090, etc en accès direct

sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 3000/tcp  # Grafana accessible UNIQUEMENT via Traefik
sudo ufw deny 8000/tcp  # API
sudo ufw deny 9090/tcp  # Prometheus
sudo ufw enable
```

### 2. Authentification sur Services Sensibles

```yaml
# Ajouter BasicAuth sur Prometheus, Traefik, etc
- "traefik.http.routers.prometheus.middlewares=auth"
- "traefik.http.middlewares.auth.basicauth.users=admin:$$apr1$$..."
```

### 3. HSTS Headers

```yaml
# Forcer HTTPS même si user tape http://
- "traefik.http.middlewares.hsts.headers.stsSeconds=31536000"
- "traefik.http.middlewares.hsts.headers.stsIncludeSubdomains=true"
- "traefik.http.routers.grafana.middlewares=hsts"
```

---

## ⚠️ TROUBLESHOOTING

### Certificat Non Obtenu

**Erreur:** `Unable to obtain ACME certificate`

**Solutions:**
1. Vérifier DNS pointe vers IP publique correcte
2. Vérifier port 80 accessible depuis Internet
3. Vérifier email valide dans config
4. Logs détaillés: `docker service logs twisterlab_traefik --tail 100`

### Rate Limit Let's Encrypt

**Erreur:** `too many certificates already issued`

**Solutions:**
- Let's Encrypt limite: 50 certificats/semaine/domaine
- Utiliser **staging server** pour tests:
  ```yaml
  acme:
    caServer: "https://acme-staging-v02.api.letsencrypt.org/directory"
  ```
- Production: Supprimer `caServer` après tests réussis

### Wildcard Certificate Échec

**Erreur:** HTTP challenge ne supporte pas wildcard

**Solution:** Utiliser DNS challenge
```yaml
acme:
  dnsChallenge:
    provider: cloudflare  # Ou votre provider DNS
    delayBeforeCheck: 30
```

Configurer credentials DNS provider:
```bash
export CF_API_EMAIL="admin@example.com"
export CF_API_KEY="your-cloudflare-api-key"
```

---

## 📋 CHECKLIST DÉPLOIEMENT

- [ ] Domaine public configuré et DNS actif
- [ ] Ports 80/443 accessibles depuis Internet
- [ ] Email Let's Encrypt configuré
- [ ] Fichier acme.json créé avec chmod 600
- [ ] traefik.yml mis à jour avec acme config
- [ ] docker-compose.yml mis à jour avec labels TLS
- [ ] htpasswd généré pour authentification
- [ ] Stack redéployée
- [ ] Certificats obtenus (vérifier logs)
- [ ] HTTPS fonctionnel (test navigateur)
- [ ] Firewall configuré (bloquer accès direct)
- [ ] Authentification testée sur services sensibles

---

## 🎯 RÉSULTAT ATTENDU

Après configuration:

✅ **https://grafana.twisterlab.example.com** - Grafana avec certificat valide
✅ **https://prometheus.twisterlab.example.com** - Prometheus protégé par auth
✅ **https://traefik.twisterlab.example.com** - Traefik dashboard avec auth
✅ **http://** → Redirige automatiquement vers **https://**
✅ Certificats renouvelés automatiquement tous les 60 jours

---

**Auteur**: TwisterLab Team
**Version**: 1.0
**Dernière Mise à Jour**: 2025-11-10
