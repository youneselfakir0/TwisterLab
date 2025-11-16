# TwisterLab Production Deployment

This directory contains all the necessary files for deploying TwisterLab to production environments.

## Directory Structure

```
deployment/
├── nginx/
│   └── nginx.conf          # Nginx reverse proxy configuration
├── Dockerfile.prod         # Production Docker image
├── deploy.sh              # Deployment automation script
└── monitor.sh             # Production monitoring script
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Domain name configured
- SSL certificates (Let's Encrypt recommended)

### Initial Setup

1. **Configure Environment Variables**

   ```bash
   cp .env.prod.example .env.prod
   # Edit .env.prod with your production values
   ```

2. **Run Initial Setup**

   ```bash
   ./deployment/deploy.sh setup
   ```

3. **Deploy to Production**

   ```bash
   ./deployment/deploy.sh deploy
   ```

## Configuration Files

### Environment Variables (.env.prod)

Key production settings:

```bash
# Domain and SSL
DOMAIN=your-domain.com
SSL_CERT_PATH=/etc/nginx/ssl/live/${DOMAIN}/fullchain.pem
SSL_KEY_PATH=/etc/nginx/ssl/live/${DOMAIN}/privkey.pem

# Database
POSTGRES_DB=twisterlab_prod
POSTGRES_USER=twisterlab
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=postgres

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
ADMIN_PASSWORD=secure-admin-password

# External Services
OLLAMA_BASE_URL=http://ollama:11434
OPENWEBUI_URL=http://openwebui:8080

# Monitoring
PROMETHEUS_METRICS=true
LOG_LEVEL=INFO
```

### Nginx Configuration

The `nginx.conf` provides:

- **SSL/TLS Termination**: HTTPS with modern cipher suites
- **Rate Limiting**: API protection and authentication endpoints
- **Load Balancing**: Upstream configuration for API services
- **Security Headers**: XSS protection, content security policy
- **Static File Caching**: Optimized delivery of assets
- **WebSocket Support**: For real-time features

### Docker Production Setup

The production Docker setup includes:

- **Multi-stage Builds**: Optimized image size
- **Security**: Non-root user, minimal attack surface
- **Health Checks**: Automatic service monitoring
- **Resource Limits**: Memory and CPU constraints
- **Secrets Management**: Secure credential handling

## Deployment Commands

### Full Deployment

```bash
./deployment/deploy.sh deploy
```

### Rollback

```bash
ROLLBACK_TAG=v1.0.0 ./deployment/deploy.sh rollback
```

### Database Backup

```bash
./deployment/deploy.sh backup
```

### Health Checks

```bash
./deployment/deploy.sh health
```

### Cleanup

```bash
./deployment/deploy.sh cleanup
```

## Monitoring

### Automated Monitoring

```bash
# Run monitoring checks
./deployment/monitor.sh

# Schedule with cron (daily at 6 AM)
0 6 * * * /path/to/twisterlab/deployment/monitor.sh
```

### What Gets Monitored

- **Service Health**: All Docker containers
- **API Endpoints**: Response times and availability
- **System Resources**: CPU, memory, disk usage
- **Database Connections**: PostgreSQL and Redis
- **Error Logs**: Recent errors in application logs
- **SSL Certificates**: Expiration warnings

### Alerts

Configure alerts by setting environment variables:

```bash
export ALERT_EMAIL=admin@your-domain.com
export SLACK_WEBHOOK=https://hooks.slack.com/services/...
```

## SSL Certificate Management

### Automatic (Let's Encrypt)

```bash
# Certificates are automatically obtained during setup
./deployment/deploy.sh setup
```

### Manual Certificates

1. Place certificates in `deployment/ssl/live/your-domain.com/`
2. Update paths in `nginx.conf`
3. Restart nginx: `docker-compose restart nginx`

## Backup and Recovery

### Automated Backups
Backups are created automatically during deployment:

```bash
# Manual backup
./deployment/deploy.sh backup

# List backups
ls -la backups/
```

### Recovery
```bash
# Restore from specific backup
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < backups/backup_file.sql
```

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.prod.yml
services:
  api:
    deploy:
      replicas: 3
    # ... other config
```

### Database Scaling
- Use PostgreSQL read replicas for read-heavy workloads
- Implement Redis clustering for high availability
- Consider Azure Database for PostgreSQL for managed scaling

## Security Considerations

### Network Security
- All services run in isolated Docker networks
- Nginx acts as reverse proxy with rate limiting
- Database ports not exposed externally

### Authentication
- JWT tokens with configurable expiration
- Role-based access control
- Password hashing with bcrypt

### Secrets Management
- Docker secrets for sensitive data
- Environment variables for configuration
- No secrets in version control

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check resource usage
docker system df
```

**SSL certificate errors:**
```bash
# Renew certificates
certbot renew

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

**Database connection issues:**
```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec api python -c "import psycopg2; psycopg2.connect(os.environ['DATABASE_URL'])"
```

### Performance Tuning

**API Performance:**
- Adjust worker count in Dockerfile.prod
- Configure connection pooling
- Enable response compression

**Database Performance:**
- Monitor slow queries
- Adjust connection limits
- Consider read replicas

## Maintenance

### Updates
```bash
# Update all images
docker-compose -f docker-compose.prod.yml pull

# Deploy updates
./deployment/deploy.sh deploy
```

### Log Rotation
```bash
# Configure log rotation in docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Regular Tasks
- Monitor disk usage
- Rotate logs weekly
- Update SSL certificates monthly
- Review security updates

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Run health checks: `./deployment/deploy.sh health`
3. Review monitoring: `./deployment/monitor.sh`
4. Check system resources: `docker system df`

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DOMAIN` | Domain name for SSL | your-domain.com |
| `POSTGRES_DB` | Database name | twisterlab_prod |
| `POSTGRES_USER` | Database user | twisterlab |
| `SECRET_KEY` | App secret key | (required) |
| `JWT_SECRET_KEY` | JWT signing key | (required) |
| `OLLAMA_BASE_URL` | Ollama service URL | http://ollama:11434 |
| `LOG_LEVEL` | Logging level | INFO |
| `PROMETHEUS_METRICS` | Enable metrics | true |