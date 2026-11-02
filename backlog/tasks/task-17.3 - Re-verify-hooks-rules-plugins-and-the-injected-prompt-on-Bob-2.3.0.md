---
id: TASK-17.3
title: 'Re-verify hooks, rules, plugins and the injected prompt on Bob 2.3.0'
status: To Do
assignee: []
created_date: '2026-11-02 22:51'
labels:
  - 'model:secondaire'
milestone: m-2
dependencies:
  - TASK-17.1
parent_task_id: TASK-17
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
bob-override-rules (rule_locations.py, templates incl. hooks/command-guard.mjs) and bob-agent-rules (reference/injected-rules.md, command-migration.md, dump_system_prompt.py) describe the hook contract, rule roots and precedence, plugins, and how the system prompt is assembled. 2.3.0 adds PermissionRequest and PermissionResolved hook events, runs hooks in remote workspaces, adds plugin mcp.json and a global plugin dir ~/.bob/plugins/<name>/, changes plugin skills enable state, forwards MCP server instructions and the live date and active mode into the prompt, adds a web search tool and makes subagent turn limits inherit from the parent. The installed templates must still work on 2.3.0.

Shared facts (session of 2026-11-02): Bob installed = 2.3.0, build 1.126.0+bob2.3.0.20261026121409, extension.js sha1 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (10 911 633 bytes), product.json commit b48bf62595b330a56b628a82441207f506fbc6a4, schema 013_workspace_editor_sessions (migrations 012_task_editor_sessions and 013_workspace_editor_sessions new). The outgoing baseline is private/baseline-2.2.3/ (complete, webview included); the new one is frozen in private/baseline-2.3.0/ (four files + web/assets with web-assets.sha256, README still to write) and extracted in private/diff/2.3.0/; the 2.2.3 extraction is private/diff/2.2.1/ (byte-identical bundle). Step-3 verdicts already run: private/diff/anchors-verdicts-2.2.3-2.3.0.txt (102 anchors: 11 CHANGED, 1 MISSING in B = _alwaysAllowedTools, 1 MISSING in A = isWorkspaceTrusted, hook-runner string EDITED 13359 -> 16390 chars). Step-4 delta: private/diff/compare-2.2.3-2.3.0.txt (+723 strings, +704 props, 751 strings added, 152 removed). Public changelog read 2026-11-02 at https://bob.ibm.com/docs/ide/changelog (2.3.0, October 2026; no version between 2.2.3 and 2.3.0). A real task run by 2.3.0 exists in ~/.bob/db/bob.db: id 6cc0a0b9..., title QUOI de neuf bob?, 7 messages, 3 priced calls (2026-11-02 22:45 UTC). Method and procedure: private/SOURCES.md (Re-verifying on a new build, 8 steps; durable-anchor rule). Model milestone: m-1 (TASK-13.x, TASK-14). AGENTS.md rules bind every task: state the build and source of every fact, scripts stay Python 3.8+ stdlib read-only offline, five identical _bobcheck.py copies, no personal data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The hook contract in the notes (events, exit codes, JSON output, handler types) is re-checked on 2.3.0 and the two new events are documented with their stdin and blocking semantics, from the bundle
- [ ] #2 command-guard.mjs is exercised on 2.3.0 (a real Bob task where the hook blocks a command, or the hook runner invoked as Bob invokes it) and node --check passes
- [ ] #3 rule_locations.py lists 2.3.0's rule and plugin roots in 2.3.0's order and states folder-trust behaviour as 2.3.0 implements it; run against the real installation
- [ ] #4 injected-rules.md and command-migration.md are re-checked on 2.3.0 (prompt sections, rule tags, new MCP instructions, date and mode context, subagent limits, tool set); dump_system_prompt.py --list runs on the real 2.3.0 task and its sections match the note
<!-- AC:END -->
