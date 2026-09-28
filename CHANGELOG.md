# Changelog

## 0.3 — 2026-09-29

Verified on IBM Bob 2.2.0, and ready for the next Bob after it.

- **Re-verified on IBM Bob 2.2.0** (`bob-code` 2.2.0, build `1.126.0+bob2.2.0.20260924155054`).
  Every script and reference note now states the build its facts were checked on, and no script
  warns on a 2.2.0 install. How the delta was established despite a bundle that renamed most of
  its internals — and what actually changed inside Bob — is in
  [docs/bob-2.1.0-to-2.2.0.md](docs/bob-2.1.0-to-2.2.0.md):
  - **Custom agents: `model:` is now an error, use `modelTier:`.** Bob 2.2.0 rejects the old
    frontmatter field instead of ignoring it. The shipped `explore-premium.md` agent and the
    `premium-subagents.md` rule that points at it are fixed, and the agent was loaded in a real
    Bob 2.2.0 task to prove it.
  - **Hooks: seven events instead of five, HTTPS handlers, structured JSON replies.**
    `PreCompact`/`PostCompact` are new; a hook can answer with `hookSpecificOutput`
    (`updatedInput`, `permissionDecision`, `additionalContext`) instead of only exit code 2, and
    can be a `{"type":"http", "url":…}` handler next to a shell command.
    `skills/bob-override-rules/templates/hooks/command-guard.mjs` keeps its simpler stderr + exit
    2 contract, which 2.2.0 still honours unchanged.
  - **Rules and skills gain a `.bob/plugins/<name>/` root.** Each rule kind reads `.bob/` first,
    then every plugin alphabetically; precedence between kinds is unchanged.
    `rule_locations.py` now lists those roots in 2.2.0's order, and says what it cannot tell about
    folder trust (2.2.0 takes it from the IDE, not from a file).
  - **Settings: `autoCondense*` renamed to `autoCompact` / `compactionThresholdPercent`.** Old
    files still load, migrated on read; defaults unchanged (on, 90%).
  - **Command security check moved off a flag and onto a server-routed model tier.** 2.1.0 read
    `command-security-model` and fell back to `openai/gpt-oss-20b`; 2.2.0 asks the server for tier
    `security` (falling back to `premium-ide` if the router fails). `bob-version` still shows
    `command-security-model` and `summary-model`, marked as pushed but no longer read, and lists
    the flags 2.2.0 does read.
  - **`execute_command` gains a `background` mode**: the process is detached, output goes to a log
    file, and the tool returns immediately with the pid.
  - **System prompt: discipline rules, per-model layouts, XML rule tags.** New prompt-section
    registry with four configs (`default`, `boreas`, `aquarius`, `orion`) chosen by model id, a
    `promptConfigPath` override, `<agents_md>`/`<workspace_rules>`/`<global_rules>` XML tags
    instead of markdown headings. `dump_system_prompt.py` reads the new layout as before.
  - **Database: new `key_value_store` table** (migration `011_key_value_store`), caching the
    server feature flags (`featureFlags.v1`).
  - **`_meta.spend` on an LLM call is now `{cost, contextTokens}` only.** The token breakdown
    (input/output/cache/reasoning) is gone, so `bob-telemetry` shows `n/a` instead of a false zero
    for tokens on 2.2.0 calls, adds a `ctx` column, and can no longer infer the model class from
    the unit price; Bobcoin totals are unaffected. The 2.0 / 0.833 Bobcoins-per-million rates in
    `bob-agent-rules` are explicitly the 2.1.0 measurement — they cannot be re-measured on 2.2.0.
  - Libraries: PostHog and LangChain/LangGraph/LangSmith removed; gRPC, a larger MCP SDK
    (protocol v2) and a bigger OTLP trace exporter added.
  - `VERIFIED_EXTENSION` is `2.2.0` and `VERIFIED_SCHEMA` is `011_key_value_store` in the five
    copies of `_bobcheck.py`.
- **See where Bob stands next to Cursor, Claude Code, OpenCode, Codex and Kimi Code.** One
  page per tool ([docs/](docs/)), each read from that tool's own build, plus
  [docs/bob-in-perspective.md](docs/bob-in-perspective.md) for the side-by-side; the Bob column
  is updated to 2.2.0 where the delta changed it.

## 0.2 — 2026-09-09

Two more Bob behaviours you can now explain and stop.

- **Understand why skills appear in `.bob/skills/` on their own.** Ask Bob why skills you never
  created keep coming back after you delete them, and it now has the answer — and it is not `/init`.
- **Stop them coming back.** Ask for a permanent fix and Bob applies one you can commit, so the
  skills stay gone for your whole team.
- **Get a Backlog task when you ask for a task.** Ask why Bob starts a subtask instead of creating
  a tracker task and it explains the mix-up; ask it to stop and it writes the rule that makes
  "task" mean your tracker again.

## 0.1 — 2026-09-08

First release. Five skills that answer questions about Bob from inside Bob.

- **Know which Bob you are running.** Version, build, the exact extension in use, whether Bob Shell
  is installed, and which models the server pushed to your machine today.
- **See what Bob costs you.** Bobcoins and tokens per task, per subagent and per call, split
  between the standard and the economy model — so an expensive habit becomes visible instead of
  showing up on the bill.
- **Understand approvals.** Why Bob asks you to confirm a command, whether a given command would be
  auto-approved before you run it, what the "Security warning" banner really means, and how to
  block a command for good.
- **See the rules Bob follows.** The instructions Bob gives itself about subagents, model choice
  and answering inline — read from the conversation Bob actually ran, not from a manual — and where
  your own `AGENTS.md` and `.bob/rules/` rank against them.
- **Make Bob follow your rules instead.** Always spawn a subagent when you ask for one, run
  subagents on the premium model, put your project workflow first, keep `/init` away from
  `AGENTS.md`, or refuse dangerous commands — Bob writes the right file in the right folder for you.
- **Trust the answers.** Every script checks the Bob version it is running against and warns you
  when your build is newer than the one these answers were verified on.
