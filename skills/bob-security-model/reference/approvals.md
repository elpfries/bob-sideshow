# Approvals in IBM Bob — bob-code 2.3.0

**Build and sources.** Every fact is read on bob-code **2.3.0**, build `1.126.0+bob2.3.0.20261026121409`
(`dist/extension.js`, 10 911 633 bytes, SHA-1 `57b8ecdb5c7fe7967695aaea023243f6d5ea3a30`), unless a sentence
names another build. Sources, named per fact: **bundle** (the installed `extension.js`, read directly and diffed
against the 2.2.3 bundle with a renaming-invariant tool), **webview** (the files under `dist/web/`, string
presence only — the approval dialog was not diffed), **db** (`~/.bob/db/bob.db`, read-only), **en.json**
(`dist/translations/en.json`). The delta that led here is `docs/bob-2.2.3-to-2.3.0.md` (sections 1 to 3); the one
before is `docs/bob-2.1.0-to-2.2.0.md`.

**Anchors.** Every name in backticks is a literal a minifier cannot rename (a method or object-key name, a
settings key, a message, a prompt text) — never a module export name. `ApprovalEngine`, `assessCommandSecurity`
and `_alwaysAllowedTools` are not anchors: the first two were 2.1.0 export names, and the module constant
`_alwaysAllowedTools` is gone from 2.3.0 (its four ids are listed below; the anchor is `isAutoApproved`).
`getCommands` is an unrelated command-palette method and never was evidence here.

**Labels.** "2.3.0" = re-read on that build. A fact that could not be re-checked on 2.3.0 keeps the label of the
build where it was last verified and says so (last section). The "Safe mode" and trust-level texts of `en.json`
are Bob Shell (terminal) strings: they have no literal in `extension.js` and are never IDE behaviour.

## Where a tool call is decided (2.3.0, bundle)

1. **PreToolUse hook** (`hooks.PreToolUse`) runs first, at the start of tool execution: exit 2 or a JSON
   `permissionDecision:"deny"` cancels the call before anything below; `updatedInput` rewrites the arguments. It
   runs before the security check below, which therefore sees the rewritten input. (The earlier wording "after
   Bob's own security check, before approval" was wrong; the order is the same on 2.2.3, read in the frozen copy.)
2. Bob computes the facts the gates need: path references, `isOutsideWorkspace`, `isBobHomeWrite`, and for
   `execute_command` / `run_pase_command` the command list, `unverifiable` and `requiresSecurityApproval`.
3. The approval flow (a shared class with a `resolve` method; on 2.2.3 the same steps ran in the chat-side
   `onToolCallHandler`): (a) the tool sources' `onToolWillExecute` listeners (a cancel returns); (b)
   `seedTaskAllowedMcpTools`; (c) `validateToolExecution` — outside the workspace unless `outsideWorkspaceAllowed`,
   then the deny list; (d) the four always-approved tools `ask_followup_question`, `start_workflow`,
   `create_html_artifact`, `create_chart`, otherwise `isAutoApproved` (= `shouldAutoApprove`); (e) otherwise
   `askUser`: the `PermissionRequest` hook, then the prompt, then the `PermissionResolved` hook.

The order of (c), (d), (e) is unchanged since 2.2.3. New on 2.3.0: a call to one of the four always-approved tools
is reported to the "Tool Call Decision" telemetry event with action `auto_approved` (2.2.3 returned for them
without a telemetry call). One prompt is shown at a time (`serializePrompts: true` in the IDE); before a queued
prompt is shown the call is rechecked with `isAutoApproved`, so an "always allow" answer silently approves the
queued calls it now covers.

## Auto-approval decision (`shouldAutoApprove`, in this order — 2.3.0, bundle; same text as 2.2.3)

0. `requiresExplicitApproval` (below) → never auto-approved. Then `isBuiltinSkill` (a built-in skill) → approved,
   even with the master toggle off.
1. `approval.autoApprovalEnabled` (toolbar master toggle; per task, initialised from global).
2. Group not in `approval.forbiddenApprovalGroups` (hidden from the settings UI; `[]` by default; the organisation
   policy `DisabledAutoApprovalGroups` writes the same key).
3. Not `requiresSecurityApproval`, not `isBobHomeWrite`; outside the workspace only with
   `permissionOptions: [{groupId, enableOutsideWorkspace: true}]` (the settings UI offers read and edit; the code
   accepts any group). `outsideWorkspaceAllowed` (default `false`) is a separate, earlier switch: with it off,
   `validateToolExecution` cancels the call (`Tools are blocked from working outside of the current workspace.`).
   File tools now **require absolute paths** (`path must be an absolute path (e.g. <workspace>/src/file.ts)`): a
   relative path is a tool error, not an approval question. A read of a file the user attached to a message, or of
   a saved tool output, is not counted as outside the workspace.
4. Group in `allowed_permissions`: `read edit execute browser mcp skill todo subtask subagent mode` plus the hidden
   `artifact` and `workflow`. (`browser` is a registered, non-hidden group on 2.2.3 and 2.3.0; this note omitted
   it before. The settings row for it is conditioned on `experiments.webFetch`, and the organisation policy's list
   of valid ids omits `browser`, `artifact` and `workflow`.)
5. Shell tool: not `unverifiable`, and **every** sub-command `allow` against `approvedCommands` (global
   `allowedExecutors[toolId=execute_command]` + task `taskCommandApprovals`) vs `deniedCommands`. MCP tool: its
   group `mcp` is in `allowed_permissions` **and** its id is in the task's `taskAllowedMcpTools`. Other tools in an
   allowed group: approved. A tool with no permission group is never auto-approved.

**MCP "always allow".** A server's `alwaysAllow` list (`isAlwaysAllowed`) is copied into the task key
`taskAllowedMcpTools` by `seedTaskAllowedMcpTools` at the **first tool call of the task** (2.2.3: when the task was
loaded), only while that key is `undefined`. "Always allow" in the prompt appends to the same key and to
`allowed_permissions`. MCP tool annotations (`readOnlyHint` and friends) are used nowhere in the IDE.

Per-task keys (`tasks.approval_config`, db): `autoApprovalEnabled`, `allowed_permissions`, `taskCommandApprovals`,
`taskAllowedMcpTools` — the only four the task reads back (`getEffectiveApprovalConfig` overlays them on the global
block). Older rows of the db hold more keys (a copy of the whole block); 2.3.0 ignores them. Everything else:
`~/.bob/settings/settings.json`. "Always approve" in the prompt offers the full text or its first word
(`commandVariants`: the first word alone when it is already approved on its own) and writes to the **task**, not to
the global list.

Anchor verdicts 2.2.3 → 2.3.0 (renaming-invariant diff): `requiresExplicitApproval`, `applyApprovalResponse`,
`isBuiltinSkill`, `getEffectiveApprovalConfig` IDENTICAL; `shouldAutoApprove` CHANGED (2 edits, in the neighbouring
`waitUntilAutoApproved`, whose listener is now removed on approval); `validateToolExecution` CHANGED (29 edits, all
in the caller that moved into the flow class — the method body is the same text); `isAutoApproved`,
`isApproveAllEnabled`, `promptWithHooks` MISSING in 2.2.3 (new).

## Matching (2.3.0, bundle)

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
`cd src && npm test | tee log` → three commands, all must allow; a parse error gives no commands, i.e.
`unverifiable`. Paths stay as typed. Defaults (15, identical to 2.2.3):
`cat git diff git log git rev-parse git show git status grep head tail ls sort wc which du df`.
The deny list is checked twice: `validateToolExecution` cancels a denied command before any prompt (using the
global approved list), and `shouldAutoApprove` decides again with the task approvals added.

The matcher body, read on 2.3.0 at its call sites (reached from `shouldAutoApprove` and `validateToolExecution`), is
the 2.2.0 and 2.1.0 text modulo the minifier's local names. The names below are placeholders, not to be grepped on
a future build — only the surrounding method names are durable:

```js
// 2.3.0, minified locals renamed
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

`approval_check.py`'s `longest_match` / `decide` reimplement this; no divergence found on 2.3.0.

## Other gates

- `unverifiable`: parse error, no command, `${var@P}`, dynamic PowerShell. Never auto-approved, no setting.
  2.3.0, bundle: the flag is `{commands, unverifiable: n.length===0, requiresSecurityApproval, securityReason}`;
  an empty command list is the whole condition. Which inputs make the parser fail was not enumerated.
- `isBobHomeWrite`: command text mentions `.bob/settings.json` or `.bob/settings/settings.json`
  (case-insensitive), or an edit-group call touches `~/.bob/**` or the workspace `.bob/settings.json`. Never
  auto-approved; the prompt says "This operation accesses protected Bob files and requires explicit approval."
  (webview). 2.3.0, bundle: anchor `isBobHomeWrite` IDENTICAL to 2.2.3.

## `requiresSecurityApproval` (security check)

Computed for every `usage: "command"` parameter (`execute_command`, `run_pase_command`), every call, no cache. The
steps, in the order of the 2.3.0 function (anchors `Command attempts to write to a path blocked by`,
`Command is too complex`, `Command to analyze`):

1. Regex heuristics, always on → dangerous, no reason: `${var@P|Q|E|A|a}`; octal/hex/unicode escapes in
   `${v:=…}`-style expansions; `${!name}`; here-string fed by `$(…)`/backticks; extglob `@(e:…:)`.
2. **New on 2.3.0 — write to an ignored path.** If the IDE supplies ignore patterns (`getIgnorePatterns`) and the
   command text writes to a path they match → dangerous, reason `Command attempts to write to a path blocked by
   .gitignore or .bobignore.` The writes recognised are `>` `>>`, `tee`, `dd of=`, the target of `cp`/`mv`
   (including `-t`), and PowerShell `Set-Content` / `Add-Content` / `Out-File`; a path containing `$` is skipped,
   and so is a path outside the workspace. The patterns are the user patterns of the workspace: `.bobignore` always,
   `.gitignore` only when `session.respectGitIgnore` is true (default **false**); empty lines, comments and `!`
   lines are dropped, trailing slashes removed; the default `.env` entry is not among them. Matching uses the
   node-ignore library (case-insensitive). It runs **before** the `isCommandSecurityEnabled` test, so it applies with
   command security off, and it costs no model call. `approval_check.py` models it as an approximation (see its
   docstring); it cannot know the patterns of a workspace it is not run in.
3. `isCommandSecurityEnabled` false (settings root; UI "Command Security Verification", shown only when the server
   flag `command-security-enabled` is true — default `true` in the bundle) or no provider → safe.
4. Over 5 000 chars: head sent, tail scanned for `| bash|sh|zsh|fish|python|perl|ruby`, `| sudo sh`,
   `base64 -d | sh` → "too complex, needs manual verification".
5. Model check (unchanged since 2.2.0): the check asks for the internal, non-user-selectable model tier
   `"security"` (`resolveModelForTier`); the provider POSTs `{model:"router", messages, metadata:{model_tier:"security"}}`
   to `/chat/completions` and uses the model id the server answers with; if the router call fails, the local tier
   table (no `security` entry) gives `premium-ide`. The context and categories are the **system** prompt, the short
   `Command to analyze … Working directory … {IGNORE_SECTION}` block is the user message. Categories: secrets access,
   exfiltration, remote code execution, destructive ops, privilege escalation, resource exhaustion, obfuscation,
   ignored-files access (with the `.gitignore`/`.bobignore` patterns when there are some); routine-ops exemptions
   (package managers, venv, `cat .env` locally, kubeconfig flags, `make install`, `oc login`, read-only root SSH to
   IBM Fyre). Output schema `{dangerous, reason?}`, 15 s timeout.
6. Timeout, bad answer, network error → dangerous, no reason (fail-closed).

Anchor verdicts 2.2.3 → 2.3.0: the heuristic function, the 5 000-char rule and its three tail patterns, the schema,
the timeout and the fail-closed catch were read side by side in both builds: unchanged. `requiresSecurityApproval`
IDENTICAL (it is the object key; the gate was added in the function that sets it), `resolveModelForTier`
IDENTICAL, `Command to analyze` and `Command is too complex and needs manual verification.` SAME string,
`commandVariants` CHANGED (6 edits: the lookup of the ignore patterns and the reading of user-attached files as
non-outside paths).

Effects: never auto-approved; "Security warning" banner with the reason (or a generic sentence); "I understand the
risk" checkbox required; "always approve" hidden; the banner's "Configure security verification" link opens the
approved list, which has no effect on the flag (webview, string presence on 2.3.0; the dialog code was not diffed).
Stored per call in `messages.data.toolUsage.commandUse` — keys `unverifiable`, `commands`,
`requiresSecurityApproval`, `commandVariants` (db, rows written by 2.3.0 and earlier; `bob-telemetry security`).

## There is no yolo mode

**The IDE has no yolo mode and no setting that turns approval off altogether** (2.3.0, bundle: the word does not
occur in `extension.js`). The code has one path of that kind — the approval flow reads an `isApproveAllEnabled`
option, and when it is true everything that does not need explicit approval is approved — but the IDE builds the
flow without that option and nothing in the bundle sets it: it is present as code, not wired, not exercised. Do
not invent a setting for it.

**Keys the `approval` block accepts** (read from the 2.3.0 defaults object and from the code that consumes them; no
schema check of the settings file was found, so an unknown key is simply never read):

| Key | Default | Effect |
|---|---|---|
| `autoApprovalEnabled` | `true` | master toggle (task-level once the toolbar writes it) |
| `allowed_permissions` | `["read"]` | groups approved without a prompt |
| `outsideWorkspaceAllowed` | `false` | `true` lets tools reach outside the workspace at all |
| `permissionOptions` | `[]` | `[{groupId, enableOutsideWorkspace}]`: auto-approve outside the workspace per group |
| `allowedExecutors` | one `execute_command` entry, the 15 commands, no denials | `[{toolId, approvedCommands, deniedCommands}]` |
| `editApprovalPreviewMode` | `"editor"` | how the edit diff is shown (`"chat"` is the other value read) |
| `forbiddenApprovalGroups` | `[]` | groups that always prompt |

The per-task keys `taskCommandApprovals` and `taskAllowedMcpTools` live in `tasks.approval_config`, not in the
settings file. Outside the block: `isCommandSecurityEnabled` (settings root) and `session.respectGitIgnore`.

**The word appears in one place only: Bob Shell.** `--yolo` is a deprecated alias of `--auto-approve` there
(en.json: "--yolo is deprecated. Use --auto-approve instead. Enabling auto-approve." and "--yolo is deprecated and
ignored in headless mode where auto-approve is the default"). None of that exists in the IDE bundle. The environment variables the IDE reads for development, support and model selection
(`BOB_DEV_KEY`, `BOB_SUPPORT_KEY`, `BOB_USE_MODEL_ENV`; 2.3.0, bundle: all three still read) are not approval flags.

**The most permissive configuration reachable from the settings — this is not a yolo mode.** It widens every
switch the IDE lets you widen, and still asks about everything listed under it:

```json
{ "approval": { "autoApprovalEnabled": true,
    "allowed_permissions": ["read","edit","execute","browser","mcp","skill","todo","subtask","subagent","mode","artifact","workflow"],
    "outsideWorkspaceAllowed": true,
    "permissionOptions": [{"groupId":"read","enableOutsideWorkspace":true},{"groupId":"edit","enableOutsideWorkspace":true},{"groupId":"execute","enableOutsideWorkspace":true}],
    "allowedExecutors": [{"toolId":"execute_command","approvedCommands":["git","npm","node","python3","ls","cat","grep","find","mkdir","cp","mv"],"deniedCommands":["rm -rf /","git push --force"]}] } }
```

(The `execute` entry of `permissionOptions` has no toggle in the settings UI; the code accepts it. Whether an
`execute_command` ever counts as outside the workspace was not established.) This still asks, on 2.3.0:

- every command the security check flags: the always-on heuristics; a **write to a path covered by `.bobignore`
  (or `.gitignore` when `session.respectGitIgnore` is on)**, which holds even with `isCommandSecurityEnabled: false`;
  and, while `isCommandSecurityEnabled` is true (its default), the model check, which also fails closed;
- writes to `~/.bob` and `.bob/settings.json` (`isBobHomeWrite`);
- anything outside the workspace for a group without `enableOutsideWorkspace` (and, with `outsideWorkspaceAllowed`
  off, a hard cancel instead of a prompt);
- groups in `forbiddenApprovalGroups` (also set by the organisation policy `DisabledAutoApprovalGroups`);
- MCP tools whose id is not in `taskAllowedMcpTools` (seeded from `alwaysAllow`);
- commands the parser cannot verify, and any first token not in `approvedCommands` (no wildcard);
- a command on the deny list is cancelled, not prompted;
- an untrusted folder: the harness forces `autoApprovalEnabled` off (next section), but where the IDE enforces that
  is **undetermined** — do not promise either outcome.

## Folder trust (2.3.0, bundle)

`workspaceTrusted` is `options.workspaceTrusted !== false`; the IDE passes the editor's `workspace.isTrusted` in
`activate()`. An untrusted workspace gets the default configuration with `approval.autoApprovalEnabled = false`
(`security.folderTrust.enabled` copied), no workspace rules, skills, modes, agents or hooks, and no MCP start. That
is the same code as 2.2.3 (anchor `workspaceTrusted` IDENTICAL; `isWorkspaceTrusted` is now a real method name).
**Undetermined, on both builds:** the IDE's approval path reads the IDE global approval settings
(`getEffectiveApprovalConfig` over the global block), not the harness `getConfig()`, and the approval-config class
has an `isUntrusted` option that the IDE does not pass — so where "untrusted ⇒ no auto-approval" is enforced in the
IDE is not established. `security.folderTrust.enabled` defaults to `true`; what the IDE does with it is not visible
in the bundle. The "Safe mode" / trust-level texts are Bob Shell.

## Enforcement without the model

- `deniedCommands`: cancels with a note to Bob (`Attempted to execute commands that are on the deny list: …`).
  Token-prefix only. Checked before any prompt, and not overridable by a `PermissionRequest` hook.
- `hooks.PreToolUse` (global or workspace `.bob/settings.json`):
  `[{"matcher":"^execute_command$","hooks":[{"type":"command","command":"node .bob/hooks/guard.mjs","timeout":5}]}]`.
  stdin `{session_id, cwd, hook_event_name, tool_name, tool_input, tool_use_id}`; exit 2 blocks, stderr (else
  stdout) is the reason Bob sees; other codes ignored; 10 s default, 1 MB output; runs outside approval, also for
  subagents; **first in the sequence above — before Bob's own security check and before approval**. 2.3.0, bundle:
  the hook runner (anchors `hooks cannot block`, `blocked by hook`, `Ignoring invalid PreToolUse hook output`)
  keeps this contract: HTTP handlers, JSON output (`hookSpecificOutput.updatedInput`, `permissionDecision:"deny"`,
  `{"decision":"block"}` for `UserPromptSubmit`, `additionalContext`), and plain text starting with `{` that fails
  to parse is ignored with a warning. Changed since 2.2.3: the event set is **nine** (`PermissionRequest` and
  `PermissionResolved` added); exit 2 cannot block either of them (it joins `SessionStart`, `PostCompact`,
  `PostToolUse`, `Stop`); a matcher group may list `fileSystems` (default `["file"]`); and if a hook or the user
  changed a call's input, the tool result begins "Your <tool> call was changed before execution (PreToolUse hook or
  user edit)". `command-guard.mjs` (`skills/bob-override-rules/templates/hooks/command-guard.mjs`) never emits JSON,
  only stderr + exit 2, and is unaffected.
- `PermissionRequest` hook (new on 2.3.0; runs only when Bob would show a prompt): it can answer
  `{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"|"deny"}}}`. `deny`
  rejects the call; `allow` approves without a prompt **except** for calls that need explicit approval (forbidden
  groups, security flag, writes to the Bob home, outside the workspace without the group option) — there the prompt
  still opens. The deny list and the outside-workspace refusal run before it and cannot be overridden. `allow` with
  `updatedInput` is ignored with a warning. Not established: how several handlers are merged (the "any deny wins"
  sentence is the bundled skill text), and whether it fires for a subagent's calls.
- Custom mode without `execute`. Mode `restrictions` only know `fileRegex` (2.3.0, bundle: anchor `restrictions`
  IDENTICAL; the check in the tool-call code tests `fileRegex` only).

## Docs vs bundle

- "prefix of the full command string" → prefix by tokens, after splitting into sub-commands.
- "deniedCommands takes precedence" → longer pattern wins, tie → allow.
- Wildcards mentioned in docs → none in the bundle.
- Not in the settings UI: `forbiddenApprovalGroups` (the UI reads it to hide groups), `artifact`/`workflow` groups,
  `security.folderTrust.enabled`, `disableGlobalHooks` (webview 2.3.0: the last two have no literal in `dist/web/`;
  the settings screens were not diffed).

## Not re-verified on 2.3.0 (label kept)

- The approval dialog and the settings screens in the webview: only string presence was checked on 2.3.0; their
  behaviour was last read on 2.2.0 and was not diffed (77 logical webview files changed).
- `web_search` (permission group `browser`, gated by `experiments.webSearch`, default `false`, and a host
  condition): registration in the production IDE is undetermined; not exercised.
- Which shell inputs make the tree-sitter parse fail (the `unverifiable` case beyond an empty command list).
