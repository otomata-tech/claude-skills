#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/.." && pwd)/skills"
DIST="$(cd "$(dirname "$0")/.." && pwd)/dist/api/skills"

rm -rf "$(dirname "$DIST")"
mkdir -p "$DIST"

skills_json="["
first=true

for skill_dir in "$SKILLS_DIR"/*/; do
    skill_md="$skill_dir/SKILL.md"
    [ -f "$skill_md" ] || continue

    content=$(cat "$skill_md")

    # Parse frontmatter
    name=""
    description=""
    if echo "$content" | head -1 | grep -q '^---'; then
        frontmatter=$(echo "$content" | sed -n '/^---$/,/^---$/p' | sed '1d;$d')
        name=$(echo "$frontmatter" | grep '^name:' | head -1 | cut -d: -f2- | xargs)
        description=$(echo "$frontmatter" | grep '^description:' | head -1 | cut -d: -f2- | xargs)
    fi

    # Fallback to directory name
    dir_name=$(basename "$skill_dir")
    [ -z "$name" ] && name="$dir_name"

    # Strip frontmatter for markdown field
    markdown=$(echo "$content" | sed '/^---$/,/^---$/d')

    # URL-safe name for file paths (replace : with -)
    safe_name=$(echo "$name" | tr ':' '-')

    # Add to list JSON
    if [ "$first" = true ]; then
        first=false
    else
        skills_json+=","
    fi
    skills_json+=$(jq -nc --arg n "$name" --arg d "$description" '{name:$n, description:$d}')

    # Write detail JSON
    mkdir -p "$DIST/$safe_name"
    jq -nc --arg n "$name" --arg d "$description" --arg c "$content" --arg m "$markdown" \
        '{name:$n, description:$d, content:$c, markdown:$m}' > "$DIST/$safe_name.json"

    # Write raw SKILL.md
    cp "$skill_md" "$DIST/$safe_name/raw"
done

skills_json+="]"
echo "$skills_json" | jq '.' > "$DIST.json"

echo "Built $(echo "$skills_json" | jq length) skills → $DIST"
