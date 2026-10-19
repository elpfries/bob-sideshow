---
id: TASK-16
title: >-
  Re-verify bob-sideshow on IBM Bob 2.2.3 and store the 2.2.1 and 2.2.3 build
  baselines
status: Done
assignee: []
created_date: '2026-10-19 08:17'
updated_date: '2026-10-19 09:33'
labels:
  - 'model:secondaire'
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
IBM Bob auto-updated in place from 2.2.0 to 2.2.1 (2026-10-05) and then to 2.2.3 (2026-10-14; 2.2.2 was never observed on this machine). Every shipped script now prints "bob-code 2.2.3 installed, verified on 2.2.0 — reference notes may be stale", and `VERIFIED_EXTENSION` still says 2.2.0 in the five `_bobcheck.py` copies.

What is already established (steps 1-5 of the re-verification procedure in `private/SOURCES.md`, run 2026-10-05 and 2026-10-19, written up in `private/baseline-2.2.1/README.md` and `private/baseline-2.2.3/README.md`): the `bob-code` bundle of 2.2.3 is byte-identical to 2.2.1 (sha1 6062c88fb39bb33a7b1f24f8d2cf08911e8dcac5), and 2.2.1 differs from 2.2.0 by 34 bytes — one string, a Jenkins translations path only used in development mode (`BOB_IDE_EXTERNAL_PKG_USER` → `BOB_IDE_EXTERNAL`). 46/46 durable landmarks present, 0 strings or props added or removed, `translations/en.json` identical, schema still `011_key_value_store`. The public changelog attributes 2.2.1 to an "internal bug fix" and 2.2.2/2.2.3 to Remote-SSH; `product.json` confirms the moving parts are the VS Code shell files, not `bob-code`. So no reference note changes on its merits: this task is the remaining steps 6-8 of the procedure plus the storage the procedure asks for and that the 2.2.x baselines skipped.

Two gaps to close while doing it. First, `private/baseline-2.2.0/` and `-2.2.1/` deliberately did not copy `dist/web/assets` (the webview bundles, ~57 MB), so UI-text deltas between builds cannot be diffed; the 2.2.0 and 2.2.1 webview assets are gone from the machine (the installed app is 2.2.3), the only hope is the update endpoint still serving those zips. Second, steps 6 (`dump_system_prompt.py --list`) and 7 (`bob_telemetry.py summary` / `calls`) need a task really executed by the new build; as of 2026-10-19 none exists (the tasks created since 2.2.1 are empty shells with 0 messages).

AGENTS.md rules that bind this task: `VERIFIED_*` is bumped only after re-verifying on the new build and last; the five `_bobcheck.py` copies stay identical (one `shasum`); every stated fact names the build it was read on; `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` before a PR; the CHANGELOG section is dated and the release (tag `v0.4`, `gh release create`) happens after it lands — the release itself is the maintainer`s call, not part of this task. `private/` is gitignored: baselines are stored there, never committed. Model to follow: TASK-13.3 (the 2.2.0 relabel) and TASK-15 (the procedure).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 TASK-16.1 is Done: the 2.2.3 baseline is stored with its webview assets, the 2.2.0/2.2.1 webview recovery attempt is recorded, and the freeze step of the procedure names `dist/web/assets`
- [x] #2 TASK-16.2 is Done: steps 6-8 ran on a real 2.2.3 task, `VERIFIED_*` says 2.2.3 in five identical copies, no script warns on 2.2.3, published files restate the build, CHANGELOG 0.4 is written
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Transmis par TASK-16.2 (2026-10-19) pour TASK-16, cloture par la session principale.

Fait : etapes 6-7 de la procedure de re-verification executees sur la tache reelle 2.2.3 9ad66ac118bfa4983e111fcbe843ead8 (dump_system_prompt.py --list : 12 sections/8 blocs, identique a 2.2.0 ; bob_telemetry.py summary/calls/security : 4 appels tarifes, _meta.spend = {cost, contextTokens} uniquement, meme forme que 2.2.0), consignees dans private/SOURCES.md sous "Steps 6-7 on 2.2.3 (TASK-16.2)". VERIFIED_EXTENSION bumpe a "2.2.3" dans les cinq copies de _bobcheck.py (VERIFIED_SCHEMA reste "011_key_value_store"), shasum confirme un seul hachage sur les cinq : d40c5ea921c22ef32001b21b8ddd179f3530cf20. Treize fichiers publies relabellises a bob-code 2.2.3 / build 1.126.0+bob2.2.3.20261014125159 (README.md, rule_locations.py, command-guard.mjs, approval_check.py, approvals.md, command-migration.md, injected-rules.md, bob_telemetry.py, bob-telemetry/SKILL.md, bob_version.py, docs/bob-in-perspective.md, docs/cursor-vs-bob.md, docs/claude-code-vs-bob.md), chacun citant soit l'identite de bundle 2.2.1/2.2.3 prouvee par TASK-16.1 soit une re-confirmation directe sur trafic/installation 2.2.3. Etiquettes 2.2.0 gardees avec leur raison la ou le fait n'a pas ete re-verifie (taux de facturation d'injected-rules.md) ou designe l'histoire (docs/codex-vs-bob.md "since bob-code 2.2.0", docs/bob-2.1.0-to-2.2.0.md lui-meme, section CHANGELOG 0.3). Un court paragraphe date a ete ajoute en fin de docs/bob-2.1.0-to-2.2.0.md section "Re-checking on the next build" renvoyant au CHANGELOG, sans reecrire la page. CHANGELOG.md : nouvelle section "## 0.4 -- 2026-10-19" au-dessus de 0.3. python3 -m py_compile skills/*/scripts/*.py et node --check skills/bob-override-rules/templates/hooks/command-guard.mjs passent (code retour 0 chacun). git status confirme qu'aucun fichier sous private/ n'est modifie par ce commit (private/ reste gitignore).

Reste a faire par le mainteneur, hors perimetre de TASK-16.2 : tag annote v0.4 sur le commit qui porte la section CHANGELOG 0.4, puis `gh release create v0.4` avec cette section comme notes de release -- geste de release volontairement laisse de cote par AGENTS.md et par le brief de TASK-16.2.

Clôture par la session principale (2026-10-19). Preuve nommée par critère : AC #1 — TASK-16.1 Done (commit e468cdd) ; refait depuis la session principale : 691 lignes dans chaque web-assets.sha256 (2.2.0, 2.2.1, 2.2.3), 5 hachages tirés au sort identiques à l'app installée, listes 2.2.0 et 2.2.3 identiques, private/SOURCES.md étape 2 nomme dist/web/assets (lignes 171-182), grep de données personnelles vide. AC #2 — TASK-16.2 Done (commit 26d9fa6) ; refait depuis la session principale : les cinq scripts exécutés contre l'installation 2.2.3 depuis le dépôt puis, après ./install.sh, depuis ~/.bob/skills — aucun avertissement, bob_version.py dit reference MATCH ; shasum des cinq _bobcheck.py = d40c5ea921c2 unique ; py_compile et node --check OK ; section CHANGELOG 0.4 datée relue. Fait trouvé à froid, hors périmètre des deux sous-tâches, non traité : la base ~/.bob/db/bob.db a perdu aujourd'hui toutes les tâches antérieures au 2026-09-21 (26 tâches / 147 appels tarifés ce matin, 17 tâches / 17 appels après relance de Bob). Cause lue dans le bundle 2.2.3 : à l'initialisation, cleanupOldTasks(tasks.retentionDays, défaut 30 jours) purge les tâches plus vieilles que la rétention ; le plus ancien survivant date de 28 jours. Aucune note livrée ne mentionne cette rétention ; bob-telemetry présente la base comme l'historique complet. À faire : une tâche pour documenter le réglage tasks.retentionDays et sa conséquence dans bob-telemetry et bob-version (décision de l'utilisateur). Coût total de TASK-16 (sous-tâches, orchestration comprise) : ≈ 6,75 EUR équivalent API et 38 min effectives pour les deux sous-tâches, détail dans .kimi-code/skills/run-milestone/calibration.md. Reste au mainteneur : tag annoté v0.4 sur 26d9fa6 ou plus tard, puis gh release create v0.4 avec la section CHANGELOG 0.4 comme notes.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Bob 2.2.3 re-vérifié : bundle bob-code identique à 2.2.1 et à 34 octets de 2.2.0 (une chaîne de mode développement), webview et traductions identiques, schéma inchangé ; baselines 2.2.0/2.2.1/2.2.3 stockées dans private/ webview comprise (16.1) ; étapes 6-8 exécutées sur une tâche réelle 2.2.3, VERIFIED_* à 2.2.3 dans cinq copies identiques, 13 fichiers ré-étiquetés, CHANGELOG 0.4 (16.2). Vérifié par exécution des cinq scripts contre l'installation réelle, depuis le dépôt et depuis ~/.bob/skills après install.sh, sans avertissement. Release v0.4 laissée au mainteneur.
<!-- SECTION:FINAL_SUMMARY:END -->
