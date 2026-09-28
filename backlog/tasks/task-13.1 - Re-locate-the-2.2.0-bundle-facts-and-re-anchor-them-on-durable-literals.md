---
id: TASK-13.1
title: Re-locate the 2.2.0 bundle facts and re-anchor them on durable literals
status: To Do
assignee: []
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 20:01'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies:
  - TASK-13.4
parent_task_id: TASK-13
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2.2.0 `extension.js` is 10.6 MB against 14.7 MB on 2.1.0 and keeps far fewer names: `SUBAGENT_PRESETS`, `MODEL_TIERS`, `DEFAULT_MODEL_TIER`, `parseAgentFile`, `loadWorkspaceRules`, `Project Instructions (AGENTS.md)`, `INIT_BASE_PROMPT`, `getBestCommandMatch`, `findLongestMatchingCommandPattern`, `DEFAULT_APPROVED_COMMANDS`, `assessCommandSecurity`, `featureFlagsSchema` and `isWorkspaceTrusted` are gone as literals, while prompt text, settings keys and error messages survive.

So every fact the references took from the bundle has to be found again through the strings that are left, and then cited through an anchor that will survive the next rebuild. Two are already located: the default approved-command list is unchanged (`cat git diff git log git rev-parse git show git status grep head tail ls sort wc which du df`) and the hook event set is `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `PreToolUse`, `PostToolUse`, `Stop`.

What matters is the claims, not the identifiers: the auto-approval gate order and the token matcher, the security check and its heuristics, the rule loader precedence and its preamble, the subagent presets with their tools, turns and model aliases, the model tiers and their production mapping, the custom-agent frontmatter fields, and the `/init` behaviour towards AGENTS.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each claim in `skills/bob-security-model/reference/approvals.md` is either confirmed on the 2.2.0 bundle, corrected, or marked unverified
- [ ] #2 Each claim in `skills/bob-agent-rules/reference/injected-rules.md` about subagents, tiers, rule precedence and custom agents is confirmed, corrected, or marked unverified
- [ ] #3 `skills/bob-agent-rules/reference/command-migration.md` still describes what 2.2.0 does to `commands/*.md`
- [ ] #4 The hook payload contract and event set, and the shipped `command-guard.mjs` matcher and exit-code behaviour, are confirmed against 2.2.0
- [ ] #5 Every anchor cited in a reference note is a literal that exists in the 2.2.0 bundle, and none is a minified identifier name
- [ ] #6 The token matcher that `approval_check.py` reimplements is compared against the 2.2.0 code, and the script is corrected if it diverges
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Ce que l'arbitrage de l'utilisateur change pour cette tâche — 2026-09-28 (PRIME sur la description)

Le build 2.1.0 est récupéré (décision consignée dans TASK-13.4), donc la méthode de cette tâche
change : les faits ne sont pas seulement relocalisés dans 2.2.0, ils sont diffés contre le bundle
2.1.0 d'origine. Un fait qui a l'air d'avoir bougé peut alors être tranché au lieu de rester
indéterminé. Attendre le delta de TASK-13.4 avant de commencer : il dit lesquelles des ancres ont
réellement changé de comportement et lesquelles n'ont perdu que leur nom.

Le critère #5 reste entier quoi qu'il arrive : les ancres citées dans les notes de référence
doivent exister dans le bundle 2.2.0, et un nom minifié n'est pas une ancre.
<!-- SECTION:NOTES:END -->
