---
id: TASK-16.1
title: >-
  Store the 2.2.1 and 2.2.3 build baselines, webview included, and amend the
  freeze step
status: To Do
assignee: []
created_date: '2026-10-19 08:18'
labels:
  - 'model:secondaire'
dependencies: []
parent_task_id: TASK-16
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
First half of TASK-16, doable now with no dependency on Bob traffic. The installed app is 2.2.3; its `bob-code` bundle is byte-identical to 2.2.1 (sha1 6062c88fb39bb33a7b1f24f8d2cf08911e8dcac5), so `private/baseline-2.2.1/` already holds the four files the method reads and `private/diff/2.2.1/` its extraction. What no 2.2.x baseline holds is `dist/web/assets/` (the webview bundles, ~57 MB, 691 files on 2.2.3): the method reads UI texts there (security warning, model picker, settings labels) and a build-to-build diff of them is impossible today. The 2.2.0 and 2.2.1 webview assets no longer exist on this machine; `private/baseline-2.1.0/` shows the only way back: the update endpoint `https://api.us-east.bob.ibm.com/update/...` served the 2.1.0 zip, it may still serve 2.2.0 and 2.2.1. Everything lands in gitignored `private/`, on the model of `private/baseline-2.2.0/README.md` and `-2.2.1/README.md`; the procedure to amend is "Re-verifying on a new build", step 2, in `private/SOURCES.md`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `private/baseline-2.2.3/` holds `extension.js`, `product.json`, `extensions/bob-code/package.json`, `dist/translations/en.json` AND `dist/web/assets/`, each hashed and checked identical to the installed app, with the build string, in its README; the extraction in `private/diff/` is referenced
- [ ] #2 The missing webview assets of 2.2.0 and 2.2.1 are either recovered from the update endpoint into their baseline folders with hashes, or the attempt and its failure are recorded in those READMEs
- [ ] #3 Step 2 of the procedure in `private/SOURCES.md` lists `dist/web/assets` among the files to freeze, and the `bundle_diff.py anchors` and `compare` verdicts for 2.2.0 → 2.2.1 → 2.2.3 are recorded there
- [ ] #4 `git status` shows nothing under `private/`; no personal path or data in any README written
<!-- AC:END -->
