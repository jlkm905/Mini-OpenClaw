import json
import uuid
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from pydantic import BaseModel

from graph.agent import build_agent

app = FastAPI(title="Mini-OpenClaw")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_ROOT = Path(__file__).parent
SESSIONS_DIR = BACKEND_ROOT / "sessions"
MEMORY_LOG_DIR = BACKEND_ROOT / "memory" / "logs"
SESSIONS_DIR.mkdir(exist_ok=True)
MEMORY_LOG_DIR.mkdir(parents=True, exist_ok=True)

# Directories the frontend editor is allowed to write into
_WRITE_DIRS = {"memory", "skills", "workspace", "sessions"}
# Root-level files the frontend may write (e.g. MEMORY.md lives at backend root)
_WRITE_ROOT_FILES = {"MEMORY.md"}

agent = build_agent()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class SaveFileRequest(BaseModel):
    path: str
    content: str


# ---------------------------------------------------------------------------
# Path safety helpers
# ---------------------------------------------------------------------------

def _safe_path(path_str: str) -> Path:
    """Resolve path and ensure it stays within BACKEND_ROOT."""
    try:
        resolved = (BACKEND_ROOT / path_str).resolve()
        resolved.relative_to(BACKEND_ROOT.resolve())  # raises ValueError if outside
        return resolved
    except ValueError:
        raise HTTPException(status_code=403, detail="Path traversal not allowed")


def _assert_writable(path_str: str) -> None:
    parts = Path(path_str).parts
    if not parts:
        raise HTTPException(status_code=403, detail="Invalid path")
    if len(parts) == 1:
        if parts[0] not in _WRITE_ROOT_FILES:
            raise HTTPException(
                status_code=403,
                detail=f"Root-level writes only allowed for: {_WRITE_ROOT_FILES}",
            )
    elif parts[0] not in _WRITE_DIRS:
        raise HTTPException(
            status_code=403,
            detail=f"Writes only allowed inside: {_WRITE_DIRS}",
        )


# ---------------------------------------------------------------------------
# Message serialization
# ---------------------------------------------------------------------------

def _serialize_message(msg) -> dict:
    content = msg.content
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    d: dict = {"type": msg.type, "content": content}
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        d["tool_calls"] = msg.tool_calls
    if hasattr(msg, "tool_call_id") and msg.tool_call_id:
        d["tool_call_id"] = msg.tool_call_id
    if hasattr(msg, "name") and msg.name:
        d["name"] = msg.name
    return d


def _deserialize_messages(history: list[dict]) -> list:
    out = []
    for m in history:
        t = m["type"]
        if t == "human":
            out.append(HumanMessage(content=m["content"]))
        elif t == "ai":
            out.append(AIMessage(content=m["content"], tool_calls=m.get("tool_calls", [])))
        elif t == "tool":
            out.append(ToolMessage(
                content=m["content"],
                tool_call_id=m.get("tool_call_id", ""),
                name=m.get("name", ""),
            ))
    return out


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def _load_session(session_id: str) -> list[dict]:
    path = SESSIONS_DIR / f"{session_id}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _save_session(session_id: str, history: list[dict]) -> None:
    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(history, indent=2, ensure_ascii=False))


def _append_memory_log(user_msg: str, ai_reply: str) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"\n## {timestamp}\n**User:** {user_msg}\n**Agent:** {ai_reply}\n"
    with open(MEMORY_LOG_DIR / f"{today}.md", "a", encoding="utf-8") as f:
        f.write(entry)


# ---------------------------------------------------------------------------
# SSE helpers & streaming generator
# ---------------------------------------------------------------------------

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _stream_agent(
    input_messages: list,
    session_id: str,
    history: list[dict],
    user_msg: str,
):
    """Async generator that streams LangGraph events as SSE and saves the session."""
    new_messages: list = []
    final_reply = ""

    try:
        async for event in agent.astream_events({"messages": input_messages}, version="v2"):
            kind = event["event"]

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                token = chunk.content if isinstance(chunk.content, str) else ""
                if token:
                    final_reply += token
                    yield _sse({"type": "token", "content": token})

            elif kind == "on_chat_model_end":
                output = event["data"].get("output")
                # Normalise AIMessageChunk → AIMessage when needed
                if isinstance(output, AIMessageChunk):
                    output = AIMessage(
                        content=output.content if isinstance(output.content, str) else "",
                        tool_calls=list(output.tool_calls) if output.tool_calls else [],
                    )
                if isinstance(output, AIMessage):
                    new_messages.append(output)

            elif kind == "on_tool_start":
                yield _sse({
                    "type": "tool_call",
                    "name": event["name"],
                    "args": event["data"].get("input", {}),
                })

            elif kind == "on_tool_end":
                output = event["data"].get("output")
                if isinstance(output, ToolMessage):
                    new_messages.append(output)
                    content_str = output.content if isinstance(output.content, str) else str(output.content)
                else:
                    content_str = str(output)
                yield _sse({
                    "type": "tool_result",
                    "name": event["name"],
                    "content": content_str[:3000],
                })

        # ---- persist after stream ends ----
        new_human = HumanMessage(content=user_msg)
        new_entries = [_serialize_message(new_human)] + [_serialize_message(m) for m in new_messages]
        history.extend(new_entries)
        _save_session(session_id, history)
        _append_memory_log(user_msg, final_reply)

        yield _sse({"type": "done", "content": final_reply, "session_id": session_id})

    except Exception as exc:
        yield _sse({"type": "error", "message": str(exc)})


# ---------------------------------------------------------------------------
# Routes — Chat
# ---------------------------------------------------------------------------

@app.post("/api/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    history = _load_session(session_id)
    existing_messages = _deserialize_messages(history)
    new_human = HumanMessage(content=req.message)
    input_messages = existing_messages + [new_human]

    if req.stream:
        return StreamingResponse(
            _stream_agent(input_messages, session_id, history, req.message),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Non-streaming fallback
    result = await agent.ainvoke({"messages": input_messages})
    agent_messages = result["messages"][len(input_messages):]
    reply: str = result["messages"][-1].content
    if not isinstance(reply, str):
        reply = str(reply)

    new_entries = [_serialize_message(new_human)] + [_serialize_message(m) for m in agent_messages]
    history.extend(new_entries)
    _save_session(session_id, history)
    _append_memory_log(req.message, reply)

    return ChatResponse(reply=reply, session_id=session_id)


# ---------------------------------------------------------------------------
# Routes — File management
# ---------------------------------------------------------------------------

@app.get("/api/files")
async def read_file_api(path: str = Query(..., description="Path relative to backend root")):
    safe = _safe_path(path)
    if not safe.exists() or not safe.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return {"path": path, "content": safe.read_text(encoding="utf-8")}


@app.post("/api/files")
async def save_file_api(req: SaveFileRequest):
    _assert_writable(req.path)
    safe = _safe_path(req.path)
    safe.parent.mkdir(parents=True, exist_ok=True)
    safe.write_text(req.content, encoding="utf-8")
    return {"path": req.path, "saved": True}


# ---------------------------------------------------------------------------
# Routes — Session management
# ---------------------------------------------------------------------------

@app.get("/api/sessions")
async def list_sessions():
    sessions = []
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        stat = path.stat()
        try:
            history = json.loads(path.read_text(encoding="utf-8"))
            msg_count = len(history)
        except Exception:
            msg_count = 0
        created_ts = getattr(stat, "st_birthtime", stat.st_ctime)
        sessions.append({
            "session_id": path.stem,
            "file_path": str(path.relative_to(BACKEND_ROOT)),
            "created_at": datetime.fromtimestamp(created_ts).isoformat(),
            "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "message_count": msg_count,
        })
    return sessions


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str) -> list[dict]:
    history = _load_session(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return history


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    path.unlink()
    return {"deleted": session_id}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
