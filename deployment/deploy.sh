#!/bin/bash

# TwisterLab Production Deployment Script
# This script handles the complete production deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="twisterlab"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
DOMAIN=${DOMAIN:-"your-domain.com"}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Dependencies check passed"
}

setup_environment() {
    log_info "Setting up environment..."

    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Production environment file not found. Creating from template..."
        cp .env.prod.example .env.prod
        log_error "Please edit .env.prod with your production values before continuing."
        exit 1
    fi

    # Load environment variables
    set -a
    source .env.prod
    set +a

    log_success "Environment setup complete"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."

    if [ "$DOMAIN" = "your-domain.com" ]; then
        log_warning "Using default domain. Please update DOMAIN in .env.prod for SSL setup."
        return
    fi

    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        log_info "Installing certbot..."
        apt-get update && apt-get install -y certbot
    fi

    # Obtain SSL certificate
    if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        log_info "Obtaining SSL certificate for $DOMAIN..."
        certbot certonly --webroot -w /var/www/html -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    else
        log_info "SSL certificate already exists for $DOMAIN"
    fi

    log_success "SSL setup complete"
}

backup_database() {
    log_info "Creating database backup..."

    # Create backup directory if it doesn't exist
    mkdir -p backups

    # Generate backup filename with timestamp
    BACKUP_FILE="backups/twisterlab_$(date +%Y%m%d_%H%M%S).sql"

    # Create backup using pg_dump
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T postgres pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > $BACKUP_FILE

    log_success "Database backup created: $BACKUP_FILE"
}

deploy() {
    log_info "Starting deployment..."

    # Pull latest images
    docker-compose -f $DOCKER_COMPOSE_FILE pull

    # Build custom images if needed
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache

    # Start services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30

    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec api alembic upgrade head

    log_success "Deployment complete"
}

health_check() {
    log_info "Performing health checks..."

    # Check if services are running
    if ! docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        log_error "Some services are not running"
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        exit 1
    fi

    # Check API health
    if ! curl -f -s http://localhost/api/v1/health > /dev/null; then
        log_error "API health check failed"
        exit 1
    fi

    log_success "Health checks passed"
}

rollback() {
    log_info "Rolling back deployment..."

    # Stop current deployment
    docker-compose -f $DOCKER_COMPOSE_FILE down

    # Restore from backup if available
    if [ -n "$ROLLBACK_TAG" ]; then
        log_info "Restoring from backup tag: $ROLLBACK_TAG"
        docker-compose -f $DOCKER_COMPOSE_FILE pull $ROLLBACK_TAG
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
    fi

    log_success "Rollback complete"
}

cleanup() {
    log_info "Cleaning up old resources..."

    # Remove unused Docker images
    docker image prune -f

    # Remove old backups (keep last 7 days)
    find backups -name "*.sql" -mtime +7 -delete

    log_success "Cleanup complete"
}

show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the application to production"
    echo "  rollback   Rollback to previous deployment"
    echo "  backup     Create database backup"
    echo "  cleanup    Clean up old resources"
    echo "  health     Run health checks"
    echo "  setup      Initial setup (environment, SSL)"
    echo "  help       Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  DOMAIN     Domain name for SSL certificates"
    echo "  ROLLBACK_TAG  Docker tag to rollback to"
}

# Main script
case "${1:-deploy}" in
    "deploy")
        check_dependencies
        setup_environment
        backup_database
        deploy
        health_check
        cleanup
        ;;
    "rollback")
        setup_environment
        rollback
        health_check
        ;;
    "backup")
        setup_environment
        backup_database
        ;;
    "cleanup")
        cleanup
        ;;
    "health")
        health_check
        ;;
    "setup")
        check_dependencies
        setup_environment
        setup_ssl
        ;;
    "help"|*)
        show_usage
        ;;
esac