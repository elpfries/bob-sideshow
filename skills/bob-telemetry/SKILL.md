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

When explaining (build 2.2.3 unless a bullet says 2.3.0; 2.3.0 = `1.126.0+bob2.3.0.20261026121409`):
- `cost` is in Bobcoins.
- A root task's cost includes its subagents, its tokens do not: never add parent and subagent rows.
- Bob stores no model name; the class is inferred from the unit price — ≈ 2.0 Bobcoins per
  million tokens = standard (`premium-ide`), ≈ 0.833 = economy (`explorer`, used by `explore`
  subagents). Any other rate means billing changed: report it.
- On bob-code 2.2.0 (checked 2026-09-28 on live traffic) and bob-code 2.2.3 (checked 2026-10-19 on
  live traffic, task 9ad66ac1), calls no longer carry token counts at all (`_meta.spend` is
  `{cost, contextTokens}` only), so the class is always `n/a` and the unit price cannot be measured;
  token columns show `n/a` rather than 0, and the `ctx` column (context tokens for that call) is
  still available. Bobcoins totals are unaffected.
- 2.3.0 (checked 2026-11-03 on live traffic, task 6cc0a0b9: three priced calls, `_meta.spend` =
  `{cost, contextTokens}`, e.g. `{"cost":0.036608,"contextTokens":18304}`; `summary`, `tasks`, `calls`,
  `tools`, `security`, `changes`, `context` all run unchanged): same shape, class still `n/a`. The Bobcoins
  per million tokens measured on 2.1.0 (≈ 2.0 standard, ≈ 0.833 economy) are 2.1.0 figures, not
  re-measured since.
- The history is short, by design (2.3.0, source: `dist/extension.js` of build
  `1.126.0+bob2.3.0.20261026121409`, `cleanupOldTasks` and `deleteTaskTrees`; first seen 2026-10-19 on a
  2.2.3 install, where the database went from 26 tasks / 147 priced calls to 17 / 17 after one restart):
  at startup of the task manager Bob deletes every root task that is not pinned and whose `updated_at`
  is older than the setting `tasks.retentionDays` (default 30; a value of 0 or less disables the purge),
  then logs `Cleaned up N tasks older than D days`. Messages and pending approvals go with them
  (`ON DELETE CASCADE`). On 2.3.0 the delete is recursive (`WITH RECURSIVE` over `parent_id`): sub-task
  trees of any depth are removed with their root; 2.2.3 removed one level of children. Sub-tasks are never
  selected on their own, they follow their root. So the database holds at best about 30 days of history and
  totals from `summary` only cover that window (`summary` prints the oldest task's creation date). To keep
  more, raise `tasks.retentionDays` or pin the task.
- Schema 013_workspace_editor_sessions (2.3.0, from the migration SQL in the bundle, confirmed in the live
  database read-only): migrations 012_task_editor_sessions and 013_workspace_editor_sessions add no table
  and no column. 012 deleted the orphan `editorSession:<task id>` rows of `key_value_store` and created two
  triggers; 013 drops them and recreates them keyed by project: `delete_workspace_editor_session` (after a
  task delete, if no other task has that `project_id`, delete `editorSession:<project_id>`) and
  `ignore_orphan_editor_session_insert` (an insert of an `editorSession:<project_id>` key with no matching
  task is silently ignored). The live `sqlite_master` has exactly those two triggers; the live
  `key_value_store` holds only `featureFlags.v1`, no `editorSession:` row, and nothing in the bundle writes
  one (the string occurs only inside the SQL), so what an editor session stores is undetermined. The
  telemetry views read none of this.

The script prints titles, commands and paths, never message bodies.
