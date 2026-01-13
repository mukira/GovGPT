#!/bin/bash

# Health Check Script
# Verifies all services are running correctly

set -e

echo "Running health checks..."

# Check backend API
check_backend() {
    echo -n "Checking backend API... "
    response=$(curl -s -o /dev/null -w "%{http_code}" ${BACKEND_URL:-http://localhost:8000}/health)
    
    if [ "$response" -eq 200 ]; then
        echo "✓ OK"
        return 0
    else
        echo "✗ FAILED (HTTP $response)"
        return 1
    fi
}

# Check frontend
check_frontend() {
    echo -n "Checking frontend... "
    response=$(curl -s -o /dev/null -w "%{http_code}" ${FRONTEND_URL:-http://localhost:5173})
    
    if [ "$response" -eq 200 ]; then
        echo "✓ OK"
        return 0
    else
        echo "✗ FAILED (HTTP $response)"
        return 1
    fi
}

# Check Qdrant connection
check_qdrant() {
    echo -n "Checking Qdrant connection... "
    if [ -z "$QDRANT_URL" ]; then
        echo "⚠ SKIPPED (no URL configured)"
        return 0
    fi
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$QDRANT_URL/collections")
    
    if [ "$response" -eq 200 ] || [ "$response" -eq 401 ]; then
        echo "✓ OK"
        return 0
    else
        echo "✗ FAILED (HTTP $response)"
        return 1
    fi
}

# Check database connection
check_database() {
    echo -n "Checking database connection... "
    if [ -z "$DATABASE_URL" ]; then
        echo "⚠ SKIPPED (no URL configured)"
        return 0
    fi
    
    # Simple connection test
    python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.close()
    print('✓ OK')
except Exception as e:
    print(f'✗ FAILED: {str(e)}')
    exit(1)
"
}

# Main health check
main() {
    failed=0
    
    check_backend || failed=$((failed+1))
    check_frontend || failed=$((failed+1))
    check_qdrant || failed=$((failed+1))
    check_database || failed=$((failed+1))
    
    echo ""
    if [ $failed -eq 0 ]; then
        echo "All health checks passed ✓"
        exit 0
    else
        echo "$failed health check(s) failed ✗"
        exit 1
    fi
}

main
