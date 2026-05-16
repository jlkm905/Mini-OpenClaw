import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent

from tools import load_tools
from graph.skills_snapshot import generate_snapshot

_BACKEND = Path(__file__).parent.parent
load_dotenv(_BACKEND / ".env")

_WORKSPACE = _BACKEND / "workspace"

_SOUL_PATH = _WORKSPACE / "SOUL.md"
_IDENTITY_PATH = _WORKSPACE / "IDENTITY.md"
_USER_PATH = _WORKSPACE / "USER.md"
_AGENTS_PATH = _WORKSPACE / "AGENTS.md"
_MEMORY_PATH = _WORKSPACE / "MEMORY.md"

_MAX_SECTION_CHARS = 20_000

_PROVIDER_DEFAULTS = {
    "openai":     "gpt-4o",
    "anthropic":  "claude-sonnet-4-5",
    "gemini":     "gemini-2.0-flash",
    "openrouter": "openai/gpt-4o",
}


def _truncate(text: str) -> str:
    if len(text) > _MAX_SECTION_CHARS:
        return text[:_MAX_SECTION_CHARS] + "\n...[truncated]"
    return text


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _build_system_prompt(skills_xml: str) -> str:
    sections = [
        _truncate(skills_xml.strip()),
        _truncate(_read(_SOUL_PATH)),
        _truncate(_read(_IDENTITY_PATH)),
        _truncate(_read(_USER_PATH)),
        _truncate(_read(_AGENTS_PATH)),
        _truncate(_read(_MEMORY_PATH)),
    ]
    return "\n\n".join(s for s in sections if s)


def _require_key(env_var: str, provider: str) -> str:
    value = os.getenv(env_var, "").strip()
    if not value:
        raise ValueError(
            f"PROVIDER is set to '{provider}' but {env_var} is missing. "
            f"Add it to your .env file."
        )
    return value


def _build_llm():
    provider = os.getenv("PROVIDER", "openai").lower()
    model = os.getenv("MODEL_NAME", "").strip() or _PROVIDER_DEFAULTS.get(provider, "gpt-4o")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=_require_key("OPENAI_API_KEY", provider),
            temperature=0,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            api_key=_require_key("ANTHROPIC_API_KEY", provider),
            temperature=0,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=_require_key("GOOGLE_API_KEY", provider),
            temperature=0,
        )

    if provider == "openrouter":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=_require_key("OPENROUTER_API_KEY", provider),
            temperature=0,
        )

    raise ValueError(f"Unknown PROVIDER '{provider}'. Choose: openai | anthropic | gemini | openrouter")


def build_agent():
    llm = _build_llm()
    skills_xml = generate_snapshot()
    return create_agent(llm, load_tools(), system_prompt=_build_system_prompt(skills_xml))
