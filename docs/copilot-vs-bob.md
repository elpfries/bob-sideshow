# GitHub Copilot vs Bob: the same five questions

Sixth of the series after [cursor-vs-bob.md](cursor-vs-bob.md), [claude-code-vs-bob.md](claude-code-vs-bob.md),
[opencode-vs-bob.md](opencode-vs-bob.md), [codex-vs-bob.md](codex-vs-bob.md) and
[kimi-code-vs-bob.md](kimi-code-vs-bob.md). bob-sideshow answers five questions about IBM Bob:
which version am I running, what did it cost, why does it ask for approval, which rules does it
follow, and how do I make it follow mine. This note asks the same five questions of GitHub
Copilot as it ships inside Visual Studio Code.

Verified on Visual Studio Code 1.145.0 (commit `a717861c`, built 2026-11-03) with its built-in
extension `copilot-chat` 0.73.0 (display name "GitHub Copilot", completions core 1.378.1799) and
the embedded Copilot CLI SDK `@github/copilot` 1.0.73, macOS. Same method as for Bob: read the
shipped files, the local databases and the settings; no private API, no network capture.

Two limits to keep in mind. The code facts below come from the 0.73.0 bundles. The stored-data
facts come from 111 chat session files written on this machine between April and November 2026;
the recent ones that were sampled were recorded by extension 0.54.0, and none was confirmed as
recorded by 0.73.0. Where a fact rests on stored data, the text says so.

## Where Copilot keeps things

Copilot is no longer an extension the user installs: it ships inside the application, at
`Visual Studio Code.app/Contents/Resources/app/extensions/copilot/` (139 MB), and the chat core
(approvals, sandbox, hooks, rule discovery) lives in VS Code itself. Nothing named Copilot
appears in `~/.vscode/extensions/`.

VS Code calls each agent runtime a harness, and this build has three for Copilot plus two guests:

| Harness | Where | Role |
|---|---|---|
| Local | `extensions/copilot/dist/extension.js` (19.7 MB, minified, string literals intact) plus `out/vs/workbench/workbench.desktop.main.js` (22 MB) | the agent of the chat panel: prompt, tools, subagents in the extension; approvals, sandbox, hooks, rule files in the workbench |
| Copilot Agent Host ("Background Agent", session type `copilotcli`) | `extensions/copilot/node_modules/@github/copilot/` (96 MB); `product.json` also pins a runtime `1.0.103-unstable` and an SDK `1.0.27-unstable` | the Copilot CLI runtime, run in a separate agent-host process |
| Cloud agent | GitHub's servers | asynchronous, works through pull requests |
| Claude, Codex (guests) | SDKs 0.3.304 and 0.163.0, downloaded on demand (`agentSdks` in `product.json`) | other vendors' agents hosted in the same agent-host process |

This note is about the Local harness. Most rule and hook settings state in their own description
"This setting is only used by the Local agent harness"; the Agent Host harness follows the
Copilot CLI's own conventions and was not surveyed.

Local state, under `~/Library/Application Support/Code/User/`:

| File | What it holds |
|---|---|
| `workspaceStorage/<id>/chatSessions/<uuid>.jsonl` | one file per chat session: requests, responses, tool calls, models, tokens |
| `globalStorage/emptyWindowChatSessions/` | the same, for windows with no folder open |
| `workspaceStorage/<id>/GitHub.copilot-chat/transcripts/<uuid>.jsonl` | an event log per session: `session.start`, `user.message`, `assistant.turn_start`, `assistant.message`, `tool.execution_start`, `tool.execution_complete` |
| `workspaceStorage/<id>/GitHub.copilot-chat/` | also `debug-logs/`, `memory-tool/memories/`, `chat-session-resources/` |
| `globalStorage/github.copilot-chat/session-store.db` | SQLite index of past sessions (`sessions`, `turns`, `checkpoints`, `session_files`, a full-text `search_index`) |
| `globalStorage/github.copilot-chat/{ask,plan,explore}-agent/*.agent.md` | the built-in agents, written out as ordinary agent files |
| `globalStorage/agent-host.db` | sessions of the agent-host harnesses |
| `settings.json`, `mcp.json`, `chatLanguageModels.json` | settings, MCP servers, bring-your-own-key models |
| `~/.copilot/` | home shared with the Copilot CLI: `config.json`, `session-state/`, `logs/`, and the personal folders `skills/`, `agents/`, `instructions/`, `hooks/` |

## 1. Which version am I running?

Three numbers, in three files. `product.json` gives the VS Code version, commit and build date,
and pins the Copilot CLI runtime and the guest SDK versions. `extensions/copilot/package.json`
gives the extension version and the completions core. `node_modules/@github/copilot/package.json`
gives the embedded SDK. Because Copilot ships with the editor, one VS Code update moves all of
them at once; there is no separate channel to watch, unlike Cursor's agent runtime.

Each stored request also records the extension version that produced it
(`requests[].agent.extensionVersion`), which is how this note knows its stored sessions are
older than its bundles.

## 2. What did it cost?

Answerable, in Copilot's own unit. Stored sessions (recorded by 0.54.0) hold, per request:

- the model asked for (`modelId`) and the dated model the server actually used
  (`result.metadata.resolvedModel`, for example `gpt-5.4-2026-03-05`), plus the model of each
  tool-call round;
- prompt and output tokens, thinking tokens per round, and a breakdown of the prompt by category
  with a percentage each (`promptTokenDetails`);
- a `copilotCredits` value, and the same number in the line shown under the answer
  ("GPT-5.4 • N credits");
- the price sheet of the selected model as the client received it: `inputCost`, `outputCost`,
  `cacheCost`, long-context variants, `multiplier`, `priceCategory`.

In the 0.73.0 bundle the number comes from the server: each response carries
`copilot_usage.total_nano_aiu`, and the debug view prints it as "AIC" after dividing by 10^9.
Subagent credits are tracked separately (`chat.subagents.showCreditUsage`).

So Copilot stores a price and a model, where Bob stores a price without a model and Claude Code
a model without a price. The catch is the unit: credits, not money. The conversion to a currency
and the meaning of the `inputCost` figures are not in the client.

The same file records how every tool call was approved (`isConfirmed`, a numeric kind and, for
remembered approvals, a scope such as `session`) and the permission level of each request, so
approval friction is measurable from local data alone. Usage can also be exported over
OpenTelemetry (`chat.agentHost.otel.*`), with organisation policies controlling whether content
and identity are captured.

## 3. Why does it ask for approval?

Rules first, like Bob, but with far finer patterns and no mandatory model check.

**Permission levels.** A picker per session: Default permissions ("Asks when approval settings
don't apply"), Allow all ("Auto-approve all tool calls and retry on errors"), Autopilot (Preview)
("continue until the task is done"). A fourth level, Assisted ("An LLM judge evaluates each tool
call. Tools it doesn't approve require your approval"), is in the code but not in the default
list; an organisation's managed settings can select it. The old global switch
`chat.tools.global.autoApprove` is described by its own setting text as "YOLO mode" and
"extremely dangerous". An agent turn stops to ask after `chat.agent.maxRequests` requests
(50 by default).

**Terminal commands.** `chat.tools.terminal.autoApprove` maps a pattern to `true`, `false` or
`null`. A pattern is a command prefix or a `/regex/flags`. The command line is split into
sub-commands and inline commands, and each one is tested: any deny rule wins; otherwise a rule
approved for the session, then an allow rule; no match means ask. A rule can instead target the
whole command line (`{ "approve": false, "matchCommandLine": true }`); both levels must be free of
denials, and one of them must be fully approved. VS Code ships 134 default rules (82 allow, 52 deny):
read-only commands allowed (`ls`, `cat`, `grep`, `git status`-style regexes, `docker ps`,
`npm ls`), and `rm`, `dd`, `kill`, `curl`, `wget`, `chmod`, `chown`, `jq`, `xargs`, `eval`
denied, with flag-level exceptions (`find` is allowed, `find -delete` and `find -exec` are not).
`chat.tools.terminal.ignoreDefaultAutoApproveRules` drops them. Scripts declared in the
workspace `package.json` are approved by default; a detected file write outside the workspace
(a redirection, `sed -i`) always asks.

Compared with Bob: Bob matches token prefixes without wildcards and resolves a tie to allow;
Copilot matches regexes per sub-command and resolves a tie to deny.

**File edits.** `chat.tools.edits.autoApprove` is a glob map where the last matching pattern
wins. By default every edit is approved except `.git/**`, `.env`, `package.json`, lock files,
project and build files, `.vscode/*.json`, and the agent's own configuration: `.mcp.json`,
`.github/agents/**`, `.github/hooks/**`, `.claude/agents/**`, `.claude/settings*.json`,
`.codex/config.toml`, `.codex/hooks.json`. Same guard as Bob's and Cursor's protected files, but
as an editable default, and extended to the other vendors' files.

**URLs and tools.** `chat.tools.urls.autoApprove` approves requests and responses separately;
`chat.tools.eligibleForAutoApproval` names tools that must always ask.

**Model check.** Advisory only. With `chat.tools.riskAssessment.enabled` (on by default) a small
model (`copilot-utility-small`) labels each confirmation Safe, Caution or Review carefully, with
one sentence of explanation. Its prompt is in the workbench bundle: deleting source code,
`curl | bash` and any package install are red; pushing or modifying local files is orange;
read-only is green. It informs the dialog and does not decide; an error yields no label and the
dialog appears as usual. Bob's check is the opposite design: it decides, and it fails closed.

**Sandbox.** `chat.agent.sandbox.enabled`, off by default, wraps terminal commands with
`@vscode/sandbox-runtime` 0.0.1 (a macOS profile, and bubblewrap plus `socat` on Linux, with a
seccomp filter and a local proxy for network rules). Settings cover allowed and denied network
domains, extra filesystem paths, and whether MCP and language servers run inside it. By default
a command blocked by the sandbox can be re-run outside it after confirmation
(`chat.agent.sandbox.allowUnsandboxedCommands`). Bob has nothing comparable.

## 4. Which rules does it follow?

**Prompt in the bundle, assembled in code.** The agent prompt is not one text: it is built from
components, and the opening "You are a highly sophisticated automated coding agent with
expert-level knowledge across many different programming languages and frameworks" appears ten
times, once per variant. Variants are picked by model family (`claude`, `gemini`, `grok`, and
six code names `vscModelA` to `vscModelF`), and experiments can switch between them. An advanced
user setting, `github.copilot.chat.omitBaseAgentInstructions`, drops the base instructions.

**Not stored per session.** A session keeps the rendered user message and a rendered global
context, not the system prompt. The full request is visible live in the chat debug view; writing
it to disk (`github.copilot.chat.agentDebugLog.fileLogging.enabled`) is off by default. Bob
stores the full prompt with every task; here it has to be captured on purpose.

**Instruction files**, each behind its own setting:

| File | Where | Default |
|---|---|---|
| `copilot-instructions.md` | `.github/` | on |
| `AGENTS.md` | workspace roots | on |
| nested `AGENTS.md` | subfolders; listed for the model to read, not attached | off |
| `CLAUDE.md`, `CLAUDE.local.md` | workspace roots, `.claude/`, `~/.claude/` | on |
| `*.instructions.md` | `.github/instructions/`, `.claude/rules/`, `~/.copilot/instructions/`, `~/.claude/rules/`, the user profile | on |
| organisation instructions | GitHub | on |
| the same files in parent repositories | above the workspace | off |

An instructions file applies by glob (`applyTo`), on demand through its `description`, or by
manual attachment. Custom instructions go into the system message by default
(`github.copilot.chat.customInstructionsInSystemMessage`). Copilot is the only tool of the series
that reads `AGENTS.md`, `CLAUDE.md` and its own format out of the box; Bob reads `AGENTS.md`
only. The shipped guidance still says to pick one of `copilot-instructions.md` and `AGENTS.md`,
not both.

**Subagents.** One generic tool in the workbench (`runSubagent`: "Launch a new agent to handle
complex, multi-step tasks autonomously", synchronous, stateless, nesting off by default and
capped at depth 5) and three specialised tools in the extension: `explore_subagent`,
`search_subagent` (off by default) and `execution_subagent` (default model setting
`gpt-5.6-luna`, ten tool calls). Custom agents are `*.agent.md` files in `.github/agents/`,
`.claude/agents/` or `~/.copilot/agents/`, with `tools`, `model` (a list is a fallback order),
`reasoning-effort`, `agents` (which subagents it may call), `handoffs` and inline `hooks`.

**The explore subagent is a file.** The extension writes `Explore.agent.md`,
`Plan.agent.md` and `Ask.agent.md` into its storage folder. Explore declares read-only tools,
`agents: []`, and the model list `Claude Haiku 4.5`, `Gemini 3 Flash (Preview)`, `Auto`: a small
model first, as in Bob. Two differences: the choice is a setting
(`chat.exploreAgent.defaultModel`, `github.copilot.chat.exploreAgent.model`), and its prompt
says "Pay attention to provided agent instructions/rules/skills", where Bob hides project rules
from `explore`.

**The opposite nudge.** When the tools are present, the agent prompt says "For any context
searching, use explore_subagent to search and gather data instead of directly calling
grep_search, semantic_search or file_search" and "For most execution tasks and terminal commands,
use execution_subagent". Bob's prompt says "Default: do the work yourself".

**Skills.** `.github/skills/`, `.agents/skills/`, `.claude/skills/` in the project;
`~/.copilot/skills/`, `~/.agents/skills/`, `~/.claude/skills/` for the user. Twelve skills ship
in `extensions/copilot/assets/prompts/skills/`; `agent-customization`, `create-hook`,
`create-agent`, `create-instructions`, `create-skill` and `troubleshoot` document Copilot from
the inside, the job bob-sideshow does for Bob, and `migrate-customizations` imports another
tool's files on request.

## 5. How do I make it follow mine?

**Rules**: a Markdown file in one of the folders above. Same caveat as for Bob: instructions,
not enforcement.

**Permissions**: the three maps of section 3, at user or workspace level, with deny winning.

**Hooks**: eight events in the Local harness: `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
`PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`. One fewer than Bob's nine,
but with the subagent events Bob lacks and without Bob's `PostCompact` and permission events. A
hook is a shell command (`type: command` is the only type: no HTTPS handler, no prompt hook),
declared in `.github/hooks/*.json`, in `~/.copilot/hooks/`, or inline in an agent file. It
receives JSON on stdin, answers with JSON (`permissionDecision` of `allow`, `ask` or `deny` for
`PreToolUse`; `decision: block` for `PostToolUse`), and exit code 2 blocks, as in Bob and Claude
Code. Hooks from all locations run; none overrides another.

Two compatibility layers. Claude Code's `settings.json` files are among the default hook
locations, but their hooks only run when `chat.useClaudeHooks` is switched on. The Copilot CLI's
own format is parsed too, and it is the richer one: fifteen event names (`sessionStart`,
`sessionEnd`, `userPromptSubmitted`, `userPromptTransformed`, `preToolUse`, `preMcpToolCall`,
`postToolUse`, `postToolUseFailure`, `errorOccurred`, `agentStop`, `subagentStart`,
`subagentStop`, `preCompact`, `permissionRequest`, `notification`), and the schema describes
fields the Local format does not have: a `matcher` regular expression, an HTTP `url` with
`headers`, a native `exec` with `args`. Their description says "Supported values depend on the
active harness". In the Local format a hook has no matcher: it fires for every tool and has to
filter on the JSON it receives. What the Agent Host harness actually executes was not surveyed.

**Model routing**: the `model` list of an agent file, the explore and plan model settings, and
separate settings for the small utility models.

**Organisation tier.** About fifty chat policies exist (`ChatToolsAutoApprove`,
`ChatToolsTerminalEnableAutoApprove`, `ChatHooks`, `ChatAllowManagedHooksOnly`,
`ChatAllowManagedMcpServersOnly`, `ChatAgentSandboxEnabled`, …), and the client also fetches
managed settings from GitHub (`copilot_internal/managed_settings`), including a
`permissions.deny` list. Bob has no managed tier.

## What a "copilot-sideshow" would and would not be

| bob-sideshow skill | Copilot equivalent | Verdict |
|---|---|---|
| bob-version | `product.json`, the extension and SDK `package.json`, `extensionVersion` in each stored request | trivial |
| bob-telemetry | `chatSessions/*.jsonl`: model asked and resolved, tokens, prompt breakdown, credits, how each tool call was approved | worth porting; the richest local record after Bob's, in credits rather than money |
| bob-security-model | three approval maps with defaults, permission levels, advisory risk label, optional sandbox | worth porting; a "would this command be auto-approved?" checker is feasible from the default rule table |
| bob-agent-rules | instruction file discovery, agent files, the built-in agents on disk | half: the prompt is in the bundle but assembled per model and not stored per session |
| bob-override-rules | settings, agent files, hooks, policies | unnecessary: Copilot ships its own `create-*` skills, and the explore model is a setting |

Open items: the meaning of the numeric `isConfirmed` kinds and of the `inputCost` units; whether
0.73.0 writes the same session fields as 0.54.0; the Agent Host harness (its rule loading, its
own sandbox and permission settings); and how the Assisted level decides.

## Landmarks

Literals that locate each subject, to re-check on a new build. "wb" is
`out/vs/workbench/workbench.desktop.main.js`, "ext" is `extensions/copilot/dist/extension.js`.

| Literal | Bundle | Locates |
|---|---|---|
| `copilotVersions` · `agentSdks` · `defaultChatAgent` | `product.json` | runtime, SDK and guest agent versions |
| `chat.permissions.default` · `"default","autoApprove","autopilot"` · `An LLM judge evaluates each tool call` | wb | permission levels |
| `isCommandLineAutoApproved` · `is denied by deny list rule` · `ignoreDefaultAutoApproveRules` | wb | terminal approval decision and default rules |
| `chat.tools.edits.autoApprove` · `"**/.github/hooks/**":!1` | wb | edit approval and protected files |
| `chatToolRiskAssessmentService` · `You assess what one terminal` | wb | advisory risk label and its prompt |
| `TerminalSandboxEngine` · `sandbox-runtime` · `allowUnsandboxedCommands` | wb | sandbox |
| `UserPromptTransformed` · `preMcpToolCall` · `permissionDecision` · `chat.useClaudeHooks` · `chat.hooks.allowManagedOnly` | wb | hook events, formats and switches |
| `copilot-instructions.md` · `CLAUDE.local.md` · `.claude/rules` · `chat.useNestedAgentsMdFiles` | wb, ext | instruction file discovery |
| `Launch a new agent to handle complex, multi-step tasks autonomously` · `allowInvocationsFromSubagents` | wb | generic subagent tool |
| `You are a highly sophisticated automated coding agent` · `familyPrefixes` · `omitBaseAgentInstructions` | ext | agent prompt and its per-model variants |
| `You are an exploration agent` · `Claude Haiku 4.5 (copilot)` · `exploreAgent.model` | ext | explore subagent and its model list |
| `total_nano_aiu` · `copilotUsageNanoAiu` · `copilotCredits` | ext, wb, stored sessions | credit usage |
| `managedSettingsUrl` · `permissions.deny` · `policy:{name:"Chat` | `product.json`, wb | organisation tier |
