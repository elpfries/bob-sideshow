# Kimi Code vs Bob: the same five questions

Last of the series after [cursor-vs-bob.md](cursor-vs-bob.md), [claude-code-vs-bob.md](claude-code-vs-bob.md),
[opencode-vs-bob.md](opencode-vs-bob.md) and [codex-vs-bob.md](codex-vs-bob.md). bob-sideshow
answers five questions about IBM Bob: which version am I running, what did it cost, why does it
ask for approval, which rules does it follow, and how do I make it follow mine. This note asks
the same five questions of Moonshot's Kimi Code.

Verified on the VS Code extension `moonshot-ai.kimi-code` 0.7.5 (SDK `@moonshot-ai/kimi-code-sdk`
0.20.0), installed in Cursor minutes before this survey, macOS. No session has run and the Kimi
Code home does not exist yet, so everything comes from the shipped code. That code is unusually
readable: the extension bundle is unminified and keeps `//#region` markers naming every source
file of the `agent-core` package, so this note can cite modules, not just string literals. Kimi
Code is open source (Apache-2.0, github.com/MoonshotAI/kimi-code).

`Kimi.app` on this machine is the Kimi chat client (`com.moonshot.kimichat` 3.2.1), unrelated to
Kimi Code.

## Where Kimi Code keeps things

Since 0.6.0 the extension no longer launches a separate Python CLI: it runs the TypeScript "v1
engine" in-process through the Node SDK, inside `dist/extension.js` (10.7 MB). A "v2 engine" is
also bundled and is off by default (`kimi.useAgentCoreV1` and `KIMI_CODE_LEGACY_FLAG` pick the
engine). The terminal app shares the same home, config, login and sessions when both resolve
the same `KIMI_CODE_HOME`.

| Path | What it holds |
|---|---|
| `~/.kimi-code/` (or `$KIMI_CODE_HOME`) | the home; the older `~/.kimi/` is migrated on request |
| `~/.kimi-code/config.toml` | user config: providers, models, thinking, permission, hooks, subagent, secondary model, swarm, cron, tools |
| `~/.kimi-code/sessions/wd_<slug>_<sha256-12>/<session-id>/` | one folder per session, bucketed by working directory: `wire.jsonl` (every record), `context.jsonl`, `state.json`, `blobs/`; index in `session_index.jsonl` |
| `~/.kimi-code/AGENTS.md`, `~/.kimi-code/SYSTEM.md` | global instructions; a global replacement of the main agent's system prompt |
| `~/.kimi-code/agents/`, `~/.kimi-code/skills/`, `~/.kimi-code/plugins/installed.json` | user agents, skills, plugins |
| `<project>/.kimi-code/` | `AGENTS.md`, `agents/`, `skills/`, `mcp.json`, `local.toml` |
| `~/.agents/AGENTS.md`, `.agents/agents/`, `.agents/skills/` | vendor-neutral fallbacks, read alongside the branded folders |

VS Code settings are few: `kimi.yoloMode`, `kimi.showThinkingContent`, `kimi.editorContext`,
`kimi.useAgentCoreV1`. Everything that matters is in `config.toml`.

## 1. Which version am I running?

The extension version is in its folder name and `package.json`; the SDK version in the
changelog. There is no `kimi --version` here because there is no separate binary. Session
records carry a wire format version (`1.3`, `1.4`) with migrations, so an old session tells
you which record shape produced it.

## 2. What did it cost?

Tokens per model, money only if the provider says so.

A `UsageRecorder` accumulates, per model and per turn, input, output, cache-read and
cache-creation tokens, and logs a `usage.record` line into `wire.jsonl` with its model. The
session usage schema also has an optional `total_cost_usd`, a context size and a turn count.
Whether the cost field is filled depends on the provider adapter; the OpenAI-compatible adapter
only normalises `prompt_tokens`, `completion_tokens` and `cached_tokens` and sets no price. No
price table was found in the bundle. So: exact tokens per model from the local records, money
only when a provider reports it. Between Bob (price, no model) and Claude Code (model, no price),
Kimi Code sits on Claude Code's side.

The `wire.jsonl` also records permission decisions, mode changes and every tool call, so a
`bob-telemetry`-style script would read one file per session.

## 3. Why does it ask for approval?

**A policy chain, first answer wins.** The permission manager runs nineteen policies in a fixed
order and takes the first non-empty result. In order: a PreToolUse hook can deny; `AgentSwarm`
must be the only tool call in its turn; in `auto` mode `AskUserQuestion` is denied; plan mode
denies writes except to the plan file; user `deny` rules; `auto` mode approves; approvals given
earlier in the session; user `ask` rules; user `allow` rules; a review ask when leaving plan
mode or starting a goal; plan-mode tool approvals; **sensitive files ask** (`.env` and friends,
key files, with exemptions); **git control paths ask** (`.git/`); `yolo` mode approves; swarm
mode approves `AgentSwarm`; a built-in list of always-approved read-only tools (`Read`, `Grep`,
`Glob`, `WebSearch`, `FetchURL`, `Agent`, `AskUserQuestion`, `Skill`…); `Write` and `Edit`
inside the workspace of a git repository are approved; otherwise ask.

Three consequences. Bob's approved-command list is one policy among nineteen here. A user `deny`
rule beats `yolo`, unlike Bob where the allowed list is the whole story. And writes inside a git
repository never ask, on the reasoning that git is the undo.

**Modes.** `manual` (default), `auto`, `yolo`; the session can override the config value
(`defaultPermissionMode`). `auto` is not a classifier: it approves everything `yolo` does but
refuses to ask the user questions, which makes it the headless mode. There is no model-based
security check anywhere in the chain, and no sandbox.

**Rule syntax.** `Tool` or `Tool(args)`, tool name glob-matched with picomatch, argument pattern
glob-matched against a subject the tool defines (the command string for `Bash`, a path for file
tools, an id for task tools), `!pattern` to negate. In `config.toml` a rule is
`{tool, match, decision, reason}`, with `deny`, `allow`, `ask` shorthand lists; scopes are
`user`, `project`, `turn-override`, plus `session-runtime` for "approve for session" answers,
which are kept in memory and written to `wire.jsonl` so a resumed session restores them.

**Enforcement without the model.** `deny` rules, a `PreToolUse` hook, plan mode, a subagent
profile without write tools.

## 4. Which rules does it follow?

**Prompt in the bundle, and replaceable.** The default profile's prompt starts "You are Kimi Code
CLI, an interactive general AI agent running on a user's computer" and runs 18 KB: language
mirroring, minimal diffs, no git mutations without asking, a blast-radius rule for destructive
and outward-facing actions ("A one-time approval covers that one action in that one context,
not a standing license: unless a durable instruction (an `AGENTS.md` entry, or an explicit
request to operate autonomously) authorizes it in advance, confirm each time"), then
environment, project information, skills and plugin sections. There is no subagent-usage
section at all: that guidance lives in the tool descriptions and the subagent profiles.
`~/.kimi-code/SYSTEM.md` replaces this prompt outright for the default profile; a project
`agent.md` or `--agent-file` ranks above it. No other tool in this series lets the user swap the
whole system prompt from a file.

**Instruction files.** Discovery order: `~/.kimi-code/AGENTS.md`; `~/.agents/AGENTS.md` (or
`agents.md`); then for each directory from the project root (first parent with `.git`) down to
the working directory, `.kimi-code/AGENTS.md` and then `AGENTS.md` or `agents.md`. Root to leaf,
all concatenated, deduplicated by path, with a warning above 32 KB. CLAUDE.md is not read; a
bundled migration skill copies Claude Code and Codex instructions, skills and MCP settings into
the Kimi Code home on request, listing exactly which files it reads. Same stance as Bob's
`/init` and Codex's importer: read the competitor's files once, write your own.

**Subagents.** Profiles are YAML with `extends`, `tools`, `whenToUse`, `promptVars`,
`systemPromptPath` and a `modelPreference` of `primary` or `secondary`. Built in: `agent`
(main), `coder` (the only subagent with write tools), `explore` ("prompt-enforced read-only":
it has `Bash` but is told to use it only for read-only commands), `plan`. Custom ones live in
`.kimi-code/agents/` or `.agents/agents/` (project) and `~/.kimi-code/agents/` or
`~/.agents/agents/` (user). Two tools spawn them: `Agent` (one) and `AgentSwarm` (several in
parallel, one swarm per turn). Subagents can be foreground or background, with a two-hour
default timeout; background ones are tracked by `TaskList`, `TaskOutput`, `TaskStop`.

**The secondary model, Bob's economy tier made explicit.** `[secondary_model]` in `config.toml`
points at a `[models]` entry plus a subagent-only patch (`default_effort` sets the subagent
thinking effort); `KIMI_SECONDARY_MODEL` and `KIMI_SECONDARY_EFFORT` override it. A profile
declares whether it prefers the primary or the secondary model, and the `Agent` tool takes a
`model` parameter. Bob hard-wires `explore` to the economy model and hides it; Kimi Code makes
the same split a config section and a per-profile preference.

**Vocabulary.** The subagent tool is `Agent`, not `Task`. But `TaskList`, `TaskOutput` and
`TaskStop` manage background processes and subagents, and `TodoList` manages the plan, so
"task" and "todo" both exist as tool names; a tracker instruction saying "create a task" has no
tool to collide with, but "list the tasks" does.

## 5. How do I make it follow mine?

**Rules**: AGENTS.md at any level, `.kimi-code/AGENTS.md` for the project, `SYSTEM.md` to
replace the prompt itself.

**Permissions**: `[permission]` rules in user or project config, `deny` included, with the
guarantee that a `deny` outranks `yolo`.

**Hooks**: `[[hooks]]` entries in `config.toml` with `event`, `matcher`, `command`, `timeout`
(default 30 s, max 600). Sixteen events: PreToolUse, PostToolUse, PostToolUseFailure,
PermissionRequest, PermissionResult, UserPromptSubmit, Stop, StopFailure, Interrupt,
SessionStart, SessionEnd, SubagentStart, SubagentStop, PreCompact, PostCompact, Notification.
Hooks receive JSON on stdin with `hookEventName`, `sessionId`, `cwd` and the tool input; a
blocking result from PreToolUse becomes a deny with the hook's reason. No `hooks.json` file and
no exit-code table were found; the config section is the only source.

**Model routing**: `[secondary_model]`, `modelPreference` in a profile, the `model` parameter of
`Agent`.

## What a "kimi-sideshow" would and would not be

| bob-sideshow skill | Kimi Code equivalent | Verdict |
|---|---|---|
| bob-version | extension and SDK version, wire format version in records | trivial |
| bob-telemetry | `wire.jsonl` per session: usage per model, tool calls, permission decisions | ported as a development-only skill (`.kimi-code/skills/kimi-telemetry`, not shipped): usage per model and agent, tool calls; money only when the provider reports it |
| bob-security-model | the nineteen-policy chain, glob rules, sensitive-file and git-path asks | worth porting; the chain order is the thing to document |
| bob-agent-rules | prompt in the bundle, profiles in YAML, AGENTS.md discovery order | worth porting; the secondary model is the Bob parallel to explain |
| bob-override-rules | SYSTEM.md, permission rules, hooks, secondary model | unnecessary as a skill: every override is a file or a config key |

Open items: whether any provider adapter fills `total_cost_usd`, the subject string the `Bash`
tool hands to rule matching (the module was not isolated), and what the v2 engine changes in the
policy chain. Resolved by a live CLI session on 2026-09-19 (wire `protocol_version` 1.5): the
session folder holds per-agent wire files at `agents/<name>/wire.jsonl`, with `usage.record`
lines per turn (`inputOther`, `output`, `inputCacheRead`, `inputCacheCreation`), tool calls nested
in `context.append_loop_event`, and context sizes in `token_counting.measured` — read by the
development-only skill `.kimi-code/skills/kimi-telemetry`.

## Landmarks

Region names in `dist/extension.js` (`//#region ../../packages/agent-core/src/...`), to re-check
on a new build.

| Region or literal | Locates |
|---|---|
| `agent/permission/policies/index.ts` | the ordered policy chain |
| `agent/permission/matches-rule.ts` · `matchesGlobRuleSubject` | rule syntax and matching |
| `agent/permission/policies/file-access-ask.ts` · `isSensitiveFile` | sensitive files and git paths |
| `agent/permission/policies/default-tool-approve.ts` | always-approved tools |
| `permissionMode/configSection.ts` · `"manual", "auto", "yolo"` | modes |
| `session/hooks/types.ts` · `HookDefSchema` · `HOOKS_SECTION` | hook events and config |
| `profile/default/system.md` · `You are Kimi Code CLI` · `SYSTEM.md` | prompt and its override |
| `profile/default/agent.yaml` · `coder.yaml` · `explore.yaml` · `modelPreference` | subagent profiles |
| `config/secondary-model.ts` · `KIMI_SECONDARY_MODEL` | secondary model |
| `profile/agentfile/roots.ts` · `.kimi-code/agents` · `.agents/agents` | agent discovery roots |
| `AGENTS_MD_RECOMMENDED_MAX_BYTES` · `join$1(realHome, ".agents")` | instruction file discovery |
| `session/store/workdir-key.ts` · `"wire.jsonl"` · `agent/usage/index.ts` | session storage and usage |
| `config/path.ts` · `KIMI_CODE_HOME` · `".kimi-code"` | home resolution |
