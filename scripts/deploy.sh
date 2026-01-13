#!/bin/bash

# Government Analysis Platform Deployment Script
# This script handles deployment to production

set -e  # Exit on error

echo "=================================="
echo "Gov Analysis Platform Deployment"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check required environment variables
check_env() {
    echo -e "${YELLOW}Checking environment variables...${NC}"
    
    required_vars=(
        "GROQ_API_KEY"
        "QDRANT_URL"
        "QDRANT_API_KEY"
        "SUPABASE_URL"
        "SUPABASE_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}Error: $var is not set${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ All required environment variables are set${NC}"
}

# Build frontend
build_frontend() {
    echo -e "${YELLOW}Building frontend...${NC}"
    cd frontend
    npm ci
    npm run build
    cd ..
    echo -e "${GREEN}✓ Frontend built successfully${NC}"
}

# Deploy frontend to Vercel
deploy_frontend() {
    echo -e "${YELLOW}Deploying frontend to Vercel...${NC}"
    cd frontend
    vercel --prod
    cd ..
    echo -e "${GREEN}✓ Frontend deployed${NC}"
}

# Deploy backend to Modal
deploy_backend() {
    echo -e "${YELLOW}Deploying backend to Modal...${NC}"
    cd backend
    modal deploy modal_app.py
    cd ..
    echo -e "${GREEN}✓ Backend deployed${NC}"
}

# Run health checks
health_check() {
    echo -e "${YELLOW}Running health checks...${NC}"
    ./scripts/health-check.sh
    echo -e "${GREEN}✓ Health checks passed${NC}"
}

# Main deployment flow
main() {
    echo ""
    echo "Starting deployment process..."
    echo ""
    
    check_env
    build_frontend
    deploy_frontend
    deploy_backend
    health_check
    
    echo ""
    echo -e "${GREEN}=================================="
    echo -e "Deployment completed successfully! 🚀"
    echo -e "==================================${NC}"
}

# Run main function
main
