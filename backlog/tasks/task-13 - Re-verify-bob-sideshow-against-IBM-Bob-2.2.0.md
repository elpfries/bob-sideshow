---
id: TASK-13
title: Re-verify bob-sideshow against IBM Bob 2.2.0
status: To Do
assignee: []
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 22:26'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Bob shipped 2.2.0 (`bob-code` 2.2.0, build `1.126.0+bob2.2.0.20260924155054`) and every skill now prints a mismatch warning on start: the reference notes, the version and schema constants, the README and the comparison docs all say 2.1.0. Until the facts are re-read on the new build, the project advertises a provenance it no longer has.

Three kinds of drift are already visible on the installed 2.2.0 build.

The database gained a migration, `011_key_value_store`, and a `key_value_store` table, so `VERIFIED_SCHEMA` is stale in all five copies of `_bobcheck.py`.

The extension bundle went from 14.7 MB to 10.6 MB and is minified more aggressively. The exported identifier names the 2.1.0 notes lean on as anchors — `SUBAGENT_PRESETS`, `MODEL_TIERS`, `DEFAULT_MODEL_TIER`, `parseAgentFile`, `loadWorkspaceRules`, `INIT_BASE_PROMPT`, `getBestCommandMatch`, `findLongestMatchingCommandPattern`, `DEFAULT_APPROVED_COMMANDS`, `assessCommandSecurity`, `featureFlagsSchema`, `isWorkspaceTrusted` — no longer exist as literals, while prompt text, settings keys and error messages survive. Every note anchored on a name has to be re-located from the strings that are left, and re-anchored on something that survives minification. Some facts do hold: the default approved-command list is unchanged, and the hook event set is `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `PreToolUse`, `PostToolUse`, `Stop` — which the current references never spell out.

Nothing crashes: all five scripts run on 2.2.0. So this is verification and honest re-labelling, with repair only where a fact turns out to have moved. The system-prompt section list is the exception that needs new data — the newest stored prompt predates the update, so it can only be compared from a task created under 2.2.0.

AGENTS.md requires every fact to state the build it was read from, and `VERIFIED_*` to be bumped only after re-verification, so the constants move last, not first.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every published version claim reads 2.2.0 — the three reference notes, the script docstrings and headers, README, CHANGELOG and the comparison docs
- [ ] #2 `VERIFIED_EXTENSION` is 2.2.0 and `VERIFIED_SCHEMA` is `011_key_value_store`, the five `_bobcheck.py` copies stay byte-identical (one `shasum`), and no skill warns on a 2.2.0 install
- [ ] #3 Each of the five scripts is run against the 2.2.0 installation and its output checked, not just its exit code: version, telemetry (including the new table and the measured unit prices), prompt dump on a task created under 2.2.0, approval check, rule locations
- [ ] #4 The subagent guidance, model tiers, rule precedence and approval-gate facts are each re-located in the 2.2.0 bundle, and the ones that moved are corrected rather than reworded
- [ ] #5 Anchors cited for a fact are ones that survive the new minification — prompt text, settings keys or messages, not minified identifier names
- [ ] #6 The documented hook event set and hook payload contract, including the shipped guard template, match 2.2.0
- [ ] #7 Any fact that could not be re-verified on 2.2.0 is marked as such instead of being carried over silently
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-09-29 -- Les quatre sous-taches de TASK-13 sont closes. Preuves :
- TASK-13.4 (page docs/) : commit fec4c78, docs/bob-2.1.0-to-2.2.0.md.
- TASK-13.1 (relocalisation des faits 2.2.0, template explore-premium.md, contrat command-guard.mjs) : commits d16cec7 et 770d8e5.
- TASK-13.2 (re-verification base et scripts sur bob-code 2.2.0) : commit df6dace.
- TASK-13.3 (re-etiquetage du projet en 2.2.0, bump VERIFIED_*) : commit 0437172.
Details et preuves d execution dans les notes de chaque sous-tache. TASK-13 elle-meme et la milestone ne sont pas cloturees par cette note.
<!-- SECTION:NOTES:END -->
