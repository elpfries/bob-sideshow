# Claude Code vs Bob: the same five questions

Companion to [cursor-vs-bob.md](cursor-vs-bob.md). bob-sideshow answers five questions about IBM
Bob: which version am I running, what did it cost, why does it ask for approval, which rules does
it follow, and how do I make it follow mine. This note asks the same five questions of Claude Code.

Verified on Claude Code 2.1.274, the build shipped inside the VS Code / Cursor extension
`anthropic.claude-code-2.1.274-darwin-arm64`, macOS. Same method as for Bob and Cursor: the
shipped binary, the local transcripts and the settings; no private API, no network capture.
Claude Code releases several times a week, so every path and field below is "true on this build".

## Where Claude Code keeps things

One program, not two. The extension ships a single native binary (`resources/native-binary/claude`,
214 MB, a Bun-compiled Mach-O) and the CLI install under `~/.local/bin/claude` is the same
program. It is not a JavaScript bundle you can read directly, but `strings` on it yields every
prompt, setting description and error message, which is enough for the same literal-search method
used on Bob.

| Path | What it holds |
|---|---|
| `~/.claude/projects/<cwd-slug>/<session>.jsonl` | one transcript per session: every message, tool call, tool result, with model and token usage |
| `~/.claude/projects/<cwd-slug>/<session>/subagents/agent-<id>.jsonl` | one transcript per subagent |
| `~/.claude/settings.json`, `~/.claude/settings.local.json` | user settings: permissions, hooks, model, effort |
| `<project>/.claude/settings.json`, `.claude/settings.local.json` | project settings, same schema; `.local` is meant to stay out of git |
| `/Library/Application Support/ClaudeCode/managed-settings.json` | organisation settings (also MDM plist or server-managed); absent on this machine |
| `~/.claude/CLAUDE.md`, `<project>/CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/*.md`, `~/.claude/rules/*.md` | instruction files |
| `.claude/agents/*.md`, `~/.claude/agents/*.md` | custom subagents |
| `.claude/skills/<name>/SKILL.md`, `~/.claude/skills/` | skills |
| `~/.claude/history.jsonl`, `file-history/`, `sessions/`, `plans/` | prompt history, file backups for rewind, live session records, plan files |

## 1. Which version am I running?

`claude --version` prints it. The extension folder name carries the version too, and the last ten
extension versions stay on disk (`~/.cursor/extensions/anthropic.claude-code-*`). Every transcript
record carries a `version` field, so an old session tells you which build produced it.

Feature flags are named `tengu_*` (3 294 occurrences in the binary); the ones evaluated for this
machine are cached in the IDE's state store under the key `Anthropic.claude-code`.

## 2. What did it cost?

The best-answered question of the three tools, better than Bob.

Every assistant message in a transcript carries `message.model` and `message.usage` with input
tokens, output tokens, cache reads, cache writes split by 5-minute and 1-hour TTL, thinking tokens,
service tier and speed. User records carry the permission mode in force; assistant records carry
the effort level and a request id. Subagent transcripts are separate files with `isSidechain: true`
and their own model, so parent and subagent are never mixed.

Bob stores a price per call and no model name; Claude Code stores the model name and no price.
The price is computed at display time (`/cost`, the Usage page, the SDK's `total_cost_usd`) from
Anthropic's list price, which an organisation can override per model or scale with a multiplier
(`modelPricing`, `inferenceModelPricing`). To rebuild a bill offline you need that price table;
it is not a single literal in the binary.

On this machine the transcripts hold 36 719 assistant messages across six models, and 227
subagent launches through the Agent tool (215 general-purpose, 9 Explore), 154 of them with the
model pinned to `sonnet` and 53 to `opus`. All of that comes from the JSONL files alone.

## 3. Why does it ask for approval?

**Rules.** `Tool(specifier)` strings in three lists, `allow`, `ask`, `deny`: for example
`Bash(npm run build)`, `Edit(docs/**)`, `Read(~/.zshrc)`, `WebFetch(domain:github.com)`,
`mcp__server__tool`. `*` is a wildcard; `Bash(npm run:*)` is the legacy prefix form. Deny
overrides allow. Rules come from eight sources, tagged in the binary: managed policy, user
settings, project settings, local settings, `--settings` flags, CLI arguments, the session
("always allow" answers) and the current command. Bob has one flat list per task plus one global
list; Claude Code layers them and lets an organisation pin the top layer.

**Modes.** `default` (ask for anything not allowed), `acceptEdits` (file edits auto-approved),
`plan` (read-only until the plan is accepted), `dontAsk`, `bypassPermissions` (Bob's "yolo",
which Bob's IDE does not have; can be disabled by managed settings), and `auto`.

**Model check.** `auto` mode is the counterpart of Bob's command-security model, and of Cursor's
Smart Auto: a classifier decides each call ("Allowed by auto mode classifier", "Denied by auto
mode classifier", "requires confirmation"). Its allow, soft-deny and hard-deny rule sections are
configurable, with `$defaults` to keep the built-ins. When auto mode starts, over-broad rules in
the user's allow list are stripped so they cannot bypass the classifier: `Bash(python:*)`,
`Bash(sudo:*)`, any `Agent` rule. This session runs in `auto` mode.

**Shell parsing.** Commands are parsed with tree-sitter-bash before matching, as in Bob and
Cursor; compound commands are split and each part is checked.

**Sandbox.** Like Cursor, unlike Bob: `sandbox.enabled`, filesystem rules, a network proxy with
domain allow and deny lists and optional TLS termination, `autoAllowBashIfSandboxed`,
`allowUnsandboxedCommands`. Seatbelt (`/usr/bin/sandbox-exec`) on macOS, bubblewrap on Linux.
Managed settings can lock the filesystem rules so project settings cannot relax them.

## 4. Which rules does it follow?

**The system prompt is in the binary and readable.** "You are Claude Code, Anthropic's official
CLI for Claude", the "# Doing tasks" and "# Tone and style" sections, every tool description and
every built-in agent description are plain strings. That is the opposite of Cursor (prompt built
server-side, nothing local). It is not what Bob does either: Bob stores the assembled prompt with
each task, Claude Code stores nothing of the prompt in the transcript. So the text is available,
but not the exact assembly a given session received.

**Instruction files.** Four memory tiers: managed (policy), user (`~/.claude/CLAUDE.md`), project
(`./CLAUDE.md` or `./.claude/CLAUDE.md`), local (`./CLAUDE.local.md`), plus `.claude/rules/*.md`
at user and project level. A setting `excludedClaudeMdFiles` (picomatch globs) can drop user,
project and local files but never managed ones.

**AGENTS.md is not read by default.** The binary states it: "by default the engine reads CLAUDE.md
alone and a project with only an AGENTS.md is told so once". A bundled `agents-md` plugin adds a
`projectInstructions` option with three values: `claude` (default), `agents-fallback` (AGENTS.md
only where there is no CLAUDE.md), `both`. This is the mirror image of Bob, which reads AGENTS.md
and ignores CLAUDE.md. Both tools read the other's file, and `.cursor/rules`, `.cursorrules`,
Copilot, Windsurf and Cline rules, only during `/init`.

**Subagents.** Built-in types: `general-purpose` (all tools), `Explore` (read-only search),
`Plan` (read-only, "You CANNOT and MUST NOT write, edit, or modify any files"), `claude`
(catch-all) and `claude-code-guide`. Two details echo bob-sideshow's findings on Bob's `explore`:

- `Explore` is defined with `omitClaudeMd: true`: it never sees the project's instruction files,
  exactly like Bob's `explore` never sees project rules.
- Its model is `inherit` with an "inherit cap" that can route it to a cheaper model unless
  `CLAUDE_CODE_DISABLE_EXPLORE_INHERIT_CAP` is set. Unlike Bob, the cap is documented in a
  variable and the Agent tool takes an explicit `model` parameter (`sonnet`, `opus`, `haiku`,
  `fable`); `CLAUDE_CODE_SUBAGENT_MODEL` and `_FORCE` override it globally.

Custom subagents are Markdown files with `tools`, `model` and `permissionMode` front matter in
`.claude/agents/` or `~/.claude/agents/`. There is no "Default: do the work yourself" guidance;
the Agent tool description says when to reach for it and warns a dedicated agent not to
re-delegate its whole assignment.

**Vocabulary collision, again.** Bob confuses "create a task" with its `start_subtask` tool.
Claude Code has the same pair, `TaskCreate` and `Agent`, and ships a guard message for it:
"This call used Agent-tool parameters (`prompt`/`subagent_type`). TaskCreate adds an item to the
task list… To delegate work to a subagent, use the Agent tool instead." The collision is
recognised and caught at the tool boundary rather than left to the model.

## 5. How do I make it follow mine?

**Rules**: a CLAUDE.md or a file in `.claude/rules/`; managed policy files cannot be excluded.

**Hooks** live in the `hooks` key of any settings file, or in a plugin's `hooks.json`. Events on
this build: PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, Notification,
UserPromptSubmit, SessionStart, SessionEnd, Stop, StopFailure, SubagentStart, SubagentStop,
PreCompact, PostCompact, TaskCompleted, TeammateIdle, Elicitation, ConfigChange,
InstructionsLoaded, FileChanged, CwdChanged. Four hook types: `command`, `prompt`, `agent` (a
model evaluates the policy; Haiku unless a model is named) and `http`. A hook answers with JSON
(`permissionDecision`, `permissionDecisionReason`, `updatedInput`, `additionalContext`,
`continue`, `stopReason`, `systemMessage`) or with exit code 2, whose meaning depends on the event:
block the tool call and show stderr to the model (PreToolUse), stop the agentic loop (Stop),
erase the prompt (UserPromptSubmit). Bob has one event and one exit-code rule; Cursor has 22
events; Claude Code has 21 and the richest reply format. The binary also knows Cursor's
`~/.cursor/hooks.json` and `.cursor/hooks.json` paths, for import.

**Enforcement without a hook**: `deny` rules, `plan` mode, a read-only `permissionMode` on a
custom subagent, managed settings.

## What a "claude-sideshow" would and would not be

| bob-sideshow skill | Claude Code equivalent | Verdict |
|---|---|---|
| bob-version | `claude --version`, `version` field in every transcript record | trivial |
| bob-telemetry | JSONL transcripts: model and full token usage per message, subagents in separate files | worth porting; needs a price table to give money |
| bob-security-model | layered allow/ask/deny rules, six modes, auto-mode classifier, sandbox | worth porting; a "would this be auto-approved?" checker is feasible |
| bob-agent-rules | prompt and agent definitions readable in the binary; Explore skips CLAUDE.md and may be capped to a cheaper model | worth porting, closest to Bob's case |
| bob-override-rules | 21 hook events, `model` parameter on the Agent tool, env overrides, managed settings | mostly unnecessary: the overrides bob-sideshow writes for Bob are native settings here |

Open items: the exact matching semantics of `*` versus `:*` in permission rules, where the list
price table lives in the binary, and whether the assembled system prompt of a session can be
captured locally (`--debug` output or the SDK) rather than reconstructed from the binary.

## Landmarks

Literals that locate each subject in `strings <binary>`, to re-check on a new build.

| Literal | Locates |
|---|---|
| `You are Claude Code, Anthropic's official CLI for Claude` · `# Doing tasks` · `# Tone and style` | system prompt |
| `agentType:"Explore"` · `omitClaudeMd` · `CLAUDE_CODE_DISABLE_EXPLORE_INHERIT_CAP` · `CLAUDE_CODE_SUBAGENT_MODEL` | built-in subagents and their model |
| `TaskCreate adds an item to the task list` | Agent / TaskCreate vocabulary guard |
| `Permission rules must be in an array` · `prefix matching (legacy)` | permission rule syntax |
| `Allowed by auto mode classifier` · `stripDangerousPermissionsForAutoMode` | auto mode |
| `Exit code 2 - show stderr to model and block tool call` · `permissionDecision` · `hookSpecificOutput` | hook semantics |
| `managed-settings.json` · `first-wins` · `excludedClaudeMdFiles` | settings tiers and instruction file exclusion |
| `by default the engine reads CLAUDE.md alone` · `agents-fallback` | AGENTS.md policy |
| `sandbox.autoAllowBashIfSandboxed` · `/usr/bin/sandbox-exec` · `bubblewrap` | sandbox |
| `total_cost_usd` · `inferenceModelPricing` · `USD per million input tokens` | cost computation |
