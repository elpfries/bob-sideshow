---
id: TASK-16.2
title: >-
  Run steps 6-8 on a real 2.2.3 task, bump VERIFIED_* to 2.2.3, relabel and
  write CHANGELOG 0.4
status: Done
assignee:
  - '@eric.bonkarma'
created_date: '2026-10-19 08:18'
updated_date: '2026-10-19 09:28'
labels:
  - 'model:secondaire'
dependencies:
  - TASK-16.1
parent_task_id: TASK-16
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Second half of TASK-16. Steps 1-5 of `private/SOURCES.md` "Re-verifying on a new build" are done and recorded (see TASK-16 description and `private/baseline-2.2.1/README.md`): the 2.2.3 `bob-code` bundle has no behavioural change against 2.2.0. What remains is what the bundle read cannot prove: step 6 (`skills/bob-agent-rules/scripts/dump_system_prompt.py --list`) and step 7 (`skills/bob-telemetry/scripts/bob_telemetry.py summary` and `calls`) need a task **actually executed by Bob 2.2.3** in `~/.bob/db/bob.db`; as of 2026-10-19 there is none (every task created since 2.2.1 has 0 messages). Running one small Bob task in the IDE first is part of this work. Then step 8: bump `VERIFIED_EXTENSION` / `VERIFIED_SCHEMA` in the five identical `skills/*/scripts/_bobcheck.py` copies, restate the build in every published file that currently says 2.2.0 (TASK-13.3 lists the places: README, SKILL.md files, script docstrings, `rule_locations.py`, `command-guard.mjs` header, reference notes, comparison docs build lines), keep the earlier build label on any fact not re-checked, and write the dated CHANGELOG `0.4` section. AGENTS.md: the bump is last; copies identical; py_compile and node --check before a PR; tagging `v0.4` and `gh release create` are the maintainer`s step after the section lands, not this task`s.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Steps 6 and 7 were run on a task actually executed by Bob 2.2.3 (prompt sections and guidance blocks listed, telemetry summary and unit prices read); the task id and what was observed are recorded in `private/SOURCES.md`, and any assumption in the reference notes that no longer holds is corrected
- [x] #2 `VERIFIED_EXTENSION` is `2.2.3` and `VERIFIED_SCHEMA` matches the installed database`s last migration in all five `_bobcheck.py` copies; `shasum skills/*/scripts/_bobcheck.py` shows one hash
- [x] #3 No shipped script prints a version or schema mismatch warning on the 2.2.3 installation
- [x] #4 Every published file that states "verified on 2.2.0" or the 2.2.0 build string states 2.2.3 and build `1.126.0+bob2.2.3.20261014125159` where the fact was re-checked, and keeps its earlier build label where it was not
- [x] #5 CHANGELOG has a dated `0.4` section saying what moved in Bob between 2.2.0 and 2.2.3 (bundle unchanged except the development-mode Jenkins path; 2.2.1-2.2.3 changes live in the IDE shell and Remote-SSH) and what changed in bob-sideshow
- [x] #6 `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Transmis par TASK-16.1 (2026-10-19), pour TASK-16.2.

Hachages finaux de bob-code sur 2.2.3 (ceux à citer pour le re-étiquetage) : extension.js 10 622 940 octets, sha1 6062c88fb39bb33a7b1f24f8d2cf08911e8dcac5, sha256 7ca2ec05c52ae0db946c0cf8f3bab1a738981b5c35e846b94556dba263bf5c52 — identique octet pour octet à 2.2.1 (cmp). translations/en.json 83 068 octets, sha256 569191956125f08f39df4aeb6bde89297ad59186f9a6cd13964d1885874939a9 — identique à 2.2.0 et 2.2.1. Schéma base inchangé : 011_key_value_store.

private/diff/2.2.3/ n'existe pas et ce n'est pas un oubli : private/diff/2.2.1/ sert d'extraction pour 2.2.3 aussi, parce que extension.js de 2.2.1 et 2.2.3 sont octet pour octet identiques (même sha1 ci-dessus). Si 16.2 a besoin d'une extraction bundle_diff.py pour 2.2.3, c'est private/diff/2.2.1/ qu'il faut lire.

Verdicts déjà rejoués et confirmés par un vérificateur indépendant dans TASK-16.1 (voir ses notes) : bundle_tools.py --landmarks 46/46 sur 2.2.3 installé et sur les baselines 2.2.0/2.2.1 ; bundle_diff.py anchors 2.2.0->2.2.1 avec les 102 ancres historiques -> 19 MISSING in both / 36 IDENTICAL / 46 SAME top-level string / 1 CHANGED ; avec les 46 ancres durables -> 0 MISSING / 20 IDENTICAL / 25 SAME top-level string / 1 CHANGED. Le seul CHANGED dans les deux cas est "Extension activated" (un chemin de workspace Jenkins, BOB_IDE_EXTERNAL_PKG_USER vs BOB_IDE_EXTERNAL, actif seulement en mode développement). cmp confirme 2.2.1 et 2.2.3 identiques en tout point (extension.js et en.json). Conclusion : aucune note de référence n'a besoin d'être réécrite sur le fond pour 2.2.1/2.2.2/2.2.3 ; seul VERIFIED_* doit changer.

Webview (dist/web/assets, 691 fichiers) : désormais gelée pour 2.2.0, 2.2.1 et 2.2.3 (private/baseline-<version>/app/.../dist/web/assets/ + web-assets.sha256 à côté). Les trois builds ont des hachages identiques fichier par fichier — la webview n'a pas changé depuis au moins 2.2.0, donc rien à re-vérifier côté texte UI avant de bumper VERIFIED_*.

Tâche Bob réelle sur 2.2.3 à utiliser pour les étapes 6-7 de la procédure (dump_system_prompt.py --list, bob_telemetry.py summary/calls) : id 9ad66ac118bfa4983e111fcbe843ead8, titre "liste les fichiers du dépot", 11 messages, 4 appels tarifés, créée 2026-10-19 08:27 UTC.

AC #1 (etapes 6-7 sur 9ad66ac118bfa4983e111fcbe843ead8) - preuve collee dans private/SOURCES.md nouvelle sous-section "Steps 6-7 on 2.2.3 (TASK-16.2)". Etape 6, dump_system_prompt.py --task 9ad66ac1 --list : 12 sections (role_definition 152, investigate_before_answering 358, engineering_discipline 392, tool_use 975, markdown_rules 316, auto_appended_context 645, base_rules 987, available_skills 9163, user_custom_instructions 907, project_rules 3717, environment_info 246, available_modes 2055) et 8 blocs de guidage (create_html_artifact 5554, Mode Switching 2667, office_read 778, office_edit 1009, glob 247, grep 1307, Subagents 1100, create_chart 1235), aucune section task_execution/when_stuck (boreas) ni act_and_iterate/ground_truth/define_done/prove_done (orion) - identique a ce que TASK-13.2 avait consigne sur les taches 2.2.0 f93b5fd9 et e860b444. injected-rules.md ligne du paragraphe "Prompt layout" etendue pour citer la tache 2.2.3 9ad66ac1, aucune reecriture de fond necessaire.
Etape 7, bob_telemetry.py summary : 16 root tasks, 1 subagent, 22 appels LLM, 0.7569 Bobcoins (agent 16 appels 0.6117 Bobcoins 81%, subagent explore-premium 6 appels 0.1451 Bobcoins 19%). calls filtre sur 9ad66ac1 : 4 appels tarifes, tous de classe agent (aucun subagent dans cette tache), rate/M et class affiches n/a pour toutes les lignes de la base (2.2.0 et 2.2.3 confondus) - meme limitation deja documentee, rien de nouveau sur 2.2.3. security --task 9ad66ac1 : 1 commande (backlog instructions overview), 0 flagged, 0 unverifiable. Requete sqlite3 read-only directe sur _meta.spend pour les 4 messages de la tache confirme la forme {cost, contextTokens} uniquement, sans input/output/cacheRead/cacheWrite/reasoningTokens - identique a la forme 2.2.0 deja documentee par bob_telemetry.py et bob-telemetry/SKILL.md, qui ont ete etendus (pas reecrits) pour citer la date et la tache 2.2.3. Aucune hypothese des notes de reference ne s'est revelee fausse sur 2.2.3 ; tout tenait.

AC #2 : shasum skills/*/scripts/_bobcheck.py -> un seul hachage sur les cinq copies, d40c5ea921c22ef32001b21b8ddd179f3530cf20. VERIFIED_EXTENSION = "2.2.3" dans les cinq copies ; VERIFIED_SCHEMA reste "011_key_value_store" (bob_version.py confirme sur l'installation reelle : schema 011_key_value_store, 11 migrations, aucune migration plus recente). Le texte d'indice "matcher logic comes from the 2.2.3 bundle" (utilise par approval_check.py) a ete mis a jour dans les cinq copies identiquement, en meme temps que VERIFIED_EXTENSION, pour rester une seule et meme chaine partout.

AC #3 : les cinq scripts livres executes contre l'installation reelle (bob-code 2.2.3, build 1.126.0+bob2.2.3.20261014125159, schema 011_key_value_store) apres le bump n'impriment plus aucun WARNING :
- bob_version.py : "reference    MATCH - verified on bob-code 2.2.3 / 011_key_value_store"
- dump_system_prompt.py --task 9ad66ac1 --list : "[bob-sideshow] bob-code 2.2.3, schema 011_key_value_store - verified build"
- rule_locations.py : "[bob-sideshow] bob-code 2.2.3 - verified build"
- approval_check.py "git status" : "[bob-sideshow] bob-code 2.2.3 - verified build"
- bob_telemetry.py summary : "[bob-sideshow] bob-code 2.2.3, schema 011_key_value_store - verified build"

AC #4 : grep -rn "verified on|vérifié sur|20260924155054|20261014125159" skills README.md docs (avant/apres colles dans private/SOURCES.md et dans ce rapport). Fichiers relabellises a bob-code 2.2.3, build 1.126.0+bob2.2.3.20261014125159, chaque fois avec une phrase citant TASK-16.2 et l'identite de bundle (private/SOURCES.md "Verdicts 2.2.0 -> 2.2.1 -> 2.2.3") comme preuve plutot qu'une relecture de la fonction : README.md (paragraphe de provenance), skills/bob-override-rules/scripts/rule_locations.py (docstring), skills/bob-override-rules/templates/hooks/command-guard.mjs (en-tete), skills/bob-security-model/scripts/approval_check.py (docstring), skills/bob-security-model/reference/approvals.md (titre + paragraphe d'intro), skills/bob-agent-rules/reference/command-migration.md (titre + paragraphe d'intro), skills/bob-agent-rules/reference/injected-rules.md (titre + paragraphe d'intro + confirmation de la mise en page du prompt sur la tache 9ad66ac1), skills/bob-telemetry/scripts/bob_telemetry.py (docstring, confirmation trafic 2.2.3), skills/bob-telemetry/SKILL.md (en-tete "When explaining", confirmation trafic 2.2.3), skills/bob-version/scripts/bob_version.py (docstring, commentaire FLAG_KEYS d'accompagnement, et les deux etiquettes imprimees "[pushed, not read by 2.2.3]" remplacant "2.2.0"), docs/bob-in-perspective.md (ligne Builds + en-tete de tableau), docs/cursor-vs-bob.md et docs/claude-code-vs-bob.md (phrase "Bob has seven events on 2.2.3"). Etiquettes gardees a 2.2.0 avec leur raison : skills/bob-agent-rules/reference/injected-rules.md ligne de facturation (taux Bobcoins/M tokens, jamais re-mesurable depuis que 2.2.0 a reduit _meta.spend, confirme encore reduit sur 2.2.3) ; toutes les citations "Changed on bob-code 2.2.0" / "Re-anchored on 2.2.0" / "confirmed unchanged on bob-code 2.2.0" dans approvals.md, command-migration.md et injected-rules.md (citations historiques de la preuve bundle-diff originale 2.1.0->2.2.0, pas une etiquette de verification du build courant) ; docs/codex-vs-bob.md ligne 83 "routed since bob-code 2.2.0" (historique, phrase "new in 2.2.0"-style explicitement exemptee) ; docs/bob-2.1.0-to-2.2.0.md (page historique non touchee sur le fond, un paragraphe date 2026-10-19 ajoute en fin de section "Re-checking on the next build" renvoyant au CHANGELOG) ; CHANGELOG.md section 0.3 (historique, inchangee) ; docs/kimi-code-vs-bob.md (ne concerne pas Bob).

AC #5 : CHANGELOG.md, nouvelle section "## 0.4 - 2026-10-19" au-dessus de 0.3, meme ton. Texte colle dans le rapport final.

AC #6 : python3 -m py_compile skills/*/scripts/*.py -> code retour 0, aucune sortie. node --check skills/bob-override-rules/templates/hooks/command-guard.mjs -> code retour 0, aucune sortie. git status --short ne montre aucun fichier sous private/ parmi les modifications (verifie explicitement par grep).

## Verification de livraison
Assets : aucun asset binaire produit ou modifie. Controles d'integrite executes sur les fichiers modifies : python3 -m py_compile skills/*/scripts/*.py (code retour 0) ; node --check skills/bob-override-rules/templates/hooks/command-guard.mjs (code retour 0) ; shasum skills/*/scripts/_bobcheck.py -> un seul hachage sur les cinq copies (d40c5ea921c22ef32001b21b8ddd179f3530cf20) ; les cinq scripts livres (bob_version.py, dump_system_prompt.py --list, rule_locations.py, approval_check.py, bob_telemetry.py summary) executes contre l'installation reelle bob-code 2.2.3 apres le bump, aucun n'imprime de WARNING ; grep -rn "/Users/|ericfries" sur skills docs README.md CHANGELOG.md vide (le seul hit est dans private/SOURCES.md, gitignore, et deja redige sans chemin personnel) ; git status --short ne montre aucun fichier sous private/ parmi les modifications.
Incidents : aucun -- pas d'interruption ni de relance d'etape, pas de bug d'outillage trouve (aucune modification de logique de script, seulement des chaines de version et commentaires), pas de contournement, pas d'intervention manuelle sur un resultat de script, pas de tache rouverte apres Done.
Capitalisation : versee dans private/SOURCES.md (nouvelle sous-section "Steps 6-7 on 2.2.3 (TASK-16.2)" avec les sorties reelles des etapes 6 et 7, la requete sqlite3 sur _meta.spend, et le verdict que rien n'a du etre corrige) et dans les notes d'implementation de cette tache (liste nommee des fichiers relabellises par AC, avec le detail des etiquettes 2.2.0 gardees et pourquoi). Point non evident pour la suite : le hint partage des cinq _bobcheck.py ("matcher logic comes from the 2.2.3 bundle") a ete bumpe en meme temps que VERIFIED_EXTENSION pour rester une chaine identique entre les cinq copies -- a refaire au prochain build meme s'il n'est pas explicitement nomme dans la procedure private/SOURCES.md.
Verificateur independant : non requis (Incidents = aucun).

AC #1 : private/SOURCES.md, sous-section "Steps 6-7 on 2.2.3 (TASK-16.2)" colle les sorties reelles de `python3 skills/bob-agent-rules/scripts/dump_system_prompt.py --task 9ad66ac1 --list` (12 sections, 8 blocs, pas de task_execution/when_stuck/orion) et de `python3 skills/bob-telemetry/scripts/bob_telemetry.py summary`/`calls` sur la tache 9ad66ac118bfa4983e111fcbe843ead8 (4 appels tarifes, _meta.spend = {cost, contextTokens} confirme par une requete sqlite3 read-only directe), et conclut qu'aucune hypothese de injected-rules.md / bob_telemetry.py / bob-telemetry/SKILL.md ne s'est revelee fausse -- ces notes ont ete etendues pour citer la tache 2.2.3, pas reecrites.
AC #2 : sortie de `shasum skills/*/scripts/_bobcheck.py` -> un seul hachage `d40c5ea921c22ef32001b21b8ddd179f3530cf20` sur les cinq copies ; `grep -n VERIFIED_EXTENSION skills/*/scripts/_bobcheck.py` montre `"2.2.3"` dans les cinq ; VERIFIED_SCHEMA inchange ("011_key_value_store"), confirme par la ligne `bob.db schema 011_key_value_store (11 migrations)` de la sortie reelle de bob_version.py sur l'installation.
AC #3 : sorties collees dans cette tache (section ci-dessus "les cinq scripts livres... apres le bump") : bob_version.py "reference MATCH", dump_system_prompt.py "[bob-sideshow] bob-code 2.2.3, schema 011_key_value_store - verified build", rule_locations.py et approval_check.py et bob_telemetry.py idem "verified build" -- aucun WARNING sur aucun des cinq apres le bump.
AC #4 : grep avant/apres colle dans les notes d'implementation precedentes (liste nommee des 13 fichiers relabellises et des etiquettes 2.2.0 gardees avec leur raison) ; verifie par une relecture de `grep -rn "verified on|vérifié sur|20260924155054|20261014125159" skills README.md docs` apres les edits (sortie collee dans les notes), qui montre les citations restantes et classe chacune (historique vs non re-verifiee).
AC #5 : le texte de la section CHANGELOG.md "## 0.4 -- 2026-10-19" est dans le fichier commite ; sa presence et son emplacement au-dessus de "## 0.3" sont verifiables par `head -40 CHANGELOG.md`.
AC #6 : `python3 -m py_compile skills/*/scripts/*.py` -> code retour 0, aucune sortie ; `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` -> code retour 0, aucune sortie (les deux commandes executees et leur code de retour observe dans cette session).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Steps 6-7 run on real 2.2.3 task 9ad66ac1 (prompt: 12 sections/8 blocks, same as 2.2.0 e860b444/f93b5fd9; telemetry: 4 calls, _meta.spend still {cost,contextTokens} only) and recorded in private/SOURCES.md; no reference assumption was wrong. VERIFIED_EXTENSION bumped to 2.2.3 (VERIFIED_SCHEMA stays 011_key_value_store) in all five _bobcheck.py copies, one shasum d40c5ea921c22ef32001b21b8ddd179f3530cf20. All five delivered scripts print a clean verified-build/MATCH line on the real 2.2.3 install, no WARNING. 13 published files relabelled to bob-code 2.2.3 / build 1.126.0+bob2.2.3.20261014125159 by bundle identity (TASK-16.1's proof), earlier 2.2.0 labels kept where historical or not re-checked (injected-rules.md billing rate, codex-vs-bob.md 'since 2.2.0', docs/bob-2.1.0-to-2.2.0.md itself). CHANGELOG 0.4 (2026-10-19) added above 0.3. py_compile and node --check both exit 0; git status confirms nothing under private/ changed.
<!-- SECTION:FINAL_SUMMARY:END -->
