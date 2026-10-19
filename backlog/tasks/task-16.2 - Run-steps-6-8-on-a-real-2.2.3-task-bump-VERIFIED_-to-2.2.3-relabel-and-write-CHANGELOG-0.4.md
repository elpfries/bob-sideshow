---
id: TASK-16.2
title: >-
  Run steps 6-8 on a real 2.2.3 task, bump VERIFIED_* to 2.2.3, relabel and
  write CHANGELOG 0.4
status: To Do
assignee: []
created_date: '2026-10-19 08:18'
labels:
  - 'model:secondaire'
dependencies:
  - TASK-16.1
parent_task_id: TASK-16
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Second half of TASK-16. Steps 1-5 of `private/SOURCES.md` "Re-verifying on a new build" are done and recorded (see TASK-16 description and `private/baseline-2.2.1/README.md`): the 2.2.3 `bob-code` bundle has no behavioural change against 2.2.0. What remains is what the bundle read cannot prove: step 6 (`skills/bob-agent-rules/scripts/dump_system_prompt.py --list`) and step 7 (`skills/bob-telemetry/scripts/bob_telemetry.py summary` and `calls`) need a task **actually executed by Bob 2.2.3** in `~/.bob/db/bob.db`; as of 2026-10-19 there is none (every task created since 2.2.1 has 0 messages). Running one small Bob task in the IDE first is part of this work. Then step 8: bump `VERIFIED_EXTENSION` / `VERIFIED_SCHEMA` in the five identical `skills/*/scripts/_bobcheck.py` copies, restate the build in every published file that currently says 2.2.0 (TASK-13.3 lists the places: README, SKILL.md files, script docstrings, `rule_locations.py`, `command-guard.mjs` header, reference notes, comparison docs build lines), keep the earlier build label on any fact not re-checked, and write the dated CHANGELOG `0.4` section. AGENTS.md: the bump is last; copies identical; py_compile and node --check before a PR; tagging `v0.4` and `gh release create` are the maintainer`s step after the section lands, not this task`s.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Steps 6 and 7 were run on a task actually executed by Bob 2.2.3 (prompt sections and guidance blocks listed, telemetry summary and unit prices read); the task id and what was observed are recorded in `private/SOURCES.md`, and any assumption in the reference notes that no longer holds is corrected
- [ ] #2 `VERIFIED_EXTENSION` is `2.2.3` and `VERIFIED_SCHEMA` matches the installed database`s last migration in all five `_bobcheck.py` copies; `shasum skills/*/scripts/_bobcheck.py` shows one hash
- [ ] #3 No shipped script prints a version or schema mismatch warning on the 2.2.3 installation
- [ ] #4 Every published file that states "verified on 2.2.0" or the 2.2.0 build string states 2.2.3 and build `1.126.0+bob2.2.3.20261014125159` where the fact was re-checked, and keeps its earlier build label where it was not
- [ ] #5 CHANGELOG has a dated `0.4` section saying what moved in Bob between 2.2.0 and 2.2.3 (bundle unchanged except the development-mode Jenkins path; 2.2.1-2.2.3 changes live in the IDE shell and Remote-SSH) and what changed in bob-sideshow
- [ ] #6 `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` pass
<!-- AC:END -->
