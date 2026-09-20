---
id: TASK-6
title: 'Answer approval requests with a SQLite-detected, CDP-driven approval driver'
status: To Do
assignee: []
created_date: '2026-09-19 20:15'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:primaire'
milestone: m-0
dependencies:
  - TASK-1
  - TASK-4
documentation:
  - skills/bob-security-model/reference/approvals.md
  - private/benchmark-harness.md
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The core of the harness: approvals must be answered automatically, deterministically, and without disturbing the measurement.

Detection comes from SQLite, never from pixels. The task_pending_approvals table (task_id, request_id, payload_json, created_at) states exactly what is pending and since when. It is exact, instant, and gives the request payload for cross-checking.

Actuation comes from CDP. bobide is Electron: started with a remote debugging port, the driver attaches to the chat webview and clicks the approval control by DOM selector. Screen capture, template matching and synthetic clicks are out of scope — they add their own latency to the number being measured, and a misclick lands on reject and silently changes the agent trajectory with no trace.

Two behaviours of the approval UI must be handled explicitly:

- A command flagged by the security check renders a different card: the approve control stays disabled until the acknowledgeRisk checkbox ("I understand the risk") is ticked, and the always-approve control is hidden.
- The always-approve control must never be used. It writes to taskCommandApprovals, so the next identical command is auto-approved and friction decays during the run. Only the one-shot approval keeps every request comparable.

Posting the webview reply message directly (uiReply with a toolCallId) would be faster than clicking, but the payload shape for the approval card has not been extracted; clicking by selector needs no further reverse engineering and is the expected implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pending approvals are detected by reading task_pending_approvals, with no screen capture or OCR anywhere in the harness
- [ ] #2 A pending approval is answered over CDP by acting on the approval card in the webview
- [ ] #3 Security-warning cards are recognised and their risk acknowledgement is handled before approving
- [ ] #4 The driver only ever grants one-shot approvals; it never uses always-approve and never edits the approval configuration mid-run
- [ ] #5 Several approvals queued at once are answered one by one, with no double-answer and no skipped request
- [ ] #6 A card the driver does not recognise aborts the run with a distinct status instead of being answered by guesswork
- [ ] #7 Each approval records the request payload, its created_at and the moment it was answered
- [ ] #8 The driver reports its own overhead separately from Bob time, so it can be subtracted from friction figures
<!-- AC:END -->
