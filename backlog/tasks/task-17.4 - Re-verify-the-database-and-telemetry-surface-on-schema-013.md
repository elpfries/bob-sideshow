---
id: TASK-17.4
title: Re-verify the database and telemetry surface on schema 013
status: To Do
assignee: []
created_date: '2026-11-02 22:51'
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
