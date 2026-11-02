---
id: TASK-17.4
title: Re-verify the database and telemetry surface on schema 013
status: To Do
assignee: []
created_date: '2026-11-02 22:51'
updated_date: '2026-11-02 23:11'
labels:
  - 'model:secondaire'
milestone: m-2
dependencies:
  - TASK-17.1
parent_task_id: TASK-17
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
bob-telemetry (bob_telemetry.py, SKILL.md) and bob-version (bob_version.py) read ~/.bob/db/bob.db and the server feature flags. 2.3.0 applies migrations 012_task_editor_sessions and 013_workspace_editor_sessions and may change messages.data, _meta.spend, tasks columns and flags. Also document a fact found 2026-10-19 and still absent from the notes: at startup Bob purges tasks older than tasks.retentionDays (default 30 days), so the database never holds the full history; check it on 2.3.0.

Shared facts (session of 2026-11-02): Bob installed = 2.3.0, build 1.126.0+bob2.3.0.20261026121409, extension.js sha1 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (10 911 633 bytes), product.json commit b48bf62595b330a56b628a82441207f506fbc6a4, schema 013_workspace_editor_sessions (migrations 012_task_editor_sessions and 013_workspace_editor_sessions new). The outgoing baseline is private/baseline-2.2.3/ (complete, webview included); the new one is frozen in private/baseline-2.3.0/ (four files + web/assets with web-assets.sha256, README still to write) and extracted in private/diff/2.3.0/; the 2.2.3 extraction is private/diff/2.2.1/ (byte-identical bundle). Step-3 verdicts already run: private/diff/anchors-verdicts-2.2.3-2.3.0.txt (102 anchors: 11 CHANGED, 1 MISSING in B = _alwaysAllowedTools, 1 MISSING in A = isWorkspaceTrusted, hook-runner string EDITED 13359 -> 16390 chars). Step-4 delta: private/diff/compare-2.2.3-2.3.0.txt (+723 strings, +704 props, 751 strings added, 152 removed). Public changelog read 2026-11-02 at https://bob.ibm.com/docs/ide/changelog (2.3.0, October 2026; no version between 2.2.3 and 2.3.0). A real task run by 2.3.0 exists in ~/.bob/db/bob.db: id 6cc0a0b9..., title QUOI de neuf bob?, 7 messages, 3 priced calls (2026-11-02 22:45 UTC). Method and procedure: private/SOURCES.md (Re-verifying on a new build, 8 steps; durable-anchor rule). Model milestone: m-1 (TASK-13.x, TASK-14). AGENTS.md rules bind every task: state the build and source of every fact, scripts stay Python 3.8+ stdlib read-only offline, five identical _bobcheck.py copies, no personal data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 What migrations 012 and 013 change is stated from the bundle and checked in the real database (read-only)
- [ ] #2 bob_telemetry.py summary, calls and security, and bob_version.py, run on the real 2.3.0 database and on the 2.3.0 task without error; the shape of _meta.spend and the flag set on 2.3.0 are recorded and any parsing gap is fixed minimally
- [ ] #3 The task retention purge (tasks.retentionDays, default value, when it runs) is re-checked on 2.3.0 and documented in bob-telemetry with build and source
- [ ] #4 Steps 6 and 7 of private/SOURCES.md are recorded for 2.3.0 with the task id and outputs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HANDOFF FROM TASK-17.1 (2026-11-02): facts TASK-17.4 must apply (database, telemetry, version surface). Build 2.3.0 = 1.126.0+bob2.3.0.20261026121409; sources: dist/extension.js, read-only open of ~/.bob/db/bob.db (schema 013), public changelog. Proof: docs/bob-2.2.3-to-2.3.0.md sections 6 and 7 and private/diff/anchor-details-2.2.3-2.3.0.txt (DATABASE and SERVER FLAG sections).

SCHEMA
1. Last migration 013_workspace_editor_sessions (VERIFIED_SCHEMA candidate). Migration list 001..013. NO new table: still tasks, messages, attribution_logs, task_pending_approvals, key_value_store, plus _migrations. Definitions of those tables and migrations 001..011 are the same SQL.
2. 012_task_editor_sessions SQL: DELETE FROM key_value_store WHERE substr(key,1,14)='editorSession:' AND NOT EXISTS (SELECT 1 FROM tasks WHERE id = substr(key,15)); CREATE TRIGGER delete_task_editor_session AFTER DELETE ON tasks (deletes the key editorSession:||OLD.id); CREATE TRIGGER ignore_orphan_editor_session_insert BEFORE INSERT ON key_value_store WHEN key starts with editorSession: and no task has that id => RAISE(IGNORE).
3. 013_workspace_editor_sessions SQL: DROP both triggers; DELETE the editorSession: rows with no task whose project_id equals substr(key,15); CREATE TRIGGER delete_workspace_editor_session AFTER DELETE ON tasks WHEN NOT EXISTS another task with OLD.project_id (deletes editorSession:||OLD.project_id); CREATE TRIGGER ignore_orphan_editor_session_insert again, now matching on project_id. So the key is editorSession:<project_id>. Live sqlite_master has exactly the triggers delete_workspace_editor_session and ignore_orphan_editor_session_insert. Nobody in extension.js writes editorSession rows (the string occurs only in the SQL); the live key_value_store has one row, featureFlags.v1 (2221 chars), no editorSession row. State that as undetermined.
4. bob_version.py: _migrations check must expect 013; the flag cache (featureFlags.v1 in key_value_store, mirrored by state.vscdb) now carries five new keys: web-search-path (default /search/tbob), bob-plugin-service-url (default empty), plugins-ui-enabled (default false), observation-masking-enabled (default false), context-focus-query-enabled (default false). On this install cached values: context-focus-query-enabled true, plugins-ui-enabled true, observation-masking-enabled false, web-search-path /search/tbob, bob-plugin-service-url empty. getFlagValue(...) no longer reads feedback-model and feedback-verification-enabled (keys remain in the schema), and now reads context-focus-query-enabled and observation-masking-enabled. Re-derive the pushed, not read marking from the code: keys read through getFlagValue are bob-findings-enabled, context-focus-query-enabled, dynamic-context-enabled, ibm-support-url, issue-repo-url, max-monthly-budget-allowance, observation-masking-enabled, review-flow-enabled (plus the direct reads the script already lists; re-grep rather than trusting this list for others). Group policies added: OtelConfiguration, UpdateMode. Settings added: chat.pinnedModels [], experiments.webSearch false, top-level locale empty, session.pinnedTeams in workspace .bob/settings.json.

MESSAGES AND SPEND
5. _meta.spend is UNCHANGED: the task loop builds {input, output, cacheRead, cacheWrite, cost, contextTokens, reasoningTokens} per call but the stored message holds {cost, contextTokens} only (3 assistant messages of the 2.3.0 task, e.g. cost 0.036608, contextTokens 18304). Unit prices still cannot be measured per call; bob_telemetry.py n/a columns stay. web_search would add spend as cost without tokens (flag-gated, not seen).
6. The first user message of a 2.3.0 task has envContext with current_datetime and current_mode (UTC ISO and display name) before git_status_snapshot, keys role, content, envContext, availableTools, _meta, id (same keys as before). availableTools is a 25-id list, same set as 2.2.3. Nothing else in the message shape was found to change; the toolUsage.commandUse structure was not re-diffed (use a real command call on 2.3.0 to confirm, bob_telemetry.py security).
7. Retention: tasks.retentionDays default 30 (settings default object unchanged). cleanupOldTasks(ms) selects tasks with updated_at older than the cutoff, is_pinned = 0, parent_id IS NULL, and now deletes through deleteTaskTrees: WITH RECURSIVE tree over parent_id then DELETE FROM tasks WHERE id IN tree, so descendants at ANY depth are deleted (2.2.3 deleted one level of children then the roots in one transaction). messages and task_pending_approvals go by ON DELETE CASCADE. The call site (startup of the task manager, logs Cleaned up N tasks older than D days) is unchanged. The live database has 18 tasks, oldest created 2026-10-04.
8. The Tool Call Decision telemetry event now also fires for the four always-approved tools (action auto_approved, the same action as every other auto-approved call); no database effect.

SCRIPTS TO RUN COLD AFTER install.sh (parent TASK-17 AC 2): dump_system_prompt.py --task 6cc0a0b9 --list works on 2.3.0 (warns: verified on 2.2.3, schema 011). Task 6cc0a0b9 is the only 2.3.0 task at the time of writing; do not delete it.
<!-- SECTION:NOTES:END -->
