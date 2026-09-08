# Subagents always run on the default (premium) model

This workspace rule overrides the built-in `explore` subagent preset, which is wired to the
economy `explorer` model.

- Never use the built-in `explore` subagent.
- For read-only exploration or analysis, use `explore-premium` (defined in
  `.bob/agents/explore-premium.md`, `model: premium`).
- For anything else, use `general`: it inherits the current mode's tools and the default model.
- Never describe a subagent as running on the most capable model unless it was `explore-premium`
  or `general`.

Note for the user: Plan and Ask modes only allow `explore`; switch to Agent mode when a premium
subagent is needed. In production every tier except `explorer` maps to the same `premium-ide` alias.
