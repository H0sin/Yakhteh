#!/bin/bash
set -e

echo "Running alembic migrations..."
alembic upgrade head

echo "Starting auth service..."
exec uvicorn main:app --host 0.0.0.0 --port 8000