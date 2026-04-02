---
name: session-lookup
description: "Search past Claude conversations by keyword, date, or project. Deep search in raw transcripts."
argument-hint: "[keyword] [--global] [--from YYYY-MM-DD] [--to YYYY-MM-DD] [-n N]"
---

# Session Lookup

Search past Claude Code conversations in raw transcripts.

## Usage

Run the search script:
```bash
# Current project
~/.claude/skills/session-lookup/scripts/session-search

# All projects
~/.claude/skills/session-lookup/scripts/session-search --global

# By keyword
~/.claude/skills/session-lookup/scripts/session-search "keyword" --global

# By date
~/.claude/skills/session-lookup/scripts/session-search --from "2026-02-01" --to "2026-02-05"

# Limit results (default: 5)
~/.claude/skills/session-lookup/scripts/session-search "keyword" -n 1
```

Output shows transcript sessions with `claude --resume <id>` commands.
