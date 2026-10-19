---
id: TASK-16.2
title: >-
  Run steps 6-8 on a real 2.2.3 task, bump VERIFIED_* to 2.2.3, relabel and
  write CHANGELOG 0.4
status: To Do
assignee: []
created_date: '2026-10-19 08:18'
updated_date: '2026-10-19 08:55'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Transmis par TASK-16.1 (2026-10-19), pour TASK-16.2.

Hachages finaux de bob-code sur 2.2.3 (ceux à citer pour le re-étiquetage) : extension.js 10 622 940 octets, sha1 6062c88fb39bb33a7b1f24f8d2cf08911e8dcac5, sha256 7ca2ec05c52ae0db946c0cf8f3bab1a738981b5c35e846b94556dba263bf5c52 — identique octet pour octet à 2.2.1 (cmp). translations/en.json 83 068 octets, sha256 569191956125f08f39df4aeb6bde89297ad59186f9a6cd13964d1885874939a9 — identique à 2.2.0 et 2.2.1. Schéma base inchangé : 011_key_value_store.

private/diff/2.2.3/ n'existe pas et ce n'est pas un oubli : private/diff/2.2.1/ sert d'extraction pour 2.2.3 aussi, parce que extension.js de 2.2.1 et 2.2.3 sont octet pour octet identiques (même sha1 ci-dessus). Si 16.2 a besoin d'une extraction bundle_diff.py pour 2.2.3, c'est private/diff/2.2.1/ qu'il faut lire.

Verdicts déjà rejoués et confirmés par un vérificateur indépendant dans TASK-16.1 (voir ses notes) : bundle_tools.py --landmarks 46/46 sur 2.2.3 installé et sur les baselines 2.2.0/2.2.1 ; bundle_diff.py anchors 2.2.0->2.2.1 avec les 102 ancres historiques -> 19 MISSING in both / 36 IDENTICAL / 46 SAME top-level string / 1 CHANGED ; avec les 46 ancres durables -> 0 MISSING / 20 IDENTICAL / 25 SAME top-level string / 1 CHANGED. Le seul CHANGED dans les deux cas est "Extension activated" (un chemin de workspace Jenkins, BOB_IDE_EXTERNAL_PKG_USER vs BOB_IDE_EXTERNAL, actif seulement en mode développement). cmp confirme 2.2.1 et 2.2.3 identiques en tout point (extension.js et en.json). Conclusion : aucune note de référence n'a besoin d'être réécrite sur le fond pour 2.2.1/2.2.2/2.2.3 ; seul VERIFIED_* doit changer.

Webview (dist/web/assets, 691 fichiers) : désormais gelée pour 2.2.0, 2.2.1 et 2.2.3 (private/baseline-<version>/app/.../dist/web/assets/ + web-assets.sha256 à côté). Les trois builds ont des hachages identiques fichier par fichier — la webview n'a pas changé depuis au moins 2.2.0, donc rien à re-vérifier côté texte UI avant de bumper VERIFIED_*.

Tâche Bob réelle sur 2.2.3 à utiliser pour les étapes 6-7 de la procédure (dump_system_prompt.py --list, bob_telemetry.py summary/calls) : id 9ad66ac118bfa4983e111fcbe843ead8, titre "liste les fichiers du dépot", 11 messages, 4 appels tarifés, créée 2026-10-19 08:27 UTC.
<!-- SECTION:NOTES:END -->
