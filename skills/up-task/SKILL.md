---
name: up:task
description: Analyze conversation and update todo.json with incomplete work
disable-model-invocation: true
---

# Update Todos from Conversation

Analyze the current conversation to identify incomplete work and update `todo.json`.

## Process

1. **Read** `todo.json` at project root (create if doesn't exist)

2. **Scan conversation** for:
   - Tasks marked as incomplete, blocked, or deferred
   - Errors encountered that need follow-up
   - Features partially implemented
   - "TODO", "FIXME", "later", "next time" mentions
   - Explicit user requests not yet fulfilled

3. **Auto-archive**: match completed work against active tasks

4. **Propose changes** to user:
   - Tasks to archive (with reason)
   - New tasks to add (with suggested priority)
   - Never add tasks without asking

5. **Write** `todo.json` after user approval

6. **Display** active tasks sorted by priority

7. **Output session summary** (for searchability):
```
═══════════════════════════════════════════════════
SESSION_TAG_<topic-slug>_<YYYYMMDD>
Summary: <30 words max, main topics covered>
Todos: <count active> active, <count archived this session> archived
═══════════════════════════════════════════════════
```

## File Format

```json
{
  "active": [
    {
      "id": "t1",
      "task": "Implement OAuth2 flow",
      "context": "Need Google + GitHub providers",
      "priority": "high",
      "created": "2026-01-26",
      "tags": ["auth", "feature"]
    }
  ],
  "archived": [
    {
      "id": "t0",
      "task": "Setup project structure",
      "completed": "2026-01-26",
      "tags": ["setup"]
    }
  ]
}
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Short unique id (`t1`, `t2`, ...) — auto-increment |
| `task` | yes | What needs to be done (imperative, <80 chars) |
| `context` | no | Extra info, blockers, session reference |
| `priority` | yes | `high`, `medium`, `low` |
| `created` | yes | ISO date |
| `completed` | auto | ISO date, set on archival |
| `tags` | no | Categorization |

## Rules

- Never invent tasks — only track what was actually discussed
- IDs are never reused — always increment from max existing
- Don't delete tasks — archive them with completion date
- Prune archive if >50 items (keep most recent)
- Add `todo.json` to `.gitignore` if not already there
