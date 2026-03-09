---
name: git-commit
description: Git commit conventions for domain-based commit messages (project, gitignored)
---

# Git Commit Skill

**IMPORTANT: Do NOT use this skill if you are Claude Code Web (Docker environment). Use direct Bash git commands instead to avoid interface issues.**

When creating git commits in this project:

## Commit Format

Use this format:
```
<domain>/<type>: <description> [optional-context]
```

**Valid domains:** webapp, runs, instructions, tools, projects, ci

**Valid types:**
- For content: add, update, cleanup
- For code: feat, fix, refactor, test, perf, style, docs, chore, revert

## Examples
```
runs/add: Orange CDN competitive analysis [orange-cdn]
webapp/feat: MatrixViewer for visual data [#75]
instructions/update: otomata workflow documentation
tools/fix: token loading from environment
```

## Rules
- Subject line: 50-72 characters recommended
- Use lowercase for domain and type
- Don't add period at end
- Add context in square brackets if applicable [run-name] or [#issue]

## Workflow
- **DO NOT push by default** - only commit locally
- Only push when explicitly requested by the user
- The pre-commit hook will validate the format automatically
