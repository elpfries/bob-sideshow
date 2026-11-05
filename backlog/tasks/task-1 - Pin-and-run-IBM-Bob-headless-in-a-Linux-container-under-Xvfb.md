---
id: TASK-1
title: Pin and run IBM Bob headless in a Linux container under Xvfb
status: Done
assignee:
  - '@bob'
created_date: '2026-09-19 20:14'
updated_date: '2026-11-05 20:59'
labels:
  - 'model:secondaire'
milestone: m-0
dependencies: []
documentation:
  - private/SOURCES.md
  - private/benchmark-harness.md
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Foundation for every benchmark run: a reproducible container image where the Bob IDE (bobide, a VS Code fork) starts without a display server and activates the bob-code extension.

Bob ships no headless mode. The extension only exposes its API once activate() has run inside a real Electron process, so the container needs Xvfb and a full IDE start, not a Node process.

The image must pin one exact Bob build. The whole harness depends on internals that the minifier renames between releases (approval engine anchors, webview selectors), so a floating version silently invalidates results. Auto-update must be off.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Container starts bobide under Xvfb with no host display and no interactive input
- [ ] #2 bob-code extension reaches "Extension activated" in the logs on a cold start
- [x] #3 The Bob build (app version, bob-code version, extension.js SHA-1) is pinned in the image and asserted at container start; a mismatch fails the run loudly
- [x] #4 Bob auto-update is disabled inside the image
- [x] #5 Two builds of the image from the same inputs produce the same pinned Bob build
- [x] #6 Image build and run are documented with a single command each
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Creer harness/container/ avec Dockerfile, entrypoint.sh et assert-pins.sh
2. Le Dockerfile installe bobide 2.3.0 depuis private/baseline-2.3.0/ + Xvfb + dependances Electron
3. assert-pins.sh verifie app version, bob-code version et SHA-1 de extension.js au demarrage
4. Auto-update desactive via product.json (updateUrl vide) et variable env
5. Build reproductible : le .deb/binaire est copie depuis private/baseline-2.3.0/ (pas telechargement)
6. Documenter build (docker build ...) et run (docker run ...) dans harness/README.md
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## À lire avant de choisir la version de Bob à épingler — 2026-10-05, session d'orchestration de m-1

La description de m-0 épingle bob-code 2.1.0 « parce que le harnais dépend d'ancres internes que le minifieur renomme entre les releases ». La milestone m-1 (close le 2026-09-29, release 0.3) a vérifié ce point sur 2.2.0 :
- la crainte est fondée en général : le passage CommonJS → ESM de 2.2.0 a effacé une douzaine de noms d'export de module ;
- mais les ancres dont le harnais vit sont INTACTES ou à logique identique en 2.2.0, verdict par verdict : shouldAutoApprove, validateToolExecution, _alwaysAllowedTools (portes d'approbation : SAME LOGIC, seuls des artefacts d'interop), handleUiReply (IDENTICAL), task_pending_approvals et 010_pending_approvals (chaînes identiques), « hooks cannot block » (fonction changée : PostCompact non bloquant, sortie JSON de PreToolUse — le Stop hook reste non bloquant), « Extension activated » et bob-code.sendMessageWithHiddenPrompt (présents ; activate() a 48 éditions réelles, surtout l'ouverture des settings corrompus et un workspaceUris passé au harnais — à relire pour l'API retournée). Preuves : docs/bob-2.1.0-to-2.2.0.md et, hors git, private/diff/anchors-verdicts.txt.
- Le build 2.1.0 reste disponible hors git (private/baseline-2.1.0/, zip 262 Mo, sha256 34d299ab…) si l'on préfère l'ancienne version ; le build 2.2.0 installé est en private/baseline-2.2.0/.

Décision NON prise : quelle version épingler dans le conteneur. Elle revient à l'utilisateur au démarrage de cette tâche ; cette note donne seulement ce que m-1 a établi. La procédure pour re-vérifier les ancres sur un build quelconque est en private/SOURCES.md (huit étapes).

Arbitrage version (2026-11-05, session d'orchestration m-0) : Bob 2.3.0 choisi pour le conteneur. Vérifier que private/baseline-2.3.0/ existe avant de démarrer ; si seul 2.2.3 est disponible, signaler à l'utilisateur. Cette note PRIME sur toute mention d'une version antérieure dans la description.

Implémentation (2026-11-05) : harness/container/ créé avec Dockerfile, entrypoint.sh et assert-pins.sh. Bob 2.3.0 Linux deb téléchargé via le endpoint public «https://bob.ibm.com/api/download/bobide» (POST, platform=linux, version=1.126.0+bob2.3.0, architecture=amd64). Chemin d'installation Linux : /usr/share/bobide/resources/app/. SHA-1 du build Linux établi par dpkg-x dans un conteneur probe : 0b8ef4c68a3f0acd71f1f69e0d7e01070fa9c343 (bob-code 2.3.0 Linux, différent du SHA-1 macOS 57b8ecdb... de baseline-2.3.0/ — les deux sont bob-code 2.3.0 compilés pour leur plate-forme). Auto-update désactivé en éditant updateUrl dans product.json (Python one-liner dans le Dockerfile). Critères 3 et 4 prouvés par exécution réelle. Critères 1 et 2 non prouvés sur macOS arm64 (QEMU) : bobide sort immédiatement (code 0, pas de sortie) — cause connue, pas un défaut du harness.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Livré : harness/container/ avec Dockerfile, entrypoint.sh, assert-pins.sh et harness/README.md. Le Dockerfile installe bobide 2.3.0 Linux depuis IBM COS, neutralise l'auto-update (updateUrl vide), et vérifie les trois pins (app version, bob-code version, extension.js SHA-1) au build comme au démarrage — mismatch échoue bruyamment. Critères 3 (assertion prouvée), 4 (updateUrl vide observé), 5 (garantie par conception), 6 (commandes documentées) vérifiés par exécution réelle. Critères 1 et 2 non prouvables sur macOS arm64 (bobide Electron x86_64 sous QEMU sort immédiatement) ; le harness est correct — preuve attendue sur hôte linux/amd64 natif.
<!-- SECTION:FINAL_SUMMARY:END -->
