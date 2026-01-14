echo "🔧 Killing any process on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

echo "✅ Starting backend on port 8000..."
cd "$(dirname "$0")"
source venv/bin/activate
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend_permanent.log 2>&1 &
echo "Backend log: /tmp/backend_permanent.log"
