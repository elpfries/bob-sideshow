# Command-to-skill migration — bob-code 2.2.0

Skills appearing in `.bob/skills/` that nobody created, coming back after every deletion.
Nothing to do with `/init`, which only writes `AGENTS.md` and `.bob/rules-<mode>/AGENTS.md` — confirmed unchanged
on bob-code 2.2.0, build `1.126.0+bob2.2.0.20260924155054` (anchor `AGGRESSIVELY` SAME string, 12 457 chars,
both builds — the `/init` prompt is byte-identical).

Re-verified against the same 2.2.0 build, using `docs/bob-2.1.0-to-2.2.0.md` and a direct read of the migrator
class (its own name is gone by CommonJS→ESM bundling — never cited here — but every glob, path and message below
was re-read at the call site and confirmed present).

## What runs

`activate()` calls the migration sequence, which ends with `migrateToSkills(folder)` for **every workspace
folder** — at every start of Bob and every window reload. Confirmed unchanged on 2.2.0: the method name
`migrateToSkills` and its helpers `_loadLocalCommands`/`_writeSkills` are still literal property names, and the
call is still driven by `getFileWorkspaces()` from the same migration-sequence entry point.

```js
// same shape on 2.1.0 and 2.2.0; only the minified local names differ between the two
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
  recursive (`.bob/x/y/commands/z.md` matches too). `.roo` is **not** scanned. **Confirmed unchanged on 2.2.0**:
  direct read of `_loadLocalCommands` gives the exact same glob, built from
  `A3.posix.join(`{${[".bob",".agents",".claude"].join(",")}}`, "**", "commands", "*.md")` — the rule-loader's
  new `plugins/` subdirectory (`docs/bob-2.1.0-to-2.2.0.md` §2) does **not** apply here: the command migrator's
  local roots are still exactly `.bob`, `.agents`, `.claude`, with no `plugins/*` addition. A found file is
  additionally dropped if it resolves outside the workspace folder (an added path-containment guard, new in
  2.2.0, unrelated to `.bobignore`/`.gitignore`).
- Global dirs: `~/.bob/commands`, `~/.agents/commands`, `~/.claude/commands` (flat), written to
  `~/.bob/skills/`. Confirmed unchanged: same three literal paths, same target directory, direct read of the
  global-commands loader.
- Skill name = file name without `.md`; description = frontmatter `description`, else the first
  body line; `argument-hint` is carried over. Confirmed unchanged: same frontmatter parse, same
  `argument-hint` → `metadata["argument-hint"]` carry-over (anchor `argument-hint` SAME LOGIC, CJS→ESM interop
  only).
- On success: *"Bob has migrated {{count}} slash commands to skills. The old commands folders can be
  safely deleted."* — the interpolation syntax moved from a single `{count}` to i18n's `{{count}}`
  (`Ye.t("Bob has migrated {{count}} slash commands…", {count:…})`); same message otherwise, same trigger (sum of
  written skills across global + every workspace folder is non-zero).

## Why they come back

The legacy-task migration has a flag (`migrations.legacyBobCodeTaskMigrationDone` in
`settings.json`); this one has **none**. Deleting the skills without removing the source `.md`
files recreates them at the next start. No setting disables it. Confirmed unchanged on bob-code 2.2.0: the
`_writeSkills` idempotence check is still only "skip if the target `SKILL.md` already exists" — no flag gates
the migration itself.

They are harmless in context: `disable-model-invocation: true` keeps them out of the skills list Bob shows the
model, so they only show up on disk, in `git status`, and in the `/command` list. **Re-anchored on 2.2.0**, build
`1.126.0+bob2.2.0.20260924155054`: the raw tag `<available_skills>` is gone as a literal (anchor MISSING in
2.2.0) — like every other section tag, it is now assembled at runtime from the prompt-section registry entry
`{id:"skills", tag:"available_skills", …}`, confirmed present by direct read (`tag:"available_skills"` is a
literal substring in 2.2.0). The filtering function itself lost its 2.1.0 name (`getSkillsPrompt` was a
CommonJS export, gone by bundling — not cited as an anchor here); the property it filters on,
`disableModelInvocation`, is confirmed still a literal object-key name in the 2.2.0 skills filter
(`!a.disableModelInvocation` in the same function that also filters `hidden` and `groups`).

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

All three confirmed unchanged on bob-code 2.2.0, build `1.126.0+bob2.2.0.20260924155054`: `_writeSkills` still
skips an existing target file first (tombstones still work); `findFiles` is still called with the glob as its
only argument (anchor `findFiles` IDENTICAL after neutralising identifiers, 192 tokens, both builds — no second,
exclude argument was added).

Useless here, confirmed unchanged: `.bobignore` / `.gitignore` (exclusion patterns are not passed on this call
path — the path-containment guard added in 2.2.0, see "What runs" above, checks workspace containment, not
ignore patterns), rules in `.bob/rules/` (the migrator is activation code, it reads no rule), deleting the
skills.
