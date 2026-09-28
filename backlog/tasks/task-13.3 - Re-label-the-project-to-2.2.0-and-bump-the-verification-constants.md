---
id: TASK-13.3
title: Re-label the project to 2.2.0 and bump the verification constants
status: Done
assignee:
  - '@eric.bonkarma'
created_date: '2026-09-28 19:34'
updated_date: '2026-09-28 22:28'
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
- [x] #1 `VERIFIED_EXTENSION` is `2.2.0` and `VERIFIED_SCHEMA` is `011_key_value_store` in all five copies, and `shasum skills/*/scripts/_bobcheck.py` shows one hash
- [x] #2 No shipped script prints a mismatch warning on a 2.2.0 installation
- [x] #3 No published file claims 2.1.0 provenance for a fact that now holds on 2.2.0 — reference notes, script docstrings and headers, SKILL.md files, README, the comparison docs build lines
- [x] #4 Facts kept from 2.1.0 without re-verification are labelled with the build they were read on
- [x] #5 CHANGELOG records the move to 2.2.0 and what changed in Bob between the two builds
- [x] #6 `python3 -m py_compile skills/*/scripts/*.py` and `node --check skills/bob-override-rules/templates/hooks/command-guard.mjs` pass
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

Files relabelled to bob-code 2.2.0 (facts already re-verified by TASK-13.1/13.2/13.4):
- skills/{bob-version,bob-agent-rules,bob-override-rules,bob-security-model,bob-telemetry}/scripts/_bobcheck.py: VERIFIED_EXTENSION="2.2.0", VERIFIED_SCHEMA="011_key_value_store", matcher hint "matcher logic comes from the 2.2.0 bundle". shasum confirms one hash across all five (e9a89826b6cf29d313fbd83538da7f1acd06ed92) both before and after.
- skills/bob-security-model/reference/approvals.md: title line only ("bob-code 2.2.0"); body was already re-verified by TASK-13.1.
- skills/bob-agent-rules/reference/injected-rules.md: title line, plus the prompt-layout paragraph near line 17 -- replaced "unconfirmed ... TASK-13.2's to close" with the confirmed fact TASK-13.2 transmitted: dump_system_prompt.py --list on 2.2.0 tasks f93b5fd9 and e860b444 both match the default/aquarius section list, no boreas/orion sections, default vs aquarius still indistinguishable by section list alone.
- skills/bob-agent-rules/reference/command-migration.md: title line only.
- skills/bob-telemetry/SKILL.md: "When explaining (build 2.2.0):" header.
- skills/bob-telemetry/scripts/bob_telemetry.py: docstring line ("Verified on the bob-code 2.2.0 schema (011_key_value_store); re-verified 2026-09-28 on live bob-code 2.2.0 traffic").
- skills/bob-security-model/scripts/approval_check.py: docstring line ("Would IBM Bob (bob-code 2.2.0) auto-approve...") -- per TASK-13.1's note that the matcher was compared against the 2.2.0 function with no divergence, so only the label moved.
- skills/bob-override-rules/templates/hooks/command-guard.mjs: header comment ("IBM Bob 2.2.0 hook contract") -- the contract body itself was already updated by TASK-13.1.
- README.md: provenance paragraph now cites bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054, and links docs/bob-2.1.0-to-2.2.0.md as the record of what moved from 2.1.0.
- docs/bob-in-perspective.md: "Builds:" line and the "Bob 2.1.0" table header moved to 2.2.0; the "One hook event" paragraph and the "Hook events" table cell rewritten to 7 events (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, PostCompact, Stop) with JSON replies and HTTPS handlers, since every other Bob claim in that file (audit trail, command check, AGENTS.md/hooks exit-code semantics, explore subagent, allowlist matching, no sandbox) is either confirmed unchanged by docs/bob-2.1.0-to-2.2.0.md or was not contradicted by it.
- docs/cursor-vs-bob.md and docs/claude-code-vs-bob.md: the "Bob has one pre-tool hook"/"one event and one exit-code rule" sentences corrected to seven events, JSON replies, HTTPS handlers; other tools' event counts (22, 21, ...) left untouched.
- docs/codex-vs-bob.md: the reference to Bob's "command-security-model" as the live mechanism corrected to note that bob-code 2.2.0 routes the check through a server-side "security" model tier instead of that flag.
- docs/{opencode,kimi-code}-vs-bob.md: read in full, no Bob claim there depends on a fact this delta changes (hooks, security routing, execute_command background and modelTier frontmatter are not mentioned in either); left untouched.
- CHANGELOG.md: new entry under the existing "0.2 -- unreleased" section (kept as one unreleased section rather than opening a 0.3) covering modelTier, the seven hook events plus JSON/HTTPS, the autoCompact rename, the security-tier routing, execute_command background, the prompt-section registry and plugins/ roots, key_value_store, and the reduced _meta.spend shape; explicitly does not present subagent-call storage as a 2.2.0 novelty, since TASK-13.2 proved it identical to 2.1.0.

2.1.0 mentions kept, with reason (rest of the "2.1.0" grep is historical then-vs-now comparison inside already re-verified notes, not a provenance claim for a still-open fact):
- skills/bob-override-rules/scripts/rule_locations.py: docstring stays on bob-code 2.1.0, build 1.126.0+bob2.1.0.20260827055214, now saying explicitly it is NOT re-verified on 2.2.0. Reason: docs/bob-2.1.0-to-2.2.0.md section 2 documents a plugins/ subdirectory added to every rule and skill root on 2.2.0 (.bob/plugins/<name>/, ~/.bob/plugins/<name>/), which this script's hardcoded precedence line and its scope() walk do not read; its trust check also reads trustedFolders.json, a store the delta says 2.2.0 no longer consults for trust (workspace.isTrusted from the IDE is used instead). No note from TASK-13.1 or TASK-13.2 transmitted a re-verification of this script, and AGENTS.md/TASK-13.3's own rule is to bump only after re-verifying, so both the label and the logic (out of this task's scope) stay 2.1.0.
- skills/bob-agent-rules/reference/injected-rules.md, billing-rates line ("Observed billing: premium-ide 2.0 Bobcoins / M tokens ... Not re-verified: these rates were measured on the 2.1.0 database ..."): left exactly as TASK-13.1 wrote it. TASK-13.2's own notes to this task do not report a re-measurement of the two flat rates on 2.2.0 traffic (only that _meta.spend on 2.2.0 no longer carries a token breakdown at all, which is why the rate can no longer be measured going forward) -- so this fact stays attributed to 2.1.0.
No other 2.1.0 mention survives outside those two cases, private/, backlog/, and docs/bob-2.1.0-to-2.2.0.md itself (checked by re-running the grep from the task brief after all edits, 24 remaining lines, all reviewed).

Script outputs, first line of each, before and after the VERIFIED_* bump (real installation: bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054, schema 011_key_value_store):

BEFORE (VERIFIED_EXTENSION=2.1.0, VERIFIED_SCHEMA=010_pending_approvals):
- bob_version.py: reference    DIFFERENT -- bob-code 2.2.0 installed, verified on 2.1.0; schema 011_key_value_store, verified on 010_pending_approvals -- reference notes may be stale
- bob_telemetry.py summary: [bob-sideshow] WARNING: bob-code 2.2.0 installed, verified on 2.1.0; schema 011_key_value_store, verified on 010_pending_approvals -- unknown fields are ignored
- dump_system_prompt.py --list: same WARNING line as bob_telemetry.py
- approval_check.py "git status": [bob-sideshow] WARNING: bob-code 2.2.0 installed, verified on 2.1.0 -- matcher logic comes from the 2.1.0 bundle
- rule_locations.py: [bob-sideshow] WARNING: bob-code 2.2.0 installed, verified on 2.1.0 -- unknown fields are ignored

AFTER (VERIFIED_EXTENSION=2.2.0, VERIFIED_SCHEMA=011_key_value_store):
- bob_version.py: reference    MATCH -- verified on bob-code 2.2.0 / 011_key_value_store
- bob_telemetry.py summary: [bob-sideshow] bob-code 2.2.0, schema 011_key_value_store -- verified build
- dump_system_prompt.py --list: same MATCH line as bob_telemetry.py
- approval_check.py "git status": [bob-sideshow] bob-code 2.2.0 -- verified build
- rule_locations.py: [bob-sideshow] bob-code 2.2.0 -- verified build

No script prints a WARNING after the bump. python3 -m py_compile skills/*/scripts/*.py and node --check skills/bob-override-rules/templates/hooks/command-guard.mjs both pass. grep -rn "/Users/|ericfries" over skills docs README.md CHANGELOG.md is empty. git status shows only the files listed above modified, nothing under private/.

What this task did not do: did not touch private/ or any baseline snapshot under it; did not re-open TASK-13.1/13.2/13.4 verdicts; did not modify script logic beyond the docstring/label lines already scoped (bob_telemetry.py and bob_version.py logic was TASK-13.2's, untouched here); did not fix docs/opencode-vs-bob.md or docs/kimi-code-vs-bob.md since neither depends on a delta fact; did not re-measure the 2.1.0 unit-price rates or re-verify rule_locations.py's logic against 2.2.0's plugins/ roots -- both stay explicitly labelled 2.1.0/unverified per AC #4; did not run task-telemetry on this task (excluded from self-measurement per the task brief).

## Verification de livraison
Assets : aucun asset binaire produit ou modifie. Controles d integrite executes sur les fichiers modifies : python3 -m py_compile skills/*/scripts/*.py (OK) ; node --check skills/bob-override-rules/templates/hooks/command-guard.mjs (OK) ; shasum skills/*/scripts/_bobcheck.py -> un seul hash sur les cinq copies (e9a89826b6cf29d313fbd83538da7f1acd06ed92) ; les cinq scripts livres (bob_version.py, bob_telemetry.py summary, dump_system_prompt.py --list, approval_check.py, rule_locations.py) executes contre l installation reelle bob-code 2.2.0 avant et apres le bump, plus aucun n imprime de WARNING apres ; grep -rn "/Users/|ericfries" sur skills docs README.md CHANGELOG.md vide ; git status confirme qu aucun fichier sous private/ n est modifie.
Incidents : aucun -- pas d interruption ni de relance d etape, pas de bug d outillage trouve, pas de contournement, pas d intervention manuelle sur un resultat de script, pas de tache rouverte apres Done.
Capitalisation : deja versee dans les notes d implementation ci-dessus (liste des fichiers relabellises et pourquoi, mentions 2.1.0 conservees avec leur raison -- rule_locations.py et le taux de facturation d injected-rules.md -- sorties avant/apres bump, ce qui n a pas ete fait). Point non evident pour la suite : le CHANGELOG a ete verse dans la section 0.2 -- unreleased existante plutot que d ouvrir une 0.3, pour garder une seule section non publiee ; a reconsiderer seulement si 0.2 est publiee avant que ce travail ne le soit.
Verificateur independant : non requis (Incidents = aucun).

AC #1 : grep -n "VERIFIED_" skills/*/scripts/_bobcheck.py montre VERIFIED_EXTENSION = "2.2.0" et VERIFIED_SCHEMA = "011_key_value_store" dans les cinq copies (bob-version, bob-agent-rules, bob-override-rules, bob-security-model, bob-telemetry) ; shasum skills/*/scripts/_bobcheck.py donne un seul hash, e9a89826b6cf29d313fbd83538da7f1acd06ed92, sur les cinq fichiers.
AC #2 : les cinq scripts livres executes contre l installation reelle (bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054) apres le bump impriment tous une ligne verified build ou MATCH, sans aucun WARNING -- bob_version.py : "reference    MATCH -- verified on bob-code 2.2.0 / 011_key_value_store" ; bob_telemetry.py summary : "[bob-sideshow] bob-code 2.2.0, schema 011_key_value_store -- verified build" ; dump_system_prompt.py --list : meme ligne MATCH ; approval_check.py "git status" : "[bob-sideshow] bob-code 2.2.0 -- verified build" ; rule_locations.py : "[bob-sideshow] bob-code 2.2.0 -- verified build". Les memes cinq scripts executes AVANT le bump impriment chacun un WARNING de mismatch (voir note precedente Script outputs... pour le detail ligne par ligne).
AC #3 : grep -rn "2.1.0" --include=*.md --include=*.py --include=*.mjs --include=*.json --include=*.sh . filtre de private/, backlog/ et docs/bob-2.1.0-to-2.2.0.md donne 24 lignes apres les edits (contre 41 avant), toutes revues dans la note "2.1.0 mentions kept, with reason" ci-dessus : soit des comparaisons historiques 2.1.0-vs-2.2.0 a l interieur de notes deja re-verifiees (approvals.md, command-migration.md, injected-rules.md, codex-vs-bob.md, README.md, CHANGELOG.md, bob_version.py), soit les deux faits explicitement laisses non re-verifies (rule_locations.py, le taux de facturation d injected-rules.md), couverts par AC #4.
AC #4 : liste nommee dans la note "2.1.0 mentions kept, with reason" ci-dessus -- skills/bob-override-rules/scripts/rule_locations.py (docstring : "Not re-verified on bob-code 2.2.0", raison plugins/ et trustedFolders.json) et skills/bob-agent-rules/reference/injected-rules.md ligne de facturation ("Not re-verified... measured on the 2.1.0 database", laissee telle quelle par TASK-13.1, aucune re-mesure transmise par TASK-13.2).
AC #5 : CHANGELOG.md, section "0.2 -- unreleased", nouvelle entree "Re-labelled for IBM Bob 2.2.0" avec neuf puces (modelTier, hooks/JSON/HTTPS, autoCompact, securite tier server-routed, execute_command background, prompt registry/plugins, key_value_store, _meta.spend reduit, bibliotheques) plus la puce sur le bump VERIFIED_*.
AC #6 : python3 -m py_compile skills/*/scripts/*.py termine sans erreur (code retour 0, aucune sortie) ; node --check skills/bob-override-rules/templates/hooks/command-guard.mjs termine sans erreur ; grep -rn "/Users/|ericfries" skills docs README.md CHANGELOG.md ne retourne rien (grep exit 1) ; git status ne montre aucun fichier sous private/ parmi les modifications.

Télémétrie (relevé reconstruit depuis les commits, script backfill.py, mesuré depuis la session d'orchestration après le commit) : 97 appels API (sonnet-5 : 89 pour l'agent d'implémentation, fable-5-1 : 6 pour l'orchestration, 2 appels synthétiques sans coût), 16 080 tokens de sortie, 16 266 088 cache read, 421 933 cache write, ≈ 7,69 USD ≈ 6,62 EUR équivalent API (taux de repli figé du 2026-09-03 : 1 USD = 0,8610 EUR, BCE injoignable ; tarifs de liste, pas une facture). Fenêtre entre le commit précédent (29b6f1c) et les deux commits de la tâche (0437172, ffa1bca), sous-agent compris. Le chiffre couvre UNE TENTATIVE INTERROMPUE : l'agent a été coupé par une limite de session (HTTP 429) après 82 appels d'outils, juste avant la clôture, puis repris avec son contexte intact (17 appels d'outils) — aucun travail refait. Fenêtre 25 min, temps effectif ≈ 13 min ; les ≈ 12 min de pause sont la coupure et l'attente de la reprise par l'utilisateur, pas du traitement. Chaîne conduite sur Claude Code / Fable 5.1, sous-agent sur Sonnet (label model:secondaire).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Re-labelled the project to bob-code 2.2.0 (build 1.126.0+bob2.2.0.20260924155054) and bumped the five _bobcheck.py copies (VERIFIED_EXTENSION=2.2.0, VERIFIED_SCHEMA=011_key_value_store, one shasum: e9a89826b6cf29d313fbd83538da7f1acd06ed92). Relabelled only facts TASK-13.1/13.2/13.4 already re-verified: the three reference-note titles, injected-rules.md's prompt-layout paragraph (default/aquarius confirmed on tasks f93b5fd9 and e860b444), bob-telemetry/SKILL.md, bob_telemetry.py and approval_check.py docstrings, command-guard.mjs header, README provenance paragraph, docs/bob-in-perspective.md (Builds line, hook-count paragraph and table cell rewritten to 7 events/JSON/HTTPS), and the "Bob has one hook" sentences in cursor-vs-bob.md, claude-code-vs-bob.md and codex-vs-bob.md's command-security-model reference. Left rule_locations.py and injected-rules.md's billing-rate line explicitly on bob-code 2.1.0, labelled as not re-verified (plugins/ roots and trustedFolders.json are stale in the former; unit prices were never re-measured on 2.2.0 traffic). Added a CHANGELOG entry under the existing 0.2 unreleased section. Verified all five scripts (bob_version.py, bob_telemetry.py summary, dump_system_prompt.py --list, approval_check.py, rule_locations.py) print a mismatch WARNING before the bump and a clean verified-build/MATCH line after, against the real bob-code 2.2.0 installation. python3 -m py_compile and node --check both pass; grep for /Users/ and ericfries over skills, docs, README.md, CHANGELOG.md is empty; git status shows no changes under private/.
<!-- SECTION:FINAL_SUMMARY:END -->
