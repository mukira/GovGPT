#!/usr/bin/env bash
# Pre-deployment verification script
# Run this before every deployment to catch issues

set -e  # Exit on error

echo "🧪 GovGPT Pre-Deployment Verification"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_DIR="/Users/Mukira/gov-analysis-platform/backend"
FRONTEND_DIR="/Users/Mukira/gov-analysis-platform/frontend"

cd "$BACKEND_DIR"

echo "📦 Step 1: Testing Python imports..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/Mukira/gov-analysis-platform/backend')

failures = []

# Test critical imports
imports_to_test = [
    ("app.services.llm_service", "llm_service"),
    ("app.services.vector_service", "vector_service"),
    ("app.services.chat_service", "chat_service"),
    ("app.services.news.gdelt_service", "gdelt_service"),
    ("app.services.social_media.social_aggregator", "social_aggregator"),
    ("app.utils.query_classifier", "classify_query"),
    ("app.api.chat", "router"),
    ("app.main", "app"),
]

for module_name, obj_name in imports_to_test:
    try:
        module = __import__(module_name, fromlist=[obj_name])
        obj = getattr(module, obj_name)
        print(f"  ✅ {module_name}.{obj_name}")
    except Exception as e:
        print(f"  ❌ {module_name}.{obj_name}: {e}")
        failures.append(f"{module_name}.{obj_name}")

if failures:
    print(f"\n❌ Import failures: {', '.join(failures)}")
    sys.exit(1)
else:
    print("\n✅ All imports successful!")
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Import test failed!${NC}"
    exit 1
fi

echo ""
echo "🧠 Step 2: Testing query classifier..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/Mukira/gov-analysis-platform/backend')

from app.utils.query_classifier import classify_query, get_query_confidence

# Test decision queries
decision_tests = [
    ("Should Kenya expand healthcare?", "decision"),
    ("Approve budget allocation", "decision"),
    ("What is healthcare?", "exploratory"),
    ("Explain the policy", "exploratory"),
]

failures = []
for query, expected in decision_tests:
    result = classify_query(query)
    if result == expected:
        print(f"  ✅ '{query[:30]}...' → {result}")
    else:
        print(f"  ❌ '{query[:30]}...' → Expected {expected}, got {result}")
        failures.append(query)

if failures:
    print(f"\n❌ Classification failures: {len(failures)}")
    sys.exit(1)
else:
    print("\n✅ Query classifier working correctly!")
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Query classifier test failed!${NC}"
    exit 1
fi

echo ""
echo "🏥 Step 3: Testing backend startup..."
# Kill any existing backend
pkill -f "uvicorn app.main:app" || true
sleep 2

# Start backend in background
cd "$BACKEND_DIR"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > /tmp/verify_backend.log 2>&1 &
BACKEND_PID=$!
echo "  Backend started (PID: $BACKEND_PID) on port 8001"

# Wait for startup
echo "  Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Backend started successfully!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "  ${RED}❌ Backend failed to start in 30 seconds${NC}"
        cat /tmp/verify_backend.log
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""
echo "🌐 Step 4: Testing API endpoints..."
# Test health endpoint
HEALTH=$(curl -s http://localhost:8001/health)
echo "  Health check: $HEALTH"

# Test chat stream endpoint
echo "  Testing /api/chat/stream..."
STREAM_TEST=$(curl -s -X POST http://localhost:8001/api/chat/stream \
    -H "Content-Type: application/json" \
    -d '{"message":"test"}' | head -c 200)

if [[ $STREAM_TEST == *"data:"* ]]; then
    echo -e "  ${GREEN}✅ Stream endpoint working${NC}"
else
    echo -e "  ${RED}❌ Stream endpoint not responding correctly${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Kill test backend
kill $BACKEND_PID 2>/dev/null || true
sleep 2

echo ""
echo "📱 Step 5: Checking frontend..."
cd "$FRONTEND_DIR"

# Check if key frontend files exist
if [ ! -f "src/components/ChatInterface.tsx" ]; then
    echo -e "  ${RED}❌ ChatInterface.tsx missing${NC}"
    exit 1
fi

if [ ! -f "src/components/DecisionReport.tsx" ]; then
    echo -e "  ${RED}❌ DecisionReport.tsx missing${NC}"
    exit 1
fi

echo -e "  ${GREEN}✅ Frontend files present${NC}"

echo ""
echo "🎯 Step 6: Running integration tests..."
cd "$BACKEND_DIR"

if [ -f "tests/test_integration.py" ]; then
    python -m pytest tests/test_integration.py -v --tb=short || {
        echo -e "${RED}❌ Integration tests failed!${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Integration tests passed!${NC}"
else
    echo -e "${YELLOW}⚠️  No integration tests found (tests/test_integration.py)${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✅ ALL VERIFICATION CHECKS PASSED!${NC}"
echo "======================================"
echo ""
echo "Safe to deploy! 🚀"
