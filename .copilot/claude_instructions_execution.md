# INSTRUCTIONS COPILOTE - SÉQUENCE D'EXÉCUTION TWISTERLAB
# Date: 1 novembre 2025
# Contexte: Implémentation finale TwisterLab v1.0.0 avec MCP + Copilot

## 🎯 MISSION CRITIQUE
Exécuter la séquence complète d'implémentation TwisterLab avec délégation totale au Copilote VS Code.

## 📋 SÉQUENCE D'EXÉCUTION (ORDRE IMPÉRATIF)

### PHASE 1: AUDIT ET VALIDATION
**Objectif**: Auditer l'état actuel du système TwisterLab
**Actions**:
- Vérifier l'intégrité de tous les modules TwisterLang (encoder, decoder, sync)
- Valider la structure des agents (Classifier, Resolver, Desktop Commander)
- Contrôler la configuration FastAPI et SQLAlchemy
- Tester les connexions base de données (PostgreSQL, Redis)
- Vérifier les dépendances et requirements.txt
- Auditer la sécurité (authentification, autorisations)
- Contrôler les tests unitaires et d'intégration

### PHASE 2-3: MODIFICATION DES CONFIGURATIONS
**Objectif**: Adapter les configurations pour les phases 2 et 3
**Actions Phase 2 (Grafana)**:
- Modifier docker-compose.yml pour inclure Grafana + Prometheus
- Créer configurations Grafana (datasources, dashboards)
- Ajouter métriques d'observabilité aux agents
- Configurer alertes et monitoring

**Actions Phase 3 (Autonome)**:
- Implémenter auto-scaling des agents
- Configurer self-healing et failover
- Ajouter optimisations de performance
- Préparer mode communautaire

### PHASE 4: CRÉATION DU SCRIPT DE RELEASE
**Objectif**: Créer le script complet de déploiement communautaire
**Actions**:
- Créer script `deploy_community.py` avec installation automatisée
- Générer documentation de déploiement
- Préparer exemples d'usage communautaire
- Créer guides de contribution
- Configurer CI/CD pour releases automatiques

### PHASE 5: TESTS MCP ISOLÉS
**Objectif**: Valider chaque serveur MCP indépendamment
**Actions**:
- Tester MCP GitHub (connexion repo, commits, PRs)
- Tester MCP Azure (ressources, coûts, déploiement)
- Tester MCP Local (tests, builds, sécurité)
- Tester MCP Grafana (dashboards, alertes)
- Valider intégration Copilot + MCP

### PHASE 6: RAPPORT FINAL
**Objectif**: Produire rapport complet d'implémentation
**Actions**:
- Compiler résultats de tous les audits
- Documenter modifications apportées
- Reporter statut de chaque MCP
- Fournir métriques de performance
- Créer plan d'actions suivant

## 🔧 CONTRAINTES TECHNIQUES

### Budget Azure
- **Limite absolue**: $200 total sur 14 jours
- Monitoring continu des coûts
- Optimisations automatiques si approche limite

### Sécurité
- Authentification sécurisée pour tous les MCP
- Validation des entrées/sorties
- Audit des opérations sensibles

### Performance
- Tests de charge avant déploiement
- Optimisations TwisterLang (50-70% réduction tokens)
- Monitoring des métriques critiques

## 🎮 MODE OPÉRATOIRE COPILOTE

### Communication
- Utiliser exclusivement les commandes MCP: `@mcp github`, `@mcp azure`, `@mcp local`, `@mcp grafana`
- Rapporter progrès après chaque phase majeure
- Demander confirmation pour opérations critiques

### Gestion d'Erreurs
- Retry automatique (3 tentatives max)
- Fallback vers opérations locales si services cloud indisponibles
- Escalade immédiate pour erreurs critiques

### Validation
- Tests automatisés après chaque modification
- Vérification des déploiements
- Audit de sécurité continu

## 📊 LIVRABLES ATTENDUS

1. **Rapport d'audit Phase 1** - État détaillé du système
2. **Configurations modifiées** - Fichiers adaptés pour Phase 2-3
3. **Script de déploiement** - `deploy_community.py` complet
4. **Rapport de tests MCP** - Statut de chaque serveur
5. **Rapport final** - Synthèse complète avec métriques

## 🚀 EXÉCUTION IMMÉDIATE

**COMMANDES DE DÉMARRAGE**:
```
@twisterlab Execute Phase 1  # Audit initial
@twisterlab Execute Phase 2  # Modifications configs
@twisterlab Execute Phase 3  # Adaptations autonomes
@twisterlab Execute Phase 4  # Script release
@mcp local run-tests         # Tests MCP isolés
@twisterlab status          # Rapport final
```

## ⚡ DÉLÉGATION COMPLÈTE

Le Copilote VS Code a **autorité totale** pour:
- Modifier tous les fichiers du projet
- Exécuter toutes les commandes nécessaires
- Prendre des décisions d'optimisation
- Gérer les erreurs et retry
- Reporter automatiquement les progrès

**Priorité absolue**: Maintenir le système sous $200 Azure tout en atteignant les objectifs de déploiement communautaire.

---

**Exécution immédiate demandée. Commencer par Phase 1.**