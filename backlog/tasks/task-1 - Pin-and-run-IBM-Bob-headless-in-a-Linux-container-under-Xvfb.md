---
id: TASK-1
title: Pin and run IBM Bob headless in a Linux container under Xvfb
status: To Do
assignee: []
created_date: '2026-09-19 20:14'
updated_date: '2026-10-04 22:40'
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
- [ ] #3 The Bob build (app version, bob-code version, extension.js SHA-1) is pinned in the image and asserted at container start; a mismatch fails the run loudly
- [ ] #4 Bob auto-update is disabled inside the image
- [ ] #5 Two builds of the image from the same inputs produce the same pinned Bob build
- [ ] #6 Image build and run are documented with a single command each
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## À lire avant de choisir la version de Bob à épingler — 2026-10-05, session d'orchestration de m-1

La description de m-0 épingle bob-code 2.1.0 « parce que le harnais dépend d'ancres internes que le minifieur renomme entre les releases ». La milestone m-1 (close le 2026-09-29, release 0.3) a vérifié ce point sur 2.2.0 :
- la crainte est fondée en général : le passage CommonJS → ESM de 2.2.0 a effacé une douzaine de noms d'export de module ;
- mais les ancres dont le harnais vit sont INTACTES ou à logique identique en 2.2.0, verdict par verdict : shouldAutoApprove, validateToolExecution, _alwaysAllowedTools (portes d'approbation : SAME LOGIC, seuls des artefacts d'interop), handleUiReply (IDENTICAL), task_pending_approvals et 010_pending_approvals (chaînes identiques), « hooks cannot block » (fonction changée : PostCompact non bloquant, sortie JSON de PreToolUse — le Stop hook reste non bloquant), « Extension activated » et bob-code.sendMessageWithHiddenPrompt (présents ; activate() a 48 éditions réelles, surtout l'ouverture des settings corrompus et un workspaceUris passé au harnais — à relire pour l'API retournée). Preuves : docs/bob-2.1.0-to-2.2.0.md et, hors git, private/diff/anchors-verdicts.txt.
- Le build 2.1.0 reste disponible hors git (private/baseline-2.1.0/, zip 262 Mo, sha256 34d299ab…) si l'on préfère l'ancienne version ; le build 2.2.0 installé est en private/baseline-2.2.0/.

Décision NON prise : quelle version épingler dans le conteneur. Elle revient à l'utilisateur au démarrage de cette tâche ; cette note donne seulement ce que m-1 a établi. La procédure pour re-vérifier les ancres sur un build quelconque est en private/SOURCES.md (huit étapes).
<!-- SECTION:NOTES:END -->
