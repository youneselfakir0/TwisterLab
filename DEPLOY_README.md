# 🚀 Déploiement Rapide TwisterLab

## Prérequis

- Docker & Docker Compose
- Domaine configuré (optionnel pour SSL)
- Ports 80, 443, 8000, 3000 disponibles

## Déploiement en 3 étapes

### 1. Configuration

```bash
# Copier et éditer la configuration
cp .env.prod.example .env.prod
nano .env.prod  # Configurer DOMAIN_NAME, ADMIN_EMAIL, etc.
```

### 2. Déploiement

```bash
# Rendre exécutable et lancer
chmod +x deploy.sh
./deploy.sh prod
```

### 3. Vérification

```bash
# Vérifier les services
docker-compose -f docker-compose.prod.yml ps

# Tester les endpoints
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:3000
```

## Accès

- **API**: `http://localhost:8000` ou `https://yourdomain.com`
- **WebUI**: `http://localhost:3000` ou `https://yourdomain.com/webui`
- **Documentation API**: `https://yourdomain.com/docs`

## Monitoring

```bash
# Monitoring manuel
./monitor.sh prod

# Monitoring automatique (toutes les 5 minutes)
echo "*/5 * * * * /path/to/twisterlab/monitor.sh prod" | crontab -
```

## Commandes Utiles

```bash
# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Redémarrage
docker-compose -f docker-compose.prod.yml restart

# Arrêt
docker-compose -f docker-compose.prod.yml down

# Mise à jour
docker-compose -f docker-compose.prod.yml pull && ./deploy.sh prod
```

## Support

📖 [Documentation complète](DEPLOYMENT.md)  
🐛 [Issues](https://github.com/yourorg/twisterlab/issues)  
📧 admin@yourdomain.com