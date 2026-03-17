---
name: document
description: Update project documentation (CLAUDE.md + docs/). Use after significant work to keep docs in sync.
disable-model-invocation: false
argument-hint: "[docs|all]"
---

# Update Project Documentation

Two responsibilities:
1. **CLAUDE.md** — concise project overview (always loaded)
2. **docs/** — detailed per-concept docs (loaded on demand)

For todo management, use `/up:task`.

---

## 1. CLAUDE.md — The Map

### Gather Context

- Read current `CLAUDE.md` (if exists)
- Explore codebase: directories, config files, key modules
- Review conversation history to identify what changed this session

### Write/Update CLAUDE.md

Target: **under 500 lines**. Every line must earn its place.

```markdown
# <Project Name>

<1-2 line purpose>

## Stack
<bullet list: language, frameworks, key deps>

## Architecture
<tree structure, folders only, with inline comments>
project/
├── src/           # Main application code
├── scripts/       # Build and deploy scripts
└── tests/         # Test suites

## Commands
<build, test, lint, deploy — commands only>

## Conventions
<style, naming, patterns — only what prevents mistakes>

## Key Concepts
<domain terms, business logic Claude must know>

## Docs
Detailed docs in `docs/`:
- `architecture.md` — <1-line description>
- `data-model.md` — <1-line description>

```

### CLAUDE.md Rules

- NO verbose explanations — Claude infers
- NO duplicating docs/ content — just reference with short description
- The `## Docs` section MUST list all docs/ files with a 1-line description each
- Preserve existing custom instructions (git workflow, env vars, etc.)
- Ask before removing any existing content
- Use `@docs/filename.md` import if a doc should always be loaded

---

## 2. docs/ — The Territory

### Process

1. **Assess**: review what was done this session (conversation history, git diff)
2. **Identify**: determine which existing docs are affected, or if a new doc is needed
3. **Propose**: tell the user which docs you plan to update/create and what changes
4. **Validate**: get user approval before writing
5. **Update CLAUDE.md**: ensure the `## Docs` section lists any new doc files

If nothing changed that warrants doc updates, say so and move on.

### Location

Use the path specified in existing CLAUDE.md, or default `docs/` at project root.

### Structure

Flat, 1 file per concept:

```
docs/
  architecture.md    # Components, interactions, data flow
  api.md             # Endpoints, request/response
  data-model.md      # Schema, models, relationships
  setup.md           # Prerequisites, installation, env vars
  deployment.md      # Deploy process, environments
  <concept>.md       # Domain-specific as needed
```

### Doc File Format

```markdown
# <Concept>

<1-line purpose>

## <Section>
<content: headers, tables, code blocks — no prose paragraphs>
```

### docs/ Rules

- Max 500 lines per file — split if larger
- Include file paths with line refs where useful (`src/auth/login.ts:42`)
- Update existing docs incrementally, don't rewrite from scratch
- If a doc is accurate and unaffected by recent changes, don't touch it
- Accuracy over coverage: only document what's verifiable from code

---

## 3. Summary Output

After running, output:
- Files created/modified
- CLAUDE.md changes (sections added/updated/removed)
- Docs updated/created (or "no doc changes needed")
