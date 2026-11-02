---
name: bob-version
description: Use when the user asks which IBM Bob version, build, extension, Bob Shell, database schema or server-pushed models are in use. Run it before quoting any bob-sideshow reference note.
---

# Bob version

1. `python3 "<skill-dir>/scripts/bob_version.py"` (`--json` for machine output, `--app PATH` if
   the IDE is not found).
2. Report the lines as printed. If `reference` says `DIFFERENT`, say so: measured output stays
   valid, the reference notes in other skills may not.

Facts behind the output (2.3.0, build `1.126.0+bob2.3.0.20261026121409`, checked 2026-11-03 against
`dist/extension.js` and the real database):
- Schema: `bob.db` has migrations 001..013; the last is `013_workspace_editor_sessions`. No new table.
- Server flags are read from `bob.db` `key_value_store.featureFlags.v1`, the cache bob-code loads and saves
  (64 keys here); `state.vscdb` (`bob.featureFlags.cache`, 59 keys) is an older mirror the bundle no longer
  references and which lacks the five flags new in 2.3.0, so it is only a fallback. This gap existed since
  2.2.3 (the bundle already used `featureFlags.v1`); it was found on 2.3.0.
- New in 2.3.0: `web-search-path` (default `/search/tbob`), `bob-plugin-service-url` (empty),
  `plugins-ui-enabled`, `observation-masking-enabled`, `context-focus-query-enabled` (all default false).
- `[pushed, not read by 2.3.0]` marks printed flags no code of the build reads (extension host or webview
  checked): `command-security-model`, `summary-model` (names absent from the bundle), `completion-model`,
  `next-edit-model` (schema and defaults only). Read through `getFlagValue`: `bob-findings-enabled`,
  `context-focus-query-enabled`, `dynamic-context-enabled`, `ibm-support-url`, `issue-repo-url`,
  `max-monthly-budget-allowance`, `observation-masking-enabled`, `review-flow-enabled`; read directly:
  `web-search-path`, `feedback-model`, `feedback-verification-enabled`, `bob-plugin-service-url`.
