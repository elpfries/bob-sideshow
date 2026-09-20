---
id: TASK-2
title: Authenticate Bob non-interactively and pin the model in the container
status: To Do
assignee: []
created_date: '2026-09-19 20:14'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies:
  - TASK-1
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A disposable container cannot go through an interactive login, and a benchmark cannot let the backend pick the model.

Two problems to solve together:

- Credentials must reach Bob without a browser or a human, and must not be baked into the image or committed.
- The model must be fixed for the whole suite. Bob routes some work to cheaper tiers on its own, and server-pushed feature flags (cached in the IDE globalStorage) can change model names between runs. A run whose model differs from the rest of the suite is not comparable and must be rejected rather than scored.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A run authenticates with no interactive step, using credentials injected at container start
- [ ] #2 No credential is present in the image layers or in the repository
- [ ] #3 The model tier used for the run is pinned by configuration and not left to backend routing
- [ ] #4 The model actually used is read back from bob.db after the run and recorded in the run output
- [ ] #5 A run whose recorded model differs from the pinned one is marked invalid instead of scored
<!-- AC:END -->
