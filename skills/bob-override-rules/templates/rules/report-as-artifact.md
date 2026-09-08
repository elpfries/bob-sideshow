# Reports go into an artifact

This workspace rule narrows the built-in artifact guidance ("answer those inline in markdown, no
matter how detailed they are") for one case: the user asks for a report.

- When the user asks for a "report", "document", "one-pager", "summary page" or "something I can
  share", produce it with `create_html_artifact` after the work is done, and keep the chat message
  to one or two sentences.
- Everything else stays inline: answers, task results, code, diagrams (mermaid renders in-chat).
- Ask before creating an artifact only when the request could also be read as a code deliverable.
