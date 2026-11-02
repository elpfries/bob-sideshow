---
id: TASK-17.2
title: Re-verify the approval and security model on Bob 2.3.0
status: To Do
assignee: []
created_date: '2026-11-02 22:51'
labels:
  - 'model:secondaire'
milestone: m-2
dependencies:
  - TASK-17.1
parent_task_id: TASK-17
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
bob-security-model (reference/approvals.md, scripts/approval_check.py) describes the approval gates, matcher, security check and auto-approval settings. On 2.3.0 the gate function validateToolExecution was rewritten (similarity 0.53), _alwaysAllowedTools is gone, shouldAutoApprove changed, folder trust became trust levels with a safe mode, MCP auto-approval gained its own list, and new UI strings speak of automatically approving tool calls when safety rules allow. Every claim of the note and the behaviour of approval_check.py must be re-read against 2.3.0. The note section titled Yolo in the IDE must state plainly whether a yolo-like mode exists on 2.3.0 and must not present the closest settings block as if it were one (a reader was misled into believing a yolo setting exists in the approval block).

Shared facts (session of 2026-11-02): Bob installed = 2.3.0, build 1.126.0+bob2.3.0.20261026121409, extension.js sha1 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (10 911 633 bytes), product.json commit b48bf62595b330a56b628a82441207f506fbc6a4, schema 013_workspace_editor_sessions (migrations 012_task_editor_sessions and 013_workspace_editor_sessions new). The outgoing baseline is private/baseline-2.2.3/ (complete, webview included); the new one is frozen in private/baseline-2.3.0/ (four files + web/assets with web-assets.sha256, README still to write) and extracted in private/diff/2.3.0/; the 2.2.3 extraction is private/diff/2.2.1/ (byte-identical bundle). Step-3 verdicts already run: private/diff/anchors-verdicts-2.2.3-2.3.0.txt (102 anchors: 11 CHANGED, 1 MISSING in B = _alwaysAllowedTools, 1 MISSING in A = isWorkspaceTrusted, hook-runner string EDITED 13359 -> 16390 chars). Step-4 delta: private/diff/compare-2.2.3-2.3.0.txt (+723 strings, +704 props, 751 strings added, 152 removed). Public changelog read 2026-11-02 at https://bob.ibm.com/docs/ide/changelog (2.3.0, October 2026; no version between 2.2.3 and 2.3.0). A real task run by 2.3.0 exists in ~/.bob/db/bob.db: id 6cc0a0b9..., title QUOI de neuf bob?, 7 messages, 3 priced calls (2026-11-02 22:45 UTC). Method and procedure: private/SOURCES.md (Re-verifying on a new build, 8 steps; durable-anchor rule). Model milestone: m-1 (TASK-13.x, TASK-14). AGENTS.md rules bind every task: state the build and source of every fact, scripts stay Python 3.8+ stdlib read-only offline, five identical _bobcheck.py copies, no personal data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every claim of skills/bob-security-model/reference/approvals.md is re-checked on 2.3.0 with a durable anchor; changed facts are rewritten with build and source, unchanged ones relabelled 2.3.0, unverifiable ones keep their earlier label
- [ ] #2 approval_check.py reproduces 2.3.0's matcher and gate order; it is run against the real installation on at least five commands covering allow, deny, prompt, heuristic flag and unverifiable, and its output is compared with what 2.3.0's code decides
- [ ] #3 The yolo section states first whether a yolo-like mode exists on 2.3.0, lists the keys the approval block accepts, and labels the most-permissive configuration as such with what still prompts
- [ ] #4 SKILL.md of bob-security-model still matches what the note and script say
<!-- AC:END -->
