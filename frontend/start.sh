echo "🔧 Killing any process on port 5173..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1

echo "🗑️  Clearing Vite cache..."
cd "$(dirname "$0")"
rm -rf node_modules/.vite .vite dist 2>/dev/null || true

echo "✅ Starting frontend on port 5173..."
nohup npm run dev -- --port 5173 --host > /tmp/frontend_permanent.log 2>&1 &
echo "Frontend log: /tmp/frontend_permanent.log"
