---
id: TASK-3
title: Define the deterministic Bob configuration baseline for benchmark runs
status: To Do
assignee: []
created_date: '2026-09-19 20:15'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies:
  - TASK-1
documentation:
  - skills/bob-security-model/reference/approvals.md
  - private/benchmark-harness.md
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every run must start from a byte-identical Bob configuration, and that configuration must preserve the behaviour under test.

Rule: neutralise what is noise, never what is measured. The approval model is the object of the friction benchmark, so the approved-command list, the permission groups and the auto-approval toggle keep their shipped defaults on the friction arm. Only non-approval sources of variance are pinned (retention, telemetry, autocondense, turn and cost caps, terminal profile).

Two settings need special attention because they silently void a run:

- Workspace trust. getConfig() falls back to DEFAULT_BOB_CONFIG with autoApprovalEnabled forced to false when the workspace is untrusted, discarding the whole approval config. A container opening a fresh clone hits this. Both the IDE-level trust prompt and the Bob-level security.folderTrust.enabled must be settled before the run starts.
- Command security verification. isCommandSecurityEnabled sends every command to a side model with a 15 s fail-closed timeout, no cache. That is real product behaviour and belongs in the friction arm, but it adds unbounded latency to the capability arm. It must be an explicit, recorded run parameter rather than a hidden default.

A deny list is kept in every arm as a container safety net; it is enforced by validateToolExecution before auto-approval, so it survives the patched arm too.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A run starts from a configuration written at container start, identical across runs of the same arm
- [ ] #2 Workspace trust is resolved before the first prompt, and a run that starts untrusted is rejected rather than scored
- [ ] #3 isCommandSecurityEnabled is an explicit run parameter, recorded in the run output
- [ ] #4 Approval-related defaults are left as shipped on the friction arm, and the departures are listed in the task notes
- [ ] #5 Turn and cost caps bound a runaway run without being reachable in a normal scenario
- [ ] #6 A deny list blocks destructive commands in every arm, including the patched one
<!-- AC:END -->
