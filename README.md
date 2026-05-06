# Mini OpenClaw

A simplified personal AI agent system built with LangChain/LangGraph (backend) and Next.js (frontend).

## Stack

- **Backend**: FastAPI + LangChain + LangGraph — runs on port 8002
- **Frontend**: Next.js 14+ — runs on port 3000

## Structure

```
mini-openclaw/
├── backend/        # FastAPI + LangChain/LangGraph
├── frontend/       # Next.js 14+
└── README.md
```

## Getting Started

### Backend
```bash
cd backend
uv sync
uv run python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
