---
id: TASK-1
title: Pin and run IBM Bob headless in a Linux container under Xvfb
status: To Do
assignee: []
created_date: '2026-09-19 20:14'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies: []
documentation:
  - private/SOURCES.md
  - private/benchmark-harness.md
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Foundation for every benchmark run: a reproducible container image where the Bob IDE (bobide, a VS Code fork) starts without a display server and activates the bob-code extension.

Bob ships no headless mode. The extension only exposes its API once activate() has run inside a real Electron process, so the container needs Xvfb and a full IDE start, not a Node process.

The image must pin one exact Bob build. The whole harness depends on internals that the minifier renames between releases (approval engine anchors, webview selectors), so a floating version silently invalidates results. Auto-update must be off.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Container starts bobide under Xvfb with no host display and no interactive input
- [ ] #2 bob-code extension reaches "Extension activated" in the logs on a cold start
- [ ] #3 The Bob build (app version, bob-code version, extension.js SHA-1) is pinned in the image and asserted at container start; a mismatch fails the run loudly
- [ ] #4 Bob auto-update is disabled inside the image
- [ ] #5 Two builds of the image from the same inputs produce the same pinned Bob build
- [ ] #6 Image build and run are documented with a single command each
<!-- AC:END -->
