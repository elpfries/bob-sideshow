# Templates

| File | Copy to | Purpose |
|---|---|---|
| `rules/subagents-on-request.md` | `.bob/rules/` | honor explicit subagent requests |
| `rules/premium-subagents.md` | `.bob/rules/` | never use the economy `explore` preset |
| `rules/project-workflow-first.md` | `.bob/rules/` | AGENTS.md workflow section above built-ins |
| `rules/protect-agents-md.md` | `.bob/rules/` | keep `/init` away from AGENTS.md |
| `rules/report-as-artifact.md` | `.bob/rules/` | artifacts when a report is asked for |
| `rules/command-safety.md` | `.bob/rules/` | generation-time command constraints |
| `agents/explore-premium.md` | `.bob/agents/` | read-only subagent on the `premium` tier |
| `hooks/command-guard.mjs` | `.bob/hooks/` | deterministic PreToolUse guard |
| `hooks/settings.hooks.json` | merge into `.bob/settings.json` | registers the hook |

Use `~/.bob/rules/` and `~/.bob/agents/` instead for every workspace. Rules load at the next task.
