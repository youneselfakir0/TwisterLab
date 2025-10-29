#!/bin/bash

# Script de monitoring pour TwisterLab
# Vérifie la santé des services et envoie des alertes si nécessaire

set -e

ENVIRONMENT=${1:-prod}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"
LOG_FILE="logs/monitoring_$(date +%Y%m%d).log"

# Fonction de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Fonction d'alerte (à configurer selon vos besoins)
alert() {
    local message="$1"
    log "🚨 ALERT: $message"

    # Ici vous pouvez ajouter des intégrations comme:
    # - Email: mail -s "TwisterLab Alert" admin@domain.com <<< "$message"
    # - Slack webhook
    # - PagerDuty
    # - etc.
}

log "🔍 Démarrage du monitoring TwisterLab ($ENVIRONMENT)"

# Vérifier si Docker Compose est en cours d'exécution
if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    alert "Aucun service TwisterLab n'est en cours d'exécution"
    exit 1
fi

# Vérifier chaque service
SERVICES=("postgres" "redis" "ollama" "api" "webui" "nginx")
FAILED_SERVICES=()

for service in "${SERVICES[@]}"; do
    container_name="twisterlab-${service}-${ENVIRONMENT}"

    if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
        log "✅ $service: OK"

        # Vérifications spécifiques par service
        case $service in
            "postgres")
                if ! docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U twisterlab >/dev/null 2>&1; then
                    alert "PostgreSQL n'est pas prêt à accepter des connexions"
                    FAILED_SERVICES+=("$service")
                fi
                ;;
            "redis")
                if ! docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
                    alert "Redis ne répond pas"
                    FAILED_SERVICES+=("$service")
                fi
                ;;
            "api")
                if ! curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
                    alert "API endpoint /health non accessible"
                    FAILED_SERVICES+=("$service")
                fi
                ;;
            "webui")
                if ! curl -f -s http://localhost:3000 >/dev/null 2>&1; then
                    alert "WebUI non accessible"
                    FAILED_SERVICES+=("$service")
                fi
                ;;
            "nginx")
                if ! curl -f -s http://localhost/health >/dev/null 2>&1; then
                    alert "Nginx endpoint /health non accessible"
                    FAILED_SERVICES+=("$service")
                fi
                ;;
        esac
    else
        alert "Service $service n'est pas en cours d'exécution"
        FAILED_SERVICES+=("$service")
    fi
done

# Vérifier l'utilisation des ressources
log "📊 Utilisation des ressources:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep twisterlab || true

# Vérifier l'espace disque
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    alert "Espace disque critique: ${DISK_USAGE}% utilisé"
fi

# Vérifier la mémoire
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEM_USAGE" -gt 90 ]; then
    alert "Mémoire critique: ${MEM_USAGE}% utilisé"
fi

# Résumé
if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    log "✅ Tous les services sont opérationnels"
else
    alert "Services défaillants: ${FAILED_SERVICES[*]}"
    exit 1
fi

log "🏁 Monitoring terminé"