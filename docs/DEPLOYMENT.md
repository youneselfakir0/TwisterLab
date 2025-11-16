# Guide de Déploiement de TwisterLab v2

Ce document décrit la procédure standard pour déployer, mettre à jour et maintenir l'écosystème TwisterLab v2 en production.

---

## 1. Vue d'Ensemble et Stratégie

La méthode de déploiement officielle pour TwisterLab v2 repose sur **Docker Swarm**. Cette approche nous permet de gérer l'ensemble de nos services (API, base de données, monitoring, etc.) comme une "stack" déclarative et résiliente.

Pour simplifier ce processus, le projet inclut une série de scripts **PowerShell** qui automatisent les tâches de déploiement les plus courantes.

---

## 2. Prérequis

Avant de lancer un déploiement, assurez-vous que les conditions suivantes sont remplies :

1.  **Docker Swarm Initialisé :** Le ou les nœuds de votre serveur de production doivent faire partie d'un Swarm. Si ce n'est pas le cas, exécutez :
    ```bash
    docker swarm init
    ```
2.  **Fichier d'Environnement Prêt :** Un fichier `.env.prod` doit exister à la racine du projet et être correctement rempli avec toutes les configurations et les secrets nécessaires (mots de passe de base de données, clés API, etc.). Vous pouvez le créer à partir de l'exemple :
    ```bash
    # Sous Windows, utilisez 'copy'
    copy .env.prod.example .env.prod
    # Modifiez ensuite le fichier .env.prod
    ```

---

## 3. Procédure de Déploiement Standard

Cette procédure décrit un déploiement initial ou une mise à jour complète de la stack.

### Étape 1 : Exécuter le Script de Déploiement

Le script `deploy_production_simple.ps1` est le point d'entrée principal pour un déploiement standard.

```powershell
# Exécutez le script depuis la racine du projet
./deploy_production_simple.ps1
```

Ce script va automatiquement :
- Lire la configuration depuis `.env.prod`.
- Construire les images Docker nécessaires si elles n'existent pas localement.
- Déployer ou mettre à jour la stack complète sur Docker Swarm en utilisant le fichier `docker-compose.prod.yml`.

### Étape 2 : Vérifier le Déploiement

Après l'exécution du script, vérifiez que tous les services ont démarré correctement.

```bash
# 1. Lister tous les services de la stack
docker service ls

# La colonne REPLICAS doit afficher 1/1 pour chaque service.
# NAME                MODE        REPLICAS   IMAGE
# twisterlab_api      replicated  1/1        twisterlab/api:latest
# twisterlab_postgres replicated  1/1        postgres:15-alpine
# ...

# 2. Inspecter les logs d'un service en cas de problème
# Si un service n'atteint pas 1/1, vérifiez ses logs pour des erreurs.
docker service logs twisterlab_api

# 3. Tester le point de terminaison de santé (health check)
# Remplacez <DOCKER_HOST_IP> par l'adresse IP de votre serveur.
curl http://<DOCKER_HOST_IP>:8000/health
# La réponse doit être : {"status":"healthy", ...}
```

---

## 4. Mise à Jour d'un Service Unique

Si vous avez uniquement modifié un seul service (par exemple, l'API), vous n'avez pas besoin de redéployer toute la stack. Vous pouvez effectuer une mise à jour ciblée.

1.  **Construisez et Taguez votre Nouvelle Image :**
    ```bash
    docker build -t your-registry/twisterlab-api:v2.1.0 .
    docker push your-registry/twisterlab-api:v2.1.0
    ```

2.  **Mettez à Jour le Service dans Swarm :**
    Docker Swarm effectuera une mise à jour "rolling" pour remplacer les anciens conteneurs par les nouveaux sans interruption de service.
    ```bash
    docker service update --image your-registry/twisterlab-api:v2.1.0 twisterlab_api
    ```

---

## 5. Procédure de Rollback (Retour en Arrière)

En cas de problème après une mise à jour, Docker Swarm facilite le retour à la version précédente.

### Rollback Automatisé (Recommandé)

La commande suivante annulera la dernière mise à jour du service et le fera revenir à sa configuration précédente.

```bash
# Annule la dernière mise à jour du service API
docker service update --rollback twisterlab_api
```

### Rollback Manuel

Si un script de rollback plus complexe est fourni (ex: `rollback_service.ps1`), il peut être utilisé pour des scénarios de restauration plus spécifiques. Consultez le contenu du script pour comprendre son fonctionnement avant de l'exécuter.

---

## 6. Scénarios de Déploiement Avancés

Le référentiel contient des scripts supplémentaires pour des cas d'usage plus complexes (haute disponibilité, déploiement multi-nœuds, etc.), tels que `deploy-failover-production.ps1`.

Ces scripts sont destinés aux utilisateurs avancés. Il est recommandé d'inspecter leur contenu pour bien comprendre leur impact avant de les utiliser.
