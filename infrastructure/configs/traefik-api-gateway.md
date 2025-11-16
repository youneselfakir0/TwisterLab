# =============================================================================
# TRAEFIK API GATEWAY CONFIGURATION
# Centralized routing, load balancing, and authentication for TwisterLab
# =============================================================================

# Static configuration (traefik.yml)
```yaml
# Global Configuration
global:
  checkNewVersion: true
  sendAnonymousUsage: false

# API and Dashboard
api:
  dashboard: true
  insecure: false  # Secure dashboard with authentication

# Entry Points
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt

  traefik:
    address: ":8080"

# Certificate Resolvers
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@twisterlab.local
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

# Providers
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    swarmMode: true
    network: twisterlab_network

  file:
    directory: /etc/traefik/dynamic
    watch: true

# Logging
log:
  level: INFO
  filePath: /var/log/traefik/traefik.log
  format: json

accessLog:
  filePath: /var/log/traefik/access.log
  format: json
  filters:
    statusCodes:
      - "400-599"

# Metrics
metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true
    entryPoint: metrics

# Tracing (optional)
tracing:
  serviceName: twisterlab-gateway
  jaeger:
    samplingServerURL: http://jaeger:5778/sampling
    localAgentHostPort: jaeger:6831
```

---

# Dynamic configuration (dynamic/twisterlab-routes.yml)
```yaml
# =============================================================================
# TWISTERLAB ROUTES AND MIDDLEWARES
# =============================================================================

http:
  # Routers
  routers:
    # TwisterLab API
    twisterlab-api:
      rule: "Host(`api.twisterlab.local`) || PathPrefix(`/api`)"
      service: twisterlab-api-service
      entryPoints:
        - websecure
      middlewares:
        - sso-auth
        - rate-limit
        - compress
      tls:
        certResolver: letsencrypt

    # Open WebUI
    twisterlab-webui:
      rule: "Host(`chat.twisterlab.local`)"
      service: twisterlab-webui-service
      entryPoints:
        - websecure
      middlewares:
        - sso-auth
        - compress
      tls:
        certResolver: letsencrypt

    # Grafana Dashboard
    grafana:
      rule: "Host(`grafana.twisterlab.local`)"
      service: grafana-service
      entryPoints:
        - websecure
      middlewares:
        - sso-auth
        - compress
      tls:
        certResolver: letsencrypt

    # Prometheus Metrics
    prometheus:
      rule: "Host(`prometheus.twisterlab.local`)"
      service: prometheus-service
      entryPoints:
        - websecure
      middlewares:
        - admin-auth  # Restricted to admins only
        - compress
      tls:
        certResolver: letsencrypt

    # Traefik Dashboard
    traefik-dashboard:
      rule: "Host(`traefik.twisterlab.local`) && (PathPrefix(`/api`) || PathPrefix(`/dashboard`))"
      service: api@internal
      entryPoints:
        - websecure
      middlewares:
        - admin-auth
      tls:
        certResolver: letsencrypt

  # Services
  services:
    twisterlab-api-service:
      loadBalancer:
        servers:
          - url: "http://twisterlab_api:8000"
        healthCheck:
          path: /health
          interval: 10s
          timeout: 3s
        sticky:
          cookie:
            name: twisterlab_session
            httpOnly: true
            secure: true

    twisterlab-webui-service:
      loadBalancer:
        servers:
          - url: "http://twisterlab_webui:8080"
        healthCheck:
          path: /
          interval: 30s
          timeout: 5s

    grafana-service:
      loadBalancer:
        servers:
          - url: "http://monitoring_grafana:3000"
        healthCheck:
          path: /api/health
          interval: 30s
          timeout: 5s

    prometheus-service:
      loadBalancer:
        servers:
          - url: "http://monitoring_prometheus:9090"
        healthCheck:
          path: /-/healthy
          interval: 30s
          timeout: 5s

  # Middlewares
  middlewares:
    # SSO Authentication via Forward Auth
    sso-auth:
      forwardAuth:
        address: "http://twisterlab_api:8000/auth/verify"
        authResponseHeaders:
          - "X-User-Id"
          - "X-User-Email"
          - "X-User-Roles"
        trustForwardHeader: true

    # Admin-only Authentication
    admin-auth:
      forwardAuth:
        address: "http://twisterlab_api:8000/auth/verify?required_role=admin"
        authResponseHeaders:
          - "X-User-Id"
          - "X-User-Email"
          - "X-User-Roles"
        trustForwardHeader: true

    # Rate Limiting
    rate-limit:
      rateLimit:
        average: 100
        period: 1s
        burst: 200

    # Compression
    compress:
      compress: {}

    # Security Headers
    security-headers:
      headers:
        browserXssFilter: true
        contentTypeNosniff: true
        frameDeny: true
        sslRedirect: true
        stsIncludeSubdomains: true
        stsPreload: true
        stsSeconds: 31536000
        customResponseHeaders:
          X-Powered-By: "TwisterLab"
          X-Frame-Options: "DENY"

    # CORS for API
    cors:
      headers:
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
          - OPTIONS
        accessControlAllowOriginList:
          - "https://chat.twisterlab.local"
          - "https://grafana.twisterlab.local"
        accessControlAllowHeaders:
          - "*"
        accessControlMaxAge: 3600
        addVaryHeader: true

  # Circuit Breaker (optional)
  middlewares:
    circuit-breaker:
      circuitBreaker:
        expression: "NetworkErrorRatio() > 0.30 || ResponseCodeRatio(500, 600, 0, 600) > 0.25"
```

---

# Docker Swarm Labels Configuration
```yaml
# Add these labels to your Docker services in docker-compose.unified.yml

# TwisterLab API Service
services:
  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.twisterlab-api.rule=Host(`api.twisterlab.local`) || PathPrefix(`/api`)"
      - "traefik.http.routers.twisterlab-api.entrypoints=websecure"
      - "traefik.http.routers.twisterlab-api.tls.certresolver=letsencrypt"
      - "traefik.http.routers.twisterlab-api.middlewares=sso-auth@file,rate-limit@file,compress@file"
      - "traefik.http.services.twisterlab-api.loadbalancer.server.port=8000"
      - "traefik.http.services.twisterlab-api.loadbalancer.healthcheck.path=/health"
      - "traefik.http.services.twisterlab-api.loadbalancer.healthcheck.interval=10s"

  # WebUI Service
  webui:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.webui.rule=Host(`chat.twisterlab.local`)"
      - "traefik.http.routers.webui.entrypoints=websecure"
      - "traefik.http.routers.webui.tls.certresolver=letsencrypt"
      - "traefik.http.routers.webui.middlewares=sso-auth@file,compress@file"
      - "traefik.http.services.webui.loadbalancer.server.port=8080"

  # Grafana Service
  grafana:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`grafana.twisterlab.local`)"
      - "traefik.http.routers.grafana.entrypoints=websecure"
      - "traefik.http.routers.grafana.tls.certresolver=letsencrypt"
      - "traefik.http.routers.grafana.middlewares=sso-auth@file,compress@file"
      - "traefik.http.services.grafana.loadbalancer.server.port=3000"

  # Prometheus Service
  prometheus:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.prometheus.rule=Host(`prometheus.twisterlab.local`)"
      - "traefik.http.routers.prometheus.entrypoints=websecure"
      - "traefik.http.routers.prometheus.tls.certresolver=letsencrypt"
      - "traefik.http.routers.prometheus.middlewares=admin-auth@file,compress@file"
      - "traefik.http.services.prometheus.loadbalancer.server.port=9090"
```
