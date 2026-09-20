# Contributing rules

- Skill directory name = frontmatter `name`; regex `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 chars.
- Scripts: Python 3.8+, standard library, read-only, offline. Templates may use Node.js.
- `scripts/_bobcheck.py` is copied into every skill: keep the copies identical
  (`shasum skills/*/scripts/_bobcheck.py` shows one hash). Bump `VERIFIED_*` there only after
  re-verifying the reference notes on the new build.
- State the build every fact was reverse-engineered from, and its source (bundle, database, public docs).
- Before a PR: `python3 -m py_compile skills/*/scripts/*.py`,
  `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs`, and run each script
  against a real installation.
- No personal data in examples or fixtures.

## Development tooling (not shipped)

- `.kimi-code/skills/` holds dev-only workflow skills (Backlog.md rituel: next-task, pre-clear,
  run-milestone, analyze-task, task-telemetry; plus quota-check for the subscription quota). They are active when working on this repo with
  Kimi Code; `.claude/skills/` contains relative symlinks to them for Claude Code. `install.sh`
  ships only `skills/*/`.
- `.kimi-code/hooks/` holds the dual-protocol (Claude Code / Kimi Code) Backlog gates
  (`pre-task-done.sh`, `post-task-create.sh`); declared in `.claude/settings.json` and in the
  user-level `~/.kimi-code/config.toml`. They no-op outside Backlog.md projects.
- Task complexity convention: every Backlog task carries one label — `model:secondaire`
  (default, runs on kimi-for-coding) or `model:primaire` (hard architecture, concurrency,
  orchestration; runs on k3, and gets an analyze-task design pass first). Kimi Code mapping:
  the `Agent` tool's `model` parameter; pool configured in `[secondary_model]`.

<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.48.0 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**For every user request in this project, run `backlog instructions overview` before answering or taking action.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->
