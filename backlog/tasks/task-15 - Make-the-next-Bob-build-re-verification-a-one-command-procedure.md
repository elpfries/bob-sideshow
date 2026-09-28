---
id: TASK-15
title: Make the next Bob build re-verification a one-command procedure
status: To Do
assignee: []
created_date: '2026-09-28 22:40'
updated_date: '2026-09-28 22:47'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
m-1 produced a method and a tool that make a build-to-build comparison of Bob conclusive despite minification, and `docs/bob-2.1.0-to-2.2.0.md` ends with a section on re-checking the next build. But the written re-verification procedure the project actually follows still dates from 2.1.0: its anchor list contains twelve names that the CommonJS-to-ESM bundling change erased, its first step is a landmark check that would now report them missing and prove nothing, and it does not mention the diff tool at all. The next Bob release would restart from the same confusion m-1 began with.

This task turns what m-1 learned into the procedure for the next build: anchors that survive minification (prompt text, settings keys, messages, class-method names and object keys — never a module export name), the diff tool as the first command run on a new build, the 2.2.0 bundle kept as a baseline next to the 2.1.0 one, and the order of steps ending, as AGENTS.md requires, with the `VERIFIED_*` bump. The procedure and the tooling live outside the published tree; nothing in `skills/` changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The re-verification procedure names, in order, the commands to run on a new build, starting with the anchor-verdict run of the diff tool and ending with the VERIFIED_* bump
- [ ] #2 The landmark list used by the procedure contains no module export name; every entry is proven present in the 2.2.0 bundle by running the check
- [ ] #3 The 2.2.0 bundle and its token extraction are kept as a baseline alongside 2.1.0, with build string and hashes recorded
- [ ] #4 The diff tool has a usage note good enough for someone who has not read m-1, and a dry run of the full procedure against the installed 2.2.0 build (as if it were new) reports every anchor as present
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Pointeurs — 2026-09-29, session d'orchestration (ouverte à la clôture de m-1, sur accord de l'utilisateur)

Tout vit en private/ (gitignoré, jamais commité) :
- private/SOURCES.md — la méthode et la procédure « Re-verifying on a new build » écrites pour 2.1.0 ; c'est le document à réécrire.
- private/bundle_tools.py — --landmarks et --grep ; sa liste LANDMARKS contient les douze noms d'export morts (SUBAGENT_PRESETS, MODEL_TIERS, DEFAULT_MODEL_TIER, parseAgentFile, loadWorkspaceRules, INIT_BASE_PROMPT, getBestCommandMatch, findLongestMatchingCommandPattern, DEFAULT_APPROVED_COMMANDS, assessCommandSecurity, featureFlagsSchema, isWorkspaceTrusted, plus Project Instructions (AGENTS.md)) à remplacer.
- private/bundle_diff.py — extract / compare / anchor / anchors ; private/diff/anchors.txt (102 ancres) et anchors-verdicts.txt ; private/diff/2.1.0 et 2.2.0 (extractions) ; private/diff/compare-2.1.0-2.2.0.txt.
- private/baseline-2.1.0/ — zip 2.1.0 (sha256 34d299ab…), arbre extrait, snapshot de la base (sha256 bee901ee…), changelog-2.2.0.txt. Créer private/baseline-2.2.0/ sur le même modèle (bundle 2.2.0, product.json, package.json, extraction) — le bundle installé sera écrasé par la prochaine mise à jour en place.
- private/benchmark-harness.md — notes m-0 ; ses ancres (shouldAutoApprove, validateToolExecution, handleUiReply, task_pending_approvals, _alwaysAllowedTools, hooks cannot block, Extension activated) sont vérifiées présentes en 2.2.0 par 13.4 ; ne pas les toucher, seulement les citer comme durables.
- La règle des ancres durables et la section « Re-checking on the next build » : docs/bob-2.1.0-to-2.2.0.md.
- Limites connues de l'outil, à documenter plutôt qu'à corriger si le temps manque : la règle d'interop rend invisible un vrai changement qui aurait exactement la forme « . nom » retiré ; l'étiquetage d'origine reste heuristique.

Pointeurs transmis par TASK-14 (2026-09-29) pour la procedure de re-verification.

Ancres relues et leur verdict, telles qu utilisees dans TASK-14 (aucune n est un nom d export) :
- use "modelTier" instead (anchor MISSING en 2.1.0, CHANGED en 2.2.0 sur modelTier) : sert a justifier la correction model: -> modelTier: dans templates/rules/premium-subagents.md, deja appliquee. A garder dans la liste des ancres durables.
- plugins/*/ (anchor MISSING en 2.1.0) : sert a justifier l ajout des racines .bob/plugins/<nom>/ dans rule_locations.py.
- trustedFolders.json (anchor MISSING en 2.2.0) : sert a justifier le retrait de ce fichier comme source de verite pour la confiance dans rule_locations.py.
- take precedence over your training defaults (SAME string, 468 caracteres) : preambule des regles inchange, non retouche.

Point d ambiguite resolu pendant TASK-14, a verser dans la procedure : la phrase de injected-rules.md project_rules ("each root above also includes every directory ... i.e. root 1/2 really read .bob/ then .bob/plugins/<name>/ alphabetically ... Precedence between the five kinds above is unchanged; precedence between roots is .bob/ first, plugins alphabetically after") peut se lire de deux facons. TASK-14 a retenu la lecture "kind-first, root-second" : rules-<mode> (base puis plugins alphabetique) prime entierement sur rules (base puis plugins alphabetique), qui prime sur AGENTS.md, plutot que "tous les plugins groupes apres les deux racines de base" (c etait la formulation initiale, plus grossiere, dans la description de TASK-14 elle-meme, corrigee ici). Verifie par execution sur un dossier jetable (.bob/rules/a.md, .bob/rules-agent/b.md, .bob/plugins/zeta/rules/c.md, .bob/plugins/alpha/rules/d.md) : ordre obtenu b, a, d, c - alpha avant zeta. Note que ce jeu de test ne distingue pas les deux lectures possibles (aucun plugin n a de rules-<mode> dans le test) ; si TASK-15 relit ce point sur un nouveau build, un test avec un plugin possedant a la fois rules-<mode>/ et rules/ trancherait sans ambiguite entre les deux lectures.

Fichier modifie utile a la procedure : skills/bob-override-rules/scripts/rule_locations.py (nouvelle fonction rule_dirs()) peut servir de reference d implementation si private/bundle_tools.py doit un jour exposer la meme logique de precedence.

TASK-14 n a pas touche private/ ni rien commite hors de skills/bob-override-rules/.
<!-- SECTION:NOTES:END -->
