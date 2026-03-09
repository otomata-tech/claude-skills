---
name: session:close
description: Save current session context for later resumption. Use when user wants to pause work and come back later.
argument-hint: "[title]"
---

# Session Close

Save a structured context snapshot of the current session so it can be resumed later with `session:open`.

## When to use

- User says "pause", "close", "save session", "on reprend plus tard"
- User wants to bookmark the current session before leaving

## Workflow

1. **Gather context** from the conversation:
   - **title**: from argument, or ask user (short, descriptive)
   - **branch**: run `git branch --show-current`
   - **summary**: what was accomplished this session (2-5 bullet points)
   - **pending**: what remains to be done (bullet points, can be empty)
   - **keyFiles**: important files that were read/modified (max 10)
   - **note**: optional free-form note from user

2. **Get session ID**: read from environment or find current session:
   ```bash
   # Current session transcript is the most recent .jsonl in the project dir
   ls -t ~/.claude/projects/$(pwd | sed 's|/|-|g; s|^-||')/*.jsonl 2>/dev/null | head -1
   ```
   Extract the UUID from the filename (strip `.jsonl`).

3. **Save** to `~/.claude/projects/<project-slug>/sessions.json`:
   - Read existing file (or start with `[]`)
   - Append new entry with structure below
   - Write back

4. **Confirm** to user: show title + session ID

## Session Entry Format

```json
{
  "id": "<session-uuid>",
  "title": "Short descriptive title",
  "branch": "feat/my-branch",
  "cwd": "/data/alexis/project",
  "savedAt": "2026-02-13T14:30:00Z",
  "summary": ["Did X", "Fixed Y", "Tested Z"],
  "pending": ["Still need to do A", "Waiting on B"],
  "keyFiles": ["src/foo.ts", "docs/bar.md"],
  "note": "Optional extra context"
}
```

## Storage

File: `~/.claude/projects/<project-slug>/sessions.json`

Project slug = cwd with `/` replaced by `-`, leading `-` stripped. Example: `/data/alexis/roundtable` → `-data-alexis-roundtable`.

## Rules

- Keep summary and pending concise — this will be re-injected as context later
- keyFiles should be relative to cwd
- If a session with the same ID already exists, update it (don't duplicate)
- Show the saved entry to the user for confirmation
