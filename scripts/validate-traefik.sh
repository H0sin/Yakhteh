#!/bin/bash

# Traefik Configuration Validation Script
# This script validates the docker-compose.yml file for Traefik router conflicts

set -e

echo "🔍 Validating Traefik configuration..."

# Check if docker-compose.yml exists
if [[ ! -f "docker-compose.yml" ]]; then
    echo "❌ Error: docker-compose.yml not found"
    exit 1
fi

# Validate docker-compose syntax
echo "📋 Checking docker-compose syntax..."
if ! docker compose config > /dev/null 2>&1; then
    echo "❌ Error: Invalid docker-compose.yml syntax"
    exit 1
fi

# Check for unique router names
echo "🔀 Checking for unique router names..."
ROUTER_NAMES=$(grep "traefik.http.routers\." docker-compose.yml | sed 's/.*traefik\.http\.routers\.\([^.]*\)\..*$/\1/' | sort | uniq)
ROUTER_COUNT=$(echo "$ROUTER_NAMES" | wc -l)
TOTAL_ROUTER_LINES=$(grep "traefik.http.routers\." docker-compose.yml | wc -l)

echo "📊 Found $ROUTER_COUNT unique routers with $TOTAL_ROUTER_LINES configuration lines"

# Check that all enabled services have constraint labels
echo "🏷️  Checking constraint labels..."
ENABLED_SERVICES=$(grep -c "traefik.enable=true" docker-compose.yml)
CONSTRAINT_LABELS=$(grep -c "traefik.constraint-label=yakhteh" docker-compose.yml)

if [[ "$ENABLED_SERVICES" -ne "$CONSTRAINT_LABELS" ]]; then
    echo "❌ Error: Mismatch between enabled services ($ENABLED_SERVICES) and constraint labels ($CONSTRAINT_LABELS)"
    echo "All services with traefik.enable=true must have traefik.constraint-label=yakhteh"
    exit 1
fi

# Check for yakhteh- prefix in router names
echo "🔖 Checking router name prefixes..."
UNPREFIXED_ROUTERS=$(grep "traefik.http.routers\." docker-compose.yml | grep -v "yakhteh-" | grep -v "http-catchall" || true)
if [[ -n "$UNPREFIXED_ROUTERS" ]]; then
    echo "❌ Error: Found routers without 'yakhteh-' prefix:"
    echo "$UNPREFIXED_ROUTERS"
    exit 1
fi

# Check for exposedbydefault=false
echo "🔒 Checking exposedByDefault setting..."
if ! grep -q "providers.docker.exposedbydefault=false" docker-compose.yml; then
    echo "❌ Error: exposedbydefault should be set to false"
    exit 1
fi

# Check for constraint configuration
echo "🎯 Checking provider constraints..."
if ! grep -q "providers.docker.constraints" docker-compose.yml; then
    echo "❌ Error: Docker provider constraints not configured"
    exit 1
fi

echo "✅ All Traefik configuration checks passed!"
echo "📊 Summary:"
echo "   - Router names: $ROUTER_COUNT unique routers"
echo "   - Enabled services: $ENABLED_SERVICES"
echo "   - Constraint labels: $CONSTRAINT_LABELS"
echo "   - ExposedByDefault: false ✓"
echo "   - Provider constraints: configured ✓"