import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tools import load_tools

load_dotenv()

SOUL_PATH = Path(__file__).parent.parent / "workspace" / "SOUL.md"
MEMORY_PATH = Path(__file__).parent.parent / "memory" / "MEMORY.md"
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def _build_system_prompt() -> str:
    parts = []

    if SOUL_PATH.exists():
        parts.append(SOUL_PATH.read_text(encoding="utf-8").strip())

    memory_text = MEMORY_PATH.read_text(encoding="utf-8").strip() if MEMORY_PATH.exists() else ""
    if memory_text:
        parts.append(f"\n## Long-Term Memory\n{memory_text}")

    skill_lines = []
    for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
        skill_name = skill_md.parent.name
        first_line = skill_md.read_text(encoding="utf-8").split("\n")[0].lstrip("# ").strip()
        skill_lines.append(f"- **{skill_name}**: {first_line}")

    if skill_lines:
        parts.append(
            "\n## Available Skills\n"
            + "\n".join(skill_lines)
            + "\n\nUse `read_file` to read a skill's full SKILL.md before executing it."
        )

    return "\n\n".join(parts)


def build_agent():
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        base_url=os.getenv("MODEL_BASE_URL") or None,
        api_key=os.getenv("MODEL_API_KEY", "sk-placeholder"),
        temperature=0,
    )

    # langgraph.prebuilt.create_react_agent is the recommended LangGraph-native agent API.
    # It replaces the legacy AgentExecutor + create_react_agent(chain) pattern.
    return create_react_agent(llm, load_tools(), prompt=_build_system_prompt())
