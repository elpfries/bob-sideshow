# Approvals in IBM Bob — bob-code 2.1.0

From `dist/extension.js` (`shouldAutoApprove`, `validateToolExecution`, `_alwaysAllowedTools`, `requiresSecurityApproval`,
`isBobHomeWrite`, hook runner) and the webviews. Re-verified against bob-code 2.2.0, build
`1.126.0+bob2.2.0.20260924155054`, using the bundle-diff evidence in `docs/bob-2.1.0-to-2.2.0.md`; every anchor below
is a literal confirmed present in that 2.2.0 build (prompt text, a settings key, a message, or a method/object-key
name — never a CommonJS export name). `ApprovalEngine` and `assessCommandSecurity` were bob-code 2.1.0 export names
only, gone from 2.2.0 by the CommonJS→ESM rebuild, not by behaviour; `getCommands` is an unrelated command-palette
method (`bob-code.openSettings` and friends) and was never evidence for this file.

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

Confirmed unchanged on bob-code 2.2.0: anchors `shouldAutoApprove`, `validateToolExecution`, `_alwaysAllowedTools`
are SAME LOGIC (2 CommonJS→ESM interop artefacts only, 352 → 352 tokens both builds) — the gate order above still
holds line for line.

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

Re-read directly on bob-code 2.2.0 (the export names `getBestCommandMatch` / `findLongestMatchingCommandPattern` are
gone by bundling, so the anchor tool can only place `validateToolExecution` as SAME LOGIC; the matcher body itself
was read by hand at the call site, both builds, reached from `shouldAutoApprove`/`validateToolExecution`): the
token matcher is byte-identical modulo esbuild's per-build identifier renaming (the minified names below are not
durable and are not meant to be grepped on a future build — only the surrounding method names are):

```js
// 2.2.0, minified locals
_prefixMatch = (command, patterns) => {
  let words = command.trim().split(/\s+/), best, bestLen = -1;
  for (let pat of patterns) {
    let toks = pat.trim().split(/\s+/);
    if (toks.length === 0 || toks[0] === "" || toks.length > words.length) continue;
    toks.every((t, i) => t === words[i]) && toks.length > bestLen && (best = pat, bestLen = toks.length);
  }
  return best;
};
_decide = (command, approved, denied) => {
  let a = _prefixMatch(command, approved), d = _prefixMatch(command, denied);
  if (!a && !d) return;
  if (!d) return "allow";
  if (!a) return "deny";
  return a.trim().split(/\s+/).length >= d.trim().split(/\s+/).length ? "allow" : "deny";
};
```

2.1.0's `findLongestMatchingCommandPattern`/`getBestCommandMatch` is the exact same function, only its local
variable names differ. `approval_check.py`'s `longest_match`/`decide` reimplement this correctly — no divergence
found, no change made to the script.

## Other gates

- `unverifiable`: parse error, no command, `${var@P}`, dynamic PowerShell. Never auto-approved, no setting.
  Confirmed unchanged on 2.2.0: the `unverifiable` flag lives in the same object literal as `requiresSecurityApproval`
  and `securityReason` (`{commands, unverifiable: n.length===0, requiresSecurityApproval, securityReason}`); its
  own condition (`n.length===0`) carries none of that anchor's 4 edits, which are all in the model/tier change below.
- `isBobHomeWrite`: command text mentions `.bob/settings.json` or `.bob/settings/settings.json`
  (case-insensitive), or an edit under `~/.bob/**` / workspace `.bob/settings.json`. Never auto-approved.
  Confirmed unchanged: anchor `isBobHomeWrite` IDENTICAL after neutralising identifiers (63 tokens, both builds).

## `requiresSecurityApproval` (security check)

Computed for every `usage: "command"` parameter (`execute_command`, `run_pase_command`), every call, no cache:

1. Regex heuristics, always on → dangerous, no reason: `${var@P|Q|E|A|a}`; octal/hex/unicode escapes in
   `${v:=…}`-style expansions; `${!name}`; here-string fed by `$(…)`/backticks; extglob `@(e:…:)`.
2. `isCommandSecurityEnabled` false (settings root; UI "Command Security Verification", shown only when the
   server flag `command-security-enabled` is true) or no provider → safe.
3. Over 5 000 chars: head sent, tail scanned for `| bash|sh|zsh|fish|python|perl|ruby`, `| sudo sh`,
   `base64 -d | sh` → "too complex, needs manual verification".
4. **Changed on bob-code 2.2.0** (build `1.126.0+bob2.2.0.20260924155054`; anchors `command-security-model`,
   `openai/gpt-oss-20b`, `commandSecurityModel` MISSING in 2.2.0; anchor `getCommandSecurityEnabled` CHANGED,
   4 real edits — the `commandSecurityModel: getFlagValue("command-security-model")` line was deleted; direct read
   of `resolveModelForTier`): the flag `command-security-model` and its hard-coded fallback `openai/gpt-oss-20b` are
   no longer read. The check instead asks for the internal, non-user-selectable model tier `"security"`; the
   provider resolves it by POSTing `{model:"router", messages, metadata:{model_tier:"security"}}` to
   `/chat/completions` and uses the model id the server answers with. If the router call fails, the local tier
   table is consulted — it has no `security` entry — and the fallback is `premium-ide`. The prompt split changed
   too (anchor `Command to analyze` EDITED, 7 714 → 86 chars; anchor `make install` EDITED, ratio 0.99, the one
   edit being this split): 2.1.0 sent one user message with an empty system prompt; 2.2.0 sends the context and
   categories as the **system** prompt and only the short `Command to analyze … Working directory … {IGNORE_SECTION}`
   block as the user message — same words, same categories (secrets access, exfiltration, remote code execution,
   destructive ops, privilege escalation, resource exhaustion, obfuscation, ignored-files access with
   `.gitignore`/`.bobignore` patterns), same routine-ops exemptions (package managers, venv, `cat .env` locally,
   kubeconfig flags, `make install`, `oc login`, read-only root SSH to IBM Fyre). Output schema `{dangerous, reason?}`
   and the 15 s timeout are unchanged (anchor `requiresSecurityApproval` CHANGED, 4 real edits, none of them in the
   heuristics — the 4 edits are this same model/tier change).
5. Timeout, bad answer, network error → dangerous, no reason (fail-closed). Confirmed unchanged on 2.2.0 (same
   anchor unit as step 4).

Effects: never auto-approved; "Security warning" banner with the reason (or a generic sentence);
"I understand the risk" checkbox required; "always approve" hidden; the banner's "Configure security
verification" link opens the approved list, which has no effect on the flag. Stored per call in
`messages.data.toolUsage.commandUse` (`bob-telemetry security`).

## "Yolo" in the IDE

No such flag (env read: `BOB_DEV_KEY`, `BOB_SUPPORT_KEY`, `BOB_USE_MODEL_ENV` only). Bob Shell:
`--auto-approve`, and `bob run` pre-approves everything. Confirmed unchanged on 2.2.0: all three env-var names are
still read by the dev-mode / support-logging checks. Closest IDE settings (approval defaults confirmed identical
object literals on 2.2.0):

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
  for subagents; after Bob's own security check, before approval. This is the contract `command-guard.mjs`
  (`skills/bob-override-rules/templates/hooks/command-guard.mjs`) uses, and it is still valid on bob-code 2.2.0,
  build `1.126.0+bob2.2.0.20260924155054` (direct read of the hook runner, function around anchors
  `hooks cannot block` / `blocked by hook`, both CHANGED — the 6 edits are additions, not removals). What changed:
  the event set grew from five to seven (`PreCompact`, `PostCompact` added; exit 2 now also blocks `PreCompact`
  and can no longer block `PostCompact`, alongside the unchanged `SessionStart`/`PostToolUse`/`Stop`); a handler
  can now be `{"type":"http", url, headers, allowedEnvVars, timeout}` next to `{"type":"command"}`; and stdout (or
  a 2xx HTTP body) starting with `{` is now parsed as JSON — `hookSpecificOutput.updatedInput` replaces the tool
  input, `permissionDecision:"deny"` blocks with `permissionDecisionReason`, `{"decision":"block","reason":…}`
  blocks `UserPromptSubmit`, `additionalContext` adds model context. Plain text on `PreToolUse` that starts with
  `{` but fails to parse is now ignored with the warning `Ignoring invalid PreToolUse hook output` instead of being
  treated as a reason (anchors `hookSpecificOutput`, `permissionDecision`, `updatedInput`,
  `Ignoring invalid PreToolUse hook output`, `allowedEnvVars`, `PostCompact` MISSING in 2.1.0, i.e. genuinely new).
  None of this affects `command-guard.mjs`: it never emits JSON, only stderr + exit 2, which is still read exactly
  as before.
- Custom mode without `execute`. Mode `restrictions` only know `fileRegex`. Confirmed unchanged: anchor
  `restrictions` IDENTICAL (181 tokens, both builds).

## Docs vs bundle

- "prefix of the full command string" → prefix by tokens, after splitting into sub-commands.
- "deniedCommands takes precedence" → longer pattern wins, tie → allow.
- Wildcards mentioned in docs → none in the bundle.
- Not in the settings UI: `forbiddenApprovalGroups`, `artifact`/`workflow` groups, `security.folderTrust.enabled`, `disableGlobalHooks`.
