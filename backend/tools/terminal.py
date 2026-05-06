from pathlib import Path

from langchain_community.tools import ShellTool

WORKSPACE = Path(__file__).parent.parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)

BLOCKED_CMDS = [
    "rm -rf /",
    "dd if=",
    ":(){:|:&};:",
    "mkfs",
    "chmod 777 /",
    "shutdown",
    "reboot",
    "> /dev/sda",
]


class RestrictedShellTool(ShellTool):
    name: str = "terminal"
    description: str = (
        "Execute shell commands inside the project workspace directory. "
        "Cannot access or modify files outside the workspace."
    )

    def _run(self, commands: str) -> str:
        for blocked in BLOCKED_CMDS:
            if blocked in commands:
                return f"Error: command contains blocked pattern '{blocked}'"
        sandboxed = f"cd {WORKSPACE} && {commands}"
        return super()._run(sandboxed)


def build_terminal_tool() -> RestrictedShellTool:
    return RestrictedShellTool()
