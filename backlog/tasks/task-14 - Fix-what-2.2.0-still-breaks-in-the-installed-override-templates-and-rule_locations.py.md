---
id: TASK-14
title: >-
  Fix what 2.2.0 still breaks in the installed override templates and
  rule_locations.py
status: To Do
assignee: []
created_date: '2026-09-28 22:40'
updated_date: '2026-09-28 22:41'
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
- [ ] #1 No template under skills/bob-override-rules/templates/ tells the user to write a `model:` key in an agent file; every rule template and templates/README.md is read against docs/bob-2.1.0-to-2.2.0.md and corrected or confirmed
- [ ] #2 rule_locations.py lists `.bob/plugins/<name>/rules/` and `rules-<mode>/` roots, workspace then global, in the precedence order 2.2.0 uses, proven by running it on a throwaway folder that contains such a root
- [ ] #3 rule_locations.py no longer relies on trustedFolders.json for trust, and says what it can and cannot tell about trust on 2.2.0
- [ ] #4 The script docstring states bob-code 2.2.0 as the verified build, and the script runs against the real installation with no warning
- [ ] #5 `python3 -m py_compile skills/*/scripts/*.py` passes and `shasum skills/*/scripts/_bobcheck.py` still shows one hash
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Pointeurs — 2026-09-29, session d'orchestration (ouverte à la clôture de m-1, sur accord de l'utilisateur)

- Le fait « model: → modelTier: » et sa preuve : docs/bob-2.1.0-to-2.2.0.md (agents personnalisés), notes de TASK-13.1 (critère #7 prouvé par chargement réel dans une tâche Bob 2.2.0), et le parseur lu dans le bundle 2.2.0 : regex de frontmatter « ^---\r?\n([\s\S]*?)\r?\n--- », erreur « "model" is not supported in <fichier>, use "modelTier" instead », valeurs valides fast, premium, ultra, explorer.
- Les racines de règles 2.2.0 et leur ordre : section project_rules de skills/bob-agent-rules/reference/injected-rules.md (mise à jour par 13.1) — racine .bob puis .bob/plugins/<nom>/ par ordre alphabétique, rules/ et rules-<mode>/ dans chaque racine, workspace avant global, rendu en balises workspace_rules_<mode> / workspace_rules / agents_md / global_rules_<mode> / global_rules.
- Confiance : 2.2.0 prend workspace.isTrusted de l'IDE ; trustedFolders.json n'est plus consulté (docs/bob-2.1.0-to-2.2.0.md, notes de 13.1). Le script ne peut pas lire l'état de confiance de l'IDE hors ligne : le dire plutôt que le deviner.
- Les deux bundles pour vérifier un littéral : 2.2.0 installé sous /Applications/IBM Bob.app/Contents/Resources/app/extensions/bob-code/dist/extension.js ; 2.1.0 et l'outil de diff en private/ (gitignoré) — private/bundle_diff.py anchor, private/bundle_tools.py --grep.
- Le bug de cette milestone à ne pas répéter : ne pas laisser de __pycache__ dans skills/ avant install.sh (cp -R les copie).
<!-- SECTION:NOTES:END -->
