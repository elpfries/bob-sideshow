---
id: TASK-13.2
title: Re-verify the database and script surface on the 2.2.0 schema
status: To Do
assignee: []
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 20:01'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies:
  - TASK-13.4
parent_task_id: TASK-13
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2.2.0 database is at migration `011_key_value_store` and carries a new `key_value_store` table, one migration past the schema the scripts declare verified. Everything still reads, but nothing has been checked against the new shape.

Three things need real data rather than a code read. The billing rates were never read in the bundle — they were measured as cost over tokens across stored calls, two flat rates on 2.1.0 — so they have to be re-measured on calls produced by 2.2.0. The system-prompt section list can only be compared from a task created under 2.2.0, because the newest stored prompt predates the update; a 2.1.0 dump already shows sections and guidance blocks the reference note does not list, so the note may have been incomplete or the layout may have moved. And the new `key_value_store` table has to be looked at to know whether it holds anything the telemetry or version views should report, or whether it is irrelevant to them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 What `key_value_store` holds on 2.2.0 is stated, and whether it changes anything the shipped scripts read
- [ ] #2 The unit prices are re-measured over calls made by 2.2.0 and the telemetry model classes and Bobcoin figures are confirmed or corrected
- [ ] #3 A task is created under 2.2.0 and its stored prompt compared section by section against the documented layout, with differences recorded
- [ ] #4 Every view of `bob_telemetry.py` is run on the 2.2.0 database and its output checked for plausibility, not just for absence of errors
- [ ] #5 `bob_version.py` reports the 2.2.0 app, extension, schema and server flags correctly, including any flag key that has appeared or disappeared
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Preuve 2.2.0 — arbitrage tranché par l'utilisateur, 2026-09-28 (PRIME sur la description)

Les critères #2 (tarifs re-mesurés sur des appels 2.2.0) et #3 (system prompt comparé depuis une
tâche créée sous 2.2.0) demandent du vrai usage de Bob 2.2.0, qu'aucun agent ne peut produire.
L'utilisateur génère ce trafic lui-même AVANT que la chaîne démarre, donc l'évidence doit exister
dans ~/.bob/db/bob.db quand cette tâche est prise. La vérifier d'abord : des messages postérieurs
au 2026-09-24 et des appels avec un _meta.spend non nul.

La baseline 2.1.0 est figée à part et ne doit jamais être écrasée :
private/baseline-2.1.0/bob.db.2.1.0-snapshot (sha256 bee901ee…16be6a, chmod 444). Toute
comparaison avant/après se fait entre ce fichier et la base vivante.

Ces deux critères se prouvent maintenant par exécution ; ils ne peuvent pas être cochés sur un
raisonnement, et s'il manque du trafic 2.2.0 il faut le dire plutôt que contourner.
<!-- SECTION:NOTES:END -->
