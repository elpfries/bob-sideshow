---
id: TASK-11
title: Define the benchmark scenario set and its scoring
status: To Do
assignee: []
created_date: '2026-09-19 20:17'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies:
  - TASK-8
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Without scenarios the harness measures nothing. This task defines what Bob is asked to do and how a run is graded.

The set has to serve both halves of the milestone at once. Capability needs scenarios with an objective pass condition — a test that goes green, a file that gains a property, a bug that stops reproducing — not a judgement about prose. Friction needs scenarios that genuinely exercise the approval model: commands outside the default approved list (cat, git diff, git log, git rev-parse, git show, git status, grep, head, tail, ls, sort, wc, which, du, df), writes, pipelines that split into several sub-commands, and at least one case that trips the security heuristics.

Scenarios must be self-contained and offline where possible: a network flake or a package registry outage otherwise shows up as an agent failure. Each one pins its own starting workspace so every repetition starts identically.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each scenario ships a fixed starting workspace and a deterministic pass condition that runs without a human
- [ ] #2 Scoring is reproducible: the same artefacts scored twice give the same result
- [ ] #3 The set includes scenarios that trigger approvals beyond the default approved command list, including multi sub-command pipelines
- [ ] #4 At least one scenario reliably triggers the security check, and one produces an unverifiable command
- [ ] #5 Scenarios run offline, or declare their network dependency explicitly
- [ ] #6 A scenario that fails for harness reasons is distinguishable from one the agent failed
<!-- AC:END -->
