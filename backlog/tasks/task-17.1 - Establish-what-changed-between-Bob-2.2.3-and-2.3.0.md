---
id: TASK-17.1
title: Establish what changed between Bob 2.2.3 and 2.3.0
status: To Do
assignee: []
created_date: '2026-11-02 22:51'
labels:
  - 'model:secondaire'
milestone: m-2
dependencies: []
parent_task_id: TASK-17
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Before any note is rewritten, the delta has to be stated subject by subject, with each item classed as behaviour change, cosmetic/bundling artefact, or undetermined, the way docs/bob-2.1.0-to-2.2.0.md did for the previous jump. This task turns the step 3-5 raw outputs into that page and completes the 2.3.0 baseline.

Shared facts (session of 2026-11-02): Bob installed = 2.3.0, build 1.126.0+bob2.3.0.20261026121409, extension.js sha1 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (10 911 633 bytes), product.json commit b48bf62595b330a56b628a82441207f506fbc6a4, schema 013_workspace_editor_sessions (migrations 012_task_editor_sessions and 013_workspace_editor_sessions new). The outgoing baseline is private/baseline-2.2.3/ (complete, webview included); the new one is frozen in private/baseline-2.3.0/ (four files + web/assets with web-assets.sha256, README still to write) and extracted in private/diff/2.3.0/; the 2.2.3 extraction is private/diff/2.2.1/ (byte-identical bundle). Step-3 verdicts already run: private/diff/anchors-verdicts-2.2.3-2.3.0.txt (102 anchors: 11 CHANGED, 1 MISSING in B = _alwaysAllowedTools, 1 MISSING in A = isWorkspaceTrusted, hook-runner string EDITED 13359 -> 16390 chars). Step-4 delta: private/diff/compare-2.2.3-2.3.0.txt (+723 strings, +704 props, 751 strings added, 152 removed). Public changelog read 2026-11-02 at https://bob.ibm.com/docs/ide/changelog (2.3.0, October 2026; no version between 2.2.3 and 2.3.0). A real task run by 2.3.0 exists in ~/.bob/db/bob.db: id 6cc0a0b9..., title QUOI de neuf bob?, 7 messages, 3 priced calls (2026-11-02 22:45 UTC). Method and procedure: private/SOURCES.md (Re-verifying on a new build, 8 steps; durable-anchor rule). Model milestone: m-1 (TASK-13.x, TASK-14). AGENTS.md rules bind every task: state the build and source of every fact, scripts stay Python 3.8+ stdlib read-only offline, five identical _bobcheck.py copies, no personal data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 private/baseline-2.3.0/README.md exists on the model of baseline-2.2.3, with build identity, file hashes checked against the installed app, the public changelog summary and a pointer to private/diff/2.3.0/
- [ ] #2 Every CHANGED and MISSING anchor of private/diff/anchors-verdicts-2.2.3-2.3.0.txt is resolved with bundle_diff.py anchor into a one-sentence fact (or a reclassification such as renamed), and every bob-tagged or bob-relevant added/removed string group of the compare output is either explained or listed as undetermined
- [ ] #3 docs/bob-2.2.3-to-2.3.0.md is published: per subject (approval engine and auto-approval, folder trust, hooks, rules/plugins/MCP, system prompt and tools, settings, database, UI/commands), what changed, its evidence anchor, and which bob-sideshow skill or note it affects; every claim states build 2.3.0 and its source
- [ ] #4 The anchor lists private/diff/landmarks.txt, private/diff/anchors.txt and private/bundle_tools.py LANDMARKS are updated for 2.3.0 (dead entries removed or replaced by durable literals, new subjects anchored) and python3 private/bundle_tools.py --landmarks reports all present on 2.3.0
- [ ] #5 Downstream tasks TASK-17.2, TASK-17.3 and TASK-17.4 receive in their notes the exact facts each must apply
<!-- AC:END -->
