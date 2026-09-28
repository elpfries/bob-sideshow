---
id: TASK-13.3
title: Re-label the project to 2.2.0 and bump the verification constants
status: To Do
assignee: []
created_date: '2026-09-28 19:34'
updated_date: '2026-09-28 20:30'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Tranché par l'analyse de TASK-13.4 — 2026-09-28 (PRIME sur la description)

- Le build 2.1.0 de référence des notes (sha1 d8b1130e…, suffixe 20260827055214) n'est PAS le build
  2.1.0 téléchargé (sha1 f5ebecbd…, 9 octets d'écart, autre run Jenkins). Le ré-étiquetage doit citer le
  build 2.2.0 installé (1.126.0+bob2.2.0.20260924155054, extension.js sha1 6afa9f9c…) et, pour ce qui
  reste attribué à 2.1.0, la chaîne de build des notes, sans prétendre à un diff octet pour octet.
- Le CHANGELOG doit reprendre le delta comportemental consigné dans TASK-13.4 (agents modelTier, hooks,
  settings, sécurité, execute_command background, prompt), pas seulement le bump de version.
<!-- SECTION:NOTES:END -->
