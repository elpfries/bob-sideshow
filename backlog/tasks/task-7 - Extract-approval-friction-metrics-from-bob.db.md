---
id: TASK-7
title: Extract approval friction metrics from bob.db
status: To Do
assignee: []
created_date: '2026-09-19 20:16'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies:
  - TASK-6
documentation:
  - skills/bob-telemetry/scripts/bob_telemetry.py
  - private/benchmark-harness.md
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn one run into the friction half of the benchmark.

The database already holds everything needed, so the metrics are derived after the run rather than instrumented during it:

- task_pending_approvals gives every stop, its payload and its created_at; paired with the answer timestamps from the approval driver it gives how long Bob sat idle waiting for a human.
- messages.data.toolUsage.commandUse holds the per-call security verdict, stored for every command parameter with no cache, including the reason when the side model flagged it.
- tasks.approval_config records the approval state the task actually ran under, which is how a run proves it was not silently drifting.

The figures that matter: how often Bob stops, on which tools and permission groups, how much wall-clock is spent waiting, how many commands went to the security model, how many came back dangerous, and how many were unverifiable or denied outright. The driver overhead must be excluded so the number describes Bob, not the harness.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A run produces a friction record: stop count, stops per tool and per permission group, and total wait time
- [ ] #2 Security-check outcomes are counted from toolUsage.commandUse, including flagged reasons and unverifiable commands
- [ ] #3 Commands blocked by the deny list are reported separately from approval stops
- [ ] #4 Approval-driver overhead is excluded from the reported wait time
- [ ] #5 The approval configuration the run actually used is read back from tasks.approval_config and included in the record
- [ ] #6 Metrics are computed read-only from a copy of the database, leaving the run artefacts untouched
<!-- AC:END -->
