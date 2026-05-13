# Mini OpenClaw

Mini OpenClaw is a simplified, learning-oriented reimplementation of [OpenClaw](https://github.com/jlkm905/OpenClaw). Where OpenClaw is a full-featured personal agent system, this project strips it down to its essential ideas — making the internals easier to study, modify, and build on. It is intended for anyone who wants to understand how a personal AI agent works from the ground up, without the complexity of a production system.

## Core Design Areas

- **Skill design** — modular, file-based skills that the agent can discover and invoke dynamically
- **Memory design** — a structured memory system that persists context across conversations and informs agent behavior
- **Visualizable frontend** — a Next.js UI that lets users inspect and interact with the agent's active skills and memory in real time

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
