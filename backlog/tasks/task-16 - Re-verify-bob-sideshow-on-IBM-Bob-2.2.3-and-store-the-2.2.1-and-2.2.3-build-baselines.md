---
id: TASK-16
title: >-
  Re-verify bob-sideshow on IBM Bob 2.2.3 and store the 2.2.1 and 2.2.3 build
  baselines
status: To Do
assignee: []
created_date: '2026-10-19 08:17'
updated_date: '2026-10-19 08:19'
labels:
  - 'model:secondaire'
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
IBM Bob auto-updated in place from 2.2.0 to 2.2.1 (2026-10-05) and then to 2.2.3 (2026-10-14; 2.2.2 was never observed on this machine). Every shipped script now prints "bob-code 2.2.3 installed, verified on 2.2.0 — reference notes may be stale", and `VERIFIED_EXTENSION` still says 2.2.0 in the five `_bobcheck.py` copies.

What is already established (steps 1-5 of the re-verification procedure in `private/SOURCES.md`, run 2026-10-05 and 2026-10-19, written up in `private/baseline-2.2.1/README.md` and `private/baseline-2.2.3/README.md`): the `bob-code` bundle of 2.2.3 is byte-identical to 2.2.1 (sha1 6062c88fb39bb33a7b1f24f8d2cf08911e8dcac5), and 2.2.1 differs from 2.2.0 by 34 bytes — one string, a Jenkins translations path only used in development mode (`BOB_IDE_EXTERNAL_PKG_USER` → `BOB_IDE_EXTERNAL`). 46/46 durable landmarks present, 0 strings or props added or removed, `translations/en.json` identical, schema still `011_key_value_store`. The public changelog attributes 2.2.1 to an "internal bug fix" and 2.2.2/2.2.3 to Remote-SSH; `product.json` confirms the moving parts are the VS Code shell files, not `bob-code`. So no reference note changes on its merits: this task is the remaining steps 6-8 of the procedure plus the storage the procedure asks for and that the 2.2.x baselines skipped.

Two gaps to close while doing it. First, `private/baseline-2.2.0/` and `-2.2.1/` deliberately did not copy `dist/web/assets` (the webview bundles, ~57 MB), so UI-text deltas between builds cannot be diffed; the 2.2.0 and 2.2.1 webview assets are gone from the machine (the installed app is 2.2.3), the only hope is the update endpoint still serving those zips. Second, steps 6 (`dump_system_prompt.py --list`) and 7 (`bob_telemetry.py summary` / `calls`) need a task really executed by the new build; as of 2026-10-19 none exists (the tasks created since 2.2.1 are empty shells with 0 messages).

AGENTS.md rules that bind this task: `VERIFIED_*` is bumped only after re-verifying on the new build and last; the five `_bobcheck.py` copies stay identical (one `shasum`); every stated fact names the build it was read on; `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` before a PR; the CHANGELOG section is dated and the release (tag `v0.4`, `gh release create`) happens after it lands — the release itself is the maintainer`s call, not part of this task. `private/` is gitignored: baselines are stored there, never committed. Model to follow: TASK-13.3 (the 2.2.0 relabel) and TASK-15 (the procedure).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TASK-16.1 is Done: the 2.2.3 baseline is stored with its webview assets, the 2.2.0/2.2.1 webview recovery attempt is recorded, and the freeze step of the procedure names `dist/web/assets`
- [ ] #2 TASK-16.2 is Done: steps 6-8 ran on a real 2.2.3 task, `VERIFIED_*` says 2.2.3 in five identical copies, no script warns on 2.2.3, published files restate the build, CHANGELOG 0.4 is written
<!-- AC:END -->
