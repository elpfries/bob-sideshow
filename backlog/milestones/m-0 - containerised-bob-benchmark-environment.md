---
id: m-0
title: "Containerised Bob benchmark environment"
---

## Description

A disposable Linux container that runs IBM Bob (bob-code IDE agent) headless and reproducibly, so runs can be scored automatically.

Two measurements, one harness:

1. **Capability** — can Bob complete a scenario? Scored from the workspace diff, the final assistant message, token spend and cost recorded in `~/.bob/db/bob.db`.
2. **Approval friction** — what does Bob's approval model cost? Scored from `task_pending_approvals` (how often it stops, on what, for how long) and from the security verdicts in `messages.data.toolUsage.commandUse`.

Approach: SQLite for detection, CDP for actuation. Pending approvals are detected by reading `task_pending_approvals`, and answered by attaching to the Electron webview over the Chrome DevTools Protocol (`--remote-debugging-port`). Screen capture, OCR and synthetic clicks (xdotool/OpenCV) are explicitly rejected: they inject their own latency into the measurement and a misclick silently rejects a tool call without leaving a trace.

Friction is measured as a differential: the same scenarios run with approvals live, and again against a build whose `shouldAutoApprove` is short-circuited, so the cost of the approval model is the gap between the two arms.

Everything is reverse-engineered from bob-code 2.1.0; the image pins that exact build because the harness depends on internal anchors that the minifier renames between releases.
