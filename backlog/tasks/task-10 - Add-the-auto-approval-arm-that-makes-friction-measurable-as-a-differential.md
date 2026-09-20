---
id: TASK-10
title: Add the auto-approval arm that makes friction measurable as a differential
status: To Do
assignee: []
created_date: '2026-09-19 20:16'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies:
  - TASK-1
  - TASK-9
documentation:
  - skills/bob-security-model/reference/approvals.md
  - private/benchmark-harness.md
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Friction has no absolute value; it is the gap between running the same scenarios with the approval model live and with it out of the way. This task builds the second arm.

Bob has no yolo flag in the IDE — the only environment variables it reads are BOB_DEV_KEY, BOB_SUPPORT_KEY and BOB_USE_MODEL_ENV — so the arm is produced by patching the single chokepoint in the bundle. ApprovalEngine.shouldAutoApprove is called by every approval path; short-circuiting it at the top, behind an environment variable, is enough, and the anchor occurs exactly once in the 2.1.0 bundle.

What makes this acceptable inside a container and nowhere else:

- extensions/bob-code/dist/extension.js is not covered by product.json checksums, which list only ten files under out/vs, so the IDE raises no corrupt-installation warning.
- On Linux there is no code signature to invalidate. This is a container-only build and must not be offered as a way to modify an installed Bob.
- validateToolExecution runs before auto-approval, so the container deny list still blocks destructive commands on this arm.

Modifying the application contradicts the promise the published repository makes about never touching Bob code, and most likely IBM licence terms; see the placement task before publishing anything from this arm.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The patch is applied at image build, is idempotent, and targets the pinned build only
- [ ] #2 The build fails if the patch anchor is absent or found more than once, instead of patching the wrong place
- [ ] #3 Auto-approval is gated by an environment variable, so the same image can run both arms
- [ ] #4 A run on this arm produces no rows in task_pending_approvals; any row invalidates the arm
- [ ] #5 The deny list still blocks destructive commands on the patched arm
- [ ] #6 Run records state unambiguously whether the build was patched, and the version guard reports the modified SHA-1 rather than hiding it
<!-- AC:END -->
