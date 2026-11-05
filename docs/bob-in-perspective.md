# Bob in perspective: strengths and gaps against six other agents

Closing note of the series. The six companion notes ask the same five questions of Cursor,
Claude Code, OpenCode, Codex, Kimi Code and GitHub Copilot that bob-sideshow asks of IBM Bob:
[cursor-vs-bob.md](cursor-vs-bob.md), [claude-code-vs-bob.md](claude-code-vs-bob.md),
[opencode-vs-bob.md](opencode-vs-bob.md), [codex-vs-bob.md](codex-vs-bob.md),
[kimi-code-vs-bob.md](kimi-code-vs-bob.md), [copilot-vs-bob.md](copilot-vs-bob.md). This one turns the comparison around and asks what
Bob does better, where it lags, and what that says about bob-sideshow itself.

Builds: IBM Bob 2.3.0 (`bob-code` 2.3.0, build 1.126.0+bob2.3.0.20261026121409; the Bob column was re-read
on it, see CHANGELOG 0.5); Cursor 3.19.13 with agent runtime 2026.09.15; Claude Code 2.1.274;
OpenCode 1.18.21; Codex CLI 0.154.0-alpha.6.2; Kimi Code extension 0.7.5; GitHub Copilot as
built into VS Code 1.145.0 (extension `copilot-chat` 0.73.0, Local harness only). Same method
everywhere: installed files, local databases, settings; no source code, no network capture.
Codex and Kimi Code were surveyed before any session had run, so their findings come from the
binaries alone.

Bob is neither the best nor the worst of the seven. It has two real leads and four clear gaps.

## Where Bob leads

**Complete local audit trail.** Bob is the only tool that stores, in its local database, both
the exact system prompt of every task and the price of every LLM call. Cursor stores neither
(the prompt is assembled server-side, cost never reaches the client). Claude Code and Kimi Code
store the model name and tokens but no price. OpenCode stores the price but not the prompt.
Codex stores tokens and asks its backend for the price. Copilot stores the model, the tokens and
a cost in its own credits, but not the prompt. To audit what the agent was told and
what it cost, Bob is the best placed of the seven, and `dump_system_prompt.py` plus
`bob_telemetry.py` have no equivalent elsewhere.

**Always-on, fail-closed command check.** Every shell command goes through a small model that
says whether it is dangerous; a timeout or a bad answer counts as dangerous; approved-command
lists never bypass it. Cursor (Smart Auto), Claude Code (auto mode) and Codex (guardian
reviewer) have the same idea, but as an optional mode the user switches on. Copilot runs a small
model on every confirmation, but only to label the risk; it does not decide. OpenCode and Kimi
Code have no model-based check at all.

**Native AGENTS.md with a clear precedence**, and hooks that block on exit code 2 with stderr
fed back to the model, as in Claude Code. Cursor, Codex, OpenCode and Copilot read AGENTS.md too;
Claude Code does not by default, and Kimi Code reads it with the same root-to-leaf walk.

## Where Bob lags

**The `explore` subagent is locked.** Bob wires `explore` to the economy model and hides
project rules from it, with no setting to change either. Every other tool exposes the choice:
Cursor offers default, inherit, pinned or disabled; Claude Code an environment variable and a
`model` parameter on the Agent tool; Kimi Code a `[secondary_model]` section and a per-profile
preference; OpenCode and Codex a configurable default subagent model; Copilot a model list in
an agent file and two settings. Most of
`bob-override-rules` exists to work around this one gap.

**A rudimentary allowlist.** Token-by-token prefix match, case-sensitive, no wildcards, and a
tie between an approved and a denied pattern resolves to allow. Five others accept glob
patterns, and Copilot regular expressions tested per sub-command, with deny winning. Kimi Code guarantees a user `deny` rule beats yolo mode; OpenCode fits its whole
policy into one "last matching rule wins" line; Claude Code layers eight rule sources with a
managed tier on top.

**No sandbox.** Cursor, Claude Code and Codex run commands inside a real sandbox (seatbelt on
macOS, Landlock or bubblewrap on Linux), with the network cut by default in Codex; Copilot has
one too, off by default. Bob,
OpenCode and Kimi Code rely on the model check and the user.

**Fewer hook events than four of the others.** Bob has nine (2.3.0, bundle) — `SessionStart`, `UserPromptSubmit`,
`PreToolUse`, `PostToolUse`, `PreCompact`, `PostCompact`, `Stop`, and the new `PermissionRequest` and
`PermissionResolved`, which fire only when Bob would show an approval prompt — each answers with structured
JSON (permission decision, rewritten input, extra context) and can be an HTTPS handler as well as a
shell command. Codex has twelve events, Kimi Code sixteen, Claude Code twenty-one, Cursor
twenty-two. Copilot's Local harness has eight, one fewer than Bob, but they include subagent
start and stop. A guard when a subagent starts still cannot be written for Bob.

## Rough edges specific to Bob

- **"task" means two things.** "Create a task" matches the built-in `start_subtask` tool almost
  literally, so tracker instructions in `AGENTS.md` lose to the tool definition. Claude Code has
  the same pair (`TaskCreate` / `Agent`) but ships a guard message at the tool boundary; Codex
  (`spawn_agent`) and Kimi Code (`Agent`) avoided the name.
- **Files rewritten without asking.** `/init` rewrites `AGENTS.md` "AGGRESSIVELY", and every
  `commands/*.md` file becomes a skill at each start, reappearing after deletion. No other tool
  edits the user's configuration on its own; Codex and Kimi Code import competitors' files only
  on request.
- **No managed tier.** Claude Code, Cursor, Codex and Copilot have organisation settings a project cannot
  override; Codex even refuses `approval_policy = "never"` when requirements forbid it. Bob's
  settings are user and workspace only.
- **The strongest anti-subagent nudge of the seven.** "Default: do the work yourself" plus a list
  of cases where subagents are forbidden, applied even when the user explicitly asks for one.
  Cursor, Claude Code, OpenCode and Codex describe when to delegate; Kimi Code says nothing in
  the system prompt and leaves it to tool descriptions; Copilot pushes the other way and tells
  the agent to search through its explore subagent.

## What this means for bob-sideshow

- `bob-version`, `bob-telemetry` and `bob-agent-rules` exploit Bob's audit trail, which is Bob's
  genuine advantage. Their equivalents for other tools would be weaker (no prompt on Cursor, no
  price on Claude Code or Kimi Code).
- `bob-security-model` documents a checker that is stricter than most but matches patterns more
  crudely than all. A future Bob with glob patterns and deny-wins semantics would make half of
  `approvals.md` obsolete, in a good way.
- `bob-override-rules` is the skill that would disappear first: on every other tool, the
  overrides it writes for Bob (subagent model, subagent on request, protect AGENTS.md, refuse
  commands) are native settings, a file, or a plugin hook.

In one sentence: Bob is the most auditable and the most cautious of the seven, and the least
configurable; its strengths come from what it records, its weaknesses from what it does not let
the user set.

## Side-by-side

| Question | Bob 2.3.0 | Cursor | Claude Code | OpenCode | Codex | Kimi Code | Copilot (VS Code) |
|---|---|---|---|---|---|---|---|
| System prompt readable locally | stored per task | no (server) | in binary | in binary, per model | in binary, per model | in bundle, replaceable by `SYSTEM.md` | in bundle, per model family; not stored per session |
| Cost per call, offline | yes, price only | no | tokens + model, no price | yes, price + model | tokens; price from server | tokens + model; price if provider sends it | credits + model + tokens |
| Model-based command check | always on, fail-closed | optional (Smart Auto) | optional (auto mode) | none | optional (guardian) | none | advisory risk label; judge level not in default list |
| Allowlist matching | token prefix, no wildcard, tie → allow | glob, per-tool | glob, 8 layered sources | glob, last rule wins | prefix rules in `.rules` files | glob, 19-policy chain, deny beats yolo | regex per sub-command, deny wins |
| Sandbox | none | seatbelt / bwrap | seatbelt / bwrap | none | seatbelt / Landlock, network off | none | seatbelt / bwrap, off by default |
| Hook events | 9, JSON + HTTPS | 22 | 21 | plugin API (in-process) | 12 (trusted hooks) | 16 | 8 (Local harness); 15 names in the Copilot CLI format |
| Explore subagent model | economy, fixed | setting | inherit with cap, env override | parent's | configurable default | secondary model, per profile | small-model list, setting |
| Reads AGENTS.md | yes | yes | plugin option only | yes (plus CLAUDE.md) | yes, spec in prompt | yes | yes (plus CLAUDE.md) |
| Managed / admin settings | no | yes | yes | no | yes (MDM, requirements) | no | yes (policies, managed settings) |
| Edits user files unasked | `/init`, commands → skills | no | no | no | no | no | no |
