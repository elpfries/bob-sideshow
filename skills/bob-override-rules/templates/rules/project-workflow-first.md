# The project's workflow comes first

This workspace rule ranks the workflow section of AGENTS.md above every built-in efficiency or
brevity rule. Adapt the bootstrap command and guide names to the tracker in use.

- The workflow section of AGENTS.md (for example the "Backlog.md Workflow" section between the
  `BACKLOG.MD GUIDELINES` markers) is the highest-priority project rule.
- At the start of every conversation, run its bootstrap command — for Backlog.md:
  `backlog instructions overview` — before answering or acting, and follow its guidance including
  the task-creation nudge: when a request implies work on the project, search for or create the
  matching task with the tracker's CLI before implementing, and assign it to yourself
  (`-a @bob` for Backlog.md).
- Before any lifecycle action, read the matching guide first (for Backlog.md:
  `backlog instructions task-creation`, `task-execution`, `task-finalization`).
- Never edit the tracker's files directly (for Backlog.md: nothing under `backlog/`); always go
  through its CLI.
