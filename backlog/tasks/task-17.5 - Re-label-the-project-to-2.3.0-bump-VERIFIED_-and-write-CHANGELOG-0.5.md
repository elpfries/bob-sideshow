---
id: TASK-17.5
title: 'Re-label the project to 2.3.0, bump VERIFIED_* and write CHANGELOG 0.5'
status: To Do
assignee: []
created_date: '2026-11-02 22:51'
updated_date: '2026-11-02 23:23'
labels:
  - 'model:secondaire'
milestone: m-2
dependencies:
  - TASK-17.2
  - TASK-17.3
  - TASK-17.4
parent_task_id: TASK-17
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Last step, only once TASK-17.1 to 17.4 have re-read the facts: bump VERIFIED_EXTENSION to 2.3.0 and VERIFIED_SCHEMA to 013_workspace_editor_sessions in the five identical _bobcheck.py copies, restate the build in every published file where the fact was re-checked (keep earlier labels where it was not), update README and the comparison docs build lines, and write a dated CHANGELOG 0.5 section on the model of 0.3. Model: TASK-13.3 and TASK-16.2. The release itself (tag v0.5, gh release) follows the AGENTS.md rule and is done by the orchestrating session after this task.

Shared facts (session of 2026-11-02): Bob installed = 2.3.0, build 1.126.0+bob2.3.0.20261026121409, extension.js sha1 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (10 911 633 bytes), product.json commit b48bf62595b330a56b628a82441207f506fbc6a4, schema 013_workspace_editor_sessions (migrations 012_task_editor_sessions and 013_workspace_editor_sessions new). The outgoing baseline is private/baseline-2.2.3/ (complete, webview included); the new one is frozen in private/baseline-2.3.0/ (four files + web/assets with web-assets.sha256, README still to write) and extracted in private/diff/2.3.0/; the 2.2.3 extraction is private/diff/2.2.1/ (byte-identical bundle). Step-3 verdicts already run: private/diff/anchors-verdicts-2.2.3-2.3.0.txt (102 anchors: 11 CHANGED, 1 MISSING in B = _alwaysAllowedTools, 1 MISSING in A = isWorkspaceTrusted, hook-runner string EDITED 13359 -> 16390 chars). Step-4 delta: private/diff/compare-2.2.3-2.3.0.txt (+723 strings, +704 props, 751 strings added, 152 removed). Public changelog read 2026-11-02 at https://bob.ibm.com/docs/ide/changelog (2.3.0, October 2026; no version between 2.2.3 and 2.3.0). A real task run by 2.3.0 exists in ~/.bob/db/bob.db: id 6cc0a0b9..., title QUOI de neuf bob?, 7 messages, 3 priced calls (2026-11-02 22:45 UTC). Method and procedure: private/SOURCES.md (Re-verifying on a new build, 8 steps; durable-anchor rule). Model milestone: m-1 (TASK-13.x, TASK-14). AGENTS.md rules bind every task: state the build and source of every fact, scripts stay Python 3.8+ stdlib read-only offline, five identical _bobcheck.py copies, no personal data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 VERIFIED_EXTENSION is 2.3.0 and VERIFIED_SCHEMA is 013_workspace_editor_sessions in all five copies, and shasum skills/*/scripts/_bobcheck.py shows one hash
- [ ] #2 No shipped script prints a version or schema mismatch warning on the 2.3.0 installation (all five run)
- [ ] #3 No published file claims 2.2.3 verification for a fact re-checked on 2.3.0, and facts not re-checked keep their earlier build label
- [ ] #4 CHANGELOG has a dated 0.5 section stating what changed in Bob between 2.2.3 and 2.3.0 that matters to bob-sideshow, and what changed in bob-sideshow
- [ ] #5 python3 -m py_compile skills/*/scripts/*.py and node --check skills/bob-override-rules/templates/hooks/command-guard.mjs pass; ./install.sh then every installed script runs clean from ~/.bob/skills
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HANDOFF FROM TASK-17.2 (2026-11-03), for the label bump. Build verified: 1.126.0+bob2.3.0.20261026121409, source dist/extension.js plus webview and db read-only.
Labelled 2.3.0 in skills/bob-security-model: reference/approvals.md (all of it except the items below), the docstring of scripts/approval_check.py, the header line of SKILL.md. The script still prints the verified-on-2.2.3 warning because _bobcheck.py and VERIFIED_* are untouched; after your bump it should print nothing on 2.3.0 (re-run: python3 skills/bob-security-model/scripts/approval_check.py 'git status').
Kept with an earlier label or undetermined, with reason: (a) approval dialog and settings screens: only webview string presence checked on 2.3.0, behaviour last read on 2.2.0, 77 logical webview files changed and not diffed; (b) where an untrusted folder switches off auto-approval in the IDE: undetermined on 2.2.3 and 2.3.0; (c) web_search registration in the production IDE: undetermined, not exercised; (d) merge of several PermissionRequest handlers and firing for subagents: undetermined; (e) inputs that make the tree-sitter parser fail: not enumerated; (f) whether execute_command ever counts as outside the workspace: not established.
Corrected a pre-existing error: the PreToolUse hook runs first (before the security check and the approval flow), also on 2.2.3; approvals.md used to say after the security check. Worth a look in bob-override-rules (TASK-17.3) and in the command-guard.mjs header if either repeats the old order (I found no other occurrence of the sentence in skills/ docs/ README.md).
Out of scope, noticed: docs/codex-vs-bob.md line 75 says a Codex flag is Bob's yolo; a reader could take it for an IBM Bob IDE setting (the IDE has none).
approval_check.py gained --workspace and an approximated ignored-path write gate; if you change the CHANGELOG or README wording about the script, say approximation.
<!-- SECTION:NOTES:END -->
