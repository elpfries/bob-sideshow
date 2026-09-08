# Subagents: an explicit request is always honored

This workspace rule overrides Bob's built-in "Subagents" guidance — "Default: do the work
yourself" and the "Do NOT use subagents for …" list — whenever the user asks for a subagent.

- When the user asks for a subagent in any wording ("subagent", "sub-agent", "sous-agent", "spawn",
  "delegate", "in parallel", "lance un agent"), call `spawn_subagent` immediately. Do not evaluate
  whether it is necessary, cheaper, or doable with direct tool calls.
- Never reply that a subagent is unnecessary. If the current mode does not allow the requested
  subagent type, say which restriction applies and offer to switch to Agent mode; never silently
  do the work inline instead.
- Give the subagent a complete, self-contained `description`: goal, scope, files or directories to
  look at, expected output format. If several subagents are requested, spawn them in the same turn
  so they run in parallel.
- When reporting back, name the subagent type you used.
