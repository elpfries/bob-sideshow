---
id: TASK-17.2
title: Re-verify the approval and security model on Bob 2.3.0
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HANDOFF FROM TASK-17.1 (2026-11-02): facts TASK-17.2 must apply. Build 2.3.0 = 1.126.0+bob2.3.0.20261026121409, source = dist/extension.js (frozen in private/baseline-2.3.0, compared with the installed app), full proof in docs/bob-2.2.3-to-2.3.0.md sections 1 and 2 and in private/diff/anchor-details-2.2.3-2.3.0.txt.

1. Gate order is UNCHANGED, the code location moved. 2.2.3: chat-side class, onToolCallHandler. 2.3.0: a shared flow class, method resolve: (a) PreToolUse event (onToolWillExecute; cancel returns), (b) seedTaskAllowedMcpTools, (c) engine.validateToolExecution (outside workspace unless allowed; deny list), (d) the four always-approved tools ask_followup_question, start_workflow, create_html_artifact, create_chart, else isAutoApproved (engine.shouldAutoApprove), (e) otherwise askUser (PermissionRequest hook, then the prompt, PermissionResolved hook). The identifier _alwaysAllowedTools no longer exists: cite the four ids and the anchor isAutoApproved instead. The engine methods requiresExplicitApproval, shouldAutoApprove, validateToolExecution, applyApprovalResponse are the same code as 2.2.3 (read side by side). Default approval settings and the 15 default approved commands are identical.

2. New behaviour to document in approvals.md: a call to one of the four always-approved tools is now reported to the Tool Call Decision telemetry event with action auto_approved (the track call runs); in 2.2.3 no telemetry call was made for them, only the auto-approved calls of the other tools were reported.

3. NO yolo-like mode in the IDE 2.3.0. The flow class has an option isApproveAllEnabled (true => auto-approve everything that does not require explicit approval) but the IDE constructs the flow with only registry, telemetry, serializePrompts:true, sourceEnv, permissionHooks; the key has no writer anywhere in extension.js (one occurrence, the reader). Say: present as a code path, not wired in the IDE bundle, not exercised. Do not invent a setting for it. Items to keep from the patch chapter of private/benchmark-harness.md are unaffected but its anchors (onToolCallHandler context) moved.

4. Trust. Same code as 2.2.3: workspaceTrusted = options.workspaceTrusted !== false; untrusted => harness getConfig returns the default config with approval.autoApprovalEnabled=false (security.folderTrust.enabled copied), no workspace rules, skills, modes, agents, hooks, no MCP start. isWorkspaceTrusted is now a real class-method name (the 17.1 MISSING in 2.2.3 was an export name). OPEN, do not state as fact: the IDE approval path reads the IDE global approval settings (getEffectiveApprovalConfig over Br.values.approval), not the harness getConfig, and the approval-config class has an isUntrusted option the IDE does not pass; so where untrusted => no auto-approval is enforced in the IDE is not established on either build. The Safe mode / trust levels strings in en.json are Bob Shell only (zero hits in extension.js): never cite them as IDE behaviour.

5. MCP auto-approval. alwaysAllow of a server definition (isAlwaysAllowed) seeds the task key taskAllowedMcpTools, now at the FIRST tool call of the task (was at task load) and only when the key is undefined. An MCP tool is auto-approved only if permission group mcp is in allowed_permissions AND its id is in taskAllowedMcpTools. The skill text of Configure MCP now says alwaysAllow skips the confirmation prompt while MCP auto-approval is on (the MCP toggle still wins). The en.json string Comma-separated list of tools to auto-approve while MCP auto-approval is on and Automatically approve tool calls when safety rules allow are Shell only. MCP tool annotations (readOnlyHint etc.) are used nowhere in the IDE bundle outside the SDK schema.

6. Security check: a NEW first gate in the function that decides requiresSecurityApproval: a command whose text writes to a path matched by .gitignore or .bobignore patterns (redirection > >>, tee, dd of=, cp/mv target, PowerShell Set-Content/Add-Content/Out-File; paths containing a dollar sign skipped) is flagged dangerous with reason: Command attempts to write to a path blocked by .gitignore or .bobignore. It runs BEFORE the isCommandSecurityEnabled test, so it applies with command security off and costs no model call. Patterns come from the IDE (getIgnorePatterns on the env). The heuristic regexes, the 5000-char head/tail rule with its three tail patterns, the timeout, the {dangerous, reason} schema, fail-closed, and the security tier are unchanged. approval_check.py and approvals.md should mention the new gate; the script cannot know the ignore patterns, so state it as not modelled.

7. File tools now REQUIRE absolute paths (error: path must be an absolute path (e.g. <workspace>/src/file.ts); list_files accepts a dot). Re-check the outside-workspace examples in approvals.md.

8. A PermissionRequest hook can pre-empt the prompt (allow/deny) except for calls that need explicit approval (forbidden groups, security flag, writes to the Bob home, outside workspace): see 17.3 note for the contract.

9. Open items to leave labelled undetermined: web_search tool (gated by experiments.webSearch default false and, as read, a host condition the production IDE does not meet; permission group browser); the webview approval dialog was not diffed (77 logical webview files changed); token matcher body is unchanged text-wise (engine side read).
<!-- SECTION:NOTES:END -->
