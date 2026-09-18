# OpenCode vs Bob: the same five questions

Companion to [cursor-vs-bob.md](cursor-vs-bob.md) and [claude-code-vs-bob.md](claude-code-vs-bob.md).
bob-sideshow answers five questions about IBM Bob: which version am I running, what did it cost,
why does it ask for approval, which rules does it follow, and how do I make it follow mine. This
note asks the same five questions of OpenCode.

Verified on OpenCode 1.18.21 installed with Homebrew, plugin SDK 1.18.18, macOS. Same method: the
shipped binary, the local database and the settings; no private API, no network capture. OpenCode
is open source (MIT, github.com/anomalyco/opencode), so everything below could also be checked
against the source; this note deliberately sticks to what the installed copy shows.

## Where OpenCode keeps things

One native binary (`/opt/homebrew/Cellar/opencode/<version>/bin/opencode`, 144 MB, Bun-compiled
Mach-O, as Claude Code's). `strings` yields the prompts, the agent table, the permission defaults
and the config loader.

| Path | What it holds |
|---|---|
| `~/.local/share/opencode/opencode.db` | SQLite, 959 MB here: `session`, `message`, `part`, `todo`, `project`, `permission`, and an `event` log |
| `~/.local/share/opencode/snapshot/<project>/` | one bare git repository per project, used for undo and revert |
| `~/.local/share/opencode/log/opencode.log` | which config files were loaded, which model was streamed for which agent |
| `~/.cache/opencode/models.json` | the models.dev catalogue: 221 providers with per-token prices and limits |
| `~/.local/state/opencode/model.json`, `prompt-history.jsonl` | recent models and their "variant" (effort), prompt history |
| `~/.config/opencode/opencode.json(c)` | user config; `.opencode/` folders and `opencode.json(c)` in the project |
| `~/.config/opencode/{agent,command,skill}/`, `.opencode/{agent,command,skill,plugin,tool}/` | custom agents, slash commands, skills, plugins, tools (singular or plural folder names both work) |

Config files are loaded in this order and deep-merged, later wins: `~/.config/opencode/`
(`config.json`, `opencode.json`, `opencode.jsonc`), then `opencode.json(c)` found walking up from
the working directory (root first), then each `.opencode/` directory, then the file named by
`OPENCODE_CONFIG`. Unknown keys are rejected.

## 1. Which version am I running?

`opencode --version`. Every session row in the database records the version that created it, and
the log prints it at session creation. The VS Code extension (`sst-dev.opencode` 0.0.13) is a thin
launcher and carries no agent code.

## 2. What did it cost?

Fully answerable, the only one of the four tools where the answer is exact and local.

Every assistant message stores `providerID`, `modelID`, `agent`, `mode`, `variant`, a `cost` in
USD and a `tokens` object with input, output, reasoning, cache read and cache write. The cost is
computed at write time from the models.dev prices in the cache, so it survives price changes and
needs no table to interpret. The `session` row carries the totals, the parent session id, the
agent and the model, and a summary of files, additions and deletions.

On this machine: 2 700 assistant messages, 40 sessions, 9 of them subagents. Cost per model and
agent falls out of one `GROUP BY`; the biggest line is the `build` agent on DeepSeek V4 Pro through
OpenRouter, USD 22.5 for 1 441 messages. Cache writes are zero everywhere: OpenRouter does not
report them.

Tool usage is in `part` rows of type `tool` with the tool name, status, input and output (2 089
`bash`, 928 `read`, 219 `edit`, 11 `task` here). Bob's `changes` view has an equivalent in the
session summary diffs and the git snapshots.

## 3. Why does it ask for approval?

**One mechanism for everything.** A permission is a rule `{permission, pattern, action}` where
`permission` is a tool name or a pseudo-tool (`bash`, `edit`, `read`, `task`, `skill`,
`external_directory`, `doom_loop`, `question`, `plan_enter`, `plan_exit`) and `action` is
`allow`, `ask` or `deny`. Evaluation is one line: the **last** rule whose permission and pattern
both glob-match wins; no match means `ask`. Rulesets are merged in order: built-in defaults, the
agent's own rules, the user's `permission` config, then the approvals given during the session.

Built-in defaults: everything `allow`; `doom_loop` and `external_directory` `ask` (except the
workspace, `/tmp` and the project's own directories); `read` of `*.env` files `ask`;
`question`, `plan_enter`, `plan_exit` `deny`. The `plan` agent adds `edit: deny` except for plan
files, and `task: {general: deny}`.

**Shell.** Each command is parsed with tree-sitter-bash (PowerShell grammar on Windows), split
into sub-commands, and each becomes a pattern. The "always allow" offer is the command's leading
tokens plus ` *`, a prefix rule, as in Bob. Absolute paths outside the workspace turn into
`external_directory` asks. "Always" answers live in memory: the UI says "until OpenCode is
restarted", and the `permission` table is empty on this machine.

**Doom loop.** The same tool called with the same input several times in a row triggers a
`doom_loop` ask ("Continue after repeated failures"). Neither Bob, Cursor nor Claude Code has this.

**What is absent.** No sandbox: one of the prompt variants tells the model "The operating
environment is not in a sandbox … you MUST be extremely cautious". No model-based security check
like Bob's, Cursor's Smart Auto or Claude Code's auto mode. No allowlist file with Bob-style
`deniedCommands`; a `deny` rule on `bash` with a pattern does the same job.

## 4. Which rules does it follow?

**The system prompt is in the binary and chosen per model.** Eight variants, selected by
substring of the model id: GPT-4 / o1 / o3 get the "keep going until resolved" prompt, other GPT
models a Codex or generic GPT prompt, Gemini its own, Claude its own, Kimi its own, Meta's Muse
its own, everything else the default. The prompt is not stored with the session, only the model
id is, so the variant a session used is known but the exact assembled text is not.

**Instruction files.** Global: `~/.config/opencode/AGENTS.md`, or failing that
`~/.claude/CLAUDE.md` unless `disableClaudeCodePrompt` is set. Project: walking up from the
working directory to the git worktree, the first of `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md` that
exists. Subdirectory instruction files are loaded lazily: when the agent reads a file, the
`AGENTS.md` files between that file and the project root are injected once per session. The
`instructions` config key adds globs or URLs. `OPENCODE_DISABLE_PROJECT_CONFIG` turns project
files off. `.cursorrules` and `.cursor/rules` are read only by `/init`, which writes AGENTS.md.

So OpenCode is the one tool that reads both AGENTS.md and CLAUDE.md by default, AGENTS.md first.

**Agents.** Built in: `build` (default, primary), `plan` (primary, edits denied), `general`
(subagent, all tools but the todo list), `explore` (subagent, read-only: grep, glob, list, read,
bash, web fetch and search; everything else denied), and three hidden ones, `title`, `summary`,
`compaction`, with every tool denied. Custom agents come from the `agent` config key or
`.opencode/agent/*.md` with `model`, `variant`, `prompt`, `permission`, `mode`
(`primary`, `subagent`, `all`), `temperature`, `steps`.

**Model choice.** A subagent runs on its own configured model, else on the parent's: the database
shows `general` subagents on the parent's DeepSeek and a custom `orientation-checker` pinned to
Gemini Flash Lite. There is no economy routing of `explore`, so Bob's main grievance does not
arise. Titles use a "small model": the `small_model` config key, else a per-provider fallback
family list (`gpt-nano` on OpenCode's own provider). Compaction uses the session's model.
Subagents cannot spawn subagents by default (`subagent_depth` 1); their session row carries
`task: deny`.

**Vocabulary collision, once more.** The subagent tool is literally named `task`, its call
"creates a task", and its output is wrapped in `<task id=… state=…>`. The same ambiguity
bob-sideshow documents for Bob's `start_subtask` exists here with an even shorter name, and no
guard message was found in the binary.

## 5. How do I make it follow mine?

**Rules**: AGENTS.md at the project root or in a subdirectory, a global AGENTS.md, or
`instructions` globs in the config.

**Permissions**: the `permission` key in any config file, per tool and per pattern, including
`deny`. Because the last matching rule wins, a project config can override a user config, and an
agent definition can override both.

**Plugins instead of hooks.** OpenCode has no shell-script hooks and no exit-code protocol.
Extension is a JavaScript or TypeScript module in `.opencode/plugin/` or an npm package named in
the `plugin` key, loaded in-process with the SDK `@opencode-ai/plugin`. Hook points on this SDK:
`event`, `config`, `tool` (register tools), `auth`, `provider`, `chat.message`, `chat.params`,
`chat.headers`, `permission.ask` (answer `allow`, `deny` or `ask` yourself), `command.execute.before`,
`tool.execute.before`, `tool.execute.after`, `shell.env`, `tool.definition`, and experimental
transforms of the message list, the system prompt, compaction and text completion. `permission.ask`
does what Bob's `PreToolUse` hook and `deniedCommands` do, with the whole permission request in
hand. `experimental.chat.system.transform` lets a plugin rewrite the system prompt, which none of
the other three tools allow.

**Skills** in `.opencode/skill/`, `~/.config/opencode/skill/`, plus `~/.claude/skills/` and
`~/.agents/skills/` auto-loaded, so Claude Code skills work unchanged.

## What an "opencode-sideshow" would and would not be

| bob-sideshow skill | OpenCode equivalent | Verdict |
|---|---|---|
| bob-version | `opencode --version`, `session.version` | trivial |
| bob-telemetry | `session` and `message` tables with cost and tokens per model and agent | worth porting, and simpler than Bob's: the cost is already there |
| bob-security-model | one glob ruleset, last match wins; tree-sitter split; doom loop; no sandbox, no classifier | worth porting; a "would this be asked?" checker is a dozen lines |
| bob-agent-rules | prompts in the binary, agent table with per-agent rulesets, lazy AGENTS.md loading | worth porting; the `task` name collision is the finding to document |
| bob-override-rules | config `permission`, agent definitions, `permission.ask` plugin | unnecessary as a skill: every override is a config key or a plugin |

Open items: how `ShellTool.collect` decides which sub-commands count (the token sets it consults
were not extracted), whether the database `permission` table is written by any code path on this
build, and which prompt variant applies to models whose id matches none of the eight substrings
beyond "the default".

## Landmarks

Literals that locate each subject in `strings <binary>`, to re-check on a new build.

| Literal | Locates |
|---|---|
| `You are opencode, an interactive CLI tool` · `function ud(e){if(e.api.id.includes("muse")` | prompt variants and their selector |
| `fn("Instruction.systemPaths")` · `"CONTEXT.md"` · `disableClaudeCodePrompt` | instruction file discovery |
| `fn("Instruction.resolve")` | lazy loading of subdirectory AGENTS.md |
| `doom_loop:"ask"` · `external_directory:{` · `"*.env":"ask"` | default ruleset |
| `name:"explore"` · `mode:"subagent"` · `hidden:!0` | built-in agent table |
| `fn("Permission.ask")` · `findLast` · `{action:"ask",permission:j,pattern:"*"}` | ruleset evaluation |
| `fn("ShellTool.parse")` · `fn("ShellTool.collect")` · `fn("ShellTool.ask")` | shell parsing and pattern generation |
| `Subagent depth limit reached` · `Unknown agent type` · `<task id=` | task tool |
| `fn("Provider.getSmallModel")` · `small_model` | title model |
| `OPENCODE_CONFIG` · `findUp(["opencode.json","opencode.jsonc"]` | config loading order |
| `The operating environment is not in a sandbox` | absence of sandbox, stated to the model |
