# Yakhteh (یخچه)

Multi-tenant medical platform for doctors and clinics in Iran. This monorepo uses a microservices architecture with Python (FastAPI), PostgreSQL, Redis, and Docker.

## Services
- auth_service: Authentication, JWT, user profiles
- clinic_service: Clinic info, staff, subscriptions

## Quickstart (Local)
1) Create and review .env (already provided with sample values)
2) Build and start

```bash
docker compose up -d --build
```

3) Run DB migrations inside containers (first time)

```bash
# Auth service
docker compose exec auth_service alembic upgrade head

# Clinic service
docker compose exec clinic_service alembic upgrade head
```

4) Open docs
- Auth service: http://localhost:8001/docs
- Clinic service: http://localhost:8002/docs

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
