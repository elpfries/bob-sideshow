---
id: TASK-17.3
title: 'Re-verify hooks, rules, plugins and the injected prompt on Bob 2.3.0'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HANDOFF FROM TASK-17.1 (2026-11-02): facts TASK-17.3 must apply (hooks, rules, plugins, prompt, tools, sub-agents). Build 2.3.0 = 1.126.0+bob2.3.0.20261026121409; sources: dist/extension.js, a stored 2.3.0 task (id prefix 6cc0a0b9), changelog. Proof: docs/bob-2.2.3-to-2.3.0.md sections 3 to 5 and private/diff/anchor-details-2.2.3-2.3.0.txt (full line diff of the Configure Hooks skill text is in that file).

HOOKS
1. Nine events: SessionStart, UserPromptSubmit, PreCompact, PostCompact, PreToolUse, PostToolUse, PermissionRequest, PermissionResolved, Stop. The settings default object still lists the first seven only.
2. PermissionRequest / PermissionResolved run only when Bob would show an approval prompt (never for auto-approved or blocked calls); matcher = Bob tool name (regex, like PreToolUse); Bob waits for both. Payload: session_id, cwd, hook_event_name, tool_name, tool_input, tool_use_id; PermissionResolved adds decision = approved | rejected (dismissed prompt counts) | cancelled (task stopped first).
3. PermissionRequest structured answer: hookSpecificOutput {hookEventName: PermissionRequest, decision: {behavior: allow|deny, message (deny only), interrupt (deny only, true also stops the task after the rejection)}}. deny => call rejected, note = message or Rejected by a configured hook. allow => no prompt, EXCEPT when the call needs explicit approval (forbidden groups, security flag, write to the Bob home or .bob/settings.json, outside workspace) where the prompt still opens. allow with updatedInput is ignored with warning Ignoring PermissionRequest allow with updatedInput, which is not supported (rewrite input in PreToolUse). Unknown decision => warning Ignoring invalid PermissionRequest hook decision. The sentence a deny from any handler wins over an allow is the bundled skill text; the merge code was not read.
4. Exit 2 cannot block PermissionRequest/PermissionResolved (hooks cannot block warning), like SessionStart, PostCompact, PostToolUse, Stop. Still blocks UserPromptSubmit, PreToolUse, PreCompact. Other non-zero exits ignored. Unchanged: HTTP handlers, allowedEnvVars, PreToolUse updatedInput / permissionDecision, additionalContext, 10 s default timeout.
5. fileSystems: a matcher group may list URI schemes; default ["file"] so hooks run in LOCAL folders only; remote workspaces get hooks only if the group lists their scheme; in remote workspaces commands run from the home directory and workspace settings files are not read. Check the shipped templates (command-guard.mjs, settings.hooks.json): they work for local folders; mention fileSystems as an option, do not add it by default unless verified.
6. New prompt-visible notice: when a PreToolUse hook rewrote the input (or the user edited it), the tool result begins: Your <tool> call was changed before execution (PreToolUse hook or user edit). Executed values: {...}.
7. Subagents forward the parent onPreToolUse AND now onPreCompact. Whether PermissionRequest fires for subagent calls: not checked.

RULES / PLUGINS / MCP
8. Rule loading unchanged (roots, depth, precedence, preamble). project_rules size 3717 chars in both stored tasks. The TASK-14 plugin ordering control (a plugin with both rules-<mode>/ and rules/) is still untested.
9. MCP config globs: workspace {mcp.json, plugins/*/mcp.json} (as before); global now {settings/mcp.json, plugins/*/mcp.json}, i.e. ~/.bob/plugins/<name>/mcp.json is read (new). Modes already read plugins/*/custom_modes.yaml in both scopes.
10. Plugin installer (marketplace client, flags bob-plugin-service-url and plugins-ui-enabled): installs to .bob/plugins/<name> (workspace) or ~/.bob/plugins/<name> (global); writes mcp.json: stdio servers need a relative command (absolute is skipped), args/env/cwd expand PLUGIN_ROOT and PLUGIN_DATA placeholders (dollar-brace form), remote servers keep url+headers; servers also defined by mcp/*.yaml parameter files are left out and the shipped mcp.json is first renamed mcp.template.json; data dir plugins/.data/<name>.
11. NEW system-prompt section mcp_instructions (id mcpInstructions) after project_rules, before environment_info, in all four prompt configs: preamble Instructions provided by connected MCP servers. Follow them when using that server's tools., one server element per server with name and instructions, each cut at 8 KiB (Server instructions truncated.). Not seen in a stored prompt (the 2.3.0 task had no MCP server): label as read in the bundle, not observed.
12. dump_system_prompt.py splits on tag blocks: mcp_instructions is a new tag to expect; the stored 2.3.0 prompt has the same 12 sections as 2.2.3 (sizes in the page), 35,639 chars, default/aquarius shape.

PROMPT AND CONTEXT
13. Date, time and mode are NOT in the system prompt: the first user message envContext now holds environment_details with current_datetime (UTC ISO string), current_mode (display name, e.g. Agent), then active_file, external_changes, git_status_snapshot. 2.2.3 had only git_status_snapshot in the stored task.
14. Guidance blocks (stored): new read_file block 748 chars (context focus: context_focus_query; emitted only when flag context-focus-query-enabled is on; ON on this installation); office_edit 1009 to 1496; glob 247 to 396; grep 1307 to 1460; create_chart 1235 to 1362; available_skills 9163 to 9641.
15. Tools: the 25 tool ids offered are the same set as the 2.2.3 task. office_edit backs up before first edit, operations restore, save_backup, delete_backup. create_chart takes a stable id (new version on reuse). File tools require absolute paths. web_search exists (group browser, experiments.webSearch default false, registration condition not met by the production IDE as read): say present but gated off, not available. execute_command cwd text now (absolute), omit for workspace root.
16. Sub-agents: spawned agent turn limit = agent maxTurns ?? parent.getMaxTurns() (was ?? 25). The built-in explore preset LOST its maxTurns:50 and inherits the parent (100 default); review agent keeps 30. The general preset 25 now has a source (the ?? 25 in 2.2.3) and is gone in 2.3.0. Update bob-agent-rules and the Subagents block note; the shipped template explore-premium.md should not state a turn count unless it sets maxTurns itself. modelTier validation, forbidden tools, tiers unchanged.
17. Skills: office-insights skill only added when office_read is registered; symlinked skills fix: not located.
<!-- SECTION:NOTES:END -->
