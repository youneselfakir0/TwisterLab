#!/bin/bash
# ============================================================================
# Script de rebuild et déploiement API avec métriques Prometheus
# ============================================================================

set -e  # Exit on error

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "================================================================"
echo " TwisterLab API - Rebuild & Deploy with Prometheus Metrics"
echo "================================================================"
echo -e "${NC}"

# 1. Build new Docker image
echo -e "${BOLD}[1/4]${NC} Building new Docker image..."
docker build -f infrastructure/dockerfiles/Dockerfile.api.local \
    -t twisterlab/api:metrics \
    -t twisterlab/api:latest \
    .

echo -e "${GREEN}✓ Image built successfully${NC}"

# 2. Tag with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker tag twisterlab/api:metrics twisterlab/api:${TIMESTAMP}
echo -e "${GREEN}✓ Tagged as twisterlab/api:${TIMESTAMP}${NC}"

# 3. Update service
echo -e "${BOLD}[2/4]${NC} Updating twisterlab_api service..."
docker service update \
    --image twisterlab/api:metrics \
    --force \
    twisterlab_api

echo -e "${GREEN}✓ Service update initiated${NC}"

# 4. Wait for service to be running
echo -e "${BOLD}[3/4]${NC} Waiting for service to stabilize..."
sleep 15

# 5. Verify deployment
echo -e "${BOLD}[4/4]${NC} Verifying deployment..."

# Check service status
SERVICE_STATUS=$(docker service ls --filter name=twisterlab_api --format "{{.Replicas}}")
echo "Service status: ${SERVICE_STATUS}"

# Test /health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Health: ${HEALTH_RESPONSE}"

# Test /metrics endpoint
echo "Testing /metrics endpoint..."
METRICS_RESPONSE=$(curl -s http://localhost:8000/metrics | grep -c "agent_operations_total" || echo "0")

if [ "$METRICS_RESPONSE" -gt 0 ]; then
    echo -e "${GREEN}✓ Metrics endpoint operational (found agent_operations_total)${NC}"
else
    echo -e "${YELLOW}⚠ Metrics endpoint may not be fully configured${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}"
echo "================================================================"
echo " Deployment Complete!"
echo "================================================================"
echo -e "${NC}"
echo ""
echo "API Endpoints:"
echo "  Health:  http://192.168.0.30:8000/health"
echo "  Metrics: http://192.168.0.30:8000/metrics"
echo "  Docs:    http://192.168.0.30:8000/docs"
echo ""
echo "Verify metrics:"
echo "  curl http://192.168.0.30:8000/metrics | grep agent_"
echo ""
