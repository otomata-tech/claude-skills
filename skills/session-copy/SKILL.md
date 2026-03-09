---
name: session:copy
description: Copy a Claude Code session between project folders (import to here, or export to another path).
argument-hint: "[keyword] [to /path]"
---

# Session Copy

Copy a conversation between project folders.

## When to use

- User wants to continue a session that was started in a different project folder (import)
- User wants to copy a session from here to another project folder (export)

## Workflow

1. **Determine direction** -- If user says "copy to /some/path" or "export to...", it's an export. Otherwise it's an import (default).

2. **Search** -- Run the search script. For import: `--global` to find foreign sessions. For export: search local sessions (no `--global`).

```bash
# Import: search globally
~/.claude/skills/session-search/scripts/session-search --global
~/.claude/skills/session-search/scripts/session-search "keyword" --global

# Export: search local project
~/.claude/skills/session-search/scripts/session-search
~/.claude/skills/session-search/scripts/session-search "keyword"
```

3. **Filter & Display** -- For import: discard sessions already in current project. For export: show local sessions. Discard the current active session in both cases. Ask the user to pick if multiple results.

4. **Copy** -- Run the copy script:

```bash
# Import (from foreign project to here, default)
~/.claude/skills/session-copy/scripts/session-copy --session-id <uuid>

# Export (from here to another project)
~/.claude/skills/session-copy/scripts/session-copy --session-id <uuid> --to /target/path
```

5. **Instruct** -- The script prints the new session UUID and a resume command. Tell the user to run `claude --resume <new-id>` from the target directory. Do NOT suggest `--continue`.

## Notes

- The script copies (not moves) -- the original session stays intact
- The destination gets a new UUID so source and destination are fully independent
- The script handles both the `.jsonl` file and any subagents directory
- `--to` accepts any existing directory path
