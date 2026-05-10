import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from tools import load_tools
from graph.skills_snapshot import generate_snapshot

load_dotenv()

_BACKEND = Path(__file__).parent.parent
_WORKSPACE = _BACKEND / "workspace"

_SOUL_PATH = _WORKSPACE / "SOUL.md"
_IDENTITY_PATH = _WORKSPACE / "IDENTITY.md"
_USER_PATH = _WORKSPACE / "USER.md"
_AGENTS_PATH = _WORKSPACE / "AGENTS.md"
_MEMORY_PATH = _BACKEND / "MEMORY.md"

_MAX_SECTION_CHARS = 20_000


def _truncate(text: str) -> str:
    if len(text) > _MAX_SECTION_CHARS:
        return text[:_MAX_SECTION_CHARS] + "\n...[truncated]"
    return text


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _build_system_prompt(skills_xml: str) -> str:
    sections = [
        _truncate(skills_xml.strip()),         # 1. SKILLS_SNAPSHOT
        _truncate(_read(_SOUL_PATH)),           # 2. SOUL.md
        _truncate(_read(_IDENTITY_PATH)),       # 3. IDENTITY.md
        _truncate(_read(_USER_PATH)),           # 4. USER.md
        _truncate(_read(_AGENTS_PATH)),         # 5. AGENTS.md
        _truncate(_read(_MEMORY_PATH)),         # 6. MEMORY.md
    ]
    return "\n\n".join(s for s in sections if s)


def build_agent():
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        base_url=os.getenv("MODEL_BASE_URL") or None,
        api_key=os.getenv("MODEL_API_KEY", "sk-placeholder"),
        temperature=0,
    )

    skills_xml = generate_snapshot()
    return create_agent(llm, load_tools(), system_prompt=_build_system_prompt(skills_xml))
