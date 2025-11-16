# Architecture de TwisterLab v2

## 1. Vue d'Ensemble et Philosophie

TwisterLab v2 est conçu comme un **Écosystème d'IA Vivant** (*Living AI Ecosystem*). Plutôt que d'être des scripts sans état, les agents sont des services autonomes, monitorables et résilients, qui fonctionnent en continu.

L'architecture est décomposée en quatre couches distinctes :

1.  **Control Plane (API) :** Le point d'entrée sécurisé pour toutes les interactions externes.
2.  **Execution Plane (Agents) :** Là où les agents autonomes vivent et exécutent leurs tâches.
3.  **Data & Persistence Layer :** La mémoire à long et court terme du système.
4.  **Observability Layer :** La couche qui permet de surveiller, mesurer et comprendre le comportement du système.

![High-Level Architecture Diagram](https://i.imgur.com/your-diagram-url.png) 
*(Note : Un diagramme visuel sera ajouté pour illustrer ces interactions.)*

---

## 2. Principes Fondamentaux

Chaque composant de TwisterLab v2 adhère aux principes suivants :

- **Autonomie :** Les agents gèrent leur propre état et leur cycle de vie. Ils sont conçus pour fonctionner sur de longues périodes.
- **Observabilité :** Chaque agent expose un statut, des métriques (via Prometheus) et des logs structurés, permettant un monitoring en temps réel de sa santé et de ses performances.
- **Standardisation :** Tous les agents héritent d'une classe de base commune (`UnifiedAgentBase`), garantissant une interface et un comportement prévisibles (méthodes `.run()`, `.health_check()`, gestion des statuts).

---

## 3. Décomposition par Couche

### a. Control Plane (API)

Le Control Plane est une application **FastAPI** qui sert de passerelle unique et sécurisée vers l'écosystème.

- **Framework :** **FastAPI** pour ses hautes performances, sa nature asynchrone et sa validation de données native.
- **Structure Modulaire :** Le code est organisé en `APIRouter` pour séparer les préoccupations :
    - `api/routes/system.py` : Gère les endpoints non-métier (`/health`, `/metrics`, `/token`).
    - `api/routes/agents.py` : Gère toutes les interactions avec les agents (`/agents`, `/execute`).
- **Sécurité :** L'accès aux endpoints sensibles (comme `/execute`) est protégé par **JWT (JSON Web Tokens)**. La logique de création et de validation des tokens est centralisée dans `api/security.py`.
- **Validation des Données :** **Pydantic** est utilisé (`api/schemas.py`) pour valider automatiquement toutes les données entrantes et sortantes, garantissant la robustesse et la fiabilité des échanges.

### b. Execution Plane (Agents)

C'est le cœur du système, là où la logique métier est exécutée.

- **`AgentRegistry` :** Un singleton (`agents/registry.py`) qui agit comme le **registre central** de tous les agents. Il est responsable de leur instanciation au démarrage de l'API et de leur mise à disposition. C'est la **source unique de vérité** sur les agents disponibles et leur état.
- **`UnifiedAgentBase` :** La classe de base abstraite (`agents/base/unified_agent.py`) dont tous les agents doivent hériter. Elle impose un contrat commun :
    - Un cycle de vie standard avec une méthode `run(context)`.
    - Une gestion d'état standardisée avec l'enum `AgentStatus` (e.g., `IDLE`, `RUNNING`, `ERROR`).
    - Des hooks intégrés pour l'auto-guérison et l'émission de métriques.

### c. Data & Persistence Layer

Cette couche constitue la mémoire du système.

- **PostgreSQL :** Utilisé pour le stockage à long terme des données critiques et structurées (par exemple, l'historique des tickets, les résultats d'audits, les configurations des workflows).
- **Redis :** Utilisé pour le stockage de données volatiles et l'accès rapide :
    - Cache pour les sessions et les données fréquemment consultées.
    - Potentiellement comme bus de messages pour la communication inter-agents.

### d. Observability Layer

Cette couche fournit les outils pour observer et comprendre le système en temps réel.

- **Prometheus :** Un service de monitoring qui collecte périodiquement ("scrape") les métriques exposées par l'endpoint `/metrics` de l'API.
- **Grafana :** Un outil de visualisation qui se connecte à Prometheus pour afficher les métriques sous forme de tableaux de bord. Il permet de suivre la santé de l'API, les performances des agents, le nombre de tickets traités, etc.
- **Logging Structuré :** Tous les composants, de l'API aux agents, sont configurés pour émettre des logs dans un format JSON structuré, ce qui facilite leur collecte, leur recherche et leur analyse par des outils centralisés.

---

## 4. Architecture de Déploiement

L'ensemble de l'écosystème est conçu pour être déployé de manière cohérente et reproductible.

- **Containerisation :** Chaque service (API, PostgreSQL, Redis, Prometheus, Grafana, etc.) est packagé dans une image **Docker**.
- **Orchestration :** **Docker Swarm** est utilisé pour gérer l'ensemble des services comme une "stack" unifiée. Il gère le déploiement, le scaling et la mise en réseau des conteneurs.
- **Réseau :** Un réseau "overlay" Docker est créé, permettant une communication sécurisée et transparente entre tous les services de la stack, où qu'ils soient déployés sur le cluster Swarm.
- **Configuration :** La configuration spécifique à chaque environnement (développement, production) est gérée via des fichiers `.env`, qui sont chargés par les services au démarrage.
- **Gestion des Secrets :** L'objectif à terme est de migrer tous les secrets (mots de passe, clés API) vers le système de gestion des secrets de Docker Swarm pour une sécurité maximale.
