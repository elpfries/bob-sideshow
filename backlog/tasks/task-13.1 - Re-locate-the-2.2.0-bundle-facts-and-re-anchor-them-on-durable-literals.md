---
id: TASK-13.1
title: Re-locate the 2.2.0 bundle facts and re-anchor them on durable literals
status: To Do
assignee: []
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 20:30'
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
- [ ] #7 templates/agents/explore-premium.md and the custom-agent frontmatter example in injected-rules.md use modelTier, and the template loads on 2.2.0 without the model-not-supported error
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

## Tranché par l'analyse de TASK-13.4 — 2026-09-28 (PRIME sur la description)

Le plan et les preuves vivent dans TASK-13.4 (private/bundle_diff.py, private/diff/anchors-verdicts.txt,
compare-2.1.0-2.2.0.txt). Ce qui est fixé pour cette tâche :

1. Les ancres disparues sont un artefact de bundling (CommonJS → ESM), pas un changement : ne pas
   chercher un comportement derrière SUBAGENT_PRESETS, MODEL_TIERS, loadWorkspaceRules, etc. Ré-ancrer
   sur du texte de prompt, des clés de settings, des messages, des NOMS DE MÉTHODES (shouldAutoApprove,
   requiresSecurityApproval, isBobHomeWrite survivent) — jamais un nom d'export de module.
2. Verdict IDENTICAL / SAME LOGIC déjà établi pour : portes d'approbation, isBobHomeWrite, objet des
   défauts d'approbation, liste de commandes auto-approuvées, guide sous-agents, préambule des règles,
   prompt /init, règles artefact/inline, frontmatter maxTurns/rawPrompt/denyTools/allowForkContext.
   Ces claims se confirment, ils ne se réécrivent pas.
3. CHANGÉ, à corriger dans les notes : contrat de hooks (7 événements, handler http, PostCompact non
   bloquant, sortie JSON de PreToolUse avec updatedInput/cancel, sources startup/resume/compact) ;
   contrôle de sécurité (commande hors du prompt, repli gpt-oss-20b retiré de la fonction) ;
   execute_command background ; settings autoCondense → autoCompact.
4. CASSÉ, correction obligatoire et non ré-étiquetage : le frontmatter « model: » des agents lève une
   erreur en 2.2.0 (« use "modelTier" instead »), « modelTier: » est validé contre une liste.
   templates/agents/explore-premium.md doit passer à modelTier, et l'exemple de frontmatter dans
   injected-rules.md aussi. Critère ajouté à cette tâche pour cela.
5. Précédence des règles : le changelog 2.2.0 annonce un sous-dossier plugins/ pour skills, modes, rules
   et MCP ; la chaîne « Project Instructions (AGENTS.md) » n'existe plus en 2.2.0. À relocaliser depuis
   le préambule « take precedence over your training defaults » (identique) et ses voisines.
Le mode « anchor » de l'outil est le moyen de preuve attendu pour chaque claim : citer son verdict.
<!-- SECTION:NOTES:END -->
