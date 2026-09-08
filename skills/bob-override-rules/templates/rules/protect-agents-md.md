# AGENTS.md is maintained by hand: never rewrite it

This workspace rule overrides the `/init` behaviour ("If there's already an AGENTS.md, improve it …
AGGRESSIVELY clean them up") and any request to condense or clean up instruction files.

- Treat `AGENTS.md` and `CLAUDE.md` as read-only project policy. Do not rewrite, condense,
  "improve" or delete sections from them, even when asked to initialize or clean up the project.
- If the user runs `/init` or asks to regenerate AGENTS.md, say that the file is maintained by
  hand and propose to append a clearly delimited section instead; do not touch existing content.
- Put Bob-specific guidance in `.bob/rules/` rather than in AGENTS.md.
- Do not create `.bob/rules-agent/AGENTS.md`, `.bob/rules-ask/AGENTS.md` or
  `.bob/rules-plan/AGENTS.md` unless the user explicitly asks for mode-specific rules.
