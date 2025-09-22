#!/bin/bash
set -e

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to log error and exit
log_error() {
    log "ERROR: $1" >&2
    exit 1
}

SERVICE_NAME=${1:-"service"}
log "Starting $SERVICE_NAME startup process..."

# Wait for database to be available (basic health check)
log "Checking database connectivity..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if python -c "
import asyncio
import asyncpg
import sys

async def check_db():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@postgres_db:5432/yakhteh')
        await conn.close()
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

result = asyncio.run(check_db())
sys.exit(0 if result else 1)
" 2>/dev/null; then
        log "Database is ready"
        break
    else
        log "Database not ready, waiting... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    log_error "Database is not available after $max_attempts attempts"
fi

# Run database migrations if alembic is available
if [ -f "alembic.ini" ]; then
    log "Running alembic migrations..."
    if alembic upgrade head; then
        log "Database migrations completed successfully"
    else
        log_error "Database migrations failed"
    fi

    # Verify migrations were applied correctly
    log "Verifying database schema..."
    if python -c "
import asyncio
import asyncpg
import sys

async def check_tables():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@postgres_db:5432/yakhteh')
        result = await conn.fetch(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public'\")
        await conn.close()
        return len(result) > 0
    except Exception as e:
        print(f'Table verification failed: {e}')
        return False

result = asyncio.run(check_tables())
sys.exit(0 if result else 1)
"; then
        log "Database schema verification successful"
    else
        log_error "Database schema verification failed"
    fi
else
    log "No alembic.ini found, skipping migrations"
fi

log "All startup checks passed. Starting $SERVICE_NAME..."
exec uvicorn main:app --host 0.0.0.0 --port 8000