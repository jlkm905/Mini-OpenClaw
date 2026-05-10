import re
from pathlib import Path

_SKILLS_DIR = Path(__file__).parent.parent / "skills"
_SNAPSHOT_PATH = Path(__file__).parent.parent / "SKILLS_SNAPSHOT.md"
_ROOT = Path(__file__).parent.parent


def _parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def generate_snapshot() -> str:
    """Scan skills/, write SKILLS_SNAPSHOT.md, return its XML content."""
    entries = []
    for skill_md in sorted(_SKILLS_DIR.rglob("SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        name = meta.get("name") or skill_md.parent.name
        description = meta.get("description", "")
        location = "./" + skill_md.relative_to(_ROOT).as_posix()
        entries.append(
            f"  <skill>\n"
            f"    <name>{name}</name>\n"
            f"    <description>{description}</description>\n"
            f"    <location>{location}</location>\n"
            f"  </skill>"
        )

    content = "<available_skills>\n" + "\n".join(entries) + "\n</available_skills>\n"
    _SNAPSHOT_PATH.write_text(content, encoding="utf-8")
    return content
