import json
import uuid
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from graph.agent import build_agent

app = FastAPI(title="Mini-OpenClaw")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS_DIR = Path("sessions")
MEMORY_LOG_DIR = Path("memory/logs")
SESSIONS_DIR.mkdir(exist_ok=True)
MEMORY_LOG_DIR.mkdir(parents=True, exist_ok=True)

agent = build_agent()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


# --- Session helpers ---

def _load_session(session_id: str) -> list[dict]:
    path = SESSIONS_DIR / f"{session_id}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _save_session(session_id: str, history: list[dict]) -> None:
    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(history, indent=2, ensure_ascii=False))


def _append_memory_log(user_msg: str, ai_msg: str) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"\n## {timestamp}\n**User:** {user_msg}\n**Agent:** {ai_msg}\n"
    with open(MEMORY_LOG_DIR / f"{today}.md", "a", encoding="utf-8") as f:
        f.write(entry)


# --- Routes ---

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or str(uuid.uuid4())
    history = _load_session(session_id)

    messages = [
        HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
        for m in history
    ]
    messages.append(HumanMessage(content=req.message))

    result = await agent.ainvoke({"messages": messages})
    reply: str = result["messages"][-1].content

    history.extend([
        {"role": "human", "content": req.message},
        {"role": "assistant", "content": reply},
    ])
    _save_session(session_id, history)
    _append_memory_log(req.message, reply)

    return ChatResponse(reply=reply, session_id=session_id)


@app.get("/sessions")
async def list_sessions() -> list[str]:
    return [p.stem for p in sorted(SESSIONS_DIR.glob("*.json"))]


@app.get("/sessions/{session_id}")
async def get_session(session_id: str) -> list[dict]:
    history = _load_session(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return history


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    path.unlink()
    return {"deleted": session_id}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
