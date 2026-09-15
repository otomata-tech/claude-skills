# claude-skills

Repository of generic, reusable skills for Claude Code. Each skill is a directory with
a `SKILL.md`; users install via symlink into `~/.claude/skills/`. See `README.md` for
the user-facing skill list and other skill sources.

## Structure

One skill = `skills/<slug>/` with a required `SKILL.md` (+ optional `scripts/`).
`scripts/build-api.sh` aggregates every `SKILL.md` frontmatter into `dist/api/` (a flat
`skills.json` + one `skills/<slug>.json` per skill).

## SKILL.md frontmatter

```yaml
---
name: <slug>                   # Falls back to dir name if absent
description: <one line>        # Used by the model to decide relevance
disable-model-invocation: false
argument-hint: "[arg1|arg2]"   # Optional, displayed in autocomplete
---
```

`name` is what users type as `/<name>` — it can differ from the directory name (e.g.
`skills/session/` exposes itself as `session-lookup`).

## Commands

```bash
./scripts/build-api.sh   # Regenerate dist/api/ JSON from all SKILL.md
```

No tests, no lint — skills are markdown.

## Conventions

- Slug = directory name when possible; a different `name:` only when there's a
  meaningful reason (fs slug generic but the skill needs a specific public name).
- Description must be specific enough for the model to decide whether to invoke —
  avoid vague descriptions like "helper for stuff".
- No legacy fallbacks in skill bodies — if a skill is renamed, update references
  rather than aliasing.
- Keep SKILL.md under ~200 lines unless the skill genuinely needs more — long
  instructions mean the model picks up less of it.

## Adding / renaming a skill

- Add : `skills/<slug>/SKILL.md` + row in README's `## Skills` table + symlink into
  `~/.claude/skills/<slug>` to test locally + `./scripts/build-api.sh` if the JSON API
  is consumed externally.
- Rename : `git mv skills/<old> skills/<new>`, update `name:` in `SKILL.md` + README,
  replace the symlink.

Other repos contribute skills the same way (`/data/oto/skills/`, `/data/howto/skills/`,
etc.) — see README's "Other skill sources" table.
