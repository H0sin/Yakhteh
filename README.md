# Yakhteh (یخچه)

Multi-tenant medical platform for doctors and clinics in Iran. This monorepo uses a microservices architecture with Python (FastAPI), PostgreSQL, Redis, and Docker.

## Services
- auth_service: Authentication, JWT, user profiles
- clinic_service: Clinic info, staff, subscriptions

## Quickstart (Local)
1. Fill in the .env file with your configuration.
2. Run the platform:

```bash
docker compose up --build
```

The entire platform, including the API server and background workers, is now running.
- Auth service docs: http://localhost:8001/docs

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
