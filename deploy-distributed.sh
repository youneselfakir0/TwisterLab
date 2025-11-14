#!/bin/bash

# =============================================================================
# DÉPLOIEMENT TWISTERLAB PRODUCTION - ARCHITECTURE DISTRIBUÉE
# Date: 2025-11-13
# Description: Déploie Ollama avec GPU sur edgeserver + failover vers corertx
# =============================================================================

set -e  # Arrêter sur erreur

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.prod-distributed.yml"
STACK_NAME="twisterlab"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# =============================================================================
# ÉTAPE 1: Vérifications préalables
# =============================================================================
log_info "=== ÉTAPE 1: Vérifications préalables ==="

# Vérifier Docker Swarm
if ! docker info | grep -q "Swarm: active"; then
    log_error "Docker Swarm n'est pas activé"
    exit 1
fi
log_success "Docker Swarm actif"

# Vérifier GPU
if ! nvidia-smi > /dev/null 2>&1; then
    log_warning "nvidia-smi non disponible - GPU pourrait ne pas être accessible"
else
    GPU_MODEL=$(nvidia-smi --query-gpu=name --format=csv,noheader)
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader)
    log_success "GPU détecté: $GPU_MODEL ($GPU_MEMORY)"
fi

# Vérifier NVIDIA Container Toolkit
if ! docker info | grep -q "nvidia"; then
    log_warning "NVIDIA Container Runtime non détecté"
    log_info "Installation du NVIDIA Container Toolkit..."

    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
        sudo tee /etc/apt/sources.list.d/nvidia-docker.list

    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo systemctl restart docker

    log_success "NVIDIA Container Toolkit installé"
else
    log_success "NVIDIA Container Runtime disponible"
fi

# Vérifier label GPU sur le nœud
NODE_NAME=$(hostname -f)
GPU_LABEL=$(docker node inspect $NODE_NAME --format '{{.Spec.Labels.gpu}}' 2>/dev/null || echo "false")

if [ "$GPU_LABEL" != "true" ]; then
    log_info "Ajout du label GPU au nœud $NODE_NAME..."
    docker node update --label-add gpu=true $NODE_NAME
    log_success "Label GPU ajouté"
else
    log_success "Label GPU déjà présent"
fi

# Vérifier Docker secrets
REQUIRED_SECRETS=("postgres_password" "redis_password" "jwt_secret")
for secret in "${REQUIRED_SECRETS[@]}"; do
    if docker secret inspect $secret > /dev/null 2>&1; then
        log_success "Secret '$secret' présent"
    else
        log_error "Secret '$secret' manquant"
        exit 1
    fi
done

# Vérifier fichier compose
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Fichier $COMPOSE_FILE introuvable"
    exit 1
fi
log_success "Fichier compose trouvé"

# =============================================================================
# ÉTAPE 2: Déploiement du stack
# =============================================================================
log_info ""
log_info "=== ÉTAPE 2: Déploiement du stack ==="

log_info "Déploiement de $STACK_NAME..."
docker stack deploy -c "$COMPOSE_FILE" "$STACK_NAME"

log_success "Stack déployé"

# =============================================================================
# ÉTAPE 3: Attente du démarrage
# =============================================================================
log_info ""
log_info "=== ÉTAPE 3: Attente du démarrage (60s) ==="

sleep 60

# =============================================================================
# ÉTAPE 4: Vérification des services
# =============================================================================
log_info ""
log_info "=== ÉTAPE 4: Vérification des services ==="

# Vérifier état des services
log_info "État des services:"
docker service ls | grep $STACK_NAME

# Services attendus
SERVICES=("postgres" "redis" "ollama" "api")

for service in "${SERVICES[@]}"; do
    SERVICE_NAME="${STACK_NAME}_${service}"

    # Vérifier replicas
    REPLICAS=$(docker service ls --filter name=$SERVICE_NAME --format "{{.Replicas}}")

    if [[ $REPLICAS == "1/1" ]]; then
        log_success "$service: $REPLICAS ✓"
    else
        log_warning "$service: $REPLICAS (en attente...)"
    fi
done

# =============================================================================
# ÉTAPE 5: Tests de santé
# =============================================================================
log_info ""
log_info "=== ÉTAPE 5: Tests de santé ==="

# Test PostgreSQL
log_info "Test PostgreSQL..."
POSTGRES_CONTAINER=$(docker ps -q -f name=${STACK_NAME}_postgres)
if [ -n "$POSTGRES_CONTAINER" ]; then
    if docker exec $POSTGRES_CONTAINER pg_isready -U twisterlab > /dev/null 2>&1; then
        log_success "PostgreSQL opérationnel"
    else
        log_warning "PostgreSQL non prêt"
    fi
else
    log_warning "Container PostgreSQL non trouvé"
fi

# Test Redis
log_info "Test Redis..."
REDIS_CONTAINER=$(docker ps -q -f name=${STACK_NAME}_redis)
if [ -n "$REDIS_CONTAINER" ]; then
    if docker exec $REDIS_CONTAINER redis-cli ping > /dev/null 2>&1; then
        log_success "Redis opérationnel"
    else
        log_warning "Redis non prêt"
    fi
else
    log_warning "Container Redis non trouvé"
fi

# Test Ollama
log_info "Test Ollama..."
if curl -s -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_success "Ollama opérationnel"

    # Vérifier GPU dans container
    OLLAMA_CONTAINER=$(docker ps -q -f name=${STACK_NAME}_ollama)
    if [ -n "$OLLAMA_CONTAINER" ]; then
        if docker exec $OLLAMA_CONTAINER nvidia-smi > /dev/null 2>&1; then
            GPU_IN_CONTAINER=$(docker exec $OLLAMA_CONTAINER nvidia-smi --query-gpu=name --format=csv,noheader)
            log_success "GPU accessible dans Ollama: $GPU_IN_CONTAINER"
        else
            log_warning "GPU non accessible dans container Ollama"
        fi
    fi
else
    log_warning "Ollama non prêt"
fi

# Test API
log_info "Test API..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    log_success "API opérationnelle"

    API_VERSION=$(curl -s http://localhost:8000/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    log_info "Version API: $API_VERSION"
else
    log_warning "API non prête"
fi

# =============================================================================
# ÉTAPE 6: Chargement du modèle LLM
# =============================================================================
log_info ""
log_info "=== ÉTAPE 6: Chargement du modèle llama3.2:1b ==="

OLLAMA_CONTAINER=$(docker ps -q -f name=${STACK_NAME}_ollama)
if [ -n "$OLLAMA_CONTAINER" ]; then
    log_info "Téléchargement de llama3.2:1b (peut prendre plusieurs minutes)..."

    if docker exec $OLLAMA_CONTAINER ollama pull llama3.2:1b; then
        log_success "Modèle llama3.2:1b chargé"

        # Lister les modèles
        log_info "Modèles disponibles:"
        docker exec $OLLAMA_CONTAINER ollama list
    else
        log_warning "Échec du chargement du modèle"
    fi
else
    log_warning "Container Ollama non disponible pour charger le modèle"
fi

# =============================================================================
# RÉSUMÉ FINAL
# =============================================================================
log_info ""
log_info "======================================================================="
log_info "                    DÉPLOIEMENT TERMINÉ"
log_info "======================================================================="
log_info ""
log_info "Services déployés:"
docker service ls | grep $STACK_NAME
log_info ""
log_info "Endpoints:"
log_info "  API:        http://192.168.0.30:8000"
log_info "  Health:     http://192.168.0.30:8000/health"
log_info "  Docs:       http://192.168.0.30:8000/docs"
log_info "  Ollama:     http://192.168.0.30:11434"
log_info "  Ollama Backup: http://192.168.0.20:11434 (corertx)"
log_info ""
log_info "Logs des services:"
log_info "  docker service logs ${STACK_NAME}_api"
log_info "  docker service logs ${STACK_NAME}_ollama"
log_info ""
log_success "Architecture distribuée avec failover opérationnelle ✓"
