# syntax=docker/dockerfile:1.7-labs

# Builder stage
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir -r requirements.txt -w /wheels

# Runtime stage
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# System runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt /app/
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy source
COPY app ./app
COPY main.py ./main.py
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY startup.sh ./startup.sh

# Make startup script executable
RUN chmod +x ./startup.sh

EXPOSE 8000

# Default command - run migrations then start service
CMD ["./startup.sh"]
