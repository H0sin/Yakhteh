# Multi-Service Swagger UI Configuration

This document explains how the multi-service Swagger UI configuration works in the Yakhteh platform.

## Overview

The platform now supports service-specific Swagger documentation accessible through custom paths, allowing teams to view documentation for individual services separately.

## Available Endpoints

### Production URLs (replace `${MY_DOMAIN}` with your domain)

- **Main API Documentation**: `https://api.${MY_DOMAIN}/docs`
  - Shows auth service endpoints
  - Default entry point for API documentation

- **Scheduling Service Documentation**: `https://api.${MY_DOMAIN}/scheduling`
  - Shows only scheduling-related endpoints
  - Includes `/api/v1/appointments` and `/api/v1/availability` endpoints

- **Clinic Service Documentation**: `https://api.${MY_DOMAIN}/inventory`
  - Shows only clinic-related endpoints  
  - Includes `/api/v1/clinics` endpoints

### Local Development URLs

- **Auth Service**: `http://localhost:8001/docs`
- **Scheduling Service**: `http://localhost:8002/docs`
- **Clinic Service**: `http://localhost:8003/docs`

## How It Works

### 1. FastAPI Configuration

Each service is configured with explicit Swagger UI paths:

```python
app = FastAPI(
    title="Service Name", 
    version="0.1.0",
    docs_url="/docs",      # Swagger UI endpoint
    redoc_url="/redoc"     # ReDoc endpoint
)
```

### 2. Traefik Routing Configuration

Each service has two types of routes configured in Traefik:

#### API Routes
Handle actual API calls:
```yaml
- "traefik.http.routers.yakhteh-scheduling.rule=Host(`api.${MY_DOMAIN}`) && PathPrefix(`/api/v1/appointments`, `/api/v1/availability`)"
```

#### Documentation Routes
Handle Swagger UI access with path rewriting:
```yaml
- "traefik.http.routers.yakhteh-scheduling-docs.rule=Host(`api.${MY_DOMAIN}`) && PathPrefix(`/scheduling`)"
- "traefik.http.routers.yakhteh-scheduling-docs.middlewares=yakhteh-scheduling-rewrite"
- "traefik.http.middlewares.yakhteh-scheduling-rewrite.replacepathregex.regex=^/scheduling(.*)"
- "traefik.http.middlewares.yakhteh-scheduling-rewrite.replacepathregex.replacement=/docs$$1"
```

### 3. Path Rewriting Mechanism

When a request comes to `/scheduling`, Traefik:
1. Matches the route rule `PathPrefix(/scheduling)`
2. Applies the `replacepathregex` middleware to rewrite `/scheduling` → `/docs`
3. Forwards the rewritten request to the service as `/docs`
4. The service responds with its standard Swagger UI content

## Request Flow Example

1. User visits: `https://api.example.com/scheduling`
2. Traefik receives request with path `/scheduling`
3. Traefik applies regex replacement: `/scheduling` → `/docs`
4. Request forwarded to scheduling service as `/docs`
5. Service responds with Swagger UI for scheduling endpoints only

## Benefits

1. **Service Isolation**: Each team can access only their service's documentation
2. **Clean URLs**: Intuitive paths like `/scheduling` and `/inventory`
3. **Backward Compatibility**: Original `/docs` endpoints still work
4. **Centralized Access**: All documentation accessible through single API domain

## Adding New Services

To add documentation for a new service:

1. **Configure FastAPI** with explicit docs URLs:
```python
app = FastAPI(
    title="New Service",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

2. **Add Traefik labels** to docker-compose.yml:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.constraint-label=yakhteh"
  # API routes
  - "traefik.http.routers.yakhteh-newservice.rule=Host(`api.${MY_DOMAIN}`) && PathPrefix(`/api/v1/newservice`)"
  - "traefik.http.services.yakhteh-newservice.loadbalancer.server.port=8000"
  # Docs routes
  - "traefik.http.routers.yakhteh-newservice-docs.rule=Host(`api.${MY_DOMAIN}`) && PathPrefix(`/newservice`)"
  - "traefik.http.routers.yakhteh-newservice-docs.middlewares=yakhteh-newservice-rewrite"
  - "traefik.http.middlewares.yakhteh-newservice-rewrite.replacepathregex.regex=^/newservice(.*)"
  - "traefik.http.middlewares.yakhteh-newservice-rewrite.replacepathregex.replacement=/docs$$1"
```

3. **Run validation**:
```bash
./scripts/validate-traefik.sh
```

## Testing

To test the configuration:

1. **Start services**: `docker compose up -d`
2. **Verify main docs**: Visit `https://api.${MY_DOMAIN}/docs`
3. **Verify service docs**: Visit `https://api.${MY_DOMAIN}/scheduling`
4. **Check service isolation**: Ensure each endpoint shows only relevant APIs

## Troubleshooting

### Common Issues

1. **404 on custom paths**: Check Traefik routing rules and middleware configuration
2. **Wrong documentation shown**: Verify service selection and path stripping
3. **SSL/TLS errors**: Ensure Let's Encrypt certificates are properly configured

### Validation Commands

```bash
# Check Traefik configuration
./scripts/validate-traefik.sh

# Verify docker-compose syntax
docker compose config

# Check router configuration
docker compose logs traefik | grep -i "router"
```