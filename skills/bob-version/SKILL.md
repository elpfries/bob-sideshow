---
name: bob-version
description: Use when the user asks which IBM Bob version, build, extension, Bob Shell, database schema or server-pushed models are in use. Run it before quoting any bob-sideshow reference note.
---

# Bob version

1. `python3 "<skill-dir>/scripts/bob_version.py"` (`--json` for machine output, `--app PATH` if
   the IDE is not found).
2. Report the lines as printed. If `reference` says `DIFFERENT`, say so: measured output stays
   valid, the reference notes in other skills may not.
