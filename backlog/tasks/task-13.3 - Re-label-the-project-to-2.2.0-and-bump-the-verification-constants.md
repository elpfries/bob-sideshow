---
id: TASK-13.3
title: Re-label the project to 2.2.0 and bump the verification constants
status: To Do
assignee: []
created_date: '2026-09-28 19:34'
updated_date: '2026-09-28 21:56'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies:
  - TASK-13.1
  - TASK-13.2
parent_task_id: TASK-13
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Last step, and only once the facts have actually been re-read: the project says 2.1.0 in about twenty places and the five copies of `_bobcheck.py` declare 2.1.0 and `010_pending_approvals` verified, so every skill warns on a 2.2.0 install even where nothing changed.

AGENTS.md makes the order explicit — `VERIFIED_*` is bumped only after re-verifying the notes on the new build, and the five copies must stay identical, one `shasum`. Alongside them, the version strings in the reference note titles, the script docstrings, `rule_locations.py`, the `command-guard.mjs` header, `bob-telemetry/SKILL.md`, README, and the build lines in the comparison docs all have to state the build they now hold for. Where a fact was verified on 2.1.0 and could not be re-checked, the fix is to say so, not to relabel it 2.2.0.

CHANGELOG gets the entry that lets a reader tell what moved between the two builds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `VERIFIED_EXTENSION` is `2.2.0` and `VERIFIED_SCHEMA` is `011_key_value_store` in all five copies, and `shasum skills/*/scripts/_bobcheck.py` shows one hash
- [ ] #2 No shipped script prints a mismatch warning on a 2.2.0 installation
- [ ] #3 No published file claims 2.1.0 provenance for a fact that now holds on 2.2.0 — reference notes, script docstrings and headers, SKILL.md files, README, the comparison docs build lines
- [ ] #4 Facts kept from 2.1.0 without re-verification are labelled with the build they were read on
- [ ] #5 CHANGELOG records the move to 2.2.0 and what changed in Bob between the two builds
- [ ] #6 `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Tranché par l'analyse de TASK-13.4 — 2026-09-28 (PRIME sur la description)

- Le build 2.1.0 de référence des notes (sha1 d8b1130e…, suffixe 20260827055214) n'est PAS le build
  2.1.0 téléchargé (sha1 f5ebecbd…, 9 octets d'écart, autre run Jenkins). Le ré-étiquetage doit citer le
  build 2.2.0 installé (1.126.0+bob2.2.0.20260924155054, extension.js sha1 6afa9f9c…) et, pour ce qui
  reste attribué à 2.1.0, la chaîne de build des notes, sans prétendre à un diff octet pour octet.
- Le CHANGELOG doit reprendre le delta comportemental consigné dans TASK-13.4 (agents modelTier, hooks,
  settings, sécurité, execute_command background, prompt), pas seulement le bump de version.

Notes transmises par TASK-13.1 (2026-09-28), perimetre volontairement non touche pendant la re-verification des trois notes de reference (skills/bob-security-model/reference/approvals.md, skills/bob-agent-rules/reference/injected-rules.md, skills/bob-agent-rules/reference/command-migration.md), du template skills/bob-override-rules/templates/agents/explore-premium.md et du hook skills/bob-override-rules/templates/hooks/command-guard.mjs. A votre charge :

1. Titres des trois notes : toutes commencent encore par bob-code 2.1.0, alors que leurs faits sont maintenant verifies et corriges contre 2.2.0, build 1.126.0+bob2.2.0.20260924155054.
2. command-guard.mjs, ligne d en-tete : mentionne encore IBM Bob 2.1.0 hook contract. Le commentaire de contrat lui meme a ete complete pour mentionner la voie JSON de sortie 2.2.0 ; seule la mention de version reste a votre charge.
3. approval_check.py : docstring toujours Would IBM Bob (bob-code 2.1.0) auto-approve this shell command. Le matcher de jetons qu il reimplemente a ete compare a la fonction 2.2.0 (verdict : aucune divergence), donc le script n a pas besoin d etre modifie sur le fond, seulement sur son etiquetage de version.
4. _bobcheck.py (cinq copies, un seul hash confirme au commit de cette tache) : l avertissement de version qu il affiche (bob-code 2.2.0 installe, verifie sur 2.1.0...) est volontairement laisse tel quel, il est correct tant que VERIFIED_* n a pas ete mis a jour apres re-verification du build. C est cette tache qui doit bumper les constantes VERIFIED_* apres avoir revalide les notes sur le nouveau build.
5. README et CHANGELOG du depot (non touches par TASK-13.1) : a verifier s ils mentionnent aussi bob-code 2.1.0 ou une version figee a mettre a jour.

Transmission de TASK-13.2 vers TASK-13.3 (verification sur trafic reel 2.2.0, 2026-09-28).

SCRIPTS MODIFIES PAR TASK-13.2 (perimetre etroit, VERIFIED_* non touche):
1. skills/bob-telemetry/scripts/bob_telemetry.py - docstring toujours: Verified on the bob-code 2.1.0 schema (ligne intacte, VERIFIED_* reste proprietaire de _bobcheck.py); une phrase a ete ajoutee sous cette ligne documentant que sur 2.2.0 _meta.spend est reduit a cost et contextTokens. Code: fonction spend() detecte desormais tokensKnown (presence des cles input/output) et transporte contextTokens; cmd_calls, cmd_tasks, cmd_summary affichent n/a au lieu de 0 pour les colonnes de tokens quand tokensKnown est faux; cmd_calls gagne une colonne ctx.
2. skills/bob-telemetry/SKILL.md - la ligne d en-tete build 2.1.0 est restee inchangee; une puce a ete ajoutee sous la section When explaining pour signaler que sur 2.2.0 la classe est toujours n/a et le tarif unitaire non mesurable, avec la colonne ctx disponible en remplacement.
3. skills/bob-version/scripts/bob_version.py - docstring toujours: Read-only; Python 3.8+, standard library only (ligne intacte); une note a ete ajoutee dessous documentant la reverification du 2026-09-28 sur build 1.126.0+bob2.2.0.20260924155054. FLAG_KEYS etendu aux 8 cles que 2.2.0 lit reellement via getFlagValue (bob-findings-enabled, dynamic-context-enabled, feedback-model, feedback-verification-enabled, ibm-support-url, issue-repo-url, max-monthly-budget-allowance, review-flow-enabled), en gardant les 6 cles historiques. command-security-model et summary-model restent affiches mais annotes pushed, not read by 2.2.0 (texte et JSON) au lieu d etre retires.

FAITS DE TELEMETRIE A PORTER AU CHANGELOG (perimetre TASK-13.3):
- Sur bob-code 2.2.0, _meta.spend des appels LLM ne porte plus que cost et contextTokens (verifie sur les 19 appels du trafic 2.2.0 disponible, sans exception): input, output, cacheRead, cacheWrite, reasoningTokens ont disparu. Le tarif unitaire (Bobcoins par million de tokens, 2.0 standard et 0.833 economy sur 2.1.0, re-mesure confirmee sur le snapshot) ne peut plus etre calcule sur du trafic 2.2.0. Seuls le cout par appel et contextTokens restent disponibles.
- Le rangement des appels de sous-agents en base (0 message sous l id de la tache sous-agent, transcript complet imbrique dans le champ messages du message tool du parent, avec un _meta.spend agrege sur le message parent egal a la somme des appels internes) est IDENTIQUE entre 2.1.0 et 2.2.0 - verifie directement sur les 4 taches subagent du snapshot 2.1.0 et sur la tache enfant 22251a4d du trafic 2.2.0. Ce n est pas un changement de 2.2.0 malgre l intuition initiale de la note d orchestration; le CHANGELOG ne doit donc pas presenter ceci comme une nouveaute 2.2.0.

DECISION FLAGS SERVEUR A CONFIRMER DANS LE CHANGELOG: command-security-model et summary-model restent pousses par le serveur (vus identiques dans key_value_store.featureFlags.v1 et dans state.vscdb) mais ne sont plus lus par bob-code 2.2.0 pour leur usage d origine (voir docs/bob-2.1.0-to-2.2.0.md section 6). bob_version.py les affiche desormais avec l annotation pushed, not read by 2.2.0 plutot que de les retirer.

POINT POUR LES NOTES DE REFERENCE (proprietaire TASK-13.1, hors perimetre TASK-13.2, signale pour suite eventuelle): skills/bob-agent-rules/reference/injected-rules.md ligne 17 marquait la config de prompt production comme non confirmee et assignait la verification a TASK-13.2. C est fait: dump_system_prompt.py --list sur les deux taches 2.2.0 (f93b5fd9, e860b444) donne la meme liste de sections que le layout default/aquarius documente, sans aucune section boreas (task_execution, when_stuck) ni orion (act_and_iterate, ground_truth, define_done, prove_done). La distinction default versus aquarius reste indiscernable par la seule liste de sections. Le fichier de reference lui-meme n a pas ete modifie (hors perimetre de TASK-13.2).

Aucune donnee personnelle dans cette transmission (pas de chemin /Users, pas de contenu de tache Bob).
<!-- SECTION:NOTES:END -->
