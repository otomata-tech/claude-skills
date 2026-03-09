---
name: up:research
description: Log research work, experiments, or learnings to progress.yaml. Use after significant exploration or POC work.
disable-model-invocation: true
argument-hint: "[topic]"
---

# Log Research Entry

Add structured entries to `progress.yaml` tracking research, experiments, and learnings.

## Process

1. **Read** `progress.yaml` at project root (create if doesn't exist)

2. **Analyze conversation** for:
   - Research questions explored
   - Experiments run and their results
   - Key learnings/insights
   - Decisions made
   - Blockers or open questions
   - Links to resources, docs, deployments

3. **Draft entry** and show to user:
   ```yaml
   - date: 2026-02-01
     topic: "LangSmith Deployment POC"
     summary: "Tested agentic approach for browser automation"
     learnings:
       - "Graph = structure, Prompt = instructions"
       - "Secrets can be updated via API without redeploy"
     decisions:
       - "Use agentic approach (LLM decides sequence)"
     next:
       - "Add browser tools (click, type, screenshot)"
     links:
       - "https://ht-ordinary-temporary-18.eu.langgraph.app"
   ```

4. **Get approval** before writing

5. **Append** to progress.yaml

## File Format

```yaml
# Progress Log
# Research entries, experiments, learnings

entries:
  - date: "2026-02-01"
    topic: "Short topic name"
    summary: "1-2 sentence summary"
    learnings:
      - "Key insight 1"
      - "Key insight 2"
    decisions:
      - "Decision made and why"
    blockers:
      - "Open question or blocker"
    next:
      - "Follow-up action"
    links:
      - "url or path"
    session: "SESSION_TAG_xxx" # optional, for cross-reference
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| `date` | yes | ISO date |
| `topic` | yes | Short topic (<50 chars) |
| `summary` | yes | 1-2 sentences |
| `learnings` | no | Key insights discovered |
| `decisions` | no | Decisions made with rationale |
| `blockers` | no | Open questions, blockers |
| `next` | no | Follow-up actions |
| `links` | no | URLs, file paths, references |
| `session` | no | SESSION_TAG for cross-reference with todos |

## Rules

- Entries are append-only (never edit past entries)
- Keep summaries concise — this is a log, not a report
- Link to detailed docs if available (e.g., `docs/orchestration-comparison.md`)
- Reference todo items if applicable (e.g., "see t12")
- One entry per topic per day (merge if same topic)

## Example Output

```yaml
entries:
  - date: "2026-02-01"
    topic: "LangSmith Deployment"
    summary: "Deployed POC agent to LangSmith cloud, configured secrets via API"
    learnings:
      - "Graph defines structure (nodes/edges), prompt defines behavior"
      - "For agentic: graph is just LLM<->tools loop, LLM decides sequence"
      - "Secrets API: PATCH /v2/deployments/{id} with {secrets: [{name, value}]}"
    decisions:
      - "Test agentic approach before workflow approach"
    next:
      - "Add browser_click, browser_type, browser_screenshot tools"
      - "Test Wise login end-to-end"
    links:
      - "https://ht-ordinary-temporary-18-....eu.langgraph.app"
      - "docs/orchestration-comparison.md"
    session: "SESSION_TAG_langsmith-deployment-poc_20260201"
```
