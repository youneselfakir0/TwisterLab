# Rapport d'Audit : Architecture du Stack Monitoring TwisterLab

**Date de l'audit :** 15 novembre 2025

---

### **1. Résumé des changements & Incohérences Majeures**

J'ai analysé trois fichiers de configuration Docker Compose qui définissent des architectures de monitoring distinctes :

*   **`docker-compose.monitoring.yml`**: Cette configuration est orientée pour un **cluster Docker Swarm**. Elle utilise des `configs` et des volumes `external`, ce qui est une bonne pratique pour la gestion des configurations et des données persistantes dans un environnement Swarm multi-nœuds. Les services (Prometheus, Grafana, Jaeger, Alertmanager) sont configurés pour être exposés via Traefik.
*   **`docker-compose.monitoring-full.yml`**: Cette configuration semble être une approche **"tout-en-un"** potentiellement destinée à un environnement de développement ou à un déploiement sur un seul nœud. Contrairement à la version Swarm, elle utilise des *bind-mounts* pour les fichiers de configuration au lieu des `configs` Docker Swarm, ce qui réduit sa flexibilité et sa portabilité dans un cluster. Elle inclut une collection plus large d'exportateurs (Node-Exporter, Postgres-Exporter, Redis-Exporter, cAdvisor, Blackbox-Exporter). L'utilisation de `container_name` est également présente, ce qui est généralement déconseillé en mode Swarm car cela peut interférer avec la gestion des services par Swarm.
*   **`docker-compose.test-monitoring.yml`**: Ce fichier définit un environnement de **test d'intégration** autonome. Il inclut ses propres services de base de données (PostgreSQL, Redis) avec des mots de passe de test, ainsi que les composants de monitoring de base (Prometheus, Grafana).

**Incohérence fondamentale détectée :** Le projet maintient deux stratégies de déploiement distinctes et potentiellement conflictuelles pour les configurations (Docker Swarm `configs` vs. *bind-mounts*). Cette dualité introduit un risque élevé d'erreurs, de confusion et de difficultés de maintenance lors des déploiements en production.

---

### **2. Risques & Failles de Sécurité Détectés**

*   **Risque Critique : Mots de passe et identifiants en clair**
    *   **`docker-compose.monitoring.yml`**: Le mot de passe administrateur de Grafana (`GF_SECURITY_ADMIN_PASSWORD=admin`) est codé en dur et trivial.
    *   **`docker-compose.monitoring-full.yml`**: Les identifiants complets de la base de données PostgreSQL (`DATA_SOURCE_NAME: "postgresql://twisterlab:twisterlab_password@..."`) sont exposés en clair.
    *   **Impact :** Ces informations sensibles sont directement accessibles dans les fichiers de configuration, offrant un accès non autorisé aux services de monitoring et potentiellement à la base de données de production à toute personne ayant accès au code ou aux fichiers de déploiement.

*   **Risque Élevé : Utilisation d'images Docker non versionnées (`:latest`)**
    *   **Concerne tous les fichiers** (`docker-compose.monitoring.yml`, `docker-compose.monitoring-full.yml`, `docker-compose.test-monitoring.yml`). Tous les services utilisent l'étiquette `:latest` pour leurs images Docker.
    *   **Impact :** Un redéploiement peut entraîner le téléchargement d'une nouvelle version de l'image sans avertissement, introduisant des modifications imprévues, des bugs, des incompatibilités ou même des failles de sécurité. Cela compromet la reproductibilité et la stabilité des déploiements.

*   **Risque Moyen : Incohérence des configurations et des chemins**
    *   Le port exposé pour Prometheus est `9091:9090` dans `docker-compose.monitoring.yml` (avec un commentaire mentionnant un conflit avec Traefik), mais `9090:9090` dans les autres fichiers. Cette divergence peut entraîner des erreurs de configuration ou de connectivité si les configurations de scraping ne sont pas ajustées en conséquence.
    *   Les chemins des fichiers de configuration varient (`./monitoring/` vs `./infrastructure/monitoring/`), ce qui rend la gestion des configurations plus complexe et sujette aux erreurs.

*   **Risque Moyen : Absence de Healthchecks**
    *   Le fichier `docker-compose.monitoring.yml`, qui semble être la configuration principale pour la production en Swarm, ne contient **aucun `healthcheck`** pour ses services.
    *   **Impact :** Docker Swarm peut considérer un conteneur comme "en cours d'exécution" même s'il est dans un état dégradé ou non fonctionnel (par exemple, Grafana ne répondant pas aux requêtes, ou Prometheus incapable de collecter des métriques). Cela peut entraîner un routage de trafic vers des services non opérationnels.

*   **Risque Faible : Absence de limites de ressources**
    *   Aucun des services définis dans les fichiers n'a de limites de CPU ou de mémoire (`deploy.resources.limits`) configurées.
    *   **Impact :** Un service défaillant ou mal configuré (par exemple, une requête Prometheus gourmande en ressources) pourrait consommer toutes les ressources disponibles sur un nœud, provoquant une dégradation des performances ou une panne complète des autres services sur ce même nœud.

---

### **3. Propositions d'Améliorations (Suggestions)**

*   **Action : Unifier et standardiser la stratégie de déploiement**
    *   **Suggestion :** Adopter une approche unique et cohérente pour la gestion des configurations. La méthode utilisant les `configs` et `secrets` de Docker Swarm (telle qu'initiée dans `docker-compose.monitoring.yml`) est la plus appropriée et robuste pour un environnement de production en cluster. Le fichier `docker-compose.monitoring-full.yml` devrait être révisé pour s'aligner sur cette stratégie ou être clairement identifié comme un fichier de développement local non destiné au déploiement Swarm.
    *   `À appliquer UNIQUEMENT après validation manuelle.`

*   **Action : Sécuriser les informations sensibles avec Docker Secrets**
    *   **Suggestion :** Remplacer immédiatement tous les mots de passe et identifiants codés en dur par des **Docker Secrets**. C'est la méthode recommandée pour gérer les informations sensibles dans un environnement Docker Swarm.
        *   **Exemple pour Grafana (à adapter pour PostgreSQL et Redis) :**
            ```yaml
            # 1. Créer le secret (une seule fois sur le manager Swarm) :
            # printf "VotreMotDePasseAdminSecurise" | docker secret create grafana_admin_password -

            # 2. Mettre à jour le service Grafana dans le docker-compose.yml :
            services:
              grafana:
                environment:
                  # Utilise le suffixe _FILE pour que Grafana lise le secret depuis le fichier
                  - GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/grafana_admin_password
                secrets:
                  - grafana_admin_password # Référence le secret créé
            secrets:
              grafana_admin_password:
                external: true # Indique que le secret est géré en externe
            ```
    *   `À appliquer UNIQUEMENT après validation manuelle.`

*   **Action : Figer les versions des images Docker**
    *   **Suggestion :** Modifier toutes les références d'images Docker pour utiliser des versions spécifiques et stables (ex: `prom/prometheus:v2.51.2`, `grafana/grafana:10.4.2`). Cela garantit la reproductibilité des déploiements et minimise les risques d'introduire des régressions inattendues.
    *   `À appliquer UNIQUEMENT après validation manuelle.`

*   **Action : Améliorer la résilience et la stabilité des services**
    *   **Suggestion :**
        1.  **Ajouter des `healthchecks` :** Intégrer des `healthchecks` pertinents pour tous les services dans `docker-compose.monitoring.yml` afin que Docker Swarm puisse détecter et gérer les conteneurs non fonctionnels.
        2.  **Définir des limites de ressources :** Configurer des `deploy.resources.limits` (ex: `memory: 1G`, `cpus: '0.5'`) pour tous les services, en particulier pour Prometheus et Grafana, afin de prévenir l'épuisement des ressources et d'assurer une meilleure isolation des performances.
    *   `À appliquer UNIQUEMENT après validation manuelle.`

*   **Action : Réviser l'utilisation de `container_name`**
    *   **Suggestion :** Supprimer l'attribut `container_name` des services dans `docker-compose.monitoring-full.yml` si ce fichier est destiné à être utilisé avec `docker stack deploy`. En mode Swarm, Docker gère dynamiquement les noms des conteneurs, et l'utilisation de `container_name` peut entraîner des conflits ou empêcher la mise à l'échelle.
    *   `À appliquer UNIQUEMENT après validation manuelle.`

---
