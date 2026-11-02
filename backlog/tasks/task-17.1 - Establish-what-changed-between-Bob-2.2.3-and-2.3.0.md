---
id: TASK-17.1
title: Establish what changed between Bob 2.2.3 and 2.3.0
status: Done
assignee:
  - '@claude'
created_date: '2026-11-02 22:51'
updated_date: '2026-11-02 23:12'
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
- [x] #1 private/baseline-2.3.0/README.md exists on the model of baseline-2.2.3, with build identity, file hashes checked against the installed app, the public changelog summary and a pointer to private/diff/2.3.0/
- [x] #2 Every CHANGED and MISSING anchor of private/diff/anchors-verdicts-2.2.3-2.3.0.txt is resolved with bundle_diff.py anchor into a one-sentence fact (or a reclassification such as renamed), and every bob-tagged or bob-relevant added/removed string group of the compare output is either explained or listed as undetermined
- [x] #3 docs/bob-2.2.3-to-2.3.0.md is published: per subject (approval engine and auto-approval, folder trust, hooks, rules/plugins/MCP, system prompt and tools, settings, database, UI/commands), what changed, its evidence anchor, and which bob-sideshow skill or note it affects; every claim states build 2.3.0 and its source
- [x] #4 The anchor lists private/diff/landmarks.txt, private/diff/anchors.txt and private/bundle_tools.py LANDMARKS are updated for 2.3.0 (dead entries removed or replaced by durable literals, new subjects anchored) and python3 private/bundle_tools.py --landmarks reports all present on 2.3.0
- [x] #5 Downstream tasks TASK-17.2, TASK-17.3 and TASK-17.4 receive in their notes the exact facts each must apply
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verify baseline-2.3.0 (cmp and shasum -c against the installed app), compare the webview lists, write its README (AC1).
2. Resolve every CHANGED/MISSING anchor with bundle_diff.py anchor plus direct reads of the bundle; group and explain the compare output; keep raw outputs in private/diff/anchor-details-2.2.3-2.3.0.txt (AC2).
3. Write docs/bob-2.2.3-to-2.3.0.md on the model of the 2.1.0-to-2.2.0 page, one durable anchor per fact, class and affected skill per row; add one line to the older page; re-read against the every-sentence-has-an-anchor-or-source rule (AC3).
4. Update landmarks.txt, anchors.txt, LANDMARKS in bundle_tools.py and SOURCES.md; prove with bundle_tools.py --landmarks and bundle_diff.py anchors (AC4).
5. Append per-task handoff notes to TASK-17.2, 17.3, 17.4 (AC5); py_compile private/*.py; commit and push.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
PROOF PER CRITERION (2026-11-02, 2.3.0 = 1.126.0+bob2.3.0.20261026121409)

AC1. private/baseline-2.3.0/README.md written. Hashes recomputed on the files of the folder and compared with the installed app: cmp on extension.js, product.json, package.json, en.json and the six web/*.html = 10/10 IDENTICAL; shasum -a 256 -c web-assets.sha256 run inside the installed dist/web/assets = 690/690 OK; CFBundleVersion read with PlistBuddy. Webview list: the brief said 690 vs 691, the real order is 691 (2.2.3) then 690 (2.3.0), 28,378,082 bytes vs 27,970,512; 611 files identical, 80 names only in 2.2.3, 79 only in 2.3.0; by logical name 3 removed (PolicyLockIndicator, square-pen, user-pen), 2 added (findingGrouping, workspaceDisplay), 77 with different content. web-assets.sha256 sits inside assets/ (the 2.2.3 README says alongside; same layout as here).

AC2. Every CHANGED/MISSING anchor of anchors-verdicts-2.2.3-2.3.0.txt resolved by bundle_diff.py anchor plus direct reads; raw outputs in private/diff/anchor-details-2.2.3-2.3.0.txt (anchor diffs, the line diff of the hooks skill text, about 60 bundle excerpts, DB and flag facts, en.json and manifest deltas). Key resolutions: validateToolExecution CHANGED = the caller moved into a shared flow class (engine text identical); _alwaysAllowedTools = module constant, same four ids; isWorkspaceTrusted = export name in 2.2.3, class method in 2.3.0; hooks cannot block / PostCompact / Ignoring invalid PreToolUse hook output (one unit) = PermissionRequest and PermissionResolved added to the cannot-block list; maxTurns = persistTaskError id only, the real change is subagent maxTurns inherited and the explore preset losing maxTurns:50; SUBAGENT_FORBIDDEN_TOOLS = turn default and onPreCompact forwarding; chatWidth = pinnedModels added to chat defaults; Compaction skipped = observation masking branch; explorer = revealInExplorer takes a Uri; Extension activated = 24 activate() edits; hook-runner string 13359 to 16390 = nine events, permission events, fileSystems. Compare groups: all 11 bob-tagged strings and all 7 added bob-tagged props are explained in the page; the other families (plugins, git/reflog, LSP, OTEL, yaml/glob/lru libraries, PowerShell launcher) are explained or listed undetermined in sections 4 to 8. Two findings the anchor list did NOT flag: the new ignore-file write gate in the command security check, and absolute-path validation in file tools.

AC3. docs/bob-2.2.3-to-2.3.0.md published (9 sections as ordered by the brief, classes behaviour/artefact/undetermined, a Touches column naming the skill or note, source tags bundle/db/webview/en.json/manifest/changelog/stored prompt on every row). Re-read sentence by sentence against the rule every sentence has an anchor or a source: 15 corrections made (eleven vs twelve call sites, eleven vs ten sections, plugin template wording, an unverified library count removed, a personal task title removed, the 25-turn source dated to 2.2.3, the Lh call-site list, the observation-masking budget, others). Heuristics and security-tier claims re-verified by diffing the functions in both builds. One line added to the Re-checking section of docs/bob-2.1.0-to-2.2.0.md. No other published file touched.

AC4. landmarks: LANDMARKS in bundle_tools.py now 66 (46 minus _alwaysAllowedTools plus 21: isAutoApproved, seedTaskAllowedMcpTools, isApproveAllEnabled, isWorkspaceTrusted, Command attempts to write to a path blocked by, PermissionRequest, PermissionResolved, Ignoring invalid PermissionRequest hook decision, fileSystems, web_search, webSearch, path must be an absolute path, current_datetime, Instructions provided by connected MCP servers, pinnedTeams, observationMaskingEnabled, OtelConfiguration, mcp.template.json, PLUGIN_ROOT, 012_task_editor_sessions, 013_workspace_editor_sessions). Proof: python3 private/bundle_tools.py --landmarks = 66/66 present on the installed 2.3.0; bundle_diff.py anchors on landmarks.txt (65 lines; PLUGIN_ROOT sits in a regex literal the tokenizer cannot see, documented in the file header) = 0 MISSING in B, 17 MISSING in A (new subjects); anchors.txt gets 27 new literals and _alwaysAllowedTools replaced by isAutoApproved (129 anchors, 18 MISSING in B/both, all known 2.1.0-era export names or removed features); SOURCES.md Landmarks section and a new Verdicts 2.2.3 to 2.3.0 section updated. python3 -m py_compile private/*.py and skills/*/scripts/*.py pass; the five _bobcheck.py copies still share one hash.

AC5. Handoff notes appended to TASK-17.2 (approvals, trust, MCP auto-approval, no yolo-like mode wired in the IDE bundle, ignore-file gate, absolute paths), TASK-17.3 (nine hook events and the PermissionRequest contract, fileSystems, plugin mcp.json and installer, mcp_instructions section, environment_details date and mode, guidance blocks, subagent turn inheritance) and TASK-17.4 (migrations 012 and 013 with the exact SQL, flags, _meta.spend shape, recursive retention delete, telemetry effect). Verified present by reading the three tasks back.

NOT PROVEN / LEFT UNDETERMINED (stated in the page): where untrusted folder switches off auto-approval in the IDE; web_search registration in the production IDE (as read it is not registered; not exercised); the webview approval dialog (77 logical files changed, not diffed); merge rule of several PermissionRequest handlers (only the skill text); who writes editorSession key_value_store rows; the activate() returned API; subagent PermissionRequest; tool annotations (SDK schema only); symbolic-link skills and the execute_command hang fix (no literal).

Correction to the AC3 line above: the delta part of the page has 8 numbered sections (approval engine and auto-approval, folder trust, hooks, rules/plugins/MCP, system prompt and tools, settings, database, UI/commands/activation), not 9; and the number of review corrections was about a dozen, not an exact 15.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Established the Bob 2.2.3 to 2.3.0 delta. Wrote private/baseline-2.3.0/README.md (hashes recomputed and compared with the installed app: cmp 10/10, shasum -c 690/690; webview 691 to 690 files, 3 logical files removed, 2 added, 77 changed). Resolved every CHANGED/MISSING anchor with bundle_diff.py anchor and direct bundle reads (raw outputs in private/diff/anchor-details-2.2.3-2.3.0.txt). Published docs/bob-2.2.3-to-2.3.0.md (8 delta sections, class and affected skill per row, source tag per row) and linked it from docs/bob-2.1.0-to-2.2.0.md. Main findings: the approval gates keep their order but moved into a shared flow class (no approve-all mode wired in the IDE); a new command-security gate for writes to .gitignore/.bobignore paths; file tools require absolute paths; nine hook events with a PermissionRequest decision contract and per-file-system matcher groups; mcp_instructions prompt section and plugin/global mcp.json; date and mode in the user-message context; explore preset inherits turn limits; migrations 012/013 (no new table) and recursive task retention delete. Updated landmarks.txt, anchors.txt, LANDMARKS (66) and SOURCES.md: bundle_tools.py --landmarks 66/66, anchors on landmarks.txt 0 MISSING in B, py_compile private and skills OK. Handoff notes appended to TASK-17.2, 17.3 and 17.4. Left undetermined and stated in the page: untrusted-folder effect on IDE auto-approval, web_search registration in the production IDE, the webview approval dialog, the PermissionRequest merge rule, writers of editorSession rows.
<!-- SECTION:FINAL_SUMMARY:END -->
