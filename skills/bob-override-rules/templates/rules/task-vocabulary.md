# "Task" means a Backlog.md task

This workspace rule resolves a vocabulary collision: Bob's own `start_subtask` tool describes
itself as "create a new task instance", and a Bob conversation is internally called a task. In this
project a task is always a tracker task, never a Bob subtask or subagent.

Adapt the tracker name and commands below if the project uses something other than Backlog.md.

- When the user asks to create, split, update or close a task (task, tâche, ticket, issue), use the
  `backlog` CLI through `execute_command`. Read `backlog instructions task-creation` first, and
  never edit files under `backlog/` directly.
- Never call `start_subtask` for this, whatever its description says: that tool starts a new Bob
  conversation, not a project task. Use it only when the user explicitly says "subtask",
  "sous-tâche" or "Bob subtask".
- `spawn_subagent` delegates investigation; it never creates a task.
- `update_todo_list` tracks steps inside the current conversation; it is not the project tracker.
- When the intent is ambiguous, ask before acting rather than guessing.
