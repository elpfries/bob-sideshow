# Approvals in IBM Bob — bob-code 2.1.0

From `dist/extension.js` (`ApprovalEngine`, `getCommands`, `assessCommandSecurity`, hook runner) and the webviews.

## Auto-approval decision (`shouldAutoApprove`, in this order)

1. `approval.autoApprovalEnabled` (toolbar master toggle; per task, initialised from global).
2. Group not in `approval.forbiddenApprovalGroups` (hidden from the settings UI; `[]` by default).
3. Not `requiresSecurityApproval`, not `isBobHomeWrite`; outside the workspace only with
   `permissionOptions: [{groupId, enableOutsideWorkspace: true}]` (UI offers read/edit, code accepts any group).
4. Group in `allowed_permissions`: `read edit execute mcp skill todo subtask subagent mode` + hidden `artifact workflow`.
5. Shell tool: not `unverifiable`, and **every** sub-command `allow` against `approvedCommands`
   (global `allowedExecutors[toolId=execute_command]` + task `taskCommandApprovals`) vs `deniedCommands`.
   MCP tool: name in task `taskAllowedMcpTools` or `alwaysAllow` in `mcp.json`. Other tools: approved.

Per-task keys (`tasks.approval_config`): `autoApprovalEnabled`, `allowed_permissions`, `taskCommandApprovals`,
`taskAllowedMcpTools`. Everything else: `~/.bob/settings/settings.json`.

## Matching

```
words = command.split(/\s+/)
pattern matches ⇔ tokens(pattern) is a prefix of words, token by token, strict equality (case-sensitive)
keep the longest matching approved and denied pattern
none → prompt · only approved → allow · only denied → deny · both → longer wins, tie → allow
```

| Pattern | Command | Result |
|---|---|---|
| `git` | `git push --force` | match (prefix) |
| `git st` | `git status` | no match (tokens, not characters) |
| `Cat`, `cat README.md`, `git *` | `cat x`, `cat ./README.md`, `git push` | no match (case, exact token, `*` literal) |
| approved `git` · denied `git push` | `git push origin` | deny (longer) |
| approved `git push --force` · denied `git push` | `git push --force` | allow (longer) |
| approved `npm` · denied `npm` | `npm ci` | allow (tie) |

Matched text: each sub-command extracted by tree-sitter-bash (PowerShell AST on Windows) —
`cd src && npm test | tee log` → three commands, all must allow. Paths stay as typed.
Defaults: `cat git diff git log git rev-parse git show git status grep head tail ls sort wc which du df`.
"Always approve" in the prompt offers the full text or its first word and writes to the task, not the global list.

## Other gates

- `unverifiable`: parse error, no command, `${var@P}`, dynamic PowerShell. Never auto-approved, no setting.
- `isBobHomeWrite`: command text mentions `.bob/settings.json` or `.bob/settings/settings.json`
  (case-insensitive), or an edit under `~/.bob/**` / workspace `.bob/settings.json`. Never auto-approved.

## `requiresSecurityApproval` (security check)

Computed for every `usage: "command"` parameter (`execute_command`, `run_pase_command`), every call, no cache:

1. Regex heuristics, always on → dangerous, no reason: `${var@P|Q|E|A|a}`; octal/hex/unicode escapes in
   `${v:=…}`-style expansions; `${!name}`; here-string fed by `$(…)`/backticks; extglob `@(e:…:)`.
2. `isCommandSecurityEnabled` false (settings root; UI "Command Security Verification", shown only when the
   server flag `command-security-enabled` is true) or no provider → safe.
3. Over 5 000 chars: head sent, tail scanned for `| bash|sh|zsh|fish|python|perl|ruby`, `| sudo sh`,
   `base64 -d | sh` → "too complex, needs manual verification".
4. Model `command-security-model` (`openai/gpt-oss-20b`), empty system prompt, output `{dangerous, reason?}`,
   15 s timeout. Prompt: harm *beyond the user's intent*; routine ops exempted (package managers, venv,
   `cat .env` locally, kubeconfig flags, `make install`, `oc login`, read-only root SSH to IBM Fyre); categories:
   secrets access, exfiltration, remote code execution, destructive ops, privilege escalation, resource
   exhaustion, obfuscation, and — only with `.gitignore`/`.bobignore` patterns — ignored-files access.
5. Timeout, bad answer, network error → dangerous, no reason (fail-closed).

Effects: never auto-approved; "Security warning" banner with the reason (or a generic sentence);
"I understand the risk" checkbox required; "always approve" hidden; the banner's "Configure security
verification" link opens the approved list, which has no effect on the flag. Stored per call in
`messages.data.toolUsage.commandUse` (`bob-telemetry security`).

## "Yolo" in the IDE

No such flag (env read: `BOB_DEV_KEY`, `BOB_SUPPORT_KEY`, `BOB_USE_MODEL_ENV` only). Bob Shell:
`--auto-approve`, and `bob run` pre-approves everything. Closest IDE settings:

```json
{ "approval": { "autoApprovalEnabled": true,
    "allowed_permissions": ["read","edit","execute","mcp","skill","todo","subtask","subagent","mode","artifact","workflow"],
    "outsideWorkspaceAllowed": true,
    "permissionOptions": [{"groupId":"read","enableOutsideWorkspace":true},{"groupId":"edit","enableOutsideWorkspace":true},{"groupId":"execute","enableOutsideWorkspace":true}],
    "allowedExecutors": [{"toolId":"execute_command","approvedCommands":["git","npm","node","python3","ls","cat","grep","find","mkdir","cp","mv"],"deniedCommands":["rm -rf /","git push --force"]}] },
  "isCommandSecurityEnabled": false }
```

Still prompting: unverifiable commands, regex heuristics, `.bob` writes, MCP tools outside an allowlist,
any first token not listed (no wildcard).

## Enforcement without the model

- `deniedCommands`: cancels with a note to Bob. Token-prefix only.
- `hooks.PreToolUse` (global or workspace `.bob/settings.json`):
  `[{"matcher":"^execute_command$","hooks":[{"type":"command","command":"node .bob/hooks/guard.mjs","timeout":5}]}]`.
  stdin `{session_id, cwd, hook_event_name, tool_name, tool_input, tool_use_id}`; exit 2 blocks, stderr (else
  stdout) is the reason Bob sees; other codes ignored; 10 s default, 1 MB output; runs outside approval, also
  for subagents; after Bob's own security check, before approval.
- Custom mode without `execute`. Mode `restrictions` only know `fileRegex`.

## Docs vs bundle

- "prefix of the full command string" → prefix by tokens, after splitting into sub-commands.
- "deniedCommands takes precedence" → longer pattern wins, tie → allow.
- Wildcards mentioned in docs → none in the bundle.
- Not in the settings UI: `forbiddenApprovalGroups`, `artifact`/`workflow` groups, `security.folderTrust.enabled`, `disableGlobalHooks`.
