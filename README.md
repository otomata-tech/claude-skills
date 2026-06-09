# Claude Code Skills

Generic, reusable skills for Claude Code.

## Skills

| Skill | Description |
|-------|-------------|
| `dev-init` | Bootstrap fullstack web project (Fastify + Vue 3 + Vite + shadcn-vue + Tailwind + PG + Drizzle + Logto) |
| `prod-init` | Deploy to oto.zone / tuls.me (Caddy + systemd + Cloudflare DNS + GitHub Actions CI/CD) |
| `seo-check` | Audit SEO, Open Graph, responsive design |
| `session-lookup` | Search past Claude Code conversations by keyword/date/project (dir: `session/`) |
| `session-copy` | Duplicate the current Claude Code session into an independent copy |
| `timetrack` | Time tracking for freelance missions (logs in `/data/pro/time-entries.json`) |

`memento` moved to its own plugin (skills + Memento MCP connector): [`otomata-tech/memento-plugin`](https://github.com/otomata-tech/memento-plugin).

## Installation

Each skill is a directory with a `SKILL.md` file. Install by symlinking into `~/.claude/skills/`:

```bash
ln -sf /data/projects/claude-skills/skills/<skill> ~/.claude/skills/<skill>
```

> Note: the `session/` directory is exposed as the `session-lookup` skill (name comes from frontmatter, symlinked under that name).

## Build skills API

```bash
./scripts/build-api.sh
```

Produces `dist/api/skills.json` and per-skill JSON files — a flat API of all skills with their frontmatter.

## Other skill sources

Skills are spread across repos, each linked into `~/.claude/skills/`:

| Source | Skills |
|--------|--------|
| `/data/oto/skills/` | oto-browser, oto-cli, oto-google, oto-search, oto-whatsapp, oto-secrets, oto-task |
| `/data/howto/skills/` | brainstorm, product, strategy |
| `/data/pro/skills/` | pdf-generator |
| `/data/projects/project-tracker/skills/` | projects |
