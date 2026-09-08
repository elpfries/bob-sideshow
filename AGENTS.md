# Contributing rules

- Skill directory name = frontmatter `name`; regex `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 chars.
- Scripts: Python 3.8+, standard library, read-only, offline. Templates may use Node.js.
- `scripts/_bobcheck.py` is copied into every skill: keep the copies identical
  (`shasum skills/*/scripts/_bobcheck.py` shows one hash). Bump `VERIFIED_*` there only after
  re-verifying the reference notes on the new build.
- State the build every fact was reverse-engineered from, and its source (bundle, database, public docs).
- Before a PR: `python3 -m py_compile skills/*/scripts/*.py`,
  `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs`, and run each script
  against a real installation.
- No personal data in examples or fixtures.
