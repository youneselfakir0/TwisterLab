# Configuration CI/CD pour TwisterLab

## Variables d'environnement GitHub

### Variables obligatoires
```
AWS_REGION=us-east-1
PYTHON_VERSION=3.12
```

### Variables optionnelles
```
DOCKER_REGISTRY=your-registry.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## Secrets GitHub

### AWS (pour déploiement)
```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

### Base de données de test
```
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
TEST_REDIS_URL=redis://localhost:6379/1
```

### Monitoring et alertes
```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
DATADOG_API_KEY=your-datadog-api-key
```

### Sécurité
```
SONARQUBE_TOKEN=your-sonarqube-token
BLACKDUCK_API_TOKEN=your-blackduck-token
```

## Configuration par environnement

### Développement
- Tests unitaires uniquement
- Pas de déploiement automatique
- Notifications Slack/Discord

### Staging
- Tests complets (unitaires + intégration + charge)
- Déploiement automatique sur push
- Tests de sécurité activés

### Production
- Tests complets + sécurité + performance
- Déploiement manuel ou sur tag
- Rollback automatique en cas d'échec
- Monitoring complet

## Commandes de déploiement manuel

### Via GitHub Actions
```bash
# Déclencher un déploiement manuel
gh workflow run ci-cd.yml --ref main
```

### Via script local
```bash
# Build et push
docker build -f deployment/docker/Dockerfile.prod -t twisterlab:latest .
docker tag twisterlab:latest your-registry.com/twisterlab:latest
docker push your-registry.com/twisterlab:latest

# Déployer
kubectl apply -f k8s/production.yaml
# ou
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring du pipeline

### Métriques à surveiller
- **Temps d'exécution** : < 15 minutes pour le pipeline complet
- **Taux de succès** : > 95% sur la branche main
- **Couverture de code** : > 80%
- **Performance tests** : Temps de réponse < 1000ms P95

### Alertes
- Échec du pipeline sur main
- Dégradation des performances > 20%
- Baisse de couverture > 5%
- Vulnérabilités de sécurité détectées

## Récupération d'urgence

### Rollback rapide
```bash
# Via GitHub (si déployé)
gh workflow run rollback.yml --ref main

# Via Docker
docker tag twisterlab:v1.0.0 twisterlab:latest
docker-compose -f docker-compose.prod.yml up -d

# Via Kubernetes
kubectl rollout undo deployment/twisterlab
```

### Debug du pipeline
```bash
# Voir les logs détaillés
gh run list --workflow=ci-cd.yml
gh run view <run-id> --log

# Tester localement
act -j test
act -j docker
```

---

**Configuration validée** : ✅ Pipeline CI/CD opérationnel