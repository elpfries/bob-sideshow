---
id: TASK-13.4
title: Establish what changed between Bob 2.1.0 and 2.2.0
status: To Do
assignee: []
created_date: '2026-09-28 19:46'
updated_date: '2026-09-28 20:01'
labels:
  - 'model:primaire'
milestone: m-1
dependencies: []
parent_task_id: TASK-13
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Before anything is re-verified or relabelled, the project needs to know what actually moved between the two builds. Right now it knows only that things moved: every script warns, and a dozen anchors vanished.

The difficulty is that there is no 2.1.0 to compare against any more. The update replaced the application in place — `/Applications/IBM Bob.app` is 2.2.0, no copy of the 2.1.0 tree survives on disk, the update caches hold nothing usable, and there is no vendor changelog. So the delta has to be reconstructed from the baselines that do survive, and the task is to decide how far each one carries before trusting it.

Three baselines exist. The repository is one: the reference notes, the comparison docs and the scripts are a written record of 2.1.0, precise enough to test claim by claim against the new bundle. `~/.bob/db/bob.db` is the second and the better one, because it is untouched 2.1.0 evidence rather than a description of it — the last activity is 2026-09-19 and the update landed 2026-09-24, so all 129 stored calls were priced by 2.1.0 and all four stored system prompts were assembled by it. That makes a real before/after possible on the prompt layout and on the unit prices, but only until 2.2.0 usage starts mixing rows in, so the snapshot has to be taken before the other subtasks generate traffic. The third, optional, is retrieving the 2.1.0 build itself from the update endpoint recorded in `product.json`, which would turn the whole exercise into a diff — worth deciding on explicitly rather than by default, since it means a network fetch of a signed application.

What comes out of this is the delta itself — what changed in the prompts, the settings schema, the tool set, the approval path, the database, the hook contract — and, for each item, whether it is a real behaviour change or only a minification artefact. The distinction is the point: a vanished identifier proves nothing about behaviour, and the rest of the milestone depends on not confusing the two.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The 2.1.0 evidence in `bob.db` is snapshotted, read-only, before any 2.2.0 traffic is added to it
- [ ] #2 A documented list of differences between 2.1.0 and 2.2.0 exists, covering at least the system prompt sections and guidance blocks, the settings schema and defaults, the tool set, the hook events and payloads, the approval path, and the database schema
- [ ] #3 Each difference is classified as a behaviour change, a cosmetic or minification artefact, or undetermined
- [ ] #4 Each difference names the evidence it rests on, and differences inferred from the absence of a minified identifier are labelled as inconclusive on their own
- [ ] #5 The decision on whether to retrieve the 2.1.0 build for a direct diff is recorded with its reason, and the delta states which of its findings would change if that diff were run later
- [ ] #6 Facts the 2.1.0 notes assert that the delta cannot confirm either way are listed, so the later subtasks know what to re-read rather than re-word
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Arbitrages tranchés par l'utilisateur — 2026-09-28 (PRIME sur la description)

1. **Le build 2.1.0 est récupéré** depuis l'endpoint de mise à jour enregistré dans product.json
   (https://api.us-east.bob.ibm.com/update/versions), pour faire un vrai diff des deux bundles
   plutôt que reconstruire le delta depuis les notes. Décision de l'utilisateur, prise en
   connaissance du fetch réseau d'une application signée et de la question de terms que TASK-12
   soulève par ailleurs. Le critère #5 est donc tranché dans ce sens : consigner la décision, sa
   raison, et ce que le diff a effectivement apporté.
2. **Le delta est un livrable public**, dans docs/, dans la même veine que les docs de comparaison
   — pas dans private/ ni dans backlog/docs/. Il doit donc être écrit pour un lecteur du projet,
   énoncer le build de chaque fait comme l'exige AGENTS.md, et ne contenir aucune donnée
   personnelle issue de la base locale.

## Snapshot 2.1.0 pris avant tout travail — critère #1

Fait depuis la session d'orchestration le 2026-09-28 22:00, Bob 2.2.0 tournant, donc par
sqlite3 ".backup" via une URI mode=ro et non par copie de fichiers :

    private/baseline-2.1.0/bob.db.2.1.0-snapshot
    sha256 bee901ee943fcd707f7a9ef56b4d5a9f929a0b6a43cdaa825e064de88c16be6a
    3 018 752 octets, chmod 444, integrity_check ok
    18 tâches, 143 messages, 5 system prompts, dernier message daté 2026-09-19

Contenu antérieur à la mise à jour du 2026-09-24 : les appels stockés ont tous été tarifés par
2.1.0 et les system prompts assemblés par elle. C'est la preuve 2.1.0 du delta.

**Nuance qui limite ce snapshot, et qui n'était pas prévue dans la description** : la base a déjà
été migrée en 011_key_value_store par le premier démarrage de 2.2.0. Le snapshot porte donc un
CONTENU 2.1.0 dans un SCHÉMA 2.2.0. Le schéma 2.1.0 lui-même n'est plus récupérable par cette
voie — il faut le lire dans le SQL de migration du bundle, ou dans le bundle 2.1.0 une fois
récupéré. Ne pas présenter ce snapshot comme une preuve du schéma 2.1.0.
<!-- SECTION:NOTES:END -->
