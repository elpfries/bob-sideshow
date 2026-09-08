---
name: bob-agent-rules
description: Use when the user asks which rules IBM Bob injects — subagents ("do the work yourself"), which model or tier is used, why answers stay inline, how AGENTS.md and .bob/rules rank — or wants to see the actual system prompt Bob used.
---

# Rules Bob injects

1. `python3 "<skill-dir>/scripts/dump_system_prompt.py" --list`, then `--section NAME`,
   `--guidance Subagents` (or `create_html_artifact`), `--grep REGEX`, `--task PREFIX`, `--all`.
   This is the prompt Bob really used, stored with the task.
2. For what the prompt does not show — subagent presets and their models, tier → alias table,
   rule precedence, custom agents — read `reference/injected-rules.md`.
3. State that rules are instructions, not enforcement, and that `explore` subagents never see
   project rules. To change any of it, use the `bob-override-rules` skill.
