from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

_PROJECT_ROOT = Path(__file__).parent.parent
_ALLOWED_DIRS = {"workspace", "skills"}


class _WriteFileInput(BaseModel):
    path: str = Field(description="File path relative to the project root, e.g. workspace/MEMORY.md")
    content: str = Field(description="Full content to write to the file")


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = (
        "Write content to a file inside workspace/ or skills/. "
        "Use for updating MEMORY.md, daily logs, or skill files. "
        "Input: path (relative to project root) and content (full file text)."
    )
    args_schema: type[BaseModel] = _WriteFileInput

    def _run(self, path: str, content: str) -> str:
        parts = Path(path).parts
        if not parts or parts[0] not in _ALLOWED_DIRS:
            return f"Error: writes are only allowed inside {_ALLOWED_DIRS}."

        try:
            resolved = (_PROJECT_ROOT / path).resolve()
            resolved.relative_to(_PROJECT_ROOT.resolve())
        except ValueError:
            return "Error: path traversal not allowed."

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"Written: {path}"

    async def _arun(self, path: str, content: str) -> str:
        return self._run(path, content)
