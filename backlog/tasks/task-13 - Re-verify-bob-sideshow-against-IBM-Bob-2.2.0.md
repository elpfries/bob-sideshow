---
id: TASK-13
title: Re-verify bob-sideshow against IBM Bob 2.2.0
status: Done
assignee: []
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 22:29'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Bob shipped 2.2.0 (`bob-code` 2.2.0, build `1.126.0+bob2.2.0.20260924155054`) and every skill now prints a mismatch warning on start: the reference notes, the version and schema constants, the README and the comparison docs all say 2.1.0. Until the facts are re-read on the new build, the project advertises a provenance it no longer has.

Three kinds of drift are already visible on the installed 2.2.0 build.

The database gained a migration, `011_key_value_store`, and a `key_value_store` table, so `VERIFIED_SCHEMA` is stale in all five copies of `_bobcheck.py`.

The extension bundle went from 14.7 MB to 10.6 MB and is minified more aggressively. The exported identifier names the 2.1.0 notes lean on as anchors — `SUBAGENT_PRESETS`, `MODEL_TIERS`, `DEFAULT_MODEL_TIER`, `parseAgentFile`, `loadWorkspaceRules`, `INIT_BASE_PROMPT`, `getBestCommandMatch`, `findLongestMatchingCommandPattern`, `DEFAULT_APPROVED_COMMANDS`, `assessCommandSecurity`, `featureFlagsSchema`, `isWorkspaceTrusted` — no longer exist as literals, while prompt text, settings keys and error messages survive. Every note anchored on a name has to be re-located from the strings that are left, and re-anchored on something that survives minification. Some facts do hold: the default approved-command list is unchanged, and the hook event set is `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `PreToolUse`, `PostToolUse`, `Stop` — which the current references never spell out.

Nothing crashes: all five scripts run on 2.2.0. So this is verification and honest re-labelling, with repair only where a fact turns out to have moved. The system-prompt section list is the exception that needs new data — the newest stored prompt predates the update, so it can only be compared from a task created under 2.2.0.

AGENTS.md requires every fact to state the build it was read from, and `VERIFIED_*` to be bumped only after re-verification, so the constants move last, not first.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every published version claim reads 2.2.0 — the three reference notes, the script docstrings and headers, README, CHANGELOG and the comparison docs
- [x] #2 `VERIFIED_EXTENSION` is 2.2.0 and `VERIFIED_SCHEMA` is `011_key_value_store`, the five `_bobcheck.py` copies stay byte-identical (one `shasum`), and no skill warns on a 2.2.0 install
- [x] #3 Each of the five scripts is run against the 2.2.0 installation and its output checked, not just its exit code: version, telemetry (including the new table and the measured unit prices), prompt dump on a task created under 2.2.0, approval check, rule locations
- [x] #4 The subagent guidance, model tiers, rule precedence and approval-gate facts are each re-located in the 2.2.0 bundle, and the ones that moved are corrected rather than reworded
- [x] #5 Anchors cited for a fact are ones that survive the new minification — prompt text, settings keys or messages, not minified identifier names
- [x] #6 The documented hook event set and hook payload contract, including the shipped guard template, match 2.2.0
- [x] #7 Any fact that could not be re-verified on 2.2.0 is marked as such instead of being carried over silently
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-09-29 -- Les quatre sous-taches de TASK-13 sont closes. Preuves :
- TASK-13.4 (page docs/) : commit fec4c78, docs/bob-2.1.0-to-2.2.0.md.
- TASK-13.1 (relocalisation des faits 2.2.0, template explore-premium.md, contrat command-guard.mjs) : commits d16cec7 et 770d8e5.
- TASK-13.2 (re-verification base et scripts sur bob-code 2.2.0) : commit df6dace.
- TASK-13.3 (re-etiquetage du projet en 2.2.0, bump VERIFIED_*) : commit 0437172.
Details et preuves d execution dans les notes de chaque sous-tache. TASK-13 elle-meme et la milestone ne sont pas cloturees par cette note.

## Clôture de la tâche parente — 2026-09-29, session d'orchestration (chaîne run-milestone m-1)

Les quatre sous-tâches sont Done et poussées ; chaque critère ci-dessous est prouvé par une exécution ou un contrôle réel refait depuis la session principale sur l'arbre commité (HEAD d2b93d2), pas recopié des rapports d'agents.

Preuves par critère :
- AC #1 (toute provenance publiée dit 2.2.0) : commit 0437172 (TASK-13.3, 20 fichiers) ; grep de « 2.1.0 » sur skills/, docs/, README, CHANGELOG, install.sh, AGENTS.md hors docs/bob-2.1.0-to-2.2.0.md : il ne reste que des comparaisons historiques « 2.1.0 faisait X, 2.2.0 fait Y » dans des notes re-vérifiées, et deux faits explicitement étiquetés non re-vérifiés (voir AC #7).
- AC #2 (VERIFIED_* et un seul hash, aucun avertissement) : VERIFIED_EXTENSION = "2.2.0" et VERIFIED_SCHEMA = "011_key_value_store" dans les cinq copies ; shasum skills/*/scripts/_bobcheck.py → un seul hash e9a89826b6cf29d313fbd83538da7f1acd06ed92 ; les cinq scripts exécutés contre l'installation 2.2.0 (build 1.126.0+bob2.2.0.20260924155054) impriment « verified build » / « reference MATCH » et 0 ligne WARNING au total.
- AC #3 (chaque script exécuté et sa sortie vérifiée) : TASK-13.2 (commit df6dace) a exécuté toutes les vues de bob_telemetry.py sur la base vivante ET sur le snapshot 2.1.0 (totaux 2.1.0 reproduits : 4,7217 Bobcoins, 129 appels), dump_system_prompt.py --list sur deux tâches 2.2.0 (f93b5fd9, e860b444 ; layout default/aquarius confirmé), bob_version.py champ par champ contre product.json, package.json, _migrations, state.vscdb ; TASK-13.1 (d16cec7) a exécuté approval_check.py sur quatre commandes et rule_locations.py. Sorties re-exécutées depuis cette session après le bump : bob_telemetry.py summary → 17 tâches racines, 5 sous-agents, 147 appels, 5,3198 Bobcoins, 25 appels sans tokens affichés n/a ; dump_system_prompt.py --list → tâche e860b444, 33 260 caractères, sections role_definition … available_modes.
- AC #4 (faits sous-agents, tiers, précédence des règles, portes d'approbation relocalisés et corrigés) : TASK-13.1 — approvals.md 12 confirmés / 3 corrigés ; injected-rules.md ~15 confirmés / 7 corrigés / 3 non vérifiés ; command-migration.md 9 confirmés / 2 corrigés ; verdicts de l'outil de diff (TASK-13.4) cités pour chaque claim (IDENTICAL / SAME LOGIC pour les portes shouldAutoApprove, validateToolExecution, _alwaysAllowedTools, isBobHomeWrite ; CHANGED documenté pour hooks, sécurité, agents modelTier, settings de compaction).
- AC #5 (ancres survivant à la minification) : TASK-13.1 — 193 littéraux backtickés extraits des trois notes et vérifiés contre le bundle 2.2.0 ; 7 ancres MISSING (toutes des noms d'export de module effacés par le passage CommonJS → ESM) remplacées par du texte de prompt, des clés, des messages ou des noms de méthodes ; règle consignée dans les notes et dans docs/bob-2.1.0-to-2.2.0.md.
- AC #6 (contrat de hooks et template de garde) : TASK-13.4 (verdict anchor sur « hooks cannot block » / « blocked by hook » : 6 éditions réelles, PostCompact non bloquant, sortie JSON de PreToolUse parsée) et TASK-13.1 (7 événements, handler http, hookSpecificOutput.updatedInput / permissionDecision documentés dans approvals.md et dans le commentaire de contrat de command-guard.mjs) ; node --check command-guard.mjs passe ; contrat stderr + exit 2 confirmé valide sur 2.2.0.
- AC #7 (faits non re-vérifiés marqués) : rule_locations.py garde l'étiquette « bob-code 2.1.0, build 1.126.0+bob2.1.0.20260827055214, Not re-verified on bob-code 2.2.0 » (racines plugins/ et confiance workspace.isTrusted non relues) ; injected-rules.md marque les taux de facturation 2,0 / 0,833 Bobcoins par million comme mesurés sur la base 2.1.0 et non re-mesurables sur 2.2.0 (_meta.spend sans tokens) ; les 3 claims non vérifiées de 13.1 sont étiquetées dans la note.

Contrôles refaits sur HEAD : python3 -m py_compile skills/*/scripts/*.py OK ; node --check OK ; grep « /Users/ | ericfries » sur skills, docs, README, CHANGELOG vide ; git status propre, rien sous private/.

Écart avec la description : elle disait « pas de changelog éditeur » — faux, https://bob.ibm.com/docs/ide/changelog existe (releaseNotesUrl de product.json) et a été confronté au diff dans docs/bob-2.1.0-to-2.2.0.md. Elle prévoyait une reconstruction sans build 2.1.0 — l'utilisateur a choisi de le récupérer, ce qui a rendu le diff concluant.

Suite possible, à décider par l'utilisateur (non ouverte) : re-vérifier rule_locations.py contre les racines .bob/plugins/* de 2.2.0 et le remplacement de trustedFolders.json par workspace.isTrusted, seul script livré encore étiqueté 2.1.0.

## Verification de livraison
Assets : aucun asset binaire produit ; les artefacts de preuve (bundle 2.1.0, snapshot de base, extractions, verdicts) vivent en private/, gitignoré, jamais commités.
Incidents : une coupure d'API (limite de session, HTTP 429) pendant TASK-13.3, reprise du même agent sans travail refait, consignée dans sa télémétrie ; une erreur de requête SQL de la session d'orchestration (comparaison entier / texte sur created_at) détectée et corrigée avant toute conclusion, consignée dans les notes de TASK-13.2 ; un premier essai de chargement du template dans une tâche Bob antérieure au fichier, refait dans une tâche neuve (TASK-13.1 #7).
Capitalisation : docs/bob-2.1.0-to-2.2.0.md (méthode, delta, règle des ancres), CHANGELOG 0.2, notes des quatre sous-tâches avec télémétrie ; calibration.md de la skill run-milestone à remplir à la clôture de la milestone.
Vérificateur indépendant : TASK-13.4 et TASK-13.2 ont chacune eu un vérificateur frais (conforme) ; la tâche parente n'ajoute pas de code, ses preuves sont les exécutions ci-dessus.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Projet adapté à IBM Bob 2.2.0 par quatre sous-tâches closes : delta 2.1.0→2.2.0 établi par un diff de bundles insensible à la minification et publié dans docs/bob-2.1.0-to-2.2.0.md (fec4c78) ; notes de référence relues claim par claim, sept ancres mortes remplacées, template explore-premium.md réparé (modelTier) et chargé réellement dans Bob 2.2.0 (d16cec7, 770d8e5) ; base et scripts vérifiés sur trafic 2.2.0 réel, bob_telemetry.py et bob_version.py corrigés (df6dace) ; projet ré-étiqueté, VERIFIED_* bumpés dans les cinq copies identiques, CHANGELOG (0437172). Vérifié depuis la session principale sur HEAD : un seul hash _bobcheck.py, cinq scripts sans avertissement contre l'installation 2.2.0, py_compile et node --check OK, aucune donnée personnelle.
<!-- SECTION:FINAL_SUMMARY:END -->
