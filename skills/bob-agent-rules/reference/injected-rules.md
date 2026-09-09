# Rules Bob injects — bob-code 2.1.0

Short excerpts; `dump_system_prompt.py` prints the full text of your own prompt.

## Prompt layout

`role_definition` · `investigate_before_answering` · `engineering_discipline` · `tool_use` · `markdown_rules` ·
`auto_appended_context` · `base_rules` · `available_skills` · `user_custom_instructions` · **`project_rules`** ·
`environment_info` · tool guidance (`create_html_artifact`, office, `glob`, `grep`, IBM docs, **Subagents**,
`create_chart`, workflows) · `available_modes`.

`user_custom_instructions`: "always speak and think in the English (en) language unless the user gives you
instructions below to do otherwise" — hence English subagent briefs.

## `project_rules` — sources, strongest first (`RuleLoader`)

1. `<workspace>/.bob/rules-<mode>/**` 2. `<workspace>/.bob/rules/**` 3. `<workspace>/AGENTS.md` (root only)
4. `~/.bob/rules-<mode>/**` 5. `~/.bob/rules/**`

Preamble: "take precedence over your training defaults … workspace rules override global rules, and
mode-specific rules override common rules". Any file name, depth ≤ 5, except `.DS_Store`, `Thumbs.db`,
`.gitkeep`, `.gitignore`, `.bobignore`. Not read at run time: CLAUDE.md, `.cursorrules`, Copilot instructions
(`/init` reads them once to rewrite AGENTS.md — "AGGRESSIVELY" removing the obvious). Untrusted folder → no rules.

## Subagents (guidance block, from `spawn_subagent.getSystemPromptPart`)

"**Default: do the work yourself.** Most tasks are faster and cheaper without a subagent." Only when ALL:
self-contained with a summary back; would add significant irrelevant context; not doable in 1–2 direct tool
calls. "Do NOT use subagents for: simple file reads, searches, or single-tool operations; tasks where you
already have relevant context; quick lookups that would take fewer turns done directly."

Parameters: `description` (required), `name` (default `general`), `fork_context` (false). Parallel within a
turn. Subagents cannot use `spawn_subagent`, `start_subtask`, `start_workflow`, `switch_mode`, `update_todo_list`.

| Type | Tools | Model alias | Turns | Notes |
|---|---|---|---|---|
| `explore` | read only | `explorer` | 50 | own short prompt (`rawPrompt`: no project rules); no skills/todo; no `fork_context` |
| `general` | current mode's | default (parent tier) | 25 | full prompt, project rules included |

Modes filter with `allowedSubagents`: Plan and Ask → `["explore"]`; Agent → all. Subagent budget = parent's
remaining `maxCost`; its cost (not tokens) is added to the parent.

Custom agents: `.bob/agents/<name>.md`. Frontmatter: `name`, `description`, `groups` (default
read/edit/execute), `model` (`fast|premium|ultra|explorer`), `maxTurns`, `rawPrompt`, `allowForkContext`,
`allowTools`, `denyTools`; body = system prompt; `## Output Constraints` splits a trailer.

## Model choice

| Tier | dev gateway | production |
|---|---|---|
| fast | `fast` | `premium-ide` |
| premium (default) | `premium-ide` | `premium-ide` |
| ultra | `ultra` | `premium-ide` |
| explorer | `explorer` | `explorer` |

- Picker shown only with >1 visible tier; `fast`/`ultra` hidden outside dev mode → no picker in production.
  A tier applies to the root task, locks after the first message, persists in `env._meta.modelTier`.
- Subagents: `explore` → `explorer`, `general` → default. Compaction uses the task's model.
- Server flags: `command-security-model`, `summary-model` (`openai/gpt-oss-20b`), `completion-model`,
  `next-edit-model` (`rnj-1-test`), `feedback-model`; `experiment-*-tool-model-routing` (exposure only).
- Observed billing: `premium-ide` 2.0 Bobcoins / M tokens (in+out, no cache discount), `explorer` 0.833.

## Vocabulary collision: "task"

`start_subtask` is described to the model as "This will let you **create a new task** instance
using your provided title, message, and initial todo list", its `message` parameter as "the initial
user message or instructions for **this new task**", its `todos` examples as
`[ ] Task description (pending)`. A Bob conversation is itself a task (table `tasks`, "task
breadcrumbs", `TASK_CREATED` telemetry), and `spawn_subagent` "handles a focused **task**".

So "create a task" matches a built-in tool almost literally, while a tracker instruction
(Backlog.md, Jira…) is only prose inside `<project_rules>` — and tool definitions weigh more in
context than rules (`toolDefinitions` ≈ 6.5k tokens vs `projectRules` ≈ 1.7k in a typical task).
Two other places repeat the phrase: the `create-plan` skill ("Using the `start_subtask` tool,
create a new task for each subtask in the plan-file") and the `update_todo_list` prompt ("When
blocked, create a new task describing what needs to be resolved").

No routing logic is involved: the model disambiguates badly and the native tool wins. Fixes: say
"backlog task", add `bob-override-rules` → `templates/rules/task-vocabulary.md`, or drop the
`subtask` group from a custom mode so the tool is never exposed.

## Inline answers (`create_html_artifact` guidance)

"most of what you produce … should still just be a normal chat reply" · "only call this tool when the user
has explicitly asked for it" · "A general question, a task result, or a long answer is NOT a signal — answer
those inline in markdown, no matter how detailed they are" · never for code, tutorials, diagrams (mermaid
renders in-chat) · `create_chart` only "when the user asks for a chart".

## Also in the prompt

`base_rules`: prefer edit tools over `write_file`; complete content on write; "Be direct and technical";
"Do not ask unnecessary follow-up questions"; validate before completion. `investigate_before_answering`:
"Never speculate about code you have not opened." Skills: activate only clearly relevant ones, once per context.
