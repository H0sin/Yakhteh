# Yakhteh (یخچه)

Multi-tenant medical platform for doctors and clinics in Iran. This repository uses a microservices architecture with Python (FastAPI), React (Vite), PostgreSQL, Redis, and Docker.

## Architecture

This platform follows a microservices architecture where each service is containerized and communicates through API calls:

### Services
- **auth_service**: Authentication, JWT tokens, user management
- **clinic_service**: Clinic information, staff management, subscriptions
- **membership_service**: Membership processing (background worker)
- **scheduling_service**: Appointment scheduling and calendar management
- **pacs_service**: Medical imaging and PACS integration
- **frontend_service**: React-based web interface (Vite + TypeScript)

### Infrastructure
- **PostgreSQL**: Primary database for all services
- **Redis**: Caching and session management
- **MinIO**: Object storage for files and medical images
- **Traefik**: Reverse proxy and SSL termination

## Quickstart (Local Development)

1. Copy the example environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

2. Start the entire platform:

```bash
docker compose up --build
```

### Local Access
- Frontend interface: http://localhost:3000 (development) or http://localhost (production build)
- Auth service API docs: http://localhost:8001/docs
- Other services are accessible through the auth service or via internal networking

For development, individual service documentation:
- Auth Service: http://localhost:8001/docs
- Scheduling Service: http://localhost:8002/docs  
- Clinic Service: http://localhost:8003/docs

## Production Deployment

### Prerequisites

For automatic HTTPS with Let's Encrypt to work, you need to configure the following DNS A-records for your domain:

- `frontend.yourdomain.com` → Server IP
- `api.yourdomain.com` → Server IP  
- `traefik.yourdomain.com` → Server IP
- `minio.yourdomain.com` → Server IP

### Configuration

1. Copy and configure the environment file:
```bash
cp .env.example .env
```

2. Update the following variables in `.env`:
```bash
MY_DOMAIN=yourdomain.com
LETS_ENCRYPT_EMAIL=your-email@yourdomain.com
```

3. Deploy the platform:
```bash
docker compose up --build
```

Traefik will automatically obtain Let's Encrypt SSL certificates for all configured subdomains and handle HTTP to HTTPS redirects.

### Service Access

When deployed with a domain, services are accessible via:
- Frontend: https://frontend.${MY_DOMAIN}
- API Gateway: https://api.${MY_DOMAIN}
- Traefik Dashboard: https://traefik.${MY_DOMAIN}
- MinIO Console: https://minio.${MY_DOMAIN}

### API Documentation

- **Main API Documentation**: https://api.${MY_DOMAIN}/docs (Auth Service)
- **Scheduling Service Documentation**: https://api.${MY_DOMAIN}/scheduling
- **Clinic Service Documentation**: https://api.${MY_DOMAIN}/inventory

Each service's documentation shows only the relevant endpoints for that service, making it easier for teams to focus on their specific APIs.

Set the `MY_DOMAIN` environment variable in your `.env` file for proper Traefik routing.

## Endpoints (initial)
Auth
- POST /api/v1/auth/login (OAuth2 Password)
- POST /api/v1/auth/register
- GET  /api/v1/auth/me (requires Bearer token)

Clinics (requires Bearer token)
- GET    /api/v1/clinics/
- POST   /api/v1/clinics/
- GET    /api/v1/clinics/{clinic_id}
- PUT    /api/v1/clinics/{clinic_id}
- DELETE /api/v1/clinics/{clinic_id}

## Notes
- Async SQLAlchemy with PostgreSQL
- UUID primary keys
- Alembic migrations per service
- CORS open for local dev

## Testing
Run the auth_service tests against a local PostgreSQL.

- Start PostgreSQL (via docker-compose service):

```bash
docker compose up -d postgres_db
```

- Install dependencies and run tests (Windows PowerShell):

```powershell
cd services/auth_service
python -m pip install -r requirements.txt -r requirements-dev.txt
$env:TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/yakhteh_test"
python -m pytest
```

- Install dependencies and run tests (bash/macOS/Linux):

```bash
cd services/auth_service
python -m pip install -r requirements.txt -r requirements-dev.txt
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/yakhteh_test"
pytest
```

Notes:
- Tests auto-create the yakhteh_test database and drop all tables after the run.
- You can override the DB with TEST_DATABASE_URL (any async SQLAlchemy URL supported).

## Database Management

### External Database Access
PostgreSQL is configured to allow connections from external database management tools like DataGrip, pgAdmin, or other SQL clients.

**Connection Details:**
- Host: `localhost` (when running locally)
- Port: `5432`
- Database: `yakhteh`
- Username: `postgres`
- Password: `postgres`

For detailed configuration and security considerations, see [docs/postgresql-external-access.md](docs/postgresql-external-access.md).
