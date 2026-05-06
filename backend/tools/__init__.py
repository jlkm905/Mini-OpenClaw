from pathlib import Path

from langchain_community.tools.file_management import ReadFileTool
from langchain_experimental.tools import PythonREPLTool

from .terminal import build_terminal_tool
from .fetch_url import FetchURLTool
from .rag import KnowledgeBaseTool

PROJECT_ROOT = Path(__file__).parent.parent


class _PythonREPL(PythonREPLTool):
    name: str = "python_repl"
    description: str = (
        "Execute Python code for computation, data processing, and scripting. "
        "Input: valid Python code as a string."
    )


def load_tools() -> list:
    return [
        build_terminal_tool(),
        _PythonREPL(),
        FetchURLTool(),
        ReadFileTool(root_dir=str(PROJECT_ROOT)),
        KnowledgeBaseTool(),
    ]
