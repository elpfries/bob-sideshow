---
name: bob-override-rules
description: Use when the user wants IBM Bob to follow their own rules instead of the built-in ones — always spawn a subagent when asked, premium model for subagents, project workflow first, protect AGENTS.md from /init, reports as artifacts, no dangerous commands — and needs the right markdown in the right folder.
metadata:
  argument-hint: "[what to override]"
---

# Override Bob's rules

1. Ask what to override if unclear, then pick the template in `templates/rules/`
   (`templates/README.md` maps goal → file). A model override also needs
   `templates/agents/explore-premium.md` copied to `.bob/agents/`.
2. Pick the folder. Strongest first: `.bob/rules-<mode>/` → `.bob/rules/` → `AGENTS.md` →
   `~/.bob/rules-<mode>/` → `~/.bob/rules/`. Default: workspace `.bob/rules/`. Never AGENTS.md:
   it ranks lower and `/init` may rewrite it.
3. `python3 "<skill-dir>/scripts/rule_locations.py"` shows existing rules, agents, hooks and
   `/init` leftovers.
4. Write the file with `write_file`: English, imperative, one concern per file; keep the first
   paragraph that names the built-in rule being overridden.
5. A prohibition needs enforcement, not a rule: `deniedCommands`, a `PreToolUse` hook
   (`templates/hooks/`, exit 2 blocks — ask before enabling, hooks bypass approval), or a mode
   without `execute`.
6. Tell the user: loaded at the next task; verify with `dump_system_prompt.py --grep "<phrase>"`;
   rules are probabilistic; `explore` subagents ignore them; Plan and Ask modes allow only
   `explore`; in production every tier except `explorer` maps to `premium-ide`.
