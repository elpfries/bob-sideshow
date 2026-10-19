# Changelog

## 0.4 — 2026-10-19

Re-verified on IBM Bob 2.2.3. Nothing in Bob changed that this project needed to say differently;
the labels did.

- **Re-verified on IBM Bob 2.2.3** (`bob-code` 2.2.3, build `1.126.0+bob2.2.3.20261014125159`; database
  schema still `011_key_value_store`, 11 migrations). Bob auto-updated in place twice since the 0.3
  release, 2.2.0 → 2.2.1 (2026-10-05) → 2.2.3 (2026-10-14); 2.2.2 was never observed installed on this
  machine.
  - **`bob-code` itself is unchanged since 2.2.0, except one development-only string.**
    `extension.js` is byte-identical between 2.2.1 and 2.2.3 (same SHA-1,
    `6062c88fb39bb33a7b1f24f8d2cf08911e8dcac5`), and differs from 2.2.0 by exactly 34 bytes — one
    Jenkins workspace-path string used only when Bob is built in development mode
    (`BOB_IDE_EXTERNAL_PKG_USER` → `BOB_IDE_EXTERNAL`), confirmed by `bundle_diff.py anchors` against
    both the 102-anchor and the 46-durable-anchor list (46/46 landmarks present on all three builds;
    the single `CHANGED` anchor both runs agree on is that one string). `translations/en.json` and
    every file under the webview's `dist/web/assets/` (691 files) are identical, hash for hash,
    across 2.2.0, 2.2.1 and 2.2.3.
  - **What moved between 2.2.0 and 2.2.3 lives in the IDE shell and in Remote-SSH, not in
    `bob-code`.** The public IBM changelog attributes 2.2.1 to an internal bug fix and 2.2.2/2.2.3 to
    Remote-SSH (csh/tcsh shell support, SSH server install); `product.json`'s own integrity hashes
    confirm the moving parts are the VS Code shell files around the extension, not the extension
    itself.
  - **Confirmed on a real task run by the 2.2.3 build** (task `9ad66ac1`, 4 priced LLM calls): the
    stored system prompt still has the same 12 sections and 8 guidance blocks as the 2.2.0-era tasks
    (`f93b5fd9`, `e860b444`), with no `boreas`/`orion` sections; `_meta.spend` on every call is still
    `{cost, contextTokens}` only, so the per-call unit price (Bobcoins/M tokens) still cannot be
    measured, same as on 2.2.0; the server-pushed flag set (including the two flags marked
    `[pushed, not read]`) is unchanged.
  - No reference note needed a content correction: every fact that steps 1–7 of the re-verification
    procedure could check held unchanged. `private/SOURCES.md` records the full method and the two
    steps' outputs ("Verdicts 2.2.0 → 2.2.1 → 2.2.3" and "Steps 6-7 on 2.2.3 (TASK-16.2)").
  - **What changed in bob-sideshow**: every published file that stated "verified on 2.2.0" or cited
    that build as its verification build now says 2.2.3 and build
    `1.126.0+bob2.2.3.20261014125159`, including the `[pushed, not read by …]` labels in
    `bob-version`. Facts that were not re-checked by this task (the 2.1.0-era billing rates in
    `bob-agent-rules`, `rule_locations.py`'s plugin-trust logic) keep their earlier label, unchanged.
    `VERIFIED_EXTENSION` is `2.2.3` and `VERIFIED_SCHEMA` is still `011_key_value_store` in the five
    copies of `_bobcheck.py`.
- The 2.2.0 → 2.2.1 → 2.2.3 build baselines (including the webview, 691 files, which 0.3's baselines
  had skipped) are stored under `private/` for the next re-verification; `private/` is gitignored, so
  they ship with no release.

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
