---
id: TASK-13.3
title: Re-label the project to 2.2.0 and bump the verification constants
status: To Do
assignee: []
created_date: '2026-09-28 19:34'
updated_date: '2026-09-28 19:40'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies:
  - TASK-13.1
  - TASK-13.2
parent_task_id: TASK-13
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Last step, and only once the facts have actually been re-read: the project says 2.1.0 in about twenty places and the five copies of `_bobcheck.py` declare 2.1.0 and `010_pending_approvals` verified, so every skill warns on a 2.2.0 install even where nothing changed.

AGENTS.md makes the order explicit — `VERIFIED_*` is bumped only after re-verifying the notes on the new build, and the five copies must stay identical, one `shasum`. Alongside them, the version strings in the reference note titles, the script docstrings, `rule_locations.py`, the `command-guard.mjs` header, `bob-telemetry/SKILL.md`, README, and the build lines in the comparison docs all have to state the build they now hold for. Where a fact was verified on 2.1.0 and could not be re-checked, the fix is to say so, not to relabel it 2.2.0.

CHANGELOG gets the entry that lets a reader tell what moved between the two builds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `VERIFIED_EXTENSION` is `2.2.0` and `VERIFIED_SCHEMA` is `011_key_value_store` in all five copies, and `shasum skills/*/scripts/_bobcheck.py` shows one hash
- [ ] #2 No shipped script prints a mismatch warning on a 2.2.0 installation
- [ ] #3 No published file claims 2.1.0 provenance for a fact that now holds on 2.2.0 — reference notes, script docstrings and headers, SKILL.md files, README, the comparison docs build lines
- [ ] #4 Facts kept from 2.1.0 without re-verification are labelled with the build they were read on
- [ ] #5 CHANGELOG records the move to 2.2.0 and what changed in Bob between the two builds
- [ ] #6 `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` pass
<!-- AC:END -->
