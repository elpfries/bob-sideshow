---
id: TASK-13.2
title: Re-verify the database and script surface on the 2.2.0 schema
status: To Do
assignee: []
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 21:33'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies:
  - TASK-13.4
parent_task_id: TASK-13
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2.2.0 database is at migration `011_key_value_store` and carries a new `key_value_store` table, one migration past the schema the scripts declare verified. Everything still reads, but nothing has been checked against the new shape.

Three things need real data rather than a code read. The billing rates were never read in the bundle — they were measured as cost over tokens across stored calls, two flat rates on 2.1.0 — so they have to be re-measured on calls produced by 2.2.0. The system-prompt section list can only be compared from a task created under 2.2.0, because the newest stored prompt predates the update; a 2.1.0 dump already shows sections and guidance blocks the reference note does not list, so the note may have been incomplete or the layout may have moved. And the new `key_value_store` table has to be looked at to know whether it holds anything the telemetry or version views should report, or whether it is irrelevant to them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 What `key_value_store` holds on 2.2.0 is stated, and whether it changes anything the shipped scripts read
- [ ] #2 The unit prices are re-measured over calls made by 2.2.0 and the telemetry model classes and Bobcoin figures are confirmed or corrected
- [ ] #3 A task is created under 2.2.0 and its stored prompt compared section by section against the documented layout, with differences recorded
- [ ] #4 Every view of `bob_telemetry.py` is run on the 2.2.0 database and its output checked for plausibility, not just for absence of errors
- [ ] #5 `bob_version.py` reports the 2.2.0 app, extension, schema and server flags correctly, including any flag key that has appeared or disappeared
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Preuve 2.2.0 — arbitrage tranché par l'utilisateur, 2026-09-28 (PRIME sur la description)

Les critères #2 (tarifs re-mesurés sur des appels 2.2.0) et #3 (system prompt comparé depuis une
tâche créée sous 2.2.0) demandent du vrai usage de Bob 2.2.0, qu'aucun agent ne peut produire.
L'utilisateur génère ce trafic lui-même AVANT que la chaîne démarre, donc l'évidence doit exister
dans ~/.bob/db/bob.db quand cette tâche est prise. La vérifier d'abord : des messages postérieurs
au 2026-09-24 et des appels avec un _meta.spend non nul.

La baseline 2.1.0 est figée à part et ne doit jamais être écrasée :
private/baseline-2.1.0/bob.db.2.1.0-snapshot (sha256 bee901ee…16be6a, chmod 444). Toute
comparaison avant/après se fait entre ce fichier et la base vivante.

Ces deux critères se prouvent maintenant par exécution ; ils ne peuvent pas être cochés sur un
raisonnement, et s'il manque du trafic 2.2.0 il faut le dire plutôt que contourner.

## Tranché par l'analyse de TASK-13.4 — 2026-09-28 (PRIME sur la description)

Entrées établies pour cette tâche (preuves dans TASK-13.4) :
- Les balises <base_rules>, <tool_use>, <engineering_discipline>, <investigate_before_answering>,
  <auto_appended_context>, <markdown_rules> ont quitté les littéraux du bundle 2.2.0 : vérifier sur un
  prompt STOCKÉ 2.2.0 si elles sont encore assemblées (dump_system_prompt.py découpe dessus).
- key_value_store : « INSERT INTO key_value_store (key, value_json) … ON CONFLICT(key) DO UPDATE ».
- Le repli « openai/gpt-oss-20b » a quitté la fonction de contrôle de sécurité ; le server flag
  command-security-model est toujours poussé (vu dans state.vscdb) — dire où le modèle est choisi.
- Les tarifs 2.1.0 se mesurent sur le snapshot private/baseline-2.1.0/bob.db.2.1.0-snapshot, les 2.2.0
  sur la base vivante après le trafic généré par l'utilisateur.

## Entrees de TASK-13.4 — 2026-09-28 : la page docs/bob-2.1.0-to-2.2.0.md fait autorite

A verifier sur la base vivante et sur un prompt stocke 2.2.0 :

1. key_value_store : sur le snapshot 2.1.0 (deja migre en 011 le 2026-09-28T19:27Z) la table contient une seule ligne, cle featureFlags.v1, 2020 caracteres de JSON : 2.2.0 cache les feature flags serveur dans la base. Dire si bob_version.py doit la lire en plus ou a la place de la cle IBM.bob-code du state store, et si les cles command-security-model et summary-model y arrivent encore (le bundle 2.2.0 ne les lit plus : getFlagValue ne connait que bob-findings-enabled, dynamic-context-enabled, feedback-model, feedback-verification-enabled, ibm-support-url, issue-repo-url, max-monthly-budget-allowance, review-flow-enabled).
2. Prompt stocke 2.2.0 : les balises de sections sont encore emises en format xml (<tag> ... </tag>) mais depuis un registre ; quatre configs (default, boreas, aquarius, orion) choisies par prefixe provider/family/version du modele ; sections supplementaires possibles task_execution, when_stuck, act_and_iterate, ground_truth, define_done, prove_done ; project_rules contient desormais des groupes imbriques workspace_rules_<mode>, workspace_rules, agents_md, global_rules_<mode>, global_rules avec des elements rule / filename / content. Verifier que dump_system_prompt.py (decoupe sur ^<tag>\n...\n</tag> et sur </environment_info>) rend la bonne liste, et noter quelle config un task de production recoit.
3. Modele de securite : plus de repli openai/gpt-oss-20b, plus de flag command-security-model lu ; la verification demande le tier security au routeur serveur (POST /chat/completions, model router, metadata model_tier security), repli premium-ide. Si le state store pousse encore command-security-model, le dire comme un flag non consomme.
4. Tarifs : rien dans le diff ne touche la tarification ; les deux taux 2.1.0 (2.0 et 0.833 Bobcoins par million) se mesurent sur private/baseline-2.1.0/bob.db.2.1.0-snapshot (68 messages avec _meta.spend), les taux 2.2.0 sur la base vivante apres trafic. Si un appel de securite ou de resume apparait avec un autre taux, il vient des tiers internes security et background.
5. Schema : CREATE TABLE de tasks, messages, attribution_logs, task_pending_approvals et INSERT INTO attribution_logs byte-identiques ; seule addition key_value_store et la migration 011. VERIFIED_SCHEMA devra dire 011_key_value_store (13.3).
6. Settings : autoCondense / autoCondenseContext / compactionThreshold sont migres en session.autoCompact et session.compactionThresholdPercent a la lecture ; chat.chatWidth et session.promptConfigPath nouveaux ; hooks par defaut avec PreCompact et PostCompact.

Notes transmises par TASK-13.1 (2026-09-28), re-verification des trois notes de reference et du template sur bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054. Ce qui reste ouvert et vous concerne :

1. Prompt layout reellement recu en production : la liste des sections depend desormais d un prompt config choisi par le modele (default, boreas, aquarius, orion, choisi par le prefixe le plus long de provider/family/version). Quel modele recoit quelle config n est pas lisible dans le bundle. A verifier sur un prompt reellement stocke par bob-code 2.2.0 (dump_system_prompt.py). Deux configs ajoutent des sections (boreas : task_execution, when_stuck ; orion : act_and_iterate, ground_truth, define_done, prove_done).
2. Rendu XML de project_rules : confirme par lecture du code (balises workspace_rules_<mode>, workspace_rules, agents_md, global_rules_<mode>, global_rules, chacune avec des elements rule/filename/content), mais jamais vu sur une sortie reelle. A confirmer sur un dump reel.
3. Facturation premium-ide / explorer (2.0 et 0.833 Bobcoins par million de tokens) : mesuree sur la base 2.1.0 uniquement (le champ messages.data._meta.spend). Rien dans le diff de code ne touche la tarification, mais les tarifs doivent etre re-mesures sur du trafic 2.2.0 reel.
4. Schema de la base sous 2.2.0 : la migration 011_key_value_store est deja appliquee et cache featureFlags.v1 (2020 caracteres JSON) ; les quatre autres tables restent byte-identiques (migrations 001 a 010). Reste a verifier si messages.data porte toujours _meta.spend par appel de la meme facon sous 2.2.0.
5. Modele de securite via routeur : le controle de commande demande desormais le tier interne security a un routeur serveur (POST vers /chat/completions, metadata.model_tier=security), repli local premium-ide si le routeur echoue. Le flag serveur command-security-model existe toujours cote etat IDE mais n est plus lu par le controle ; si le routeur repond bien avec ce meme modele reste une question de base/traffic, pas de bundle.
6. Compaction : la note injected-rules.md affirme que la compaction utilise le modele de la tache ; ce point n a pas ete re-verifie sur 2.2.0 et reste marque non verifie.
<!-- SECTION:NOTES:END -->
