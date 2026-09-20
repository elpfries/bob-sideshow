---
id: TASK-12
title: Decide where the benchmark harness lives and what may be published
status: To Do
assignee: []
created_date: '2026-09-19 20:17'
updated_date: '2026-09-20 02:11'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies: []
documentation:
  - private/benchmark-harness.md
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The harness does things the published project promises it does not do, and that has to be settled before any of it is committed.

README states that bob-sideshow never touches Bob code, because the application is signed. The auto-approval arm patches the bundle. Publishing the patch in the same repository would make that statement false and change what the project is, on top of the licence question raised by modifying the application.

The repository already draws this line: private/ holds the reverse-engineering notes and bundle tools and is gitignored. The decision is whether the harness follows the same rule, moves to a separate repository, or is published with the README claim rewritten — and, separately, whether measured results may be published without the tooling that produced them.

Whatever is decided, the benchmark numbers are only meaningful next to the build they came from, so any published result has to carry the Bob build and the arm it was measured on.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A decision is recorded on where the harness lives: gitignored, separate repository, or published
- [ ] #2 If anything is published, the README claim about never touching Bob code is consistent with what ships
- [ ] #3 The licence and terms question around modifying the application is stated explicitly, not left implicit
- [ ] #4 Any published result carries the Bob build, the arm and the model it was measured on
- [ ] #5 Credentials, personal data and task history from real usage cannot leak through published artefacts
<!-- AC:END -->
