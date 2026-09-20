---
id: TASK-9
title: Build the benchmark orchestrator over disposable containers
status: To Do
assignee: []
created_date: '2026-09-19 20:16'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:primaire'
milestone: m-0
dependencies:
  - TASK-2
  - TASK-3
  - TASK-5
  - TASK-6
  - TASK-8
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The component that turns a single working run into a benchmark.

One run equals one disposable container: start, inject the prompt, drive approvals, wait for the Stop marker or the timeout, collect artefacts, destroy. No state is shared between runs — no reused bob.db, no warm workspace, no leftover task history — because Bob persists approvals and task context that would leak the previous run into the next one.

The orchestrator runs a suite as scenarios by arms by repetitions, since a single run of an LLM agent says nothing. It must tolerate a hung or crashed container without losing the rest of the suite, and it must be able to resume a partially finished suite rather than restarting from zero.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A suite runs scenarios across arms with a configurable repetition count, one container per run
- [ ] #2 No state persists between runs; a run cannot observe the previous one
- [ ] #3 A hung, crashed or invalid run is recorded and the suite continues
- [ ] #4 An interrupted suite can be resumed without rerunning completed runs
- [ ] #5 Runs can execute concurrently up to a configured limit, without approval drivers interfering with each other
- [ ] #6 The suite produces an aggregate over the per-run records, keeping raw records addressable
<!-- AC:END -->
