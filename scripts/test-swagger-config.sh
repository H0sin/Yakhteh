#!/bin/bash

# Test script for Multi-Service Swagger UI Configuration
# This script demonstrates how the routing would work in production

echo "🧪 Multi-Service Swagger UI Configuration Test"
echo "=============================================="
echo

# Check if configuration files exist
echo "📁 Checking configuration files..."
if [[ -f "docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found"
else
    echo "❌ docker-compose.yml not found"
    exit 1
fi

if [[ -f "docs/multi-service-swagger.md" ]]; then
    echo "✅ documentation found"
else
    echo "❌ documentation not found"
fi

echo

# Validate Traefik configuration
echo "🔧 Validating Traefik configuration..."
if ./scripts/validate-traefik.sh > /dev/null 2>&1; then
    echo "✅ Traefik configuration is valid"
else
    echo "❌ Traefik configuration has issues"
    exit 1
fi

echo

# Check docker-compose syntax
echo "🐳 Validating Docker Compose syntax..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has issues"
    exit 1
fi

echo

# Extract and analyze routing rules
echo "🔀 Analyzing routing configuration..."

echo
echo "📋 Configured Routes:"
echo "===================="

# Extract all router rules
grep -n "traefik.http.routers.*rule" docker-compose.yml | while read -r line; do
    # Extract router name and rule
    router_name=$(echo "$line" | sed 's/.*yakhteh-\([^"]*\)".*/\1/')
    rule=$(echo "$line" | sed 's/.*rule=\([^"]*\).*/\1/')
    echo "Router: $router_name"
    echo "Rule: $rule"
    echo
done

echo
echo "🔧 Configured Middlewares:"
echo "=========================="

# Extract middleware configurations
grep -n "traefik.http.middlewares" docker-compose.yml | while read -r line; do
    middleware=$(echo "$line" | sed 's/.*middlewares\.\([^"]*\).*/\1/')
    echo "Middleware: $middleware"
done

echo
echo "🎯 Expected URL Mappings:"
echo "========================="
echo "• https://api.domain.com/docs      → Auth Service Swagger UI"
echo "• https://api.domain.com/scheduling → Scheduling Service Swagger UI"
echo "• https://api.domain.com/inventory  → Clinic Service Swagger UI"

echo
echo "🔄 Path Rewriting Rules:"
echo "========================"
echo "• /scheduling → /docs (via regex: ^/scheduling(.*))"
echo "• /inventory  → /docs (via regex: ^/inventory(.*))"

echo
echo "✅ Configuration Test Complete!"
echo
echo "💡 To test in production:"
echo "   1. Deploy with: docker compose up -d"
echo "   2. Visit: https://api.yourdomain.com/scheduling"
echo "   3. Should see Scheduling Service documentation only"

echo
echo "🚀 Ready for deployment!"