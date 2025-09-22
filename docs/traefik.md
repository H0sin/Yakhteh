# Traefik Configuration Guide

This document explains the Traefik configuration in this project and how to prevent router conflicts.

## Overview

Traefik is configured as a reverse proxy with automatic Let's Encrypt SSL certificate management. All services are routed through Traefik with unique router names to prevent conflicts.

## Router Naming Convention

All routers follow the naming pattern: `yakhteh-{service-name}`

Example:
- Frontend: `yakhteh-frontend`
- Auth API: `yakhteh-auth`
- MinIO Console: `yakhteh-minio`

## Preventing Router Conflicts

### 1. Unique Router Names
- Always prefix router names with `yakhteh-` to avoid conflicts
- Never use generic names like `frontend`, `api`, `dashboard`

### 2. Constraint Labels
All services exposed through Traefik must include:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.constraint-label=yakhteh"
```

### 3. Provider Configuration
Traefik is configured with:
- `exposedbydefault=false`: Only explicitly enabled services are exposed
- Constraint labels: Only services with `yakhteh` constraint are discovered

## Validation

Run the validation script to check configuration:
```bash
./scripts/validate-traefik.sh
```

This script checks for:
- Valid docker-compose syntax
- Unique router names
- Proper constraint labels
- Required Traefik settings

## Adding New Services

When adding a new service to be exposed through Traefik:

1. **Add the service labels:**
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.constraint-label=yakhteh"
  - "traefik.http.routers.yakhteh-{service}.rule=Host(`{subdomain}.${MY_DOMAIN}`)"
  - "traefik.http.routers.yakhteh-{service}.entrypoints=websecure"
  - "traefik.http.routers.yakhteh-{service}.tls=true"
  - "traefik.http.routers.yakhteh-{service}.tls.certresolver=letsencrypt"
  - "traefik.http.services.yakhteh-{service}.loadbalancer.server.port={port}"
```

2. **Run validation:**
```bash
./scripts/validate-traefik.sh
```

3. **Test the configuration:**
```bash
docker compose config
```

## Troubleshooting

### "Router defined multiple times" Error

This error indicates conflicting router configurations. Common causes:

1. **Duplicate router names**: Check that all routers have unique names
2. **Auto-discovery conflicts**: Ensure `exposedbydefault=false` is set
3. **Missing constraint labels**: Verify all services have the constraint label
4. **Leftover containers**: Clean up old containers with conflicting labels

### Resolution Steps

1. Stop all containers: `docker compose down`
2. Remove orphaned containers: `docker container prune`
3. Validate configuration: `./scripts/validate-traefik.sh`
4. Start services: `docker compose up -d`

## DNS Configuration

For production deployment, configure these DNS A-records:
- `frontend.yourdomain.com` → Server IP
- `api.yourdomain.com` → Server IP  
- `traefik.yourdomain.com` → Server IP
- `minio.yourdomain.com` → Server IP

## Security Considerations

- Traefik dashboard is protected by domain restriction
- All HTTP traffic is redirected to HTTPS
- Let's Encrypt certificates are automatically managed
- Services are isolated with constraint labels