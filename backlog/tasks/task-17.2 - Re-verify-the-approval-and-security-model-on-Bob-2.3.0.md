---
id: TASK-17.2
title: Re-verify the approval and security model on Bob 2.3.0
status: Done
assignee:
  - '@claude'
created_date: '2026-11-02 22:51'
updated_date: '2026-11-02 23:24'
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
- [x] #1 Every claim of skills/bob-security-model/reference/approvals.md is re-checked on 2.3.0 with a durable anchor; changed facts are rewritten with build and source, unchanged ones relabelled 2.3.0, unverifiable ones keep their earlier label
- [x] #2 approval_check.py reproduces 2.3.0's matcher and gate order; it is run against the real installation on at least five commands covering allow, deny, prompt, heuristic flag and unverifiable, and its output is compared with what 2.3.0's code decides
- [x] #3 The yolo section states first whether a yolo-like mode exists on 2.3.0, lists the keys the approval block accepts, and labels the most-permissive configuration as such with what still prompts
- [x] #4 SKILL.md of bob-security-model still matches what the note and script say
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Re-read approvals.md claim by claim on 2.3.0 with durable anchors (bundle_diff anchors + direct reads). 2. Rewrite approvals.md (build and source per fact, new ignored-path gate, no-yolo section restructured). 3. Update approval_check.py (2.3.0, ignored-path gate as documented approximation) and SKILL.md. 4. Run the script on the real installation (allow, deny, prompt, heuristic, unverifiable, ignored-path write). 5. Notes with proof per criterion, handoff to TASK-17.5, commit and push.
<!-- SECTION:PLAN:END -->

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

PROOF PER CRITERION (2026-11-03, Bob 2.3.0 = 1.126.0+bob2.3.0.20261026121409; source = dist/extension.js, identical to the frozen private/baseline-2.3.0 copy, cmp checked; webview and db read-only)

=== AC1: claim -> anchor -> verdict (approvals.md re-read claim by claim on 2.3.0) ===
Verdicts come from bundle_diff.py anchors (2.2.3 vs 2.3.0, file of 41 literals, raw output below) plus direct reads of the 2.3.0 bundle by a small script on the frozen copy.
1. Gate order requiresExplicitApproval / shouldAutoApprove / validateToolExecution -> anchors of those names -> bodies equal as text; shouldAutoApprove CHANGED 2 edits = neighbouring waitUntilAutoApproved; validateToolExecution CHANGED 29 edits = caller moved into a shared flow class (method resolve) -> 2.3.0 CONFIRMED, location rewritten.
2. Four always-approved tools (ex _alwaysAllowedTools) -> anchor isAutoApproved (MISSING in 2.2.3), constant list of 4 ids read -> CHANGED: identifier gone, list same; new telemetry action auto_approved -> REWRITTEN.
3. Master toggle, forbiddenApprovalGroups, allowed_permissions -> anchors autoApprovalEnabled/forbiddenApprovalGroups, group registry read -> CONFIRMED; CORRECTED: the group list omitted browser (registered, non-hidden on 2.2.3 and 2.3.0); added the org policy DisabledAutoApprovalGroups (same key).
4. isBuiltinSkill step (new line in the note) -> anchor isBuiltinSkill IDENTICAL -> ADDED.
5. Outside workspace (permissionOptions + outsideWorkspaceAllowed) -> validateToolExecution note text SAME string; webview settings rows for read and edit -> CONFIRMED; ADDED: file tools require absolute paths (anchor path must be an absolute path, MISSING in 2.2.3); ADDED from the commandVariants CHANGED unit (6 edits): user-attached files are not counted as outside.
6. Shell rule: every sub-command allow against global + task approvals -> shouldAutoApprove read -> CONFIRMED.
7. MCP rule -> REWRITTEN: group mcp allowed AND id in taskAllowedMcpTools; alwaysAllow seeded at the first tool call (seedTaskAllowedMcpTools, CHANGED 20 edits, was at task load) only while undefined.
8. Per-task keys -> Wte list of 4 keys read in the approval-config class; db tasks.approval_config exists (schema 013) and older rows carry more keys -> CONFIRMED + nuance added.
9. Token matcher and tie rule -> GFe/jtr read in 2.3.0 -> identical to 2.2.0 snippet modulo names -> CONFIRMED, snippet relabelled.
10. Six-row matcher table -> follows from 9 -> CONFIRMED.
11. Default 15 approved commands -> defaults array read, equal -> CONFIRMED. Always approve offers full text or first word, writes to task -> HEr (commandVariants) and applyApprovalResponse (IDENTICAL) -> CONFIRMED.
12. unverifiable -> object literal {commands, unverifiable: n.length===0, ...} read -> CONFIRMED; what makes the parser fail not enumerated (kept as such).
13. isBobHomeWrite -> anchor IDENTICAL; regex and ~/.bob / workspace .bob/settings.json path tests read -> CONFIRMED.
14. Security check heuristics (5 groups), 5000 head/tail + 3 tail patterns, schema, 15 s timeout, fail-closed -> functions read side by side, requiresSecurityApproval IDENTICAL, Command is too complex SAME -> CONFIRMED.
15. NEW first gate: write to ignored path -> anchor Command attempts to write to a path blocked by (MISSING in 2.2.3); functions jEr, UEr, regex table, getIgnorePatterns -> getUserExcludePatterns read -> ADDED with build and source.
16. isCommandSecurityEnabled / flag command-security-enabled (default true in the bundle, webview condition featureFlags.command-security-enabled) -> CONFIRMED.
17. Model tier security, router POST, fallback premium-ide, prompt split -> resolveModelForTier IDENTICAL, kxr security constant, Command to analyze SAME -> CONFIRMED unchanged.
18. Effects (Security warning banner, I understand the risk, Configure security verification, always approve hidden) -> webview strings present on 2.3.0 -> LABEL KEPT for behaviour (presence only, dialog not diffed). commandUse stored in messages.data.toolUsage -> db rows show keys unverifiable, commands, requiresSecurityApproval, commandVariants -> CONFIRMED.
19. Yolo section -> env names BOB_DEV_KEY / BOB_SUPPORT_KEY / BOB_USE_MODEL_ENV read, 0 occurrences of yolo in extension.js, 1 of isApproveAllEnabled (reader only) -> REWRITTEN (AC3).
20. Defaults object (autoApprovalEnabled true, outsideWorkspaceAllowed false, allowed_permissions [read], permissionOptions [], allowedExecutors one entry, editApprovalPreviewMode editor, forbiddenApprovalGroups []) -> defaults literal read -> CONFIRMED; isCommandSecurityEnabled default true per the 17.1 page.
21. Hooks PreToolUse contract (stdin fields, exit 2, stderr then stdout, 10 s, 1 MB, JSON output) -> hook runner function read (Ufi=10, jfi=1MB, exit-2 list) -> CONFIRMED; set is now 9 events, exit 2 cannot block PermissionRequest/PermissionResolved, fileSystems -> REWRITTEN. CORRECTED an error older than 2.3.0: the note said the hook runs after Bob's own security check; in the 2.3.0 tool-execution function (and in 2.2.3 P2r) onPreToolUse runs first, then the security check, then the approval flow.
22. PermissionRequest hook contract -> promptWithHooks and Yfi read -> ADDED (merge rule of several handlers and subagent firing stay undetermined).
23. Custom mode restrictions only fileRegex -> anchor restrictions IDENTICAL, tool-call code tests fileRegex -> CONFIRMED.
24. Docs vs bundle bullets -> settings UI: webview has no literal for folderTrust / disableGlobalHooks; forbiddenApprovalGroups appears (UI reads it) -> CONFIRMED as string presence only.
25. Folder trust (new section) -> workspaceTrusted getter, getConfig default config with autoApprovalEnabled false -> same code as 2.2.3; enforcement point in the IDE stays UNDETERMINED (isUntrusted option not passed), Bob Shell Safe mode texts excluded.
Unverified / label kept: approval dialog behaviour and settings screens (webview not diffed), web_search registration, tree-sitter parse-failure inputs, PermissionRequest merge rule.
Count: about 22 claims confirmed or rewritten with 2.3.0 label, 4 corrected (browser group, hook order, MCP rule, absolute paths), 3 added (ignored-path gate, isBuiltinSkill, PermissionRequest), 4 left with earlier label or undetermined.

Anchor run (bundle_diff.py anchors, 2.2.3 -> 2.3.0), raw:
'shouldAutoApprove'                                                        CHANGED: 2 real edit(s) + 1 interop artefacts, similarity 0.77, 55 → 59 tokens
'requiresExplicitApproval'                                                 IDENTICAL after neutralising identifiers (187 tokens)
'validateToolExecution'                                                    CHANGED: 29 real edit(s) + 3 interop artefacts, similarity 0.53, 352 → 276 tokens
'applyApprovalResponse'                                                    IDENTICAL after neutralising identifiers (63 tokens)
'isAutoApproved'                                                           MISSING in A
'seedTaskAllowedMcpTools'                                                  CHANGED: 20 real edit(s) + 0 interop artefacts, similarity 0.17, 196 → 276 tokens
'isApproveAllEnabled'                                                      MISSING in A
'isBuiltinSkill'                                                           IDENTICAL after neutralising identifiers (187 tokens)
'getEffectiveApprovalConfig'                                               IDENTICAL after neutralising identifiers (220 tokens)
'requiresSecurityApproval'                                                 IDENTICAL after neutralising identifiers (55 tokens)
'isBobHomeWrite'                                                           IDENTICAL after neutralising identifiers (65 tokens)
'Command attempts to write to a path blocked by .gitignore or .bobignore.' MISSING in A
'Tools are blocked from working outside of the current workspace'          SAME top-level string (205 chars); neighbours not compared
'Attempted to execute commands that are on the deny list'                  SAME top-level string (57 chars); neighbours not compared
'Command is too complex and needs manual verification.'                    SAME top-level string (53 chars); neighbours not compared
'Command to analyze'                                                       SAME top-level string (86 chars); neighbours not compared
'resolveModelForTier'                                                      IDENTICAL after neutralising identifiers (62 tokens)
'getIgnorePatterns'                                                        SAME LOGIC: 1 CJS→ESM interop artefacts only (106 → 108 tokens)
'getUserExcludePatterns'                                                   IDENTICAL after neutralising identifiers (11 tokens)
'respectGitIgnore'                                                         IDENTICAL after neutralising identifiers (63 tokens)
'taskAllowedMcpTools'                                                      SAME top-level string (19 chars); neighbours not compared
'taskCommandApprovals'                                                     SAME top-level string (20 chars); neighbours not compared
'forbiddenApprovalGroups'                                                  SAME top-level string (23 chars); neighbours not compared
'DisabledAutoApprovalGroups'                                               SAME top-level string (26 chars); neighbours not compared
'BOB_DEV_KEY'                                                              IDENTICAL after neutralising identifiers (12 tokens)
'BOB_SUPPORT_KEY'                                                          IDENTICAL after neutralising identifiers (10 tokens)
'BOB_USE_MODEL_ENV'                                                        SAME top-level string (17 chars); neighbours not compared
'hooks cannot block'                                                       CHANGED: 1 real edit(s) + 0 interop artefacts, similarity 0.97, 227 → 239 tokens
'blocked by hook'                                                          IDENTICAL after neutralising identifiers (95 tokens)
'Ignoring invalid PreToolUse hook output'                                  CHANGED: 1 real edit(s) + 0 interop artefacts, similarity 0.97, 227 → 239 tokens
'path must be an absolute path'                                            MISSING in A
'workspaceTrusted'                                                         IDENTICAL after neutralising identifiers (11 tokens)
'approvedCommands'                                                         IDENTICAL after neutralising identifiers (14 tokens)
'restrictions'                                                             IDENTICAL after neutralising identifiers (181 tokens)
'fileRegex'                                                                SAME top-level string (5986 chars); neighbours not compared
'commandVariants'                                                          CHANGED: 6 real edit(s) + 0 interop artefacts, similarity 0.95, 618 → 672 tokens
'getCommandSecurityEnabled'                                                SAME LOGIC: 1 CJS→ESM interop artefacts only (106 → 108 tokens)
'isCommandSecurityEnabled'                                                 IDENTICAL after neutralising identifiers (8 tokens)
'folderTrust'                                                              IDENTICAL after neutralising identifiers (10 tokens)
'disableGlobalHooks'                                                       SAME top-level string (18 chars); neighbours not compared
'auto_approved'                                                            SAME top-level string (13 chars); neighbours not compared
'promptWithHooks'                                                          MISSING in A

=== AC2: approval_check.py against the installed 2.3.0 ===
Decision functions read: GFe (longest prefix) and jtr (allow/deny/none) for the matcher; validateToolExecution for the deny cancel; shouldAutoApprove / requiresExplicitApproval for the rest; qEr for the heuristics; jEr, UEr and the regex table LEr for the ignored-path gate (order in jEr: heuristics, ignored-path gate, securityEnabled test, model); GEr for isBobHomeWrite.
Script changes: docstring now 2.3.0; new --workspace option; ignored-path write gate modelled as an APPROXIMATION (decision: modelled, not skipped, because the 2.3.0 code is fully readable: the seven write regexes are ported verbatim, the pattern sources are .bobignore always and .gitignore only if session.respectGitIgnore is true, which the script reads from --settings; only the node-ignore matching itself is replaced by a gitignore-to-regex translation, case-insensitive like node-ignore; documented in the docstring and printed on every run; limits: exotic patterns, ~/.bob and the terminal-history dir treated as outside, parse-error unverifiable not reproduced). The version warning verified on 2.2.3 is expected until TASK-17.5 (_bobcheck.py untouched, 5 copies one hash d40c5ea9...).
Runs: the first run used the real settings file of this machine (allowed_permissions is only read there): git status gave PROMPT with reason execute not in allowed_permissions; the rest used two throw-away settings files (execute allowed) and a throw-away workspace with .bobignore listing secrets/, *.pem, /dist, !keep.pem. The version check was the real one against the installed app (it printed the 2.3.0 vs 2.2.3 warning). Raw outputs, version warning line removed from each run:
(each run also prints the expected 2.2.3 version warning: bob-code 2.3.0 installed, verified on 2.2.3, until TASK-17.5)

$ approval_check.py "git status" --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
git status → AUTO-APPROVED
  allow git status  (approved "git status")
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py "git push origin main" --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
git push origin main → BLOCKED by deny list
  deny list: "git push"
  deny  git push origin main  (denied "git push")
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py "npm test" --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
npm test → PROMPT
  no approved pattern: "npm test"
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py "echo "${!x}"" --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
echo "${!x}" → PROMPT
  requiresSecurityApproval by heuristic: indirect expansion ${!name}
  allow echo "${!x}"  (approved "echo")
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py " ; " --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
 ;  → PROMPT
  unverifiable: no command found
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py "echo hi > secrets/key.txt" --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
echo hi > secrets/key.txt → PROMPT
  requiresSecurityApproval (ignored-path write, .bobignore): writes "secrets/key.txt", pattern "secrets" - Command attempts to write to a path blocked by .gitignore or .bobignore.
  allow echo hi > secrets/key.txt  (approved "echo")
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py "echo hi > notes.txt" --settings <s-off>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
echo hi > notes.txt → AUTO-APPROVED
  allow echo hi > notes.txt  (approved "echo")
model check off · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .bobignore (3) in <ws> (.gitignore not read: session.respectGitIgnore is not true)

$ approval_check.py "echo hi >> build/x" --settings <s-on>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
echo hi >> build/x → PROMPT
  requiresSecurityApproval (ignored-path write, .gitignore): writes "build/x", pattern "build" - Command attempts to write to a path blocked by .gitignore or .bobignore.
  allow echo hi >> build/x  (approved "echo")
model check on · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .gitignore (1), .bobignore (3) in <ws>

$ approval_check.py "cp a.txt cert.PEM" --settings <s-on>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
cp a.txt cert.PEM → PROMPT
  requiresSecurityApproval (ignored-path write, .bobignore): writes "cert.PEM", pattern "*.pem" - Command attempts to write to a path blocked by .gitignore or .bobignore.
  no approved pattern: "cp a.txt cert.PEM"
model check on · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .gitignore (1), .bobignore (3) in <ws>

$ approval_check.py "tee dist/app.js" --settings <s-on>  (cwd = test workspace with .bobignore: secrets/ *.pem /dist !keep.pem)
tee dist/app.js → PROMPT
  requiresSecurityApproval (ignored-path write, .bobignore): writes "dist/app.js", pattern "/dist" - Command attempts to write to a path blocked by .gitignore or .bobignore.
  no approved pattern: "tee dist/app.js"
model check on · 3 approved · 1 denied · allowed_permissions read, execute
ignored-path write gate (approximation): .gitignore (1), .bobignore (3) in <ws>

Comparison with what the 2.3.0 code decides: allow = jtr returns allow for every sub-command and the group is allowed, so shouldAutoApprove is true (git status; echo hi > notes.txt). deny = validateToolExecution cancels with the deny-list note before any prompt (git push origin main). prompt = jtr returns undefined (npm test) so shouldAutoApprove is false. heuristic flag = qEr true so jEr returns dangerous without reason (echo with the indirect expansion). unverifiable = kEr yields no command (WEr sets unverifiable) so never auto-approved (empty command line). ignored-path write = UEr true so jEr returns dangerous with the reason BEr before the securityEnabled test, hence the PROMPT with model check off (secrets/key.txt) and the same with it on (cert.PEM matching *.pem case-insensitively, dist/app.js matching /dist, build/x matching the .gitignore pattern only when respectGitIgnore is true; with it false the same command was AUTO-APPROVED). Not proven: agreement of my gitignore translation with node-ignore on exotic patterns; the unverifiable case for parse failures; the model check itself.

=== AC3: yolo section, new form ===
The section is now titled There is no yolo mode. First sentence: The IDE has no yolo mode and no setting that turns approval off altogether (2.3.0, bundle: the word does not occur in extension.js); the isApproveAllEnabled path exists as code, is built without that option, nothing sets it: present as code, not wired, not exercised. Then a table of the seven keys the approval block reads (autoApprovalEnabled, allowed_permissions, outsideWorkspaceAllowed, permissionOptions, allowedExecutors, editApprovalPreviewMode, forbiddenApprovalGroups) plus the two per-task keys and the two keys outside the block. Then: the word appears in one place only, Bob Shell (--yolo deprecated alias of --auto-approve, en.json strings). Then the JSON labelled The most permissive configuration reachable from the settings - this is not a yolo mode, WITHOUT isCommandSecurityEnabled false, with browser added to allowed_permissions, followed by a list of what still prompts (security flag including the ignored-path write gate even with command security off, ~/.bob writes, outside workspace without the per-group option, forbidden groups, MCP outside the list, unverifiable commands and unlisted first tokens, deny list cancel, untrusted folder UNDETERMINED). The full text is in skills/bob-security-model/reference/approvals.md, section There is no yolo mode.

=== AC4: SKILL.md ===
Description now says whether a yolo-like mode exists (it does not in the IDE) and what still prompts with the most permissive settings; point 1 documents --workspace and the approximated ignored-path gate; point 2 names the new sections; the final warning adds the Bob Shell texts and the real effect of isCommandSecurityEnabled false. py_compile of all skills scripts passes; shasum of the five _bobcheck.py copies shows one hash.

=== HANDOFF TO TASK-17.5 (labels) ===
Labelled 2.3.0 (re-read on build 1.126.0+bob2.3.0.20261026121409): the whole of approvals.md except the items below; approval_check.py docstring (2.3.0) and SKILL.md header line. The Version label inside _bobcheck.py and VERIFIED_* are NOT touched: after the bump, approval_check.py will stop printing the 2.2.3 warning; nothing else in this skill depends on it.
Left with an earlier label or undetermined, with reason: (a) behaviour of the approval dialog and of the settings screens: only string presence checked on 2.3.0 (webview not diffed, 77 logical files changed) - last read 2.2.0; (b) where untrusted folder switches off auto-approval in the IDE - undetermined on 2.2.3 and 2.3.0; (c) web_search registration in the production IDE - undetermined, not exercised; (d) merge of several PermissionRequest handlers and whether it fires for subagents - undetermined; (e) inputs that make the tree-sitter parser fail - not enumerated; (f) whether an execute_command ever counts as outside the workspace - not established.
Facts for other tasks found while doing this one: the PreToolUse hook runs BEFORE Bob security check and approval (also on 2.2.3), the opposite of what approvals.md used to say; docs/codex-vs-bob.md line 75 says a Codex flag is Bob's yolo, which a reader could take for an IBM Bob IDE setting - out of scope here, worth a look in a docs pass; TASK-17.3 (hooks) can reuse the hook order and the PermissionRequest facts of approvals.md.
Not done: no change to _bobcheck.py, VERIFIED_*, README, CHANGELOG, other skills or docs.

Télémétrie (relevé reconstruit depuis les commits, script backfill.py, mesuré depuis la session d'orchestration après le commit) : 64 appels API, ≈ 4,14 USD ≈ 3,69 EUR équivalent API (taux BCE du 2026-11-02 : 1 USD = 0,8916 EUR ; tarifs de liste, pas une facture). Fenêtre 9a0bad4 → fa17908, 10 min, temps effectif ≈ 10 min, aucune pause (cohérent avec les 9,8 min de l'outil Agent, 68 appels d'outils). Orchestration sur Opus 5.5, sous-agent sur Sonnet. Contrôles refaits depuis la session principale : py_compile OK, un seul hachage pour les cinq _bobcheck.py, approval_check.py exécuté contre l'installation 2.3.0 (avertissement de version attendu jusqu'à 17.5), section There is no yolo mode présente dans approvals.md.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Re-verified the approval and security model on Bob 2.3.0 (1.126.0+bob2.3.0.20261026121409). approvals.md rewritten with build and source per fact: gate order unchanged but moved into a shared flow class, the PreToolUse hook order corrected (it runs first), MCP always-allow seeded at first call, browser group added, new ignored-path write gate in the security check, absolute-path file tools, PermissionRequest hook, folder trust with the undetermined enforcement point. The yolo section is now titled There is no yolo mode, states first that the IDE has none, lists the seven approval keys, places --yolo in Bob Shell only, and labels the most permissive JSON as not a yolo mode (no isCommandSecurityEnabled false) with what still prompts. approval_check.py is now 2.3.0, gains --workspace and an approximated ignored-path gate. Verified by 41 anchor verdicts, direct bundle reads, and ten real runs of the script compared with the 2.3.0 functions; py_compile passes and the five _bobcheck.py copies share one hash. Left undetermined: untrusted-folder enforcement in the IDE, web_search, dialog behaviour, PermissionRequest merge rule.
<!-- SECTION:FINAL_SUMMARY:END -->
