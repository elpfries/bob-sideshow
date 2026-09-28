# Bob 2.1.0 → 2.2.0: what changed in `bob-code`

Companion to the five comparison notes ([cursor-vs-bob.md](cursor-vs-bob.md),
[claude-code-vs-bob.md](claude-code-vs-bob.md), [opencode-vs-bob.md](opencode-vs-bob.md),
[codex-vs-bob.md](codex-vs-bob.md), [kimi-code-vs-bob.md](kimi-code-vs-bob.md)). This one compares
Bob with itself: everything bob-sideshow states was read on `bob-code` 2.1.0, the update to 2.2.0
replaced the application in place, and every script now warns. Before any note is re-verified or
relabelled, this page establishes what actually moved between the two builds, and for each item
whether it is a behaviour change, a cosmetic or bundling artefact, or still undetermined.

The rule of the whole exercise: a vanished identifier proves nothing about behaviour. Offsets and
minified names move on every build, so every fact below is anchored on a literal that a minifier
cannot rename — prompt text, an error message, a settings key, a method or object-key name — and
never on a byte offset.

## The baselines and what each one is worth

| Baseline | What it is | Worth |
|---|---|---|
| Bundle 2.1.0 | `extensions/bob-code/dist/extension.js` extracted from the macOS arm64 update archive `IBM-Bob-darwin-arm64-1.126.0+bob2.1.0.zip` (262 010 603 bytes, SHA-256 `34d299ab6661ab9aecf0bb33e18834276991bcadd877cebd2dc413c060154927`), fetched from the update endpoint recorded in `product.json` on 2026-09-28. `extension.js`: 14 731 421 bytes, SHA-1 `f5ebecbd954f7c99e3666bbee1f4525ed9dcdfc3`; `product.json` commit `a8240f78e496…`, dated 2026-08-26; `Info.plist` `CFBundleVersion` `1.126.0+bob2.1.0.20260827055215`. | The "before" side of the diff. It is **not** byte for byte the build the reference notes were read on (`1.126.0+bob2.1.0.20260827055214`, SHA-1 `d8b1130e9378b80a63bffc44a020efcb5ba09a63`, 14 731 430 bytes): same version, a packaging run one second later, 9 bytes shorter. The 9 bytes are exactly the `_PKG_USER` suffix of the Jenkins workspace path literal (`BOB_IDE_EXTERNAL` here, `BOB_IDE_EXTERNAL_PKG_USER` in the notes' build and in 2.2.0) — the only build-specific literal in the bundle, and nothing to do with code. |
| Bundle 2.2.0 | The installed `/Applications/IBM Bob.app/…/extensions/bob-code/dist/extension.js`: 10 622 906 bytes, SHA-1 `6afa9f9c6012df40e49cb863151c492e80c237f8`; `product.json` commit `30bf4b86252b…`, dated 2026-09-09; `CFBundleVersion` `1.126.0+bob2.2.0.20260924155054`; extension `package.json` version `2.2.0`. | The "after" side, the build every claim must hold on. |
| Local database | A read-only `.backup` of `~/.bob/db/bob.db` taken on 2026-09-28 while 2.2.0 was running, before any 2.2.0 task: 3 018 752 bytes, SHA-256 `bee901ee943fcd707f7a9ef56b4d5a9f929a0b6a43cdaa825e064de88c16be6a`, `integrity_check` ok, 18 tasks, 143 messages, 5 stored system prompts, 68 messages carrying `_meta.spend`, last message 2026-09-19. | 2.1.0 evidence for prompts and unit prices: every stored call was priced by 2.1.0 and every stored prompt assembled by it (the update landed 2026-09-24). **Not** evidence of the 2.1.0 schema: 2.2.0 had already applied `011_key_value_store` (row dated 2026-09-28T19:27Z) when the backup was taken, so the file holds 2.1.0 content in a 2.2.0 schema. The 2.1.0 schema is read from the migration SQL in the 2.1.0 bundle instead. |
| Vendor changelog | Section "2.2.0 — September 2026" of the IDE changelog, at the `releaseNotesUrl` of `product.json`. Five "New Features / Improvements" and five "Bug Fixes", written for users. | First-hand statement of intent, silent on internals. Confronted with the bundle in a section below. |
| `translations/en.json` | 577 keys on 2.1.0, 1 169 on 2.2.0: 592 added, none removed, none changed. The additions are Bob Shell (terminal) strings merged into the IDE catalog. | Confirms UI labels (`Allow outside workspace tool requests`, `Background Processes`, `Are you sure you want to stop this process?`) but says nothing about the agent. |

Everything else (`README`, the reference notes, the scripts) is the written 2.1.0 record and is what
this page exists to test.

## Method: why a text diff would mislead, and what is compared instead

The two bundles differ by 4.1 MB and a raw text diff of two multi-megabyte minified lines is noise:
esbuild renames every local identifier on every build, and 2.1.0 was emitted as **CommonJS**
(modules wrapped in functions, exports reached as `module.Name`, calls written `(0, mod.fn)(…)`,
`__toESM` / `__commonJS` helpers) while 2.2.0 is **ESM with direct bindings**. Counts in the two
files: `__toESM` 7 → 0, `__commonJS` 2 → 0, `.default.` 794 → 263, `__esModule` 1 936 → 838. Every
export name that the 2.1.0 notes used as a landmark — `SUBAGENT_PRESETS`, `MODEL_TIERS`,
`DEFAULT_MODEL_TIER`, `parseAgentFile`, `loadWorkspaceRules`, `INIT_BASE_PROMPT`,
`getBestCommandMatch`, `findLongestMatchingCommandPattern`, `DEFAULT_APPROVED_COMMANDS`,
`assessCommandSecurity`, `featureFlagsSchema`, `isWorkspaceTrusted`, `BOB_HOOK_EVENTS` — was a
property token of a CommonJS `exports` object in 2.1.0 and is a plain (renamed) binding in 2.2.0.
Their disappearance is a **bundling artefact**, not a behaviour change. Names of class methods and
object keys survive (`shouldAutoApprove`, `requiresSecurityApproval`, `isBobHomeWrite`,
`validateToolExecution`, `handleUiReply`, `_alwaysAllowedTools`, `approvedCommands`), and so does
every prompt sentence, error message and settings key.

So the comparison is made only on what a minifier cannot touch. Each bundle is tokenised; string
literals, template literals, property names, regex literals and keywords are kept; every other
identifier becomes `_`. Three views come out of that (a private, read-only, standard-library tool,
not shipped with the skills):

- **String and property sets.** Strings that vanished on one side and appeared on the other are
  paired by similarity first and shown as word-level edits; only the rest count as removed or
  added, and each is tagged by the vocabulary of the function it lives in (`bob`, `vendor:<lib>`,
  unknown). Result on strings of 8+ characters: 13 949 vanished, 3 129 appeared, 37 paired as
  edits; of the removals, 5 854 are pdf.js, 1 712 LangChain, 746 highlight.js keyword tables,
  538 PostHog, 173 parse5 and 111 Bob's own; of the additions, 386 gRPC, 293 MCP SDK, 44 Bob's own.
- **Anchors.** For a documented fact, the smallest function (or object literal, or the string
  itself) around its literal is taken in each build, occurrences are paired by resemblance, never
  by order, identifiers are neutralised and the two are diffed token by token. `(0, mod.fn)` call
  targets are folded to a bare name before diffing, and a removed `.name` with nothing or a bare
  name on the other side is counted as an interop artefact. Verdicts: **IDENTICAL** (only names
  changed), **SAME LOGIC** (only interop artefacts), **CHANGED** with the real edits listed,
  **SAME / EDITED top-level string** with a word diff, **MISSING** on one side. 102 anchors were
  run for this page: 27 SAME string, 10 IDENTICAL, 3 SAME LOGIC, 12 CHANGED, 6 EDITED,
  19 MISSING in 2.2.0 (all export names or things genuinely removed, listed below), 25 MISSING in
  2.1.0 (things genuinely added).
- **Direct reads** of the code around an anchor, in both builds, for what a token diff cannot say
  (which model a tier resolves to, which directory a glob covers).

Durable-anchor rule for every note that gets rewritten: cite prompt text, settings keys, messages,
method names and object keys — never a module export name. A verdict of "MISSING" on an export
name is inconclusive on its own and is never used as evidence here.

## The delta

Classes: **behaviour** (Bob does something else), **artefact** (cosmetic, bundling or dependency
change; Bob does the same thing), **undetermined** (cannot be settled from the bundles alone).
Evidence names the anchor literal and its verdict, the paired string edit, or the changelog entry.

### 1. System prompt: sections and guidance blocks

| Difference | Class | Evidence |
|---|---|---|
| Section tags left the string literals. 2.1.0 stored `<base_rules>\n…\n</base_rules>` inline; 2.2.0 stores the body alone and wraps it at assembly time from a **prompt-section registry**: `{id:"baseRules", tag:"base_rules", content:{type:"text", template:…}}`, rendered as `<tag>\n…\n</tag>` in `xml` format or `## tag` in `md` format. The stored prompt still has the tags in `xml` format. | artefact (assembly), to be confirmed on a stored 2.2.0 prompt | paired string edits: `[-<base_rules>⏎-] - Prefer editing …`, same for `<tool_use>`, `<engineering_discipline>`, `<investigate_before_answering>`, `<auto_appended_context>`, `<markdown_rules>`; anchors `Duplicate prompt config id`, `task_execution`, `when_stuck` MISSING in 2.1.0 |
| **The layout now depends on the model.** Four registered configs — `default`, `boreas`, `aquarius`, `orion` — chosen by the longest prefix match of `provider/family/version` of the model id, falling back to `default` (error text `No "default" prompt config found`). `default` and `aquarius`: `role_definition`, `investigate_before_answering`, `engineering_discipline`, `tool_use`, `markdown_rules`, `auto_appended_context`, `base_rules`, `available_skills`, `user_custom_instructions`, `project_rules`, `environment_info`, subtask instructions (subtasks only), tool guidance. `boreas` inserts `task_execution` after `investigate_before_answering` and `when_stuck` after `tool_use`. `orion` inserts `act_and_iterate`, `ground_truth`, `define_done`, `prove_done` after `investigate_before_answering`. Which family each codename is cannot be read locally. | behaviour | direct read of the registry; added strings `- State the next action in one short sentence…`, `- Ground every value in something you actually inspected…`, `- "Done" means a real check passed…`, `- If repeated attempts produce the same underlying failure…` |
| **A user file can replace the layout.** New session setting `promptConfigPath` (default `""`); when set, the file is parsed with the same schema (`id`, `format` xml or md, `sections`, optional `toolOverrides` per tool id) and used for the task. | behaviour | anchor `promptConfigPath` MISSING in 2.1.0; session defaults object 2.2.0 `…,profileId:"",promptConfigPath:""` |
| `project_rules` groups are XML now. 2.1.0 rendered `## Workspace Rules for "<mode>" mode`, `## Workspace Rules`, `# Project Instructions (AGENTS.md)`, `## Global Rules for "<mode>" mode`, `## Global Rules` as markdown headings. 2.2.0 renders, in the same order, `<workspace_rules_<mode>>`, `<workspace_rules>`, `<agents_md>`, `<global_rules_<mode>>`, `<global_rules>`, each holding `<rule>\n  <filename>…</filename>\n  <content>…</content>\n</rule>` entries. The preamble ("take precedence over your training defaults … mode-specific rules override common rules") is unchanged. | artefact (rendering); the note's anchor must move from `Project Instructions (AGENTS.md)` to `agents_md` | anchor `Project Instructions (AGENTS.md)` MISSING in 2.2.0; anchors `agents_md`, `workspace_rules`, `global_rules` MISSING in 2.1.0; anchor `take precedence over your training defaults` SAME string (468 chars) |
| `available_skills` has a preamble and is a `list` section: `You have access to skills that provide specialized instructions… Only activate skills that are clearly relevant… Activate each skill once per current context window…` (the same sentences existed in 2.1.0 as separate strings). | artefact | removed strings `<available_skills>⏎`, `Review the available skills below…`; added string `You have access to skills that provide specialized instructions for specific tasks. Review the available skills below…` |
| Mode-switching guidance (`# Mode Switching`, "Stay in your current mode unless there is an explicit, compelling reason to switch") is the same text, stored as an array of lines instead of one template. | artefact | anchor `Stay in your current mode` EDITED 609 → 113 chars; the 2.1.0 paragraph contains the 2.2.0 lines verbatim |
| Subagent guidance block ("Default: do the work yourself", "Do NOT use subagents for") unchanged. | identical | anchors `Default: do the work yourself`, `Do NOT use subagents for` SAME string |
| `/init` prompt unchanged (12 457 characters). | identical | anchor `AGGRESSIVELY` SAME string (12 457 chars); `INIT_BASE_PROMPT` MISSING is the export name only |
| Inline-answer rules of `create_html_artifact` unchanged (444 characters). | identical | anchors `answer those inline in markdown`, `only call this tool when the user has explicitly asked` SAME string |
| `update_todo_list` rules reworded: "Before starting the first task, call update_todo_list to mark it [-] in-progress" and "Exception: the very first task may be marked [-] in a standalone call" replace "Do not call update_todo_list to mark a task [-] in-progress before you have started working on it". | behaviour (instruction) | paired string edits `Execute these one at a time. …` (ratio 0.66) and `- Do not … task [x] done. {+Exception: …+}` |
| `ask_followup_question` gains "Follow-up questions run one at a time: call this tool at most once per assistant turn and wait for the user's response". | behaviour (instruction) | paired string edit, ratio 0.73; changelog "Follow-up questions sequenced correctly" |
| Tool guidance blocks: `getSystemPromptPart` is defined 11 times in each build (the name occurs 17 → 15 times, the difference is call sites), and a prompt config may now override any tool's block (`toolOverrides`). Whether the text of each block changed was not checked block by block. | undetermined | counts of the method name; direct read of the `tools` section renderer |

### 2. Rule loading and precedence

| Difference | Class | Evidence |
|---|---|---|
| **`plugins/` subdirectory.** The workspace rule roots are `.bob/` plus every directory (or symlink) under `.bob/plugins/`, sorted by name; each root contributes `rules/**` and `rules-<mode>/**`. Global roots likewise: `~/.bob/` plus `~/.bob/plugins/*/`. Modes read `{custom_modes.yaml,plugins/*/custom_modes.yaml}` (global: `{settings/custom_modes.yaml,plugins/*/custom_modes.yaml}`), MCP reads `{mcp.json,plugins/*/mcp.json}`. Precedence between roots: `.bob/` first, then plugins alphabetically; between kinds unchanged (workspace mode → workspace common → `AGENTS.md` → global mode → global common). | behaviour | anchor `plugins/*/` MISSING in 2.1.0; direct read of the loader (constants `"plugins"`, `"rules"`, `"rules-"`, `"AGENTS.md"`, depth 5, ignored names `.DS_Store Thumbs.db .gitkeep .gitignore .bobignore` identical); changelog "`plugins/` subdirectory for skills, modes, rules, and MCP" |
| **Skill directories narrowed to `plugins/`.** 2.1.0 read `.bob/skills/*/SKILL.md` and `.bob/*/skills/*/SKILL.md` (any one-level subdirectory of `.bob/`), plus `~/.bob/skills`, `~/.agents/skills`, `~/.claude/skills`. 2.2.0 reads `.bob/skills`, `.bob/plugins/*/skills`, `.agents/skills`, `.claude/skills` in the workspace, and for each of `~/.bob`, `~/.agents`, `~/.claude` both `<root>/skills` and `<root>/plugins/*/skills`. A skill kept under `.bob/<anything-but-plugins>/skills/` is no longer read. | behaviour | removed string `{skills/*,*/skills/*}/`; 2.2.0 path pieces `".bob","plugins","*","skills"` and `"plugins","*/skills"` read directly; changelog |
| Untrusted workspace → no rules at all (`agentsMd` undefined, empty lists): same code in both builds, and the same source of truth: both builds pass the IDE's `workspace.isTrusted` into the harness (`workspaceTrusted:`), which feeds the rule loader, workspace skills and custom agents. 2.1.0 also carried a `trustedFolders.json` / `TRUST_FOLDER` store whose `resolveFolderTrust` was defined but never called; it is gone in 2.2.0. `security.folderTrust.enabled` still defaults to `true`. | artefact (dead module removed); rules effect unchanged | anchor `trustedFolders.json` MISSING in 2.2.0; `isWorkspaceTrusted` MISSING is the export name; `workspaceTrusted:` present in both; direct read of the loader's first line in both builds |
| Rule file extensions, depth and the `AGENTS.md` root-only read: unchanged. | identical | direct read; constants above |

### 3. Subagents, tiers, custom agents

| Difference | Class | Evidence |
|---|---|---|
| **Custom agent frontmatter: `model:` is an error, `modelTier:` is validated.** 2.2.0 throws `"model" is not supported in <file>, use "modelTier" instead` and `Invalid modelTier "<value>" in <file>. Valid values: fast, premium, ultra, explorer`. 2.1.0 accepted `model` and ignored an unknown value. Consequence: bob-sideshow's shipped template `templates/agents/explore-premium.md` (`model: premium`) fails to load on 2.2.0. | behaviour, **breaks a shipped file** | anchors `use "modelTier" instead`, `Invalid modelTier` MISSING in 2.1.0; anchor `modelTier` CHANGED (19 real edits) |
| Other frontmatter fields unchanged: `name`, `description`, `groups` (default `read edit execute`), `maxTurns`, `rawPrompt`, `allowForkContext`, `allowTools`, `denyTools`; `## Output Constraints` still splits a trailer. | identical | anchors `allowForkContext`, `denyTools`, `rawPrompt`, `maxTurns` IDENTICAL; `## Output Constraints` present in both |
| Built-in `explore` preset identical after the field rename: `groups:["read"]`, `modelTier:"explorer"` (was `model:"explorer"`), `rawPrompt:true`, `maxTurns:50`, `denyTools:["update_todo_list","use_skill"]`, `allowForkContext:false`, same system prompt. | artefact (rename) | the two preset object literals are equal once `model:` is spelled `modelTier:`; anchor `Explore codebase` SAME string |
| Subagent runtime: the spawned task inherits the parent's model resolver and is given a tier (`setModelTier`) instead of a model (`setModel`); a `PreToolUse` event of the parent is forwarded to the child. Forbidden tools (`spawn_subagent start_subtask start_workflow switch_mode update_todo_list`) and groups (`subagent subtask`) unchanged. | behaviour (routing), plausibly the changelog's live tool results | anchor `SUBAGENT_FORBIDDEN_TOOLS` CHANGED (5 real edits: `setModelResolver`, `model → modelTier`, `setModel → setModelTier`, `onPreToolUse`) |
| Tier table unchanged: tiers `fast premium ultra explorer`, visible `fast premium ultra`, `fast` and `ultra` hidden outside dev mode, default `premium`; production mapping `fast → premium-ide`, `premium → premium-ide`, `ultra → premium-ide`, `explorer → explorer`. The dev-mode-only env override (`BOB_USE_MODEL_ENV` + `MODEL`) exists in both. | identical | the mapping object literal is byte-identical in both bundles; anchor `https://api.dev.bob.ibm.com` SAME string; `MODEL_TIERS`, `DEFAULT_MODEL_TIER`, `VISIBLE_MODEL_TIERS`, `isVisibleTier`, `getVisibleTiers` MISSING are export names |
| Two internal tiers appear: `security` and `background`, used for the command-security check and for helper calls (message classification, code summaries). Not user-selectable. | behaviour (see approval path) | direct read: constants `"security"`, `"background"` next to the tier list |
| Subagent line in the guidance now prints `(<groups> tools, <modelTier ?? "default"> model)`. | artefact | direct read of the preset formatter |

### 4. Tool set

| Difference | Class | Evidence |
|---|---|---|
| **New tool `web_fetch`** ("Use this tool only when completing the user's request requires reading the contents of a specific public HTTP or HTTPS page…"), in a **new permission group `browser`** ("Let Bob access external web resources for this task"), added to the Agent mode's groups between `execute` and `mcp`. | behaviour | anchors `web_fetch`, `Let Bob access external web resources` MISSING in 2.1.0; Agent mode groups literal `["read","edit","execute","browser","mcp","skill","todo","artifact","subtask","subagent","mode"]` |
| **`execute_command` gains `background: true`**: the process is started detached, stdout and stderr go to `bob_execute_command_<id>.log` under a `processes` temp directory, the tool returns at once with the pid and the log path; UI lists "Running background processes" and offers to stop one. The 2.1.0 sentence "This tool only runs commands that are expected to terminate" is gone. | behaviour | anchor `When true, runs the command in the background` MISSING in 2.1.0; paired string edit of the `cwd` paragraph (ratio 0.75); changelog "Background process indicator with stop control" |
| All other tool-name literals present in both: `apply_diff ask_followup_question create_chart create_html_artifact end_subtask execute_command glob grep insert_content list_files office_read read_file run_pase_command search_and_replace skill spawn_subagent start_subtask start_workflow switch_mode update_todo_list use_skill write_file`. | identical | string set intersection |
| Outside-workspace refusal text: "Enable \"Allow outside workspace tool requests\" in settings." replaces "This can be enabled in Settings > Chat Settings > Workspace sandbox". | artefact (wording) | paired string edit, ratio 0.78; `en.json` key `Allow outside workspace tool requests` added |
| MCP: client moved to protocol v2 (`SEP-2243`/`SEP-2352` strings, "pinning is for 2026-07-28 and later" revision negotiation, `OAuthClientProvider … discoveryState`); the "Configure MCP" and "Build a Custom MCP Server" skills now teach `"${env:MY_API_KEY}"` placeholders instead of warning that secrets are written verbatim. | behaviour (dependency + guidance) | 293 added strings tagged `mcp-sdk`; paired edits of `# Configure MCP` (0.87) and `# Build a …` (0.90); changelog "MCP client updated to v2", "MCP placeholder expansion and credential guidance" |

### 5. Settings schema and defaults

| Difference | Class | Evidence |
|---|---|---|
| **Compaction keys renamed**: `autoCondense` / `autoCondenseContext` → `autoCompact`, `autoCondenseContextPercent` / `compactionThreshold` → `compactionThresholdPercent`, all moved under `session`. A migration table in the code rewrites old files on read (`[session.autoCondense, chat.autoCondenseContext, root.autoCondense] → session.autoCompact; [session/chat.autoCondenseContextPercent, root.compactionThreshold] → session.compactionThresholdPercent`). Defaults unchanged: on, 90 %. | behaviour (key names; old files still work) | anchors `autoCompact` MISSING in 2.1.0, `autoCondense` / `autoCondenseContextPercent` CHANGED; session defaults `autoCondense:!0` → `autoCompact:!0`; log line `Compaction skipped — auto-condense disabled` → `auto-compact` |
| Session defaults otherwise identical (`defaultMode:"agent"`, `maxTurns:100`, `maxCost:0`, `mcp`, `subagents`, `maxReadFile:500`, `respectGitIgnore:false`, `profileId:""`) plus the new `promptConfigPath:""`. | identical + one addition | defaults object literals |
| `hooks` default gains `PreCompact:[]` and `PostCompact:[]` (seven events). | behaviour (see hooks) | defaults object; anchor `PostCompact` MISSING in 2.1.0 |
| Chat setting `chat.chatWidth` (default `"default"`). | behaviour (UI) | anchor `chatWidth` MISSING in 2.1.0; changelog "Configurable chat width" |
| Approval defaults identical: `autoApprovalEnabled:true`, `outsideWorkspaceAllowed:false`, `allowed_permissions:["read"]`, `permissionOptions:[]`, `allowedExecutors:[{toolId:"execute_command", approvedCommands:<defaults>, deniedCommands:[]}]`, `editApprovalPreviewMode:"editor"`, `forbiddenApprovalGroups:[]`, `isCommandSecurityEnabled:true`, `security.folderTrust.enabled:true`, `disableGlobalHooks:false`. | identical | anchors `approvedCommands`, `deniedCommands`, `outsideWorkspaceAllowed`, `isCommandSecurityEnabled` IDENTICAL; `autoApprovalEnabled`, `allowed_permissions`, `forbiddenApprovalGroups`, `disableGlobalHooks` SAME string |
| Group policy `RequiredExtensions`: "Comma-separated list of VS Code extension IDs (publisher.extension) that IBM Bob will automatically install from the marketplace on startup. Only applies in the IDE; ignored in shell." Policy hooks are "always applied in addition to" user hooks (was "run before any"). | behaviour (admin) | anchor `RequiredExtensions` MISSING in 2.1.0; paired edit of the policy-hooks description (0.76); changelog "Auto-install required extensions on startup" |
| Budget messages templated with `{{budget_limit}}`; new "Team Budget Exceeded" / "budget exceeded at team level". | behaviour (UI) | added strings; paired edits of the `Oh no! …` messages |

### 6. Approval path

| Difference | Class | Evidence |
|---|---|---|
| The three gates are the same code: `_alwaysAllowedTools` → `validateToolExecution` → `shouldAutoApprove`, and `isBobHomeWrite`. | identical | anchors `shouldAutoApprove`, `validateToolExecution`, `_alwaysAllowedTools` SAME LOGIC (2 interop artefacts, 352 tokens); `isBobHomeWrite` IDENTICAL (63 tokens) |
| Default approved commands identical: `cat`, `git diff`, `git log`, `git rev-parse`, `git show`, `git status`, `grep`, `head`, `tail`, `ls`, `sort`, `wc`, `which`, `du`, `df`. | identical | the two array literals are equal; `DEFAULT_APPROVED_COMMANDS` MISSING is the export name |
| Token matcher (`getBestCommandMatch`, `findLongestMatchingCommandPattern`): export names gone, the matcher is reached inside `validateToolExecution`, whose logic is SAME. Not re-read line by line here. | undetermined (for the note's table), gates unchanged | anchor `validateToolExecution` SAME LOGIC; the two export names MISSING |
| Edit-approval preview: `window.state.focused` → an `isWindowFocused` helper. | artefact | anchor `editApprovalPreviewMode` CHANGED (1 real edit) |
| **Security check, heuristics and flow unchanged**: the five always-on regex heuristics (`${var@P\|Q\|E\|A\|a}`, escaped payloads in `${…=…}` expansions, `${!name}`, here-string fed by `$(…)` or backticks, extglob `@(e:…:)`) are the same literals; the 5 000-character head/tail rule with its three tail patterns, the 15 s timeout, the `{dangerous, reason?}` schema and fail-closed on any error are the same. | identical | anchor `requiresSecurityApproval` CHANGED with 4 real edits, none of them in the heuristics; regex literals located in both; anchors `needs manual verification`, `Command is too complex` SAME string |
| **Security model chosen elsewhere.** 2.1.0: `commandSecurityModel` read from server flag `command-security-model`, hard-coded fallback `openai/gpt-oss-20b`, passed to the provider. 2.2.0: the check asks for tier `"security"`; the provider resolves a tier by POSTing `{model:"router", messages, metadata:{model_tier:"security"}}` to `/chat/completions` and uses the model id the server answers with; if the router fails, the local tier table is consulted (it has no `security` entry) and the fallback is `premium-ide`. The flags `command-security-model` and `summary-model` are no longer read at all (`getFlagValue` keys: 10 on 2.1.0, 8 on 2.2.0). | behaviour | anchors `openai/gpt-oss-20b`, `commandSecurityModel`, `command-security-model` MISSING in 2.2.0; anchor `getCommandSecurityEnabled` CHANGED (`commandSecurityModel: getFlagValue("command-security-model")` deleted); direct read of `resolveModelForTier` |
| The security prompt was split: 2.1.0 sent one user message with the context, categories, `Command to analyze: … Working directory: …` and the empty system prompt; 2.2.0 sends the context and categories as the system prompt and the short `Command to analyze … Working directory … {IGNORE_SECTION}` block as the user message. Same words. | artefact | anchor `make install` EDITED 7 714 → 7 603 chars, ratio 0.99 (the one edit is that block); anchor `Command to analyze` EDITED 7 714 → 86 chars (escaped length) |
| Server flag schema: `command-security-enabled`, `completion-model`, `next-edit-model`, `feedback-model` still declared; `command-security-model` and the `experiment-*-tool-model-routing` keys gone. | behaviour (flags) | anchors `command-security-model`, `tool-model-routing` MISSING in 2.2.0; `featureFlagsSchema` MISSING is the export name |

### 7. Hooks

| Difference | Class | Evidence |
|---|---|---|
| **Seven events**: `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `PreToolUse`, `PostToolUse`, `Stop` (was five). `SessionStart.source` is `startup`, `resume` or `compact`; `PreCompact` carries `trigger` (`manual`/`auto`) and `custom_instructions`; `PostCompact` carries `trigger` and `compact_summary`. After a successful `PostCompact`, `SessionStart` hooks run again with source `compact`. | behaviour | word diff of the `# Configure Hooks` skill text (anchor `hook_event_name` EDITED 9 305 → 13 359 chars); hooks defaults object; anchor `PostCompact` MISSING in 2.1.0 |
| **HTTP handlers**: `{"type":"http","url":"https://…","headers":{…},"allowedEnvVars":[…],"timeout":N}` next to `command` handlers; the payload is POSTed as JSON; header values may reference `$VAR`/`${VAR}` only for names in `allowedEnvVars`; non-2xx, redirects, errors and timeouts fail open. | behaviour | anchor `allowedEnvVars` MISSING in 2.1.0; `# Configure Hooks` diff; changelog "HTTPS hook handlers" |
| **Structured JSON output is parsed.** A stdout (or 2xx body) starting with `{` is parsed: `hookSpecificOutput.updatedInput` replaces the tool input before validation and approval; `permissionDecision: "deny"` with `permissionDecisionReason` blocks; `{"decision":"block","reason":…}` blocks `UserPromptSubmit`; `additionalContext` adds model context for `SessionStart`, `UserPromptSubmit`, `PostToolUse`. Plain text on `PreToolUse` is now ignored with the warning `Ignoring invalid PreToolUse hook output`. 2.1.0 stated "Bob does not parse structured JSON hook output". | behaviour | anchors `hookSpecificOutput`, `permissionDecision`, `updatedInput`, `Ignoring invalid PreToolUse hook output` MISSING in 2.1.0; anchor `hooks cannot block` CHANGED (6 real edits: the `startsWith("{")` branch and the `PostCompact` case) |
| Exit-code semantics: exit 2 blocks `UserPromptSubmit`, `PreToolUse` and now `PreCompact` (`Compaction was rejected by a configured hook`); it cannot block `SessionStart`, `PostToolUse`, `Stop` and now `PostCompact` (`<event> hooks cannot block`); stderr, else stdout, else `<event> blocked by hook` is the reason; other non-zero codes are logged and ignored; 10 s default timeout, 1 MB output. | behaviour (one event added to each list), rest identical | anchor `hooks cannot block` CHANGED; the 2.1.0 function body read directly |
| Payload keys `session_id`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`, `tool_response`, `last_assistant_message`, `prompt` unchanged; hook commands still "execute directly and do not use Bob's normal command-approval flow". Whether hooks run for subagent tasks was not re-checked. | identical | property tokens present in both; `# Configure Hooks` diff shows no change to those lines |

### 8. Database

| Difference | Class | Evidence |
|---|---|---|
| **New table `key_value_store (key TEXT PRIMARY KEY, value_json TEXT NOT NULL)`**, migration `011_key_value_store`, written with `INSERT INTO key_value_store (key, value_json) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json`. On the snapshot it holds one row, key `featureFlags.v1` (a 2 020-character JSON): the server feature flags are now cached in the database. | behaviour | anchors `key_value_store`, `011_key_value_store` MISSING in 2.1.0; `_migrations` rows 001…011 on the snapshot |
| The four other `CREATE TABLE` statements (`tasks`, `messages`, `attribution_logs`, `task_pending_approvals`) and `INSERT INTO attribution_logs` are byte-identical; migrations 001…010 identical. | identical | anchors `CREATE TABLE IF NOT EXISTS tasks` SAME string (1 143 chars), `INSERT INTO attribution_logs` SAME string, `010_pending_approvals`, `task_pending_approvals` SAME string |
| Whether `messages.data` still carries `_meta.spend` per call and the same unit prices: not decidable from the bundle. | undetermined (needs 2.2.0 traffic) | — |

### 9. Libraries, telemetry, build, activation

| Difference | Class | Evidence |
|---|---|---|
| Removed dependencies: PostHog (99 strings → 1), LangChain / LangGraph / LangSmith (1 712 removed strings), parse5, highlight.js keyword tables, jsonpatch, part of tiktoken. Added: gRPC with protobuf (386 strings), MCP SDK v2 (293), and a much larger OTLP trace exporter (`OTLPTraceExporter` 3 → 18 occurrences) with new validation messages for the `OTEL_EXPORTER_OTLP_*` variables — the variables themselves were already read on 2.1.0. The optional `@e2b/code-interpreter` import exists in both builds (only its install hint changed). This is most of the 4.1 MB. | artefact (dependency) for Bob's behaviour; telemetry backend changed | origin-tagged removal/addition counts; literal counts in both bundles |
| CommonJS → ESM, identifier renames, constants reordered, the Jenkins path literal suffix. | artefact | counts in the method section |
| `activate()` wiring: 46 real edits (workspace URIs and trust passed into the harness, review panel registered later, `openWorkspace` command, `Development mode is enabled` log). The `Extension activated` log line and the `bob-code.sendMessageWithHiddenPrompt` command survive. What the returned API object exposes was not re-read. | undetermined (matters to the benchmark harness, not to the skills) | anchor `Extension activated` CHANGED (46 real edits); anchor `bob-code.sendMessageWithHiddenPrompt` SAME string |
| Webview reply channel and pending approvals unchanged. | identical | anchors `handleUiReply` IDENTICAL (42 tokens), `task_pending_approvals` SAME string |

## The vendor changelog against the bundle

**Announced and confirmed in the bundle**: `RequiredExtensions` policy; `plugins/` for skills, modes,
rules and MCP; MCP client v2; background processes with stop control;
configurable chat width; HTTPS hook handlers; MCP placeholder guidance (`${env:VAR}`); follow-up
questions one at a time. "Live subagent tool results" has a plausible trace (`onPreToolUse`
forwarded to the child task) but no literal proves the UI behaviour.

**In the bundle, silent in the changelog**: the `modelTier` frontmatter error (breaks existing
`.bob/agents/*.md` files that say `model:`); structured JSON hook output (`updatedInput`,
`permissionDecision`, `additionalContext`) and the two compaction events; the renamed compaction
settings; the `web_fetch` tool and `browser` group; the model-dependent prompt layouts and
`promptConfigPath`; the security model now resolved by a server router for tier `security`
instead of a flag with a `gpt-oss-20b` fallback; PostHog and LangChain removed, gRPC/OTLP added;
`key_value_store` caching the feature flags; the new prompt discipline sentences.

**Announced and not located**: "Host tools refreshed when reopening cached tasks", "Tool result
images displayed correctly", "Virtual workspace detail preserved in workspace picker" (an
`openWorkspace` / `getFileWorkspaces()` change in activation is the nearest trace), "File watching
and search on remote workspaces". These live in the webview or in VS Code API calls with no
distinctive literal; nothing in bob-sideshow depends on them.

## Why the 2.1.0 build was retrieved, and what the diff changed

Decision: retrieve the 2.1.0 build from the update endpoint recorded in `product.json` rather than
reconstruct the delta from the notes. Reason: the notes are a description of 2.1.0, claim by claim,
and testing them against 2.2.0 alone can only say "the literal is still there" or "it is gone";
it cannot tell a disappeared export name from a removed feature, nor a moved sentence from a
rewritten one. With both bundles, every "gone" becomes a verdict. The fetch is a signed
application archive from the vendor's own update endpoint, the same bytes the IDE downloads to
update itself; no other network access was used.

What the diff gave that the notes could not:

- The CommonJS → ESM explanation for the dozen vanished landmarks, with counts. Without it the
  milestone would have re-read a dozen facts that never changed.
- IDENTICAL / SAME LOGIC / SAME-string verdicts on the approval gates, `isBobHomeWrite`,
  the approval defaults, the default command list, the subagent guidance, the rules preamble, the
  `/init` prompt, the artefact rules, the tier table, the agent frontmatter fields, the `attribution_logs`
  insert: these claims are confirmed, not re-worded.
- The precise edits behind each CHANGED verdict: the `modelTier` error, the hook parser's
  `startsWith("{")` branch, the deleted `commandSecurityModel ?? "openai/gpt-oss-20b"` line, the
  settings migration table, the `onPreToolUse` forwarding.
- Negative results that a single bundle cannot give: the security heuristics, the head/tail rule
  and the fail-closed path are the same literals in both.

What would change if the exact build of the notes (SHA-1 `d8b1130e…`, suffix `20260827055214`) were
diffed instead of the one-second-later packaging run used here: nothing in the findings. The two
2.1.0 archives share version, commit `a8240f78e496…` and build date; the 9-byte difference is
accounted for by the Jenkins path literal, and no verdict above rests on that literal. If a
future diff against that exact file showed any other difference, the affected verdicts would be
those on the anchors listed in this page, and the tool would report them; the noise floor of the
method is therefore "one path literal", not "unknown".

## Facts the 2.1.0 notes assert that this delta neither confirms nor refutes

For TASK-13.1 and TASK-13.2: re-read these on the build, do not re-word them.

1. **Rule precedence inside a root.** The order across kinds is confirmed; the order between
   `.bob/rules/` and `.bob/plugins/<name>/rules/` is read from the loader (`.bob/` first, plugins
   alphabetically) but was not exercised with files. The `<agents_md>` tag replaces the
   `# Project Instructions (AGENTS.md)` heading: `injected-rules.md` must re-anchor on `agents_md`,
   `workspace_rules`, `global_rules`.
2. **Prompt layout in `injected-rules.md`.** The section list is per model config now; which
   config a production task gets (`default`, `boreas`, `aquarius` or `orion`) can only be seen on a
   prompt stored by 2.2.0. `dump_system_prompt.py` splits on `^<tag>\n…\n</tag>` blocks and on
   `</environment_info>`; both survive in `xml` format, but new tags (`task_execution`, `when_stuck`,
   `act_and_iterate`, `ground_truth`, `define_done`, `prove_done`) and nested `<workspace_rules>` /
   `<agents_md>` groups inside `project_rules` must be checked on a real dump.
3. **Where the security model is chosen.** The bundle says: server router, tier `security`,
   fallback `premium-ide`. The server still pushes `command-security-model` (seen in the IDE's
   state store); whether the router answers with that same model or another is not visible
   locally. `approvals.md` must stop citing `openai/gpt-oss-20b` as the model and cite the tier.
4. **Unit prices.** Two flat rates on 2.1.0 (2.0 and 0.833 Bobcoins per million tokens) were
   measured on the database, never read in the code. Nothing in the diff touches pricing; the
   rates have to be re-measured on calls made by 2.2.0.
5. **`bob_version.py` server flags.** The flag cache read from the IDE state store still exists,
   but 2.2.0 also writes `featureFlags.v1` into `key_value_store`; which one is authoritative, and
   whether the schema keys `command-security-model` / `summary-model` still arrive, is a database
   question.
6. **Token matcher table in `approvals.md`** (prefix by tokens, case-sensitive, no wildcards,
   longest wins, tie → allow): the gate around it is SAME LOGIC and the default list is identical,
   but the matcher body itself was reached only through export names and was not re-read; the
   six-row example table and `approval_check.py` must be checked against the 2.2.0 function.
7. **`general` subagent preset** (current mode's tools, parent tier, 25 turns): no `maxTurns:25`
   literal exists in either bundle; the figure was read elsewhere on 2.1.0 and needs a source.
8. **Command-to-skill migration** (`command-migration.md`): none of its literals were anchored
   here; the migrator's globs may have gained `plugins/` too.
9. **Untrusted-folder behaviour**: the loader returns no rules when untrusted in both builds and
   the decision comes from the IDE's `workspace.isTrusted` in both; what the IDE prompt does with
   `security.folderTrust.enabled` is not in the bundle and was not exercised.
10. **`Extension activated` API surface** for the benchmark harness (milestone m-0): 46 edits in
    `activate()`, not re-read.

## Re-checking on the next build

The anchors that carried this page, to grep in a future `extension.js` before trusting any of
it: `Default: do the work yourself`, `take precedence over your training defaults`, `agents_md`,
`plugins/*/`, `use "modelTier" instead`, `Explore codebase`, `https://api.dev.bob.ibm.com`,
`shouldAutoApprove`, `validateToolExecution`, `isBobHomeWrite`, `requiresSecurityApproval`,
`Command is too complex`, `hooks cannot block`, `Ignoring invalid PreToolUse hook output`,
`hookSpecificOutput`, `allowedEnvVars`, `web_fetch`, `When true, runs the command in the background`,
`autoCompact`, `promptConfigPath`, `RequiredExtensions`, `key_value_store`, `Extension activated`,
`bob-code.sendMessageWithHiddenPrompt`. None of them is an export name.
