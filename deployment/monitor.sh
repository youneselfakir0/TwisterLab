#!/bin/bash

# TwisterLab Production Monitoring Script
# Monitors service health, performance, and sends alerts

set -e

# Configuration
PROJECT_NAME="twisterlab"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
LOG_FILE="logs/monitoring.log"
ALERT_EMAIL=${ALERT_EMAIL:-"admin@your-domain.com"}
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=90
RESPONSE_TIME_THRESHOLD=5000  # milliseconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

alert() {
    local message="$1"
    local severity="${2:-WARNING}"

    log "ALERT [$severity]: $message"

    # Email alert
    if command -v mail &> /dev/null && [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "TwisterLab Alert [$severity]" "$ALERT_EMAIL"
    fi

    # Slack alert
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"TwisterLab Alert [$severity]: $message\"}" \
             "$SLACK_WEBHOOK"
    fi
}

check_service_health() {
    local service="$1"

    if ! docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$service" | grep -q "Up"; then
        alert "Service $service is not running" "CRITICAL"
        return 1
    fi

    log "Service $service is healthy"
    return 0
}

check_api_health() {
    local url="${1:-http://localhost/api/v1/health}"
    local timeout=10

    if ! curl -f -s --max-time "$timeout" "$url" > /dev/null; then
        alert "API health check failed for $url" "CRITICAL"
        return 1
    fi

    log "API health check passed for $url"
    return 0
}

check_response_time() {
    local url="${1:-http://localhost/api/v1/health}"
    local start_time=$(date +%s%3N)

    if ! curl -f -s -w "%{time_total}\n" -o /dev/null "$url" > /tmp/response_time; then
        alert "Failed to measure response time for $url" "WARNING"
        return 1
    fi

    local response_time=$(cat /tmp/response_time)
    local response_ms=$(echo "$response_time * 1000" | bc 2>/dev/null || echo "0")

    if (( $(echo "$response_ms > $RESPONSE_TIME_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
        alert "Response time too high: ${response_ms}ms for $url" "WARNING"
    fi

    log "Response time: ${response_ms}ms for $url"
}

check_system_resources() {
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
        alert "High CPU usage: ${cpu_usage}%" "WARNING"
    fi

    # Memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if (( memory_usage > MEMORY_THRESHOLD )); then
        alert "High memory usage: ${memory_usage}%" "WARNING"
    fi

    # Disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if (( disk_usage > DISK_THRESHOLD )); then
        alert "High disk usage: ${disk_usage}%" "WARNING"
    fi

    log "System resources - CPU: ${cpu_usage}%, Memory: ${memory_usage}%, Disk: ${disk_usage}%"
}

check_database_connections() {
    # Check PostgreSQL connections
    local pg_connections=$(docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tail -3 | head -1 | tr -d ' ')

    if ! [[ "$pg_connections" =~ ^[0-9]+$ ]]; then
        alert "Failed to check PostgreSQL connections" "WARNING"
    else
        log "PostgreSQL active connections: $pg_connections"
    fi

    # Check Redis connections
    local redis_clients=$(docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli info clients 2>/dev/null | grep "connected_clients" | cut -d: -f2)

    if ! [[ "$redis_clients" =~ ^[0-9]+$ ]]; then
        alert "Failed to check Redis connections" "WARNING"
    else
        log "Redis connected clients: $redis_clients"
    fi
}

check_logs_for_errors() {
    local log_files=("logs/twisterlab.log" "logs/monitoring.log")
    local error_patterns=("ERROR" "CRITICAL" "Exception" "Traceback")

    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            local recent_errors=$(tail -n 100 "$log_file" | grep -i -E "$(IFS=\|; echo "${error_patterns[*]}")" | wc -l)

            if (( recent_errors > 0 )); then
                alert "Found $recent_errors errors in $log_file in the last 100 lines" "WARNING"
            fi
        fi
    done
}

generate_report() {
    local report_file="logs/daily_report_$(date +%Y%m%d).txt"

    {
        echo "=== TwisterLab Daily Report $(date) ==="
        echo ""
        echo "Service Status:"
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        echo ""
        echo "System Resources:"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"
        echo "Memory: $(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')%"
        echo "Disk: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        echo "Recent Alerts:"
        tail -n 20 "$LOG_FILE" | grep ALERT || echo "No recent alerts"
    } > "$report_file"

    log "Daily report generated: $report_file"
}

main() {
    log "Starting monitoring check..."

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Service health checks
    check_service_health "postgres"
    check_service_health "redis"
    check_service_health "api"
    check_service_health "nginx"

    # API health checks
    check_api_health "http://localhost/health"
    check_api_health "http://localhost/api/v1/health"

    # Performance checks
    check_response_time "http://localhost/api/v1/health"

    # System resource checks
    check_system_resources

    # Database checks
    check_database_connections

    # Log analysis
    check_logs_for_errors

    # Generate daily report (run once per day)
    if [ "$(date +%H)" = "06" ]; then
        generate_report
    fi

    log "Monitoring check complete"
}

# Run main function
main "$@"