# Command-to-skill migration — bob-code 2.1.0

Skills appearing in `.bob/skills/` that nobody created, coming back after every deletion.
Nothing to do with `/init`, which only writes `AGENTS.md` and `.bob/rules-<mode>/AGENTS.md`.

## What runs

`activate()` calls the migration sequence, which ends with `CommandMigrator.migrateToSkills(folder)`
for **every workspace folder** — at every start of Bob and every window reload.

```js
async migrateToSkills(ws) {
  const local  = await this._loadLocalCommands(ws);     // {.bob,.agents,.claude}/**/commands/*.md
  const global = await loadGlobalCommands(this.vsfs);   // ~/.bob|.agents|.claude /commands/*.md
  const n = await this._writeSkills(~/.bob/skills, global);
  return await this._writeSkills(path.join(ws, ".bob", "skills"), local) + n;
}

async _writeSkills(dir, commands) {
  for (const c of commands) {
    const file = path.join(dir, c.name, "SKILL.md");
    if (await this.vsfs.exists(file)) continue;         // the only idempotence check
    await this.vsfs.mkdir(path.join(dir, c.name), { recursive: true });
    await this.vsfs.writeFile(file, stringify(c.content, { name: c.name, description: c.description,
      metadata: { "user-invocable": true, "disable-model-invocation": true } }));
  }
}
```

- Local glob: `{.bob,.agents,.claude}/**/commands/*.md`, relative to each workspace folder,
  recursive (`.bob/x/y/commands/z.md` matches too). `.roo` is **not** scanned.
- Global dirs: `~/.bob/commands`, `~/.agents/commands`, `~/.claude/commands` (flat), written to
  `~/.bob/skills/`.
- Skill name = file name without `.md`; description = frontmatter `description`, else the first
  body line; `argument-hint` is carried over.
- On success: *"Bob has migrated {count} slash commands to skills. The old commands folders can be
  safely deleted."*

## Why they come back

The legacy-task migration has a flag (`migrations.legacyBobCodeTaskMigrationDone` in
`settings.json`); this one has **none**. Deleting the skills without removing the source `.md`
files recreates them at the next start. No setting disables it.

They are harmless in context: `disable-model-invocation: true` keeps them out of
`<available_skills>` (`getSkillsPrompt` filters `!disableModelInvocation`), so they only show up on
disk, in `git status`, and in the `/command` list.

## Identify

```sh
find . -path '*/.claude/commands/*.md' -o -path '*/.agents/commands/*.md' -o -path '*/.bob/*/commands/*.md'
grep -A3 '^metadata:' .bob/skills/<name>/SKILL.md   # user-invocable + disable-model-invocation = migrator
```

## Stop it

1. Remove or rename the source folder (`commands` must be an exact path segment).
2. Tombstones — commit a `SKILL.md` at each target path; `_writeSkills` then skips it. See
   `bob-override-rules/templates/skills/tombstone.sh`.
3. `"files.exclude": {"**/.claude/commands": true}` in `.vscode/settings.json`: the migrator passes
   its glob as a string, so `findFiles` gets `exclude === undefined` and VS Code applies
   `files.exclude`.

Useless here: `.bobignore` / `.gitignore` (exclusion patterns are not passed on this call path),
rules in `.bob/rules/` (the migrator is activation code, it reads no rule), deleting the skills.
