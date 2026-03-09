---
name: session:open
description: Resume a previously saved session by injecting its context. Use when user wants to continue previous work.
argument-hint: "[title or number]"
---

# Session Open

List saved sessions and inject the selected session's context into the current conversation.

## When to use

- User says "resume", "reprendre", "open session", "where were we?"
- User wants to continue work from a previous session

## Workflow

1. **Load** `~/.claude/projects/<project-slug>/sessions.json`
   - If file doesn't exist or is empty, tell user "No saved sessions for this project."

2. **List** saved sessions (most recent first):
   ```
   1. [2026-02-13] Test Roundtable docgen API (feat/pause-button)
   2. [2026-02-12] Dashboard cleanup (feat/dashboard-v2)
   ```

3. **Select**: if argument matches a title (partial) or number, auto-select. Otherwise ask user to pick.

4. **Inject context** — read the selected session and present it as a briefing:

   ```markdown
   ## Resuming: <title>

   **Branch:** `<branch>` | **Saved:** <date>

   ### What was done
   - <summary items>

   ### What's pending
   - <pending items>

   ### Key files
   - `<file1>`
   - `<file2>`

   ### Notes
   <note if any>
   ```

5. **Read key files** — proactively read the key files listed in the session to have full context.

6. **Check branch** — if current branch differs from saved branch, warn user:
   ```
   Current branch is `master` but session was on `feat/pause-button`. Switch branch?
   ```

7. **Ready** — tell user you have the context and are ready to continue.

## Storage

File: `~/.claude/projects/<project-slug>/sessions.json`

Project slug = cwd with `/` replaced by `-`, leading `-` stripped.

## Options

- **Delete a session**: if user says "delete session X" or "clean", remove it from the JSON file.
- **List only**: if user says "list sessions", just show the list without injecting.

## Rules

- Always show the list before injecting (user might want a different one)
- Read key files silently (don't dump contents to user), just confirm you've loaded them
- Keep the briefing concise — the user already knows the context, this is a reminder
