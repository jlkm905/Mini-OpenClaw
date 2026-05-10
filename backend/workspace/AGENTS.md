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

### Long-Term Memory (`MEMORY.md`)
- Update long-term memory when you learn a persistent fact about the user (preferences, habits,
  important context) that should survive across sessions.
- Do NOT store: session-specific requests, one-off questions, sensitive personal data, or
  information the user has not explicitly shared as persistent.
- Entries must be concise, factual, and human-readable — short bullets or paragraphs only.
- Never store raw conversation logs in long-term memory.

### Daily Logs (`memory/logs/YYYY-MM-DD.md`)
- Append a brief summary of significant interactions to the daily log at session end or when
  explicitly requested.
- Format: `HH:MM — one-sentence summary of what was accomplished.`
- Daily logs are for debugging and future summarization, not real-time retrieval.

### Session Context vs Persistent Memory
- Session context = anything relevant only to the current conversation.
- Persistent memory = facts that will matter in future sessions.
- Never promote session context to persistent memory automatically; only do so when the user
  confirms something should be remembered long-term.

### Auditable Updates
- When writing to `MEMORY.md`, append or clearly mark what was added.
- Prefer appending dated entries rather than silently overwriting existing content.
