# bob-sideshow

## Why

IBM Bob is brilliant, eloquent, and now and then steps on a rake: it does not always follow the
instructions it is given, and the metrics confirm the feeling that some requests are routed to an
economy model that is not suited to them. It also has to coexist with tools that steer agents
through nudges in `AGENTS.md`, such as [Backlog.md](https://github.com/MrLesk/Backlog.md) — nudges
Bob may ignore or rewrite.

bob-sideshow makes those behaviours visible — version, local telemetry, approval rules, the rules
Bob injects about subagents and model choice — and gives you the means to override them, so that
Bob interoperates with the rest of your toolchain and agentic coding stays cost-aware and as
secure as possible.

Unofficial, not affiliated with IBM. Reverse-engineered from IBM Bob 2.1.0 (`bob-code` 2.1.0, build
`1.126.0+bob2.1.0.20260827055214`, macOS). Every script checks the installed version and warns
when it differs.

## How

bob-sideshow never touches Bob's code: the application is signed, so modifying it is neither
possible nor attempted, and no vulnerability is exploited. Everything comes from reading the
shipped files, the local SQLite database (`~/.bob/db/bob.db`) and the settings, and from the same
rules, agents, skills and hooks any user can add under `.bob/`.

Those files and that database are not officially supported interfaces: their layout can change
with any release, so there is no guarantee that every feature works on future or past Bob
versions. The version guard tells you when you are off the verified build.

## Skills

- `bob-version` — which Bob am I running?
- `bob-telemetry` — what did Bob spend, on which model, in which task?
- `bob-security-model` — why does Bob ask me to approve this? would it auto-approve that?
- `bob-agent-rules` — which rules does Bob follow about subagents, models, inline answers?
- `bob-override-rules` — make Bob follow my rules instead

## Install

```sh
./install.sh                 # ~/.bob/skills/   all workspaces
./install.sh --workspace .   # ./.bob/skills/   this project
```

Bob loads skills at the next task; then type `/bob-version` or just ask.

## Uninstall

```sh
rm -rf ~/.bob/skills/bob-{version,telemetry,security-model,agent-rules,override-rules}   # global
rm -rf .bob/skills/bob-{version,telemetry,security-model,agent-rules,override-rules}     # this project
```

Files you created with `bob-override-rules` stay in place: `.bob/rules/*.md`,
`.bob/agents/explore-premium.md`, `.bob/hooks/command-guard.mjs` and the `hooks` entry in
`.bob/settings.json`. Remove the ones you no longer want.

## Example: subagents on the premium model

Bob's `explore` subagent is wired to the economy `explorer` model, whatever you ask for.
To override it:

> **You:** `/bob-override-rules` I want subagents to run on the premium model
>
> **Bob:** writes `.bob/rules/premium-subagents.md` — never use `explore`, use `explore-premium`
> or `general` — and `.bob/agents/explore-premium.md`, a read-only agent with `model: premium`,
> then tells you the rule loads at the next task.

Next conversation, in Agent mode (Plan and Ask only allow `explore`):

> **You:** launch a subagent to find where tasks are parsed
>
> **Bob:** `spawn_subagent` · `name: explore-premium` …

Then check which model was billed:

> **You:** `/bob-telemetry` which model did that subagent use?
>
> **Bob:** runs the `calls` view — the subagent's calls show `rate/M 2.000  standard`, where the
> built-in `explore` showed `0.833  economy`.

Scripts are Python 3, standard library, read-only, offline; the hook template needs Node.js.
Issues welcome, especially from other builds or platforms — attach `bob_version.py --json`.

Changes between versions: [CHANGELOG.md](CHANGELOG.md).

MIT — see [LICENSE](LICENSE).
