# Cursor vs Bob: the same five questions

bob-sideshow answers five questions about IBM Bob: which version am I running, what did it
cost, why does it ask for approval, which rules does it follow, and how do I make it follow
mine. This note asks the same five questions of Cursor and says where the answers are, where
they are the same as Bob's, and where the question has no answer.

Verified on Cursor 3.19.13 (IDE build of 2026-09-04, commit `dd066f33`) with the agent runtime
`2026.09.15-d2fe57e`, macOS. Same method as for Bob: read the shipped files, the local
databases and the settings; no private API, no network capture. Cursor updates itself often,
so treat every path and field below as "true on this build".

## Where Cursor keeps things

Unlike Bob, Cursor's agent is split in two programs:

| Program | Where | Role |
|---|---|---|
| IDE | `Cursor.app/Contents/Resources/app/out/vs/workbench/workbench.desktop.main.js` (37 MB, minified, string literals intact) | chat UI, settings, approval dialogs |
| Agent runtime | `~/Library/Application Support/Cursor/User/globalStorage/anysphere.cursor-agent-worker/agent-cli/.local/share/cursor-agent/versions/<version>/index.js` (8.6 MB) | loads rules, runs hooks, applies the allowlist and the sandbox; also the `cursor-agent` CLI |

Local state:

| File | What it holds |
|---|---|
| `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` | every conversation, message and tool call (SQLite, tables `ItemTable`, `cursorDiskKV`, `composerHeaders`) |
| `~/.cursor/ai-tracking/ai-code-tracking.db` | which lines of each commit were written by Tab, by the agent, or by hand |
| `~/.cursor/cli-config.json` | CLI settings: allowlist, approval mode, sandbox, subagent model |
| `~/.cursor/skills-cursor/` | Cursor's own built-in skills (24 on this build) |
| `~/Library/Application Support/Cursor/User/settings.json` | editor settings, a few `cursor.*` keys |

## 1. Which version am I running?

Same answer as for Bob: `product.json` and `Info.plist` inside the app give the IDE version.
The agent runtime has its own version, updated on its own; the last five builds stay on disk
under `versions/` and a symlink points at the current one.

Server-pushed feature flags are readable in clear in the runtime bundle (for example
`explore_subagent: true`, `shell_subagent: true`, `explicit_subagent_models: false`) and in
`~/.cursor/statsig-cache.json`.

## 2. What did it cost?

Partly answerable. The local database records, per conversation:

- every tool call with its name, status and duration (on this machine: 1 355 terminal
  commands, 896 file reads, 33 subagent launches, …);
- the model the user selected, and the model of each subagent;
- how full the context is, with an estimate per category (system prompt, tool definitions,
  rules, skills, MCP, subagent definitions, conversation);
- lines added and removed.

The code-tracking database goes further than anything Bob has: for each commit it scores how
many lines came from the agent, from Tab, or from a human.

What is missing, and cannot be recovered: **cost and token counts per call**. The fields exist
in the schema but are empty. When the model is "Auto" the server picks the real model and does
not write the choice back. Bob's trick of inferring the model class from the unit price has no
equivalent.

## 3. Why does it ask for approval?

Very close to Bob, with more knobs.

**Modes.** Ask Every Time, Allowlist, Allowlist with sandbox, Smart Auto, Run Everything.
The IDE stores them in `composerState` (allowlist, denylist, delete protection, outside-workspace
protection, MCP protection). The CLI stores them in `cli-config.json` with patterns such as
`Shell(ls)` or `Mcp(server, tool)` and an `approvalMode` of `allowlist`, `unrestricted` or
`auto-review`.

**Shell decision** (reconstructed from the runtime): the command is split into sub-commands with
tree-sitter-bash; every sub-command must be allowlisted; a team denylist and, when delete
protection is on, any `rm` are hard denies; a hook can force a prompt. Each refusal is tagged
(`not_allowlisted`, `delete_protection`, `blocked_by_hook`, `in_blocklist`) and that tag is what
the analytics see. The exact pattern-matching rule of the allowlist was not extracted; the
settings UI says an empty shell allowlist makes every command ask.

**Protected files.** Bob never auto-approves a write to its own settings. Cursor has the same
guard, hard-coded, over `.cursor/**/cli.json`, `mcp.json`, `permissions.json`, `.git/hooks/**`,
`.git/config` and the system certificate bundles. Rule files (`.md`, `.mdc`, `.cursorrules`)
under `~/.cursor/` are exempt.

**Model check.** Bob sends every command to a small model that says "dangerous or not". Cursor
has the same thing as an optional mode, Smart Auto: "a server classifier auto-runs safe tool
calls and prompts for the rest". It is not layered on top of the allowlist by default.

**Sandbox.** Cursor can run commands inside a real sandbox (a Rust helper, `cursorsandbox`,
using seatbelt on macOS and bubblewrap on Linux) with three policies: workspace read-write,
workspace read-only, none. Network can be filtered with an allowlist and a decision log.
Temporary policies live in `~/.cursor/sandbox-policies/`. Bob has nothing comparable.

## 4. Which rules does it follow?

**The system prompt is not on disk.** Bob stores the full prompt it used with every task, and
bob-sideshow reads it. Cursor assembles the prompt on its servers: the request carries the
rules, the skills, the subagent definitions and a "system prompt spec", and the server does the
rest. Locally there is only a token estimate per section. The guidance blocks bob-sideshow
quotes ("Default: do the work yourself", "answer those inline in markdown") do not exist in
either Cursor bundle. A `dump_system_prompt` for Cursor is impossible.

**Rule files** are loaded by the runtime, in this order:

1. `.cursorrules` at the git root (legacy, treated as always-apply);
2. for the working directory and **every parent directory up to the filesystem root**:
   `.cursor/rules/**/*.mdc`, then `AGENTS.md`, then `CLAUDE.md` and `CLAUDE.local.md`
   (the last two only when "third-party extensibility" is enabled);
3. team rules pushed by the server, appended last.

`.mdc` front matter: `description`, `globs`, `alwaysApply`, plus `environments` /
`disabled-environments`. The runtime maps each rule to one of four kinds: global, file-globbed,
agent-fetched (has a description, no globs), manually attached. Files ignored by `.cursorignore`
are skipped. The server enforces a maximum rule length.

**Subagents.** Built-in types: general purpose, explore, shell, browser, computer use, debug,
and a "cursor-guide" helper. Custom ones are Markdown files in `.cursor/agents/` (project,
higher priority) or `~/.cursor/agents/` (user), with `name`, `description`, `tools`, `model`
and `permissionMode` (`default` or `readonly`). The explore subagent's model is a setting:
Cursor's default, inherit the parent's, a pinned model, or disabled. On this machine it is
disabled. The problem bob-sideshow works around for Bob (explore wired to the economy model)
is a checkbox in Cursor.

**Skills.** `.cursor/skills/` in the project, a synced "Agent Store" for the user, and
`~/.cursor/skills-cursor/` for Cursor's own. Those built-in skills (`create-rule`,
`create-hook`, `create-subagent`, `update-cli-config`, `migrate-to-skills`, …) document Cursor
from the inside, which is the job bob-sideshow does for Bob. `migrate-to-skills` converts rules
and slash commands into skills; Bob does the opposite conversion silently at every start.

## 5. How do I make it follow mine?

**Rules**: same answer as for Bob, a Markdown file in the right folder, and the same caveat:
rules are instructions, not enforcement.

**Hooks** are where Cursor is far ahead. Bob has one pre-tool hook. Cursor has 22 events:
before and after a shell command, before and after an MCP call, before reading a file, after
editing, before the prompt is sent, session start and end, subagent start and stop, before
compaction, stop, after each response or thought, plus two for Tab. A hook lives in
`.cursor/hooks.json` (project) or `~/.cursor/hooks.json` (user), can be a script or a prompt
evaluated by a model, filters with a JavaScript regex `matcher`, can `failClosed`, and blocks
with exit code 2 or `{"permission": "deny"}`. The runtime also recognises and imports Claude
Code's `hooks.json` format. An admin `permissions.json` can disable Run Everything outright.

## What a "cursor-sideshow" would and would not be

| bob-sideshow skill | Cursor equivalent | Verdict |
|---|---|---|
| bob-version | app `product.json` + runtime `versions/` + feature flags | worth porting |
| bob-telemetry | `state.vscdb` tool calls, models, context fill; `ai-code-tracking.db` | worth porting, without cost |
| bob-security-model | allowlist, protections, Smart Auto, sandbox, hook refusal tags | worth porting, richer than Bob's |
| bob-agent-rules | rule loading order and subagent definitions only | half: no system prompt to dump |
| bob-override-rules | rules, 22 hook events, native subagent-model setting | mostly unnecessary: Cursor ships its own `create-rule` / `create-hook` / `create-subagent` skills |

Open items if this is pursued: the allowlist matching algorithm (not extracted), the format of
the `agentKv:blob:` entries (135 MB of recent conversation state), and whether any cost data
reaches the client at all.

## Landmarks

Literals that locate each subject, to re-check on a new build.

| Literal | Bundle | Locates |
|---|---|---|
| `LocalCursorRulesService` · `loadRulesFromDirAndAncestors` | runtime | rule loader and order |
| `alwaysApply` · `agentFetched` · `manuallyAttached` | runtime | rule kinds |
| `exploreSubagentModel` · `subagentModels` | runtime | subagent model setting and CLI config schema |
| `buildShellApprovalDecisionFacts` · `rmDeniedByDeleteProtection` · `Not in allowlist` | runtime | shell approval decision |
| `isHardcodedWriteProtected` · `permissions.json` | runtime | protected files |
| `beforeShellExecution` · `failClosed` · `exit code 2` | runtime, IDE | hook events and semantics |
| `sandbox-policies` · `workspace_readonly` · `insecure_none` | runtime | sandbox policies |
| `smart_mode_approval` · `--auto-review` | runtime | server classifier mode |
| `yoloCommandAllowlist` · `Run Everything` · `ALLOWLIST_MODE` | IDE | approval modes and their warnings |
| `promptTokenBreakdown` · `subagentTypeName` · `composerHeaders` | IDE | what the local database stores |
| `AgentRunRequest` · `system_prompt_spec` · `custom_system_prompt` | runtime | proof the prompt is built server-side |
