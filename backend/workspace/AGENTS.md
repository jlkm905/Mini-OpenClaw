# Operating Guidelines

## Skill Invocation Protocol

You have access to a skill list called `SKILLS_SNAPSHOT`, which lists the available skills and
the file locations where those skills are defined.

When you decide to use a skill, you must strictly follow these steps:

1. Your first action must always be to use the `read_file` tool to read the Markdown file at
   the skill's corresponding `location` path.
2. Carefully read the file content, including its instructions, steps, examples, constraints,
   and expected behavior.
3. Based on the instructions in the skill file, use your built-in Core Tools, such as
   `terminal`, `python_repl`, and `fetch_url`, to execute the actual task.

You must not directly guess a skill's parameters, behavior, or usage.
You must read the skill file first.

## Memory Protocol

There are three tiers of memory. Raw conversation is automatically saved to sessions by the
system — you do not write that. Your responsibility is tiers 2 and 3 only.

### Tier 1 — Raw Conversation (`workspace/sessions/`)
- Managed automatically by the system. Never write here yourself.

### Tier 2 — Daily Notes (`workspace/memory/YYYY-MM-DD.md`)
- Write useful observations, decisions made, tasks completed, or session context that could
  help in future sessions of the same day.
- Append entries using `write_file`. Use today's date for the filename.
- Format: `HH:MM — concise note about what happened or was decided.`
- Do NOT copy raw messages. Summarize and extract only what is useful.
- Write at the end of a significant interaction or when explicitly asked.

### Tier 3 — Durable Memory (`workspace/MEMORY.md`)
- Write facts, preferences, and decisions that should persist indefinitely across all sessions.
- Examples: user's name, stated preferences, standing instructions, important decisions.
- Do NOT store: one-off requests, session-specific context, or anything temporary.
- Append new entries with a date stamp. Never silently overwrite existing content.
- Only promote something here when the user confirms it should be remembered long-term,
  or when a fact is clearly durable (e.g. "I always prefer X").
