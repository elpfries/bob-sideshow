---
id: TASK-13.4
title: Establish what changed between Bob 2.1.0 and 2.2.0
status: To Do
assignee: []
created_date: '2026-09-28 19:46'
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
