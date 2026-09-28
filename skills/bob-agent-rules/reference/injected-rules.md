# Rules Bob injects — bob-code 2.2.0

Short excerpts; `dump_system_prompt.py` prints the full text of your own prompt.

Re-verified against bob-code 2.2.0, build `1.126.0+bob2.2.0.20260924155054`, using the bundle-diff evidence in
`docs/bob-2.1.0-to-2.2.0.md`; anchors below are literals confirmed present in that build.

## Prompt layout

**Changed on 2.2.0**: the section list below is no longer fixed. It is assembled at runtime from a prompt-section
registry, and which of four registered configs applies — `default`, `boreas`, `aquarius`, `orion` — is chosen by
the longest prefix match of the model id's `provider/family/version`, falling back to `default` (error text
`No "default" prompt config found`, anchor MISSING in 2.1.0). `default` and `aquarius` keep the section list below
unchanged; `boreas` inserts `task_execution` after `investigate_before_answering` and `when_stuck` after `tool_use`;
`orion` inserts `act_and_iterate`, `ground_truth`, `define_done`, `prove_done` after `investigate_before_answering`
(all four tags MISSING in 2.1.0, direct read of the registry). Which family each codename resolves to cannot be
read locally. Confirmed on two bob-code 2.2.0 tasks (`f93b5fd9`, `e860b444`, TASK-13.2, 2026-09-28):
`dump_system_prompt.py --list` on both gives the same section list as `default`/`aquarius` above, with no
`task_execution`/`when_stuck` (`boreas`) or `act_and_iterate`/`ground_truth`/`define_done`/`prove_done` (`orion`)
sections. `default` and `aquarius` stay indistinguishable from the section list alone.

`role_definition` · `investigate_before_answering` · `engineering_discipline` · `tool_use` · `markdown_rules` ·
`auto_appended_context` · `base_rules` · `available_skills` · `user_custom_instructions` · **`project_rules`** ·
`environment_info` · tool guidance (`create_html_artifact`, office, `glob`, `grep`, IBM docs, **Subagents**,
`create_chart`, workflows) · `available_modes`. Every one of these tag names is still a literal string in the
2.2.0 bundle (anchors `role_definition`, `tool_use`, `environment_info`, `available_modes`, `create_html_artifact`
SAME string; `project_rules` and `available_skills` present, confirmed by direct read of the section registry
— the anchor tool's own EDITED verdict on these two short literals is a spurious pairing with an unrelated
similar-length string, not a real change). Section tags themselves left the raw string literals: 2.1.0 stored
`<base_rules>\n…\n</base_rules>` inline; 2.2.0 stores the body alone and wraps it at assembly time
(`{id:"baseRules", tag:"base_rules", content:{type:"text", template:…}}`), rendered `<tag>…</tag>` in `xml` format —
the stored prompt still has the tags, this is an assembly-time artefact, not a removal.

`user_custom_instructions`: "always speak and think in the English (en) language unless the user gives you
instructions below to do otherwise" — hence English subagent briefs.

## `project_rules` — sources, strongest first (`RuleLoader`)

1. `<workspace>/.bob/rules-<mode>/**` 2. `<workspace>/.bob/rules/**` 3. `<workspace>/AGENTS.md` (root only)
4. `~/.bob/rules-<mode>/**` 5. `~/.bob/rules/**`

**Changed on bob-code 2.2.0** (build `1.126.0+bob2.2.0.20260924155054`; anchor `plugins/*/` MISSING in 2.1.0;
direct read of the loader): each root above also includes every directory (or symlink) under a sibling
`plugins/` folder, sorted by name, contributing the same `rules/**` and `rules-<mode>/**` — i.e. root 1/2 really
read `.bob/` **then** `.bob/plugins/<name>/` alphabetically, and root 4/5 read `~/.bob/` then `~/.bob/plugins/<name>/`
alphabetically. Precedence between the five kinds above is unchanged; precedence between roots is `.bob/` (or
`~/.bob/`) first, plugins alphabetically after. The rendering also changed: 2.1.0 produced the markdown headings
`## Workspace Rules for "<mode>" mode`, `## Workspace Rules`, `# Project Instructions (AGENTS.md)`,
`## Global Rules for "<mode>" mode`, `## Global Rules`; 2.2.0 renders the same five groups, same order, as XML
tags `<workspace_rules_<mode>>`, `<workspace_rules>`, `<agents_md>`, `<global_rules_<mode>>`, `<global_rules>`,
each holding `<rule><filename>…</filename><content>…</content></rule>` entries (anchor
`Project Instructions (AGENTS.md)` MISSING in 2.2.0 — re-anchor on `agents_md`, `workspace_rules`, `global_rules`,
all three confirmed present by direct read of the rule-groups renderer next to the `project_rules` prompt-section
entry; the renderer's own minified name is not cited, since it changes on every build). This is an artefact of
rendering, not a precedence change.

Preamble unchanged, confirmed byte-identical (anchor `take precedence over your training defaults` SAME string,
468 chars, both builds): "The following rules are defined by this project and take precedence over your training
defaults. They apply to every response for the duration of this session — do not revert to your defaults as the
conversation grows longer. Before taking any action, check whether a project rule applies. Where rules from
different sources conflict, the more specific source takes precedence: workspace rules override global rules,
and mode-specific rules override common rules." Any file name, depth ≤ 5, except `.DS_Store`, `Thumbs.db`,
`.gitkeep`, `.gitignore`, `.bobignore` — all five ignored-name literals confirmed SAME string on 2.2.0. Not read
at run time: CLAUDE.md, `.cursorrules`, Copilot instructions (`/init` reads them once to rewrite AGENTS.md —
"AGGRESSIVELY" removing the obvious; anchor `AGGRESSIVELY` SAME string, 12 457 chars, both builds — the `/init`
prompt is byte-identical). Untrusted folder → no rules: confirmed the same code path in both builds (both pass
the IDE's `workspace.isTrusted` into the harness); 2.1.0 additionally carried a `trustedFolders.json` /
`TRUST_FOLDER` store whose `resolveFolderTrust` was defined but never called, and that dead module is gone in
2.2.0 (anchor `trustedFolders.json` MISSING in 2.2.0) — a cleanup, not a behaviour change.

## Subagents (guidance block, from `getSystemPromptPart` on the `spawn_subagent` tool)

"**Default: do the work yourself.** Most tasks are faster and cheaper without a subagent." Only when ALL:
self-contained with a summary back; would add significant irrelevant context; not doable in 1–2 direct tool
calls. "Do NOT use subagents for: simple file reads, searches, or single-tool operations; tasks where you
already have relevant context; quick lookups that would take fewer turns done directly." Confirmed byte-identical
on bob-code 2.2.0, build `1.126.0+bob2.2.0.20260924155054` (anchors `Default: do the work yourself`,
`Do NOT use subagents for` SAME string; `getSystemPromptPart` still a literal method name in both builds — the
dotted form `spawn_subagent.getSystemPromptPart` was never itself a bundle literal, it described the call site).

Parameters: `description` (required), `name` (default `general`), `fork_context` (false). Parallel within a
turn. Subagents cannot use `spawn_subagent`, `start_subtask`, `start_workflow`, `switch_mode`, `update_todo_list`
— confirmed unchanged, anchor `SUBAGENT_FORBIDDEN_TOOLS` CHANGED (5 real edits, all renames: `setModelResolver`,
`model`→`modelTier`, `setModel`→`setModelTier`, `onPreToolUse` added to the forwarding list — the forbidden-tools
array itself, `["spawn_subagent","start_subtask","start_workflow","switch_mode","update_todo_list"]`, is
byte-identical; likewise `SUBAGENT_FORBIDDEN_GROUPS`, `["subagent","subtask"]`, unchanged). A `PreToolUse` event
of the parent is now forwarded to the child subtask (`onPreToolUse`, new in 2.2.0) — a routing addition, not a
change to what subagents themselves can call.

| Type | Tools | Model alias | Turns | Notes |
|---|---|---|---|---|
| `explore` | read only | `explorer` | 50 | own short prompt (`rawPrompt`: no project rules); no skills/todo; no `fork_context` |
| `general` | current mode's | default (parent tier) | 25 | full prompt, project rules included |

Confirmed byte-identical on 2.2.0, field rename aside: the `explore` preset object is still `groups:["read"]`,
`rawPrompt:true`, `maxTurns:50`, `denyTools:["update_todo_list","use_skill"]`, `allowForkContext:false`, and the
same system prompt (anchor `Explore codebase` SAME string), just `model:"explorer"` spelled `modelTier:"explorer"`.
It is the **only** preset registered as an object literal (`{explore: <preset>}`) — there is no `general` preset
object; `general` (or any other name that is not a registered preset or a custom agent) falls through to a
dynamic subagent built from the current mode's tools with the parent's model tier, confirmed by direct read of
`resolvePreset`. Its 25-turn default was previously unlocated ("no `maxTurns:25` literal exists in either bundle")
because it is not an object key — it is the nullish-coalescing fallback `setMaxTurns(preset?.maxTurns ?? 25)` at
the subtask-creation call site, present verbatim (same `??25` fallback, same call shape, only the parameter name
renamed) in **both** 2.1.0 and 2.2.0. This closes the "no literal source" gap left open after TASK-13.4.

Modes filter with `allowedSubagents`: Plan and Ask → `["explore"]`; Agent → all. Subagent budget = parent's
remaining `maxCost`; its cost (not tokens) is added to the parent. Confirmed unchanged: anchor `allowedSubagents`
SAME string (5 986 chars, both builds).

Custom agents: `.bob/agents/<name>.md` (confirmed unchanged path, direct read: `Q2e.posix.join("agents","*.md")`
joined under `.bob/`). Frontmatter regex is `/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/` on both builds. Fields:
`name`, `description`, `groups` (default `["read","edit","execute"]`), **`modelTier`** (`fast|premium|ultra|explorer`),
`maxTurns`, `rawPrompt`, `allowForkContext`, `allowTools`, `denyTools`; body = system prompt; `## Output Constraints`
splits a trailer. **Breaking change on bob-code 2.2.0**, build `1.126.0+bob2.2.0.20260924155054` (anchors
`use "modelTier" instead`, `Invalid modelTier` MISSING in 2.1.0; direct read of the frontmatter parser): a `model:`
key in the frontmatter now throws `"model" is not supported in <file>, use "modelTier" instead` instead of being
silently accepted and ignored as on 2.1.0; `modelTier:` is validated against exactly `fast, premium, ultra, explorer`
(`Invalid modelTier "<value>" in <file>. Valid values: fast, premium, ultra, explorer`). All other fields are
unchanged (anchors `allowForkContext`, `denyTools`, `rawPrompt`, `maxTurns` IDENTICAL; `groups` default array and
`## Output Constraints` split both confirmed present). This breaks the shipped
`skills/bob-override-rules/templates/agents/explore-premium.md`, fixed alongside this note (see acceptance
criterion #7 in TASK-13.1) — Bob's actual loading of the fixed template could not be exercised from here.

## Model choice

| Tier | dev gateway | production |
|---|---|---|
| fast | `fast` | `premium-ide` |
| premium (default) | `premium-ide` | `premium-ide` |
| ultra | `ultra` | `premium-ide` |
| explorer | `explorer` | `explorer` |

Confirmed unchanged: the tier list (`["fast","premium","ultra","explorer"]`), visible tiers
(`["fast","premium","ultra"]`) and default (`"premium"`) are the same array/string literals on 2.2.0, and the
production-mapping object above is byte-identical in both bundles (direct read; anchor `https://api.dev.bob.ibm.com`
SAME string). Two more, **internal**, non-user-selectable tiers exist in both builds: `security` (the command
security check, see `skills/bob-security-model/reference/approvals.md`) and `background` (helper calls: message
classification, code summaries) — confirmed by direct read, the two tier-id string literals sit next to the
tier-list array.

- Picker shown only with >1 visible tier; `fast`/`ultra` hidden outside dev mode → no picker in production.
  A tier applies to the root task, locks after the first message, persists in `env._meta.modelTier`.
- Subagents: `explore` → `explorer`, `general` → default (parent tier, confirmed above — no `modelTier` set means
  the child inherits the parent's model resolver). Whether compaction still uses the task's model was not
  re-checked on 2.2.0 and stays unverified.
- **Changed on bob-code 2.2.0**, build `1.126.0+bob2.2.0.20260924155054` (anchors `command-security-model`,
  `tool-model-routing` MISSING in 2.2.0; `featureFlagsSchema` MISSING is only the export name; direct read of the
  flags object — `getFlagValue` keys: 10 on 2.1.0, 8 on 2.2.0): `command-security-model` and `summary-model` are
  no longer read at all (see the security-check rewrite above); `completion-model`, `next-edit-model`
  (`rnj-1-test`), `feedback-model` are still declared unchanged; `experiment-*-tool-model-routing` is gone too.
- Observed billing: `premium-ide` 2.0 Bobcoins / M tokens (in+out, no cache discount), `explorer` 0.833. **Not
  re-verified**: these rates were measured on the 2.1.0 database (calls priced before the 2026-09-24 update), and
  nothing in the code diff touches pricing — re-measuring on 2.2.0 traffic is TASK-13.2's, not re-derivable from
  the bundle alone.

## Vocabulary collision: "task"

`start_subtask` is described to the model as "This will let you **create a new task** instance
using your provided title, message, and initial todo list", its `message` parameter as "the initial
user message or instructions for **this new task**", its `todos` examples as
`[ ] Task description (pending)`. A Bob conversation is itself a task (table `tasks`, "task
breadcrumbs", `TASK_CREATED` telemetry), and `spawn_subagent` "handles a focused **task**".

So "create a task" matches a built-in tool almost literally, while a tracker instruction
(Backlog.md, Jira…) is only prose inside the `project_rules` section (rendered `<project_rules>…</project_rules>`
at assembly time on both builds — the outer tag itself is confirmed present as a literal `tag:"project_rules"` in
the 2.2.0 prompt-section registry; the raw substring `<project_rules>` with its angle brackets is assembled at
runtime on both builds and was never itself a stable bundle literal, so it is not cited here as the anchor) — and
tool definitions weigh more in context than rules (`toolDefinitions` ≈ 6.5k tokens vs `projectRules` ≈ 1.7k in a
typical task; these are runtime measurements, not re-taken on 2.2.0, and stay unverified — the registry entry id
`projectRules` is confirmed present, CHANGED 25 real edits/811→846 tokens, consistent with the XML rendering
change documented above, not with a token-budget change). Two other places repeat the phrase: the `create-plan`
skill ("Using the `start_subtask` tool, create a new task for each subtask in the plan-file") and the
`update_todo_list` prompt ("When blocked, create a new task describing what needs to be resolved") — neither
re-checked against 2.2.0 strings specifically, stays unverified.

No routing logic is involved: the model disambiguates badly and the native tool wins. Fixes: say
"backlog task", add `bob-override-rules` → `templates/rules/task-vocabulary.md`, or drop the
`subtask` group from a custom mode so the tool is never exposed.

## Inline answers (`create_html_artifact` guidance)

"most of what you produce … should still just be a normal chat reply" · "only call this tool when the user
has explicitly asked for it" · "A general question, a task result, or a long answer is NOT a signal — answer
those inline in markdown, no matter how detailed they are" · never for code, tutorials, diagrams (mermaid
renders in-chat) · `create_chart` only "when the user asks for a chart". Confirmed byte-identical on bob-code
2.2.0 (anchors `answer those inline in markdown`, `only call this tool when the user has explicitly asked` SAME
string, 444 chars, both builds).

## Also in the prompt

`base_rules`: prefer edit tools over `write_file`; complete content on write; "Be direct and technical";
"Do not ask unnecessary follow-up questions"; validate before completion. `investigate_before_answering`:
"Never speculate about code you have not opened." Skills: activate only clearly relevant ones, once per context.
The skills preamble is reworded on 2.2.0 (artefact, same substance): 2.1.0 rendered a separate `<available_skills>`
tag followed by "Review the available skills below…"; 2.2.0 has no raw `<available_skills>` literal (assembled at
runtime, `tag:"available_skills"` in the section registry, `id:"skills"`) and prefixes the same list with "You
have access to skills that provide specialized instructions for specific tasks. Review the available skills
below… Only activate skills that are clearly relevant… Activate each skill once per current context window…" —
same guidance, reworded into one paragraph.
