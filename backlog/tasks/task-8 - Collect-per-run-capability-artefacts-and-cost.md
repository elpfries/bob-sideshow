---
id: TASK-8
title: Collect per-run capability artefacts and cost
status: To Do
assignee: []
created_date: '2026-09-19 20:16'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies:
  - TASK-5
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn one run into the capability half of the benchmark.

Everything a scorer needs is produced by the run itself and must be captured before the container is destroyed:

- the workspace diff, which is what the scenario is actually graded on;
- the final assistant message, already delivered by the Stop hook;
- spend, from tasks.costs and from messages.data._meta.spend per LLM call, which also exposes which model served each call;
- the outcome status: finished, timed out, aborted by the approval driver, or invalid.

One run produces one self-describing record. It must carry enough provenance — Bob build, model, arm, scenario, configuration hash — that a result found months later can be trusted without the surrounding scripts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each run emits a single machine-readable record with outcome, duration, cost, tokens and model
- [ ] #2 The workspace diff produced by the run is captured as an artefact
- [ ] #3 The final assistant message is captured from the Stop hook payload
- [ ] #4 The record carries provenance: Bob build and extension SHA-1, pinned model, arm, scenario id and configuration hash
- [ ] #5 Artefacts are collected before the container is destroyed, and a destroyed container loses nothing
- [ ] #6 Invalid runs are recorded with their reason instead of being dropped silently
<!-- AC:END -->
