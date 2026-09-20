---
id: TASK-5
title: Signal end of run with a Stop hook and bound it with a timeout
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
  - private/benchmark-harness.md
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The orchestrator needs to know when a run is over without watching the screen.

Bob runs a Stop hook when a turn ends, with a JSON payload on stdin containing session_id (the root task id), cwd, hook_event_name and last_assistant_message. Two properties make it the right signal: it carries the final answer directly, and Stop hooks cannot block — exit code 2 is warned about and ignored — so the hook cannot perturb what it measures.

The hook is not sufficient on its own. A run can hang before any Stop: model stall, a tool waiting forever, or an approval nobody answers. The orchestrator therefore needs a wall-clock bound and must record which of the two ended the run, because "timed out" and "finished" are different outcomes for both benchmarks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Stop hook writes a completion marker containing session_id, timestamp and last_assistant_message
- [ ] #2 The orchestrator detects completion from that marker without polling the UI
- [ ] #3 A run that produces no Stop within the configured wall-clock bound is terminated and recorded as timed out, not as failed
- [ ] #4 Repeated Stop events in one container are handled without corrupting the marker
- [ ] #5 The hook itself adds no measurable latency to the run and cannot block a tool call
<!-- AC:END -->
