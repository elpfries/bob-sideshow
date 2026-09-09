#!/usr/bin/env bash
# Stop Bob from recreating skills migrated from slash commands.
#
# Bob converts every {.bob,.agents,.claude}/**/commands/*.md file of the workspace into
# .bob/skills/<name>/SKILL.md at each start, with no "already done" flag: the only check is
# whether the target SKILL.md exists. Writing a placeholder there stops the recreation for good.
# Commit the result so the intent is versioned.
#
#   ./tombstone.sh commit release cli-release roo-resolve-conflicts roo-translate
set -euo pipefail

[ $# -gt 0 ] || { echo "usage: $0 <skill-name>..." >&2; exit 2; }

for name in "$@"; do
  dir=".bob/skills/$name"
  mkdir -p "$dir"
  cat > "$dir/SKILL.md" <<TOMBSTONE
---
name: $name
description: Placeholder blocking Bob's command-to-skill migration.
metadata:
  user-invocable: false
  disable-model-invocation: true
---

Do not delete. Bob recreates this skill from a \`commands/*.md\` file at every start unless a
SKILL.md already exists here.
TOMBSTONE
  echo "tombstoned $dir/SKILL.md"
done
