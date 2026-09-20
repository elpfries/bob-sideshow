---
id: TASK-4
title: Inject the benchmark prompt through a companion VS Code extension
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
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
bobide has no way to run a VS Code command from the command line, so the prompt has to be sent by code running inside the IDE.

bob-code activate() returns its public API object, reachable from another extension through vscode.extensions.getExtension("IBM.bob-code"). The API exposes startTask({workspaceFolder, mode, content, mask}), which opens a task and calls handleInputMessage — the same path as a human pressing enter.

Two traps worth knowing before implementing:

- openNewTask() only fills the chat input via setChatInput; it does not send. Only startTask() submits.
- bob-code.sendMessageWithHiddenPrompt is an equivalent hidden command, but the returned API is the supported surface and should be preferred.

The extension must fail loudly. If the API shape changed with a Bob update, a silent no-op would look like an agent that did nothing, which scores as a capability failure and poisons the whole suite.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The companion extension activates on startup and sends a prompt read from a path given by the environment
- [ ] #2 The prompt is submitted in agent mode against the benchmark workspace folder, without a human interaction
- [ ] #3 A missing bob-code API, a missing prompt file or a failed send aborts the run with a distinct exit status, never a silent no-op
- [ ] #4 The extension sends exactly one prompt per container, and a restart does not resend it
- [ ] #5 Bob engine compatibility is declared and verified against the pinned build
<!-- AC:END -->
