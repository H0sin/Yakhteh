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

## Production Deployment

When deployed with a domain, services are accessible via:
- Frontend: https://frontend.${MY_DOMAIN}
- API Gateway: https://api.${MY_DOMAIN}
- Traefik Dashboard: https://traefik.${MY_DOMAIN}
- MinIO Console: https://minio.${MY_DOMAIN}

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
