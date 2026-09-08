---
name: bob-telemetry
description: Use when the user asks what IBM Bob consumed or did — Bobcoins, tokens, cost per model class, per task or subagent, tools used, commands flagged as dangerous, files edited — read from the local database ~/.bob/db/bob.db.
---

# Bob telemetry

`python3 "<skill-dir>/scripts/bob_telemetry.py" <view> [--task PREFIX] [--since YYYY-MM-DD] [--db PATH] [--json]`

| view | answers |
|---|---|
| `summary` | total Bobcoins, split by model class |
| `tasks` | cost per task |
| `calls` | every LLM call: tokens, Bobcoins, model class |
| `tools` | tool usage and durations |
| `security` | commands flagged by the security check, or unparseable |
| `changes` | files Bob edited |
| `context` | what fills the context window |

When explaining (build 2.1.0):
- `cost` is in Bobcoins.
- A root task's cost includes its subagents, its tokens do not: never add parent and subagent rows.
- Bob stores no model name; the class is inferred from the unit price — ≈ 2.0 Bobcoins per
  million tokens = standard (`premium-ide`), ≈ 0.833 = economy (`explorer`, used by `explore`
  subagents). Any other rate means billing changed: report it.

The script prints titles, commands and paths, never message bodies.
