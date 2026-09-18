# Codex vs Bob: the same five questions

Companion to [cursor-vs-bob.md](cursor-vs-bob.md), [claude-code-vs-bob.md](claude-code-vs-bob.md)
and [opencode-vs-bob.md](opencode-vs-bob.md). bob-sideshow answers five questions about IBM Bob:
which version am I running, what did it cost, why does it ask for approval, which rules does it
follow, and how do I make it follow mine. This note asks the same five questions of OpenAI Codex.

Verified on Codex CLI 0.154.0-alpha.6.2, the build bundled in the VS Code extension
"Codex – OpenAI's coding agent" 26.908.40401 (publisher `openai`, extension id `chatgpt`), macOS.
The extension was installed minutes before this survey: `~/.codex` exists with its databases and
plugin cache, but no session has run, no `config.toml` exists and nobody is logged in. Everything
below therefore comes from the binary, the empty schemas, the startup log and the CLI's own help;
nothing from a real conversation. Codex is open source (github.com/openai/codex), so it can be
cross-checked against the source.

## Where Codex keeps things

One Rust binary (`<extension>/bin/macos-aarch64/codex`, 223 MB) plus a helper for "code mode" and a
bundled `rg`. `strings` on it yields the prompt templates as JSON, the config keys, the hook event
names and the feature flags. The IDE extension is a thin client: the binary runs as an
"app-server" and the webview talks JSON-RPC to it.

| Path | What it holds |
|---|---|
| `~/.codex/config.toml` | user config (absent here); `<name>.config.toml` profiles; `requirements.toml` and MDM for admins |
| `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | one transcript per thread (none yet) |
| `~/.codex/state_5.sqlite` | index of threads: rollout path, model, reasoning effort, sandbox policy, approval mode, tokens used, git branch and sha, parent/child spawn edges, projects |
| `~/.codex/logs_2.sqlite` | structured logs keyed by thread (4 883 rows after one launch) |
| `~/.codex/memories_1.sqlite`, `goals_1.sqlite`, `queue_1.sqlite` | cross-session memory pipeline, per-thread goals with a token budget, queued messages |
| `~/.codex/skills/`, `.codex/skills/`, `.agents/skills/` | skills; `skills/.system/` holds Codex's own |
| `~/.codex/.tmp/plugins/` | a git clone of OpenAI's plugin marketplace (61 plugins), refreshed at start |
| `~/.codex/rules/*.rules` | exec-policy rules written by "approve for prefix" |
| `.codex/` in a project | skills, agents, hooks, config |

The schema history is readable: 54 migrations named `threads`, `memories`, `agent jobs`,
`thread goals`, `remote control enrollments`, `external agent config imports`, `projects`,
`daybreak`… a changelog of features in the database itself.

## 1. Which version am I running?

`codex --version`. Every thread row records `cli_version`. `codex features list` prints each
feature flag with its stage (stable, experimental, under development, deprecated, removed) and
its effective state, which no other tool in this series offers. On this build: `multi_agent`,
`hooks`, `plugins`, `goals`, `guardian_approval`, `unified_exec` are stable and on; `memories`
is stable but off; `multi_agent_v2`, `code_mode`, `token_budget` are off.

## 2. What did it cost?

Tokens yes, money no, and the money exists but elsewhere.

Each thread stores `tokens_used`; each turn reports input, cached input, output, reasoning and
total tokens. There is no price table in the binary. The cost is computed by the backend and
fetched by the app-server (`turn_cost_worker_chatgpt`, "estimated usage USD micros" for ChatGPT
accounts, `total_usd` per turn for API-key accounts) and shown as an estimated thread cost next
to the five-hour and weekly limits. Offline, you get tokens per thread and per subagent, split by
model and reasoning effort, from `state_5.sqlite` and the rollouts. Bob stores the price and not
the model; Codex stores the model and asks the server for the price.

`goals` adds something Bob lacks: a thread can carry an objective with a token budget and a
status (`active`, `budget_limited`, `usage_limited`…).

## 3. Why does it ask for approval?

Two axes instead of one list.

**Sandbox mode**: `read-only`, `workspace-write`, `danger-full-access` (plus a newer
`permission_profile` / `sandbox_permissions` form, for example `disk-full-read-access`). Commands
run inside the sandbox by default: seatbelt through `/usr/bin/sandbox-exec` on macOS, Landlock or
bubblewrap through `codex-linux-sandbox` on Linux, with network disabled
(`CODEX_SANDBOX_NETWORK_DISABLED=1`) unless a network proxy with domain rules is configured.
`codex sandbox <cmd>` runs any command under the same policy, handy for testing.

**Approval policy**: `on-request` (the model asks when it wants to escalate out of the sandbox),
`on-failure` (retry outside the sandbox after asking), `never`. `untrusted` is "no longer
supported" on this build. `--dangerously-bypass-approvals-and-sandbox` is Bob's yolo; the CLI
refuses `never` when admin requirements forbid full access.

**Model check.** `--approve-for-me`, config `approvals_reviewer = "auto_review"`, feature
`guardian_approval`: a model judges each escalation with a policy prompt that begins "You are
judging one planned coding-agent action". Its trust rule is explicit: only user and developer
messages, AGENTS.md files and answers to `request_user_input` can establish authorization;
tool outputs, skills, plugin descriptions and the assistant's own text are untrusted. This is the
closest cousin of Bob's `command-security-model`, and the only one of the five tools that writes
its trust boundary into the prompt.

**Exec policy.** Prefix rules in `.rules` files:
`prefix_rule(pattern=[…], decision="allow")` and `network_rule(…)`. The TUI offers approve,
approve for session and approve for prefix; the last one appends a rule. A rule can also forbid:
"rejected: policy forbids commands starting with". Token-prefix matching, as in Bob.

**Admin layer.** `requirements.toml` (allowed permission profiles, default permissions) and MDM
managed preferences (`com.openai.codex`, key `config_toml_base64`; the startup log shows the
lookup) sit above the user config and cannot be overridden. Bob has no such layer.

## 4. Which rules does it follow?

**Prompt in the binary, one template per model family.** The templates are JSON strings
(`instructions_template`, `base_instructions`) selected from an embedded model catalogue: "You
are Codex, an agent based on GPT-5", a GPT-5.2 variant, a GPT-6 variant, a general-purpose
assistant variant, with a `{{ personality }}` slot. Model ids in the catalogue include
`gpt-5.1-codex-max` and the codenames `gpt-5.6-terra` and `gpt-5.6-luna`. Rollouts do not store
the assembled prompt, only the model and effort.

**AGENTS.md, by the spec in the prompt itself.** A file's scope is its directory subtree; deeper
files win on conflict; direct instructions beat AGENTS.md. The root file and every directory from
the working directory up to the root are injected; the agent is told to look for others when it
works elsewhere. `AGENTS.override.md` comes first, then `AGENTS.md`, then
`project_doc_fallback_filenames`, empty by default, so **CLAUDE.md is not read unless configured**.
Global instructions in `~/.codex/AGENTS.md`; size cap `project_doc_max_bytes` 32 KB.

**Imports rather than reads.** An `external_agent_config_imports` table and a migration module
import Claude Code (`~/.claude.json`, `.claude/settings.local.json`, CLAUDE.md, hooks.json, memory)
and Cursor (`.cursorrules`) into `.codex/`; plugin manifests are accepted from
`.codex-plugin/`, `.claude-plugin/` and `.cursor-plugin/`; hooks see `CLAUDE_PLUGIN_ROOT` as an
alias. Same stance as Bob's `/init`: read the competitor's files once, write your own.

**Subagents** are threads. Tools `spawn_agent`, `send_input`, `wait_agent`, `resume_agent`,
`close_agent`; parent and child are recorded in `thread_spawn_edges`. Config `[agents.<role>]`
with `default_subagent_model`, `default_subagent_reasoning_effort`, `max_depth`,
`max_concurrent_threads_per_session`; project agents in `.codex/agents/`. Guidance found in the
prompt: "Prefer delegating concrete, bounded sidecar tasks that materially advance the main task
without blocking your immediate next local step". Nothing like Bob's "do the work yourself",
and no forced economy model: the subagent model is a config key.

**Skills** use `SKILL.md` plus an `agents/openai.yaml` sidecar (`display_name`, `default_prompt`,
`allow_implicit_invocation`). Invocation by `$skill-name`; the prompt says not to use a skill "based
solely on keywords". Bundled system skills (`imagegen`, `openai-docs`) are installed at first run;
the log shows that install failing on this machine because the directory was not empty.

**Vocabulary.** No `task` tool: the subagent tool is `spawn_agent` and its parameter is
`task_name`. The collision bob-sideshow documents for Bob does not exist here; the tool named
`update_plan` is the nearest thing, and it edits the visible plan, not a tracker.

## 5. How do I make it follow mine?

**Rules**: AGENTS.md anywhere in the tree, `AGENTS.override.md` to win, `~/.codex/AGENTS.md` for
everything.

**Exec policy**: `.rules` files with `prefix_rule` and `network_rule`, deny included.

**Hooks**: `hooks.json`, events PreToolUse, PermissionRequest, PostToolUse, PreCompact,
PostCompact, SessionStart, SessionEnd, UserPromptSubmit, SubagentStart, SubagentStop, Stop,
Interrupt. A PreToolUse hook blocks ("Command blocked by PreToolUse hook"). Hooks must be
**trusted** before they run: a `trusted_hash` is recorded per hook file and
`--dangerously-bypass-hook-trust` skips the check. None of the other four tools gates hooks
this way.

**Config layers**: `-c key=value` on the command line, `--profile <name>` for
`~/.codex/<name>.config.toml`, `--ignore-user-config`, `--strict-config` to reject unknown keys.

## What a "codex-sideshow" would and would not be

| bob-sideshow skill | Codex equivalent | Verdict |
|---|---|---|
| bob-version | `codex --version`, `codex features list`, `cli_version` per thread | trivial, and the flag listing is a bonus |
| bob-telemetry | tokens per thread and turn in `state_5.sqlite` and rollouts; cost only from the server | worth porting for tokens; no offline money |
| bob-security-model | sandbox mode × approval policy, exec-policy prefix rules, guardian reviewer, admin requirements | worth porting; `codex sandbox` makes "would this run?" testable |
| bob-agent-rules | prompt templates in the binary, AGENTS.md spec, subagent config keys | worth porting; Explore-style economy routing absent |
| bob-override-rules | AGENTS.override.md, `.rules`, trusted hooks, config layers | unnecessary as a skill: every override is native |

Open items, all because no session has run yet: the exact rollout JSONL record shapes, whether
token usage per subagent lands in the child thread row or the parent's, which template the
catalogue picks for a given model id, and where `hooks.json` is looked up (the binary names
`.codex/hooks` and a plugin `hooks/hooks.json`; a user-level path was not confirmed).

## Landmarks

Literals that locate each subject in `strings <binary>`, to re-check on a new build.

| Literal | Locates |
|---|---|
| `"instructions_template": "You are Codex` · `{{ personality }}` · `model_catalog_json` | prompt templates and model catalogue |
| `# AGENTS.md spec` · `AGENTS.override.md` · `project_doc_fallback_filenames` · `project_doc_max_bytes` | instruction files |
| `"policy_template": "You are judging one planned coding-agent action` · `approvals_reviewer` · `guardian_approval` | model-based reviewer |
| `read-only` · `workspace-write` · `danger-full-access` · `sandbox_permissions` · `permission_profile` | sandbox modes |
| `/usr/bin/sandbox-exec` · `codex-linux-sandbox` · `CODEX_SANDBOX_NETWORK_DISABLED` | sandbox implementation |
| `prefix_rule(pattern=` · `network_rule(` · `policy forbids commands starting with` | exec policy |
| `requirements.toml` · `config_toml_base64` · `managed_config.toml` | admin layer |
| `PreToolUsePermissionRequestPostToolUse…Interrupt` · `trusted_hash` · `--dangerously-bypass-hook-trust` | hooks |
| `spawn_agent` · `max_concurrent_threads_per_session` · `default_subagent_model` · `thread_spawn_edges` | subagents |
| `turn_cost_worker_chatgpt` · `estimated_usage_usd_micros` · `total_token_usage` | cost and tokens |
| `external-agent-migration` · `.claude-plugin/plugin.json` · `.cursor-plugin/plugin.json` | imports from other agents |
