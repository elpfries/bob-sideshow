---
id: TASK-14
title: >-
  Fix what 2.2.0 still breaks in the installed override templates and
  rule_locations.py
status: Done
assignee:
  - '@eric.bonkarma'
created_date: '2026-09-28 22:40'
updated_date: '2026-09-28 22:49'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies: []
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two shipped artefacts still tell users, or Bob, something that is false on bob-code 2.2.0 (build `1.126.0+bob2.2.0.20260924155054`). Both were outside the scope of the four m-1 subtasks and were found when the milestone was checked cold.

`skills/bob-override-rules/templates/rules/premium-subagents.md` instructs the user to write `model: premium` in their agent file (line 8). On 2.2.0 the agent-file parser throws `"model" is not supported in <file>, use "modelTier" instead` — the very defect TASK-13.1 fixed in `templates/agents/explore-premium.md`, left behind in the rule that points at it. The other rule templates and `templates/README.md` have not been read against the delta either.

`skills/bob-override-rules/scripts/rule_locations.py` is the only shipped script still labelled 2.1.0, honestly: it does not know the `.bob/plugins/<name>/` roots that 2.2.0 reads after `.bob/` (`rules/` and `rules-<mode>/` in each, plugins alphabetically after the base root, workspace then global), so the precedence line it prints is incomplete, and it checks trust through `trustedFolders.json`, a store 2.2.0 no longer consults (it takes the IDE `workspace.isTrusted`). The facts are established in `docs/bob-2.1.0-to-2.2.0.md` and in the `project_rules` section of `skills/bob-agent-rules/reference/injected-rules.md`, both re-verified on 2.2.0.

The script stays Python 3.8+, standard library, read-only, offline; `_bobcheck.py` is not touched.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No template under skills/bob-override-rules/templates/ tells the user to write a `model:` key in an agent file; every rule template and templates/README.md is read against docs/bob-2.1.0-to-2.2.0.md and corrected or confirmed
- [x] #2 rule_locations.py lists `.bob/plugins/<name>/rules/` and `rules-<mode>/` roots, workspace then global, in the precedence order 2.2.0 uses, proven by running it on a throwaway folder that contains such a root
- [x] #3 rule_locations.py no longer relies on trustedFolders.json for trust, and says what it can and cannot tell about trust on 2.2.0
- [x] #4 The script docstring states bob-code 2.2.0 as the verified build, and the script runs against the real installation with no warning
- [x] #5 `python3 -m py_compile skills/*/scripts/*.py` passes and `shasum skills/*/scripts/_bobcheck.py` still shows one hash
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Pointeurs — 2026-09-29, session d'orchestration (ouverte à la clôture de m-1, sur accord de l'utilisateur)

- Le fait « model: → modelTier: » et sa preuve : docs/bob-2.1.0-to-2.2.0.md (agents personnalisés), notes de TASK-13.1 (critère #7 prouvé par chargement réel dans une tâche Bob 2.2.0), et le parseur lu dans le bundle 2.2.0 : regex de frontmatter « ^---\r?\n([\s\S]*?)\r?\n--- », erreur « "model" is not supported in <fichier>, use "modelTier" instead », valeurs valides fast, premium, ultra, explorer.
- Les racines de règles 2.2.0 et leur ordre : section project_rules de skills/bob-agent-rules/reference/injected-rules.md (mise à jour par 13.1) — racine .bob puis .bob/plugins/<nom>/ par ordre alphabétique, rules/ et rules-<mode>/ dans chaque racine, workspace avant global, rendu en balises workspace_rules_<mode> / workspace_rules / agents_md / global_rules_<mode> / global_rules.
- Confiance : 2.2.0 prend workspace.isTrusted de l'IDE ; trustedFolders.json n'est plus consulté (docs/bob-2.1.0-to-2.2.0.md, notes de 13.1). Le script ne peut pas lire l'état de confiance de l'IDE hors ligne : le dire plutôt que le deviner.
- Les deux bundles pour vérifier un littéral : 2.2.0 installé sous /Applications/IBM Bob.app/Contents/Resources/app/extensions/bob-code/dist/extension.js ; 2.1.0 et l'outil de diff en private/ (gitignoré) — private/bundle_diff.py anchor, private/bundle_tools.py --grep.
- Le bug de cette milestone à ne pas répéter : ne pas laisser de __pycache__ dans skills/ avant install.sh (cp -R les copie).

Verification de session - TASK-14.

Templates lus et verdicts (contre docs/bob-2.1.0-to-2.2.0.md section 3 et injected-rules.md) :
- templates/rules/premium-subagents.md : ligne 8 disait model: premium, corrige en modelTier: premium (grep model: est maintenant vide sous templates/).
- templates/agents/explore-premium.md : deja modelTier: premium depuis TASK-13.1, confirme, aucun changement.
- templates/README.md : aucune mention de model:, confirme.
- templates/rules/command-safety.md, project-workflow-first.md, protect-agents-md.md, report-as-artifact.md, subagents-on-request.md, task-vocabulary.md : aucune mention de model:, confirmes, aucun changement.
- templates/hooks/command-guard.mjs, settings.hooks.json, templates/skills/tombstone.sh : aucune mention de model:, confirmes.
- SKILL.md : etape 2 ne mentionnait pas les racines plugins/, corrigee pour lister .bob/plugins/<nom>/rules-<mode>/ et rules/ (alphabetique) aux deux niveaux workspace et global, dans l ordre derive de injected-rules.md.

rule_locations.py reecrit : ajout de plugin_names() et rule_dirs() (base rules-<mode> puis chaque plugin rules-<mode> alphabetique, puis base rules puis chaque plugin rules alphabetique) ; ligne precedence imprimee en consequence ; section trust remplacee : ne consulte plus trustedFolders.json comme source de verite, dit explicitement qu elle ne peut pas lire workspace.isTrusted hors ligne, et n affiche trustedFolders.json que si le fichier existe, etiquete explicitement comme residu 2.1.0. Docstring cite bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054.

Sortie sur dossier jetable (workspace = scratchpad/task14-throwaway avec .bob/rules/a.md, .bob/rules-agent/b.md, .bob/plugins/zeta/rules/c.md, .bob/plugins/alpha/rules/d.md, AGENTS.md) :
precedence  .bob/rules-<mode>/ > .bob/plugins/<name>/rules-<mode>/ (alpha) > .bob/rules/ > .bob/plugins/<name>/rules/ (alpha) > AGENTS.md > ~/.bob/rules-<mode>/ > ~/.bob/plugins/<name>/rules-<mode>/ (alpha) > ~/.bob/rules/ > ~/.bob/plugins/<name>/rules/ (alpha)
workspace   .../task14-throwaway
  .bob/rules-agent/b.md  2 B
  .bob/rules/a.md  2 B
  .bob/plugins/alpha/rules/d.md  2 B
  .bob/plugins/zeta/rules/c.md  2 B
  AGENTS.md  9 B
alpha precede bien zeta, confirme.

Sortie sur l installation reelle (avant push des skills, cwd = bob-sideshow) : premiere ligne [bob-sideshow] bob-code 2.2.0 - verified build, sans WARNING. Section trust : bob-code 2.2.0 takes workspace.isTrusted from the IDE at runtime; this script cannot read that state offline and does not know whether this folder is trusted. Aucune mention de trustedFolders.json (le fichier n existe pas sur cette machine, donc rien n est affiche a ce sujet, comportement attendu).

Apres ./install.sh (ecriture sous ~/.bob/skills, seule ecriture autorisee) : python3 ~/.bob/skills/bob-override-rules/scripts/rule_locations.py depuis ~ donne en premiere ligne [bob-sideshow] bob-code 2.2.0 - verified build.

Verifications outillage : python3 -m py_compile skills/*/scripts/*.py OK ; shasum skills/*/scripts/_bobcheck.py -> un seul hash e9a89826b6cf29d313fbd83538da7f1acd06ed92 sur les cinq copies (fichier non touche) ; node --check templates/hooks/command-guard.mjs OK ; grep -rn /Users/ ericfries skills vide ; git status ne montre que les quatre fichiers attendus, rien sous private/ ; __pycache__ supprime sous skills/ avant le premier commit.

Ce qui n a pas ete fait : pas de changement au perimetre de scan des agents/ et skills/ de rule_locations.py (les plugins/*/agents et plugins/*/skills ne sont pas dans les criteres d acceptation de TASK-14, qui portent seulement sur les racines de regles et la confiance) ; pas de note de reference, pas de README racine, pas de CHANGELOG ecrits (perimetre exclu par la tache).

Télémétrie (relevé reconstruit depuis les commits, script backfill.py, mesuré depuis la session d'orchestration après le commit) : 33 appels API, ≈ 1,97 USD ≈ 1,70 EUR équivalent API (taux de repli figé du 2026-09-03 : 1 USD = 0,8610 EUR, BCE injoignable ; tarifs de liste, pas une facture). Fenêtre entre le commit précédent (c149f8d) et le commit de la tâche (ea28ffd), sous-agent compris. Fenêtre 7 min, temps effectif ≈ 4 min. Cohérent avec la durée rapportée par l'agent (6,2 min, 51 appels d'outils). Chaîne conduite sur Claude Code / Fable 5.1, sous-agent sur Sonnet (label model:secondaire).

Vérification complémentaire de la session d'orchestration sur l'ordre de précédence choisi par l'agent (« sorte d'abord, racines dedans ») : la fonction de rendu du bundle 2.2.0 construit cinq groupes dans l'ordre workspace_rules_<mode>, workspace_rules, agents_md, global_rules_<mode>, global_rules, chacun recevant la liste de fichiers déjà fusionnée (racine .bob puis plugins). La ligne « precedence » imprimée par rule_locations.py est donc conforme au bundle, pas seulement à la note.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
model: -> modelTier: corrige dans templates/rules/premium-subagents.md (seul template fautif, tous les autres confirmes sans mention de model:). rule_locations.py reecrit pour bob-code 2.2.0 : racines .bob/plugins/<nom>/rules-<mode>/ et rules/ ajoutees (workspace puis global, plugins alphabetique, precedence kind-first puis root-second), section trust remplacee (ne consulte plus trustedFolders.json comme source de verite, dit explicitement ce qu elle ne peut pas savoir sur workspace.isTrusted), docstring citant bob-code 2.2.0. SKILL.md corrige au meme endroit. Verifie par execution : dossier jetable (alpha avant zeta confirme), installation reelle (verified build, sans WARNING), et apres ./install.sh depuis ~/.bob/skills (verified build). py_compile, shasum _bobcheck.py (un seul hash), node --check du hook, grep de donnees personnelles et __pycache__ tous verifies propres avant commit. Les cinq criteres d acceptation sont coches sur preuve d execution.
<!-- SECTION:FINAL_SUMMARY:END -->
