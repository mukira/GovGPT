# GovGPT

**AI-Powered Government Data Analysis Platform**

Natural language interface for government decision-makers to analyze policies, budgets, and data through intelligent conversations.

## Features

- 📄 **Unified Data Ingestion**: Upload PDFs, Excel, Word documents
- 💬 **Conversational Analysis**: Ask questions in natural language
- 📊 **Impact Analysis**: Economic, social, and regional impact assessments
- 👥 **Population-Aware Insights**: Context from demographic data
- 📰 **News & Sentiment Analysis**: Real-time public opinion tracking
- 🔍 **Explainability**: Full traceability with source citations

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+
- **LLM**: Llama 3 70B via Groq API
- **Vector DB**: Qdrant
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel (frontend) + Modal (backend)

## Quick Start

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Documentation

- [Implementation Plan](../.gemini/antigravity/brain/dd21fe43-cdec-4803-a227-34abedf6e626/implementation_plan.md)
- [Task Checklist](../.gemini/antigravity/brain/dd21fe43-cdec-4803-a227-34abedf6e626/task.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## CI/CD Pipeline

Comprehensive testing at each stage:
- ✅ Code quality checks (linting, formatting)
- ✅ Unit tests (backend & frontend)
- ✅ Integration tests
- ✅ Security scanning
- ✅ Performance benchmarks
- ✅ E2E tests
- ✅ Deployment verification

## Cost Estimate

- **Start**: $0/month (free tiers)
- **1K users**: ~$325/month
- **10K users**: ~$2,200/month

## License

MIT License - See LICENSE file for details
