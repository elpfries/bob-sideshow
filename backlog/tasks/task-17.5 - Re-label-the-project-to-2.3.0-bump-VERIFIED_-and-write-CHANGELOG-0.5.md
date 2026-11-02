---
id: TASK-17.5
title: 'Re-label the project to 2.3.0, bump VERIFIED_* and write CHANGELOG 0.5'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-02 22:51'
updated_date: '2026-11-02 23:40'
labels:
  - 'model:secondaire'
milestone: m-2
dependencies:
  - TASK-17.2
  - TASK-17.3
  - TASK-17.4
parent_task_id: TASK-17
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Last step, only once TASK-17.1 to 17.4 have re-read the facts: bump VERIFIED_EXTENSION to 2.3.0 and VERIFIED_SCHEMA to 013_workspace_editor_sessions in the five identical _bobcheck.py copies, restate the build in every published file where the fact was re-checked (keep earlier labels where it was not), update README and the comparison docs build lines, and write a dated CHANGELOG 0.5 section on the model of 0.3. Model: TASK-13.3 and TASK-16.2. The release itself (tag v0.5, gh release) follows the AGENTS.md rule and is done by the orchestrating session after this task.

Shared facts (session of 2026-11-02): Bob installed = 2.3.0, build 1.126.0+bob2.3.0.20261026121409, extension.js sha1 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (10 911 633 bytes), product.json commit b48bf62595b330a56b628a82441207f506fbc6a4, schema 013_workspace_editor_sessions (migrations 012_task_editor_sessions and 013_workspace_editor_sessions new). The outgoing baseline is private/baseline-2.2.3/ (complete, webview included); the new one is frozen in private/baseline-2.3.0/ (four files + web/assets with web-assets.sha256, README still to write) and extracted in private/diff/2.3.0/; the 2.2.3 extraction is private/diff/2.2.1/ (byte-identical bundle). Step-3 verdicts already run: private/diff/anchors-verdicts-2.2.3-2.3.0.txt (102 anchors: 11 CHANGED, 1 MISSING in B = _alwaysAllowedTools, 1 MISSING in A = isWorkspaceTrusted, hook-runner string EDITED 13359 -> 16390 chars). Step-4 delta: private/diff/compare-2.2.3-2.3.0.txt (+723 strings, +704 props, 751 strings added, 152 removed). Public changelog read 2026-11-02 at https://bob.ibm.com/docs/ide/changelog (2.3.0, October 2026; no version between 2.2.3 and 2.3.0). A real task run by 2.3.0 exists in ~/.bob/db/bob.db: id 6cc0a0b9..., title QUOI de neuf bob?, 7 messages, 3 priced calls (2026-11-02 22:45 UTC). Method and procedure: private/SOURCES.md (Re-verifying on a new build, 8 steps; durable-anchor rule). Model milestone: m-1 (TASK-13.x, TASK-14). AGENTS.md rules bind every task: state the build and source of every fact, scripts stay Python 3.8+ stdlib read-only offline, five identical _bobcheck.py copies, no personal data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 VERIFIED_EXTENSION is 2.3.0 and VERIFIED_SCHEMA is 013_workspace_editor_sessions in all five copies, and shasum skills/*/scripts/_bobcheck.py shows one hash
- [x] #2 No shipped script prints a version or schema mismatch warning on the 2.3.0 installation (all five run)
- [x] #3 No published file claims 2.2.3 verification for a fact re-checked on 2.3.0, and facts not re-checked keep their earlier build label
- [x] #4 CHANGELOG has a dated 0.5 section stating what changed in Bob between 2.2.3 and 2.3.0 that matters to bob-sideshow, and what changed in bob-sideshow
- [x] #5 python3 -m py_compile skills/*/scripts/*.py and node --check skills/bob-override-rules/templates/hooks/command-guard.mjs pass; ./install.sh then every installed script runs clean from ~/.bob/skills
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HANDOFF FROM TASK-17.2 (2026-11-03), for the label bump. Build verified: 1.126.0+bob2.3.0.20261026121409, source dist/extension.js plus webview and db read-only.
Labelled 2.3.0 in skills/bob-security-model: reference/approvals.md (all of it except the items below), the docstring of scripts/approval_check.py, the header line of SKILL.md. The script still prints the verified-on-2.2.3 warning because _bobcheck.py and VERIFIED_* are untouched; after your bump it should print nothing on 2.3.0 (re-run: python3 skills/bob-security-model/scripts/approval_check.py 'git status').
Kept with an earlier label or undetermined, with reason: (a) approval dialog and settings screens: only webview string presence checked on 2.3.0, behaviour last read on 2.2.0, 77 logical webview files changed and not diffed; (b) where an untrusted folder switches off auto-approval in the IDE: undetermined on 2.2.3 and 2.3.0; (c) web_search registration in the production IDE: undetermined, not exercised; (d) merge of several PermissionRequest handlers and firing for subagents: undetermined; (e) inputs that make the tree-sitter parser fail: not enumerated; (f) whether execute_command ever counts as outside the workspace: not established.
Corrected a pre-existing error: the PreToolUse hook runs first (before the security check and the approval flow), also on 2.2.3; approvals.md used to say after the security check. Worth a look in bob-override-rules (TASK-17.3) and in the command-guard.mjs header if either repeats the old order (I found no other occurrence of the sentence in skills/ docs/ README.md).
Out of scope, noticed: docs/codex-vs-bob.md line 75 says a Codex flag is Bob's yolo; a reader could take it for an IBM Bob IDE setting (the IDE has none).
approval_check.py gained --workspace and an approximated ignored-path write gate; if you change the CHANGELOG or README wording about the script, say approximation.

PASSATION DE TASK-17.4 (2026-11-03, build 1.126.0+bob2.3.0.20261026121409) pour TASK-17.5 :
- VERIFIED_SCHEMA à poser : 013_workspace_editor_sessions (migrations 001..013).
- Étiquetées 2.3.0 : forme de _meta.spend ({cost, contextTokens}), migrations 012/013 (triggers, aucune table), rétention récursive (cleanupOldTasks, deleteTaskTrees, tasks.retentionDays 30, seuil <= 0 désactive), jeu de flags lu par le code (getFlagValue : 8 clés ; lectures directes : web-search-path, feedback-model, feedback-verification-enabled, bob-plugin-service-url), cinq nouveaux flags, cache des flags = key_value_store featureFlags.v1 (bob_version.py le lit d'abord, state.vscdb en repli), 12 sections et 9 blocs du prompt de la tâche 6cc0a0b9.
- Laissées antérieures (non revérifiables sur 2.3.0) : taux Bobcoins/M et classes standard/economy (2.1.0) ; coût d'une racine incluant ses sous-agents (2.2.3, aucun sous-agent dans la base) ; forme de toolUsage.commandUse (vue seulement sur 2 commandes simples non signalées).
- Indéterminé : contenu d'une ligne editorSession:<project_id> (aucun écrivain dans le bundle, aucune ligne dans la base).
- Les scripts bob-telemetry et bob-version avertissent encore verified on 2.2.3 ; _bobcheck.py non touché (hachage unique).

PASSATION DE TASK-17.5 (2026-11-03, build 1.126.0+bob2.3.0.20261026121409)

Fait : VERIFIED_EXTENSION 2.3.0 et VERIFIED_SCHEMA 013_workspace_editor_sessions dans les cinq _bobcheck.py (indice "matcher logic comes from the 2.3.0 bundle" aligne), pose en dernier. Ré-étiquetage : README (ligne de build), docs/bob-in-perspective.md (build, colonne Bob 2.3.0, neuf evenements de hook), cursor-vs-bob.md et claude-code-vs-bob.md (neuf evenements sur 2.3.0, source bundle), kimi-code-vs-bob.md (la liste autorisee n'est pas la seule porte), codex-vs-bob.md et claude-code-vs-bob.md (plus de "yolo de Bob" : l'IDE n'en a pas, --yolo = alias obsolete de --auto-approve dans Bob Shell), docstring de bob_telemetry.py (schema 2.3.0). opencode-vs-bob.md : aucune etiquette de build Bob, inchange. CHANGELOG section 0.5 datee 2026-11-03.
Etiquettes 2.2.3 restantes, toutes justifiees : historique ou contraste (README "2.2.1 et 2.2.3", liens vers bob-2.2.3-to-2.3.0.md, "was 25/50 on 2.2.3", "2.2.3 removed one level of children"), faits non reverifiables sur 2.3.0 laisses (SKILL.md de bob-telemetry : classes/taux, cout racine avec sous-agents), pages de 17.2-17.4 qui citent 2.2.3 comme point de comparaison.
Hachage unique des cinq _bobcheck.py : 6256eb2b94dda0477db5d62d31446682c902acef.
Reste a la session principale : tag annote v0.5 sur le commit de cette tache, gh release create v0.5 avec la section 0.5 en notes. TASK-17 parente non close.

Vérification de livraison
AC #1 : shasum skills/*/scripts/_bobcheck.py donne un seul hachage 6256eb2b94dda0477db5d62d31446682c902acef pour les cinq ; grep -h "^VERIFIED" donne 2.3.0 et 013_workspace_editor_sessions cinq fois.
AC #2 : lances depuis ~ apres install.sh : bob_version.py (reference MATCH - verified on bob-code 2.3.0 / 013_workspace_editor_sessions), dump_system_prompt.py --task 6cc0a0b9 --list ("verified build"), rule_locations.py ("verified build"), approval_check.py "git status" ("verified build", PROMPT), bob_telemetry.py summary ("verified build", history window). Zero avertissement.
AC #3 : grep 2.2.3 / 20261014125159 avant (72 lignes hors pages de delta) et apres : chaque occurrence restante est historique, contrastive ou un fait non reverifie (voir ci-dessus) ; aucune ne pretend une verification 2.2.3 pour un fait reverifie sur 2.3.0.
AC #4 : section 0.5 du CHANGELOG ecrite (changements de Bob et de bob-sideshow, une puce par point).
AC #5 : py_compile skills/*/scripts/*.py et node --check command-guard.mjs passent ; ./install.sh puis les cinq scripts installes executes depuis ~ sans avertissement.

## Vérification de livraison
Assets : aucun asset produit ou modifié (fichiers texte et code uniquement) ; contrôles d'intégrité : cinq _bobcheck.py au hachage identique 6256eb2b94dda0477db5d62d31446682c902acef, py_compile et node --check verts.
Incidents : aucun.
Capitalisation : rien à verser de plus — tout est dans le CHANGELOG 0.5, les étiquettes et ces notes. Délibérément laissé : étiquettes antérieures sur les faits non reverifiables (taux Bobcoins, coût racine avec sous-agents, commandUse, comportement des écrans d'approbation).
Vérificateur indépendant : sans objet (Incidents = aucun).

Télémétrie (relevé reconstruit depuis les commits, script backfill.py, mesuré depuis la session d'orchestration après le commit) : 30 appels API, ≈ 1,48 USD ≈ 1,32 EUR équivalent API (taux BCE du 2026-11-02 : 1 USD = 0,8916 EUR ; tarifs de liste, pas une facture). Fenêtre b0b51b9 → 3d5588b, 3 min, temps effectif ≈ 3 min, aucune pause (cohérent avec les 2,7 min de l'outil Agent, 38 appels d'outils). Orchestration sur Opus 5.5, sous-agent sur Sonnet. Contrôles refaits depuis la session principale : hachage unique 6256eb2b94dd des cinq _bobcheck.py ; py_compile et node --check OK ; ./install.sh puis les cinq scripts installés lancés depuis le répertoire personnel, aucun avertissement, bob_version.py reference MATCH sur 2.3.0 / 013 ; aucune donnée personnelle dans les fichiers livrés.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Re-labelled to 2.3.0 (README, perspective and comparison pages, bob_telemetry docstring), VERIFIED_* bumped in the five identical _bobcheck.py (hash 6256eb2b), codex/claude yolo wording fixed, CHANGELOG 0.5 written. Verified: shasum, py_compile, node --check, install.sh and the five installed scripts from ~ with no warning.
<!-- SECTION:FINAL_SUMMARY:END -->
