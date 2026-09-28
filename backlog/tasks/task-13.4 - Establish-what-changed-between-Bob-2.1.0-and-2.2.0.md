---
id: TASK-13.4
title: Establish what changed between Bob 2.1.0 and 2.2.0
status: Done
assignee:
  - '@claude'
created_date: '2026-09-28 19:46'
updated_date: '2026-09-28 21:12'
labels:
  - 'model:primaire'
milestone: m-1
dependencies: []
parent_task_id: TASK-13
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Before anything is re-verified or relabelled, the project needs to know what actually moved between the two builds. Right now it knows only that things moved: every script warns, and a dozen anchors vanished.

The difficulty is that there is no 2.1.0 to compare against any more. The update replaced the application in place — `/Applications/IBM Bob.app` is 2.2.0, no copy of the 2.1.0 tree survives on disk, the update caches hold nothing usable, and there is no vendor changelog. So the delta has to be reconstructed from the baselines that do survive, and the task is to decide how far each one carries before trusting it.

Three baselines exist. The repository is one: the reference notes, the comparison docs and the scripts are a written record of 2.1.0, precise enough to test claim by claim against the new bundle. `~/.bob/db/bob.db` is the second and the better one, because it is untouched 2.1.0 evidence rather than a description of it — the last activity is 2026-09-19 and the update landed 2026-09-24, so all 129 stored calls were priced by 2.1.0 and all four stored system prompts were assembled by it. That makes a real before/after possible on the prompt layout and on the unit prices, but only until 2.2.0 usage starts mixing rows in, so the snapshot has to be taken before the other subtasks generate traffic. The third, optional, is retrieving the 2.1.0 build itself from the update endpoint recorded in `product.json`, which would turn the whole exercise into a diff — worth deciding on explicitly rather than by default, since it means a network fetch of a signed application.

What comes out of this is the delta itself — what changed in the prompts, the settings schema, the tool set, the approval path, the database, the hook contract — and, for each item, whether it is a real behaviour change or only a minification artefact. The distinction is the point: a vanished identifier proves nothing about behaviour, and the rest of the milestone depends on not confusing the two.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The 2.1.0 evidence in `bob.db` is snapshotted, read-only, before any 2.2.0 traffic is added to it
- [x] #2 A documented list of differences between 2.1.0 and 2.2.0 exists, covering at least the system prompt sections and guidance blocks, the settings schema and defaults, the tool set, the hook events and payloads, the approval path, and the database schema
- [x] #3 Each difference is classified as a behaviour change, a cosmetic or minification artefact, or undetermined
- [x] #4 Each difference names the evidence it rests on, and differences inferred from the absence of a minified identifier are labelled as inconclusive on their own
- [x] #5 The decision on whether to retrieve the 2.1.0 build for a direct diff is recorded with its reason, and the delta states which of its findings would change if that diff were run later
- [x] #6 Facts the 2.1.0 notes assert that the delta cannot confirm either way are listed, so the later subtasks know what to re-read rather than re-word
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# Plan validé — 2026-09-28 (analyse de conception, validée par l'utilisateur)

## Principe structurel

Un minifieur renomme variables et fonctions, mais ne peut pas toucher aux chaînes de caractères, aux
noms de propriétés (accès « .foo », clés « {foo: » ) ni aux regex sans casser le programme. Le delta
se calcule donc UNIQUEMENT sur ces jetons-là, tout identifiant étant remplacé par « _ ». Le renommage
devient invisible par construction, pas par discipline — et le diff textuel brut de 10 Mo, trompeur
par nature, n'est jamais utilisé.

## Outil (privé, non livré)

private/bundle_diff.py — Python 3.8+ stdlib, lecture seule. Trois commandes :

- extract BUNDLE OUT_DIR : tokenise (lexer maison : chaînes, templates, regex, propriétés, mots-clés),
  écrit strings/props/regexes/functions.json et l'origine (bob / vendor:<lib> / ?) de chaque fonction.
- compare DIR_A DIR_B [--top N] [--all] : ensembles de chaînes et de propriétés ; les chaînes disparues
  et apparues sont d'abord APPARIÉES par ressemblance (shingles de 5 mots puis difflib) et affichées
  comme éditions mot à mot ; le reste est retiré/ajouté, étiqueté par origine, vendor masqué par défaut.
- anchor BUNDLE_A BUNDLE_B "littéral" / anchors BUNDLE_A BUNDLE_B FICHIER : pour un fait documenté,
  extrait la fonction qui l'entoure dans chaque build (occurrences multiples appariées par ressemblance,
  jamais par ordre ; une propriété hors fonction → l'objet littéral qui l'entoure ; une chaîne hors
  fonction → comparaison de la chaîne elle-même), neutralise les identifiants, diffe jeton par jeton.
  Verdicts : IDENTICAL / SAME LOGIC (seuls des artefacts d'interop CJS→ESM) / CHANGED avec les
  éditions réelles listées / EDITED top-level string avec diff mot à mot / MISSING.

Extractions et rapports dans private/diff/ : 2.1.0/, 2.2.0/, compare-2.1.0-2.2.0.txt,
anchors.txt (68 ancres : landmarks + littéraux cités par les notes + clés de propriétés),
anchors-verdicts.txt.

## Baselines (toutes en private/, gitignoré)

- Bundle 2.1.0 : private/baseline-2.1.0/IBM-Bob-darwin-arm64-1.126.0+bob2.1.0.zip, 262 010 603 octets,
  sha256 34d299ab6661ab9aecf0bb33e18834276991bcadd877cebd2dc413c060154927, obtenu le 2026-09-28 depuis
  https://api.us-east.bob.ibm.com/update/cos-assets/ibm-bob-executables/IBM-Bob-darwin-arm64-1.126.0+bob2.1.0.zip
  (motif d'URL lu dans …/update/versions/stable/darwin/arm64/latest.json, lui-même lu dans le main.log de
  l'IDE ; le stockage S3 présigné refuse HEAD, GET fonctionne). extension.js extrait : 14 731 421 octets,
  sha1 f5ebecbd954f7c99e3666bbee1f4525ed9dcdfc3, product.json commit a8240f78e496, date 2026-08-26.
  ATTENTION : ce n'est PAS octet pour octet le build des notes (sha1 d8b1130e…, 14 731 430 octets,
  suffixe 20260827055214) — 9 octets d'écart, chemin Jenkins BOB_IDE_EXTERNAL → …_PKG_USER. Même
  version, autre run de build : plancher de bruit de la méthode, nul sur le code.
- Base bob.db 2.1.0 : private/baseline-2.1.0/bob.db.2.1.0-snapshot (voir notes ; contenu 2.1.0 dans
  un schéma déjà migré en 011).
- Changelog éditeur (source de première main, découverte via product.json releaseNotesUrl) :
  https://bob.ibm.com/docs/ide/changelog — section 2.2.0 sauvegardée en texte pendant l'analyse ; la
  reprendre pour le document public.

## Ce que l'analyse a établi

1. Les ancres disparues sont un ARTEFACT DE BUNDLING, pas un changement de comportement : 2.1.0 est du
   CommonJS (exports atteints par « module.Nom », « (0, mod.fn)(…) », wrappers __toESM/__commonJS),
   2.2.0 est de l'ESM à liaisons directes. Chiffres : __toESM 7 → 0, __commonJS 2 → 0, « .default. »
   794 → 263, __esModule 1936 → 838. Chaque ancre disparue était un jeton de propriété en 2.1.0
   (SUBAGENT_PRESETS ×3, MODEL_TIERS ×5, loadWorkspaceRules ×2, getBestCommandMatch ×4, …) et n'en est
   plus un ; les noms de MÉTHODES DE CLASSE survivent (shouldAutoApprove ×3/3, requiresSecurityApproval
   ×4/4, isBobHomeWrite ×10/10, validateToolExecution, handleUiReply, _alwaysAllowedTools).
   Règle pour les ancres durables : texte de prompt, clés de settings, messages, noms de méthodes et
   clés d'objets — jamais un nom d'export de module.
2. Les 4,1 Mo perdus sont surtout des bibliothèques retirées (PostHog, LangChain/LangGraph/LangSmith,
   parse5, tables highlight.js, jsonpatch) ; ajoutés : gRPC + export OTLP, SDK MCP v2 (SEP-2243/2352),
   e2b optionnel.

## Delta comportemental 2.1.0 → 2.2.0 (preuves dans anchors-verdicts.txt et compare-*.txt)

CHANGEMENTS DE COMPORTEMENT
- Agents personnalisés (.bob/agents/*.md) : le champ « model: » lève désormais une erreur
  (« "model" is not supported in <fichier>, use "modelTier" instead ») ; « modelTier: » est validé
  contre une liste (« Invalid modelTier … Valid values: … »). En 2.1.0, « model » était accepté et une
  valeur invalide ignorée. CONSÉQUENCE : le template livré
  skills/bob-override-rules/templates/agents/explore-premium.md (« model: premium ») casse sur 2.2.0.
- Hooks : 7 événements (SessionStart, UserPromptSubmit, PreCompact, PostCompact, PreToolUse,
  PostToolUse, Stop) ; handler « http » (url, headers, allowedEnvVars) en plus de « command » ;
  PostCompact rejoint les événements non bloquants ; une sortie stdout de PreToolUse commençant par
  « { » est parsée en JSON (updatedInput / cancel, avertissement « Ignoring invalid PreToolUse hook
  output ») ; SessionStart reçoit source startup | resume | compact ; les hooks de policy « are always
  applied in addition to » les hooks utilisateur (était « run before any »).
- Settings : autoCondense / autoCondenseContext → autoCompact, autoCondenseContextPercent →
  compactionThresholdPercent, avec table de migration dans le code ; libellé « Allow outside
  workspace tool requests ».
- Contrôle de sécurité des commandes (fonction requiresSecurityApproval, similarité 0,91) : le prompt
  du modèle ne contient plus « Command to analyze / Working directory » (la commande est passée
  autrement) ; le repli codé en dur « ?? openai/gpt-oss-20b » a quitté cette fonction. Heuristiques,
  catégories et structure de retour inchangées.
- execute_command : paramètre « background: true » (retour immédiat, pid, fichier de log) ; l'ancienne
  consigne « only runs commands that are expected to terminate » a disparu.
- Prompt système : règles de discipline étendues (« State the next action… », « Ground every
  value… », « "Done" means a real check passed… », « If repeated attempts… switch ») ; les balises
  <base_rules>, <tool_use>, <engineering_discipline>, <investigate_before_answering>,
  <auto_appended_context>, <markdown_rules> ont quitté les littéraux (enveloppe faite ailleurs — à
  vérifier sur un prompt stocké 2.2.0 pour dump_system_prompt.py, TASK-13.2) ; nouvelle intro
  available_skills ; consigne de mode « Stay in your current mode unless… » ; update_todo_list et
  ask_followup_question reformulés (une question par tour) ; nouvel outil de lecture de page HTTP.
- Base : table key_value_store, « INSERT INTO key_value_store (key, value_json) … ON CONFLICT ».
- Divers : messages de budget avec {{budget_limit}} et budget d'équipe ; policy RequiredExtensions ;
  variables OTEL_EXPORTER_OTLP_*.

IDENTIQUES (verdict IDENTICAL ou SAME LOGIC)
- Portes d'approbation shouldAutoApprove / validateToolExecution / _alwaysAllowedTools ; isBobHomeWrite ;
  objet des défauts d'approbation (approvedCommands, deniedCommands, outsideWorkspaceAllowed,
  isCommandSecurityEnabled) ; liste des commandes auto-approuvées par défaut.
- Guide sous-agents (« Default: do the work yourself »), préambule des règles (« take precedence… »),
  prompt /init (12 457 caractères identiques), règles artefact/inline, texte du modèle premium-ide,
  handleUiReply, task_pending_approvals, frontmatter maxTurns / rawPrompt / denyTools / allowForkContext,
  INSERT INTO attribution_logs.

ARTEFACTS (pas de comportement)
- Tout ce qui est classé « interop artefacts » par l'outil ; le réordonnancement des constantes de
  premier niveau ; les 9 octets de build.

INDÉTERMINÉ / À FINIR PAR L'IMPLÉMENTEUR
- Le lexer confond encore quelques tables de mots-clés highlight.js avec du code Bob (regex BOB trop
  large : \bworkflow, read_file…) et ne reconnaît pas les motifs d'interop imbriqués
  « (0, _.normalizePath)((0, _.resolvePath)… » : resserrer avant de citer des comptes.
- « make install » (prompt d'heuristiques de sécurité) : EDITED avec ratio affiché 0,00 — artefact de
  calcul sur chaîne longue ; le diff mot à mot montre une seule édition (retrait du bloc Command /
  Working directory). Le vérifier à la main.
- Précédence des règles avec le sous-dossier plugins/ annoncé par le changelog : non localisé par
  ancre (chaîne « Project Instructions (AGENTS.md) » MISSING en B) — à relocaliser en 13.1 via les
  chaînes voisines du préambule.
- Où va désormais le nom du modèle de sécurité (server flag command-security-model toujours poussé :
  « openai/gpt-oss-20b » vu dans state.vscdb) — à confirmer en 13.2.

## Étapes pour l'implémenteur de cette tâche

1. Reprendre private/diff/anchors-verdicts.txt et compare-2.1.0-2.2.0.txt ; resserrer l'étiquetage
   (points « indéterminé ») et régénérer.
2. Écrire le livrable public docs/bob-2.1.0-to-2.2.0.md (nom à aligner sur docs/ existants) :
   pour chaque différence — comportement / artefact / indéterminé — la preuve (ancre, verdict, fichier
   de rapport), le build et la source (bundle 2.1.0 téléchargé, bundle 2.2.0 installé, changelog
   éditeur, base). Aucune donnée personnelle ; ne pas citer d'offsets (ils bougent), citer des littéraux.
3. Consigner la décision « build 2.1.0 récupéré » avec son motif et ce que le diff a apporté (critère #5),
   et la liste des faits 2.1.0 non confirmables (critère #6).
4. Ne rien changer aux skills livrées : c'est 13.1 (faits/ancres/template) et 13.3 (ré-étiquetage).

## Frontières
- 13.1 : corriger le template explore-premium.md (modelTier), relocaliser la précédence des règles,
  ré-ancrer les notes, documenter le contrat de hooks 2.2.0 — les verdicts ci-dessus sont ses entrées.
- 13.2 : prompt stocké 2.2.0 (balises de sections), tarifs, key_value_store, flag de modèle de sécurité.
- 13.3 : ré-étiquetage et VERIFIED_*, après 13.1 et 13.2.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Arbitrages tranchés par l'utilisateur — 2026-09-28 (PRIME sur la description)

1. **Le build 2.1.0 est récupéré** depuis l'endpoint de mise à jour enregistré dans product.json
   (https://api.us-east.bob.ibm.com/update/versions), pour faire un vrai diff des deux bundles
   plutôt que reconstruire le delta depuis les notes. Décision de l'utilisateur, prise en
   connaissance du fetch réseau d'une application signée et de la question de terms que TASK-12
   soulève par ailleurs. Le critère #5 est donc tranché dans ce sens : consigner la décision, sa
   raison, et ce que le diff a effectivement apporté.
2. **Le delta est un livrable public**, dans docs/, dans la même veine que les docs de comparaison
   — pas dans private/ ni dans backlog/docs/. Il doit donc être écrit pour un lecteur du projet,
   énoncer le build de chaque fait comme l'exige AGENTS.md, et ne contenir aucune donnée
   personnelle issue de la base locale.

## Snapshot 2.1.0 pris avant tout travail — critère #1

Fait depuis la session d'orchestration le 2026-09-28 22:00, Bob 2.2.0 tournant, donc par
sqlite3 ".backup" via une URI mode=ro et non par copie de fichiers :

    private/baseline-2.1.0/bob.db.2.1.0-snapshot
    sha256 bee901ee943fcd707f7a9ef56b4d5a9f929a0b6a43cdaa825e064de88c16be6a
    3 018 752 octets, chmod 444, integrity_check ok
    18 tâches, 143 messages, 5 system prompts, dernier message daté 2026-09-19

Contenu antérieur à la mise à jour du 2026-09-24 : les appels stockés ont tous été tarifés par
2.1.0 et les system prompts assemblés par elle. C'est la preuve 2.1.0 du delta.

**Nuance qui limite ce snapshot, et qui n'était pas prévue dans la description** : la base a déjà
été migrée en 011_key_value_store par le premier démarrage de 2.2.0. Le snapshot porte donc un
CONTENU 2.1.0 dans un SCHÉMA 2.2.0. Le schéma 2.1.0 lui-même n'est plus récupérable par cette
voie — il faut le lire dans le SQL de migration du bundle, ou dans le bundle 2.1.0 une fois
récupéré. Ne pas présenter ce snapshot comme une preuve du schéma 2.1.0.

## Livraison TASK-13.4 — 2026-09-28 (sous-agent)

Livre : docs/bob-2.1.0-to-2.2.0.md (283 lignes), page publique, sections : baselines et leur valeur ; methode (jetons survivants, CJS vers ESM avec les comptes __toESM 7 vers 0, __commonJS 2 vers 0, .default. 794 vers 263, __esModule 1936 vers 838, regle des ancres durables) ; delta en neuf rubriques (prompt systeme, regles, sous-agents et tiers, outils, settings, approbation, hooks, base, bibliotheques et activation), chaque ligne classee comportement / artefact / indetermine avec sa preuve (litteral et verdict, edition de chaine appariee, ou entree du changelog) ; changelog editeur confronte au bundle (confirme / tu / non localise) ; decision sur le build 2.1.0 (critere 5) ; dix faits 2.1.0 non confirmables (critere 6) ; ancres a regrepper sur le prochain build.

Baselines verifiees par execution (pas recopiees) : zip 2.1.0 sha256 34d299ab... ; extension.js 2.1.0 14 731 421 octets sha1 f5ebecbd954f7c99e3666bbee1f4525ed9dcdfc3 ; Info.plist du zip CFBundleVersion 1.126.0+bob2.1.0.20260827055215 (les notes disent ...214 : run de packaging une seconde plus tard, les 9 octets sont le suffixe _PKG_USER du chemin Jenkins) ; extension.js 2.2.0 10 622 906 octets sha1 6afa9f9c6012df40e49cb863151c492e80c237f8, CFBundleVersion 1.126.0+bob2.2.0.20260924155054, product.json commit 30bf4b86..., date 2026-09-09 ; snapshot bob.db sha256 bee901ee943fcd707f7a9ef56b4d5a9f929a0b6a43cdaa825e064de88c16be6a, chmod 444, integrity_check ok, 18 taches, 143 messages, 5 system prompts, 68 messages avec _meta.spend, dernier message 1789780223615 ms = 2026-09-19T01:10Z ; ligne _migrations 011_key_value_store datee 1790623630787 ms = 2026-09-28T19:27Z, donc contenu 2.1.0 dans un schema 2.2.0 comme prevu ; key_value_store contient une ligne, cle featureFlags.v1 (2020 caracteres de JSON). Changelog editeur copie en private/baseline-2.1.0/changelog-2.2.0.txt.

Outil private/bundle_diff.py ameliore sur les trois points indetermines du plan, py_compile ok, methode inchangee : (1) regex BOB resserree (plus de read_file, write_file, workflow, subagent, apply_diff...) et detection des tables de mots-cles highlight.js (40 mots et plus separes par des espaces) avant le tag bob : chaines retirees taguees bob 834 vers 111, highlight.js 239 vers 746 ; (2) repliage des cibles d appel ( 0 , _ . nom ) en _ avant le diff, motifs imbriques compris : requiresSecurityApproval passe de 10 editions reelles a 4, toutes hors heuristiques ; (3) scopes mixtes : les wrappers de module CommonJS (plus de MAX_UNIT = 4000 jetons) ne sont plus une unite, la chaine est comparee a la chaine : make install passe de ratio 0.00 a 0.99 ; plus une preference pour la paire code-code quand sa ressemblance depasse 0.6, et un marqueur coarse au-dela de 1500 jetons.

Verdicts regeneres (private/diff/anchors-verdicts.txt, 102 ancres = 68 du plan + 34 ajoutees pour 2.2.0 ; anciens fichiers dans private/diff/prev/) : SAME top-level string 27, IDENTICAL 10, SAME LOGIC 3, CHANGED 12, EDITED 6, MISSING in B 19, MISSING in A 25. Divergences avec les verdicts cites dans le plan, toutes expliquees par les ameliorations : requiresSecurityApproval 10 vers 4 editions reelles (similarite 0.91 vers 0.98) ; make install ratio 0.00 vers 0.99 ; interop des portes d approbation 4 vers 2 ; editApprovalPreviewMode 4 vers 2 artefacts ; modelTier 27 vers 19 editions ; compactionThresholdPercent 20 vers 17 ; explorer (sans guillemets dans anchors.txt) SAME string au lieu de MISSING in both. Aucune divergence de classe.

Observations nouvelles par rapport au plan : quatre configs de prompt (default, boreas, aquarius, orion) choisies par prefixe provider/family/version du modele, sections task_execution, when_stuck, act_and_iterate, ground_truth, define_done, prove_done selon la config ; setting session.promptConfigPath ; groupes de regles rendus en XML (workspace_rules_<mode>, workspace_rules, agents_md, global_rules_<mode>, global_rules), ordre inchange, .bob puis .bob/plugins/* par ordre alphabetique ; modele de securite = tier security resolu par un routeur serveur (POST /chat/completions, model router, metadata model_tier), repli premium-ide, flags command-security-model et summary-model plus lus du tout ; outil web_fetch et groupe browser ; key_value_store cache les feature flags ; en.json 577 vers 1169 cles (Bob Shell fusionne), rien de retire ni change.

Non fait : aucun fichier de skills/, README.md ou CHANGELOG.md touche (13.1 et 13.3) ; le matcher de jetons, le preset general, le migrateur de commandes et la surface de activate() ne sont pas relus (listes au critere 6) ; aucun trafic 2.2.0 genere. Controles avant commit : grep /Users/ vide sur la page, liens relatifs existants, py_compile de bundle_diff.py ok, private/ absent de git status.

## Vérification de livraison
Assets : docs/bob-2.1.0-to-2.2.0.md (page publique) — controles executes : grep /Users/ et nom de personne vide ; cinq liens relatifs existants dans docs/ ; chaque ligne des tables du delta a une classe et une preuve ; lignes de tableau a quatre barres verticales (une barre non echappee corrigee ligne 148). private/baseline-2.1.0/bob.db.2.1.0-snapshot — sha256 bee901ee943fcd707f7a9ef56b4d5a9f929a0b6a43cdaa825e064de88c16be6a reverifie apres la tache, chmod 444 intact, integrity_check ok, comptes 18 / 143 / 5 / dernier message 2026-09-19 reexecutes. private/baseline-2.1.0/changelog-2.2.0.txt — cmp identique a la copie de session. private/bundle_diff.py — py_compile ok ; private/diff/anchors-verdicts.txt regenere et reproduit a l identique par le verificateur (diff vide, 102 ancres, 27 / 10 / 3 / 12 / 6 / 19 / 25). git status : seuls la page et trois fichiers backlog/tasks/, rien de private/.
Incidents : un bug d outillage trouve et corrige en cours de tache — apres la premiere passe d amelioration de bundle_diff.py, l appariement des occurrences preferait une chaine identique isolee a la fonction contenant l ancre (verdict de blocked by hook et maxTurns degrade en SAME top-level string) ; corrige par une preference pour la paire code-code quand sa ressemblance depasse 0.6, verdicts regeneres ensuite. Aucune interruption, aucun contournement, pas de tache rouverte.
Capitalisation : verse dans docs/bob-2.1.0-to-2.2.0.md (le delta, la methode, la regle des ancres durables, les faits non confirmables), dans les notes de TASK-13.1 et TASK-13.2 (entrees datees), dans le docstring de private/bundle_diff.py (repliage des wrappers, MAX_UNIT, regle asymetrique et sa limite) ; private/ctx.py et private/anchor_detail.py conserves (aides de lecture de contexte et de diff detaille, gitignores). Laisse deliberement : les scripts de sondage jetables du scratchpad (reconstruits en quelques lignes depuis strings.json) ; aucun changement de skills, README ou CHANGELOG (13.1 et 13.3).
Vérificateur indépendant : agent frais (general-purpose, af54f803cce6c8c8e) briefe avec les six criteres, la checklist a-i et le rapport du producteur ; il a reexecute sha256, permissions, integrity_check et comptes du snapshot, py_compile, la regeneration des 102 verdicts (diff vide), les comptes interop, et confronte deux lignes ou plus de chaque rubrique aux deux bundles. Verdict rendu : CONFORME AVEC RESERVES — six criteres satisfaits sur le fond ; huit ecarts signales : (1) e2b dit ajoute alors que present en 2.1.0, (2) variables OTEL_* dites ajoutees alors que lues en 2.1.0, (3) source de confiance presentee comme changement alors que workspace.isTrusted alimentait deja le loader en 2.1.0 et que le module trustedFolders.json y etait mort, (4) skills sous plugins/ tranchable et resserrement .bob/*/skills vers .bob/plugins/*/skills omis, (5) override BOB_USE_MODEL_ENV presente comme nouveaute, (6) 17/15 definitions de getSystemPromptPart alors que ce sont des occurrences du nom, (7) barre verticale non echappee dans une cellule, (8) 86 caracteres = longueur echappee. Les huit corrections ont ete appliquees a la page apres reverification de chacune sur les bundles (comptes e2b 3/5, OTEL_EXPORTER_OTLP_ENDPOINT 4/17, workspaceTrusted: 2/3, resolveFolderTrust jamais appele en A, chemins .bob/plugins/*/skills lus en B, getSystemPromptPart defini 11 fois dans chaque build) ; l item 9 du critere 6 et la section changelog ont ete alignes. Non verifie par le vérificateur et laisse tel quel : l execution des hooks pour les sous-agents (phrase adoucie dans la page).

## Preuves par critere d acceptation
AC #1 : commande Python sqlite3 sur file:<abs>/private/baseline-2.1.0/bob.db.2.1.0-snapshot?mode=ro&immutable=1 — pragma integrity_check = ok, tasks = 18, messages = 143, messages role system = 5, max(created_at) = 1789780223615 (2026-09-19T01:10Z) ; shasum -a 256 = bee901ee943fcd707f7a9ef56b4d5a9f929a0b6a43cdaa825e064de88c16be6a ; ls -l = -r--r--r-- 3 018 752 octets ; snapshot pris 2026-09-28 22:00 avant tout task 2.2.0 (aucun message posterieur au 2026-09-19) ; reexecute a l identique par le verificateur independant. Nuance consignee : ligne _migrations 011_key_value_store datee 2026-09-28T19:27Z, donc schema deja 2.2.0.
AC #2 : docs/bob-2.1.0-to-2.2.0.md, section The delta, rubriques 1 (prompt : sections et blocs de guidance), 5 (settings : schema et defauts), 4 (outils), 7 (hooks : evenements et payloads), 6 (approbation), 8 (base) plus 2, 3, 9 ; 55 lignes de tableau ; verdicts sources dans private/diff/anchors-verdicts.txt (102 ancres, regeneres et reproduits a l identique par le verificateur).
AC #3 : chaque ligne des neuf tableaux porte une colonne Class valant behaviour, artefact, identical ou undetermined ; controle par le verificateur (55 lignes, toutes classees) et par le comptage des barres de tableau (toutes les lignes a quatre barres).
AC #4 : chaque ligne porte une colonne Evidence nommant un litteral et son verdict, une edition de chaine appariee ou une entree du changelog ; la section Method dit que MISSING sur un nom d export est non concluant et chaque MISSING d export est annote is the export name ; verifie ligne a ligne par le verificateur (deux lignes ou plus par rubrique confrontees aux bundles, huit ecarts corriges).
AC #5 : section Why the 2.1.0 build was retrieved, and what the diff changed — decision (build recupere depuis l endpoint de product.json), raison, quatre apports du diff, et ce qui changerait avec le build exact des notes (sha1 d8b1130e..., suffixe 20260827055214) : rien dans les conclusions, bruit = un seul litteral de chemin Jenkins de 9 caracteres ; existence de la section verifiee par le verificateur.
AC #6 : section Facts the 2.1.0 notes assert that this delta neither confirms nor refutes — dix items numerotes (precedence intra-racine et agents_md, layout du prompt par config, choix du modele de securite, tarifs, flags de bob_version.py, matcher de jetons, preset general 25 tours, migration des commandes, dossier non fiable, surface de activate()), transmis par notes datees a TASK-13.1 et TASK-13.2 ; existence et contenu verifies par le verificateur.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Page publique docs/bob-2.1.0-to-2.2.0.md : baselines et leur valeur, methode insensible a la minification (CJS vers ESM, ancres durables), delta en neuf rubriques classe comportement / artefact / indetermine avec une preuve par ligne, changelog editeur confronte au bundle, decision sur le build 2.1.0 (critere 5), dix faits 2.1.0 non confirmables (critere 6). Preuves : critere 1 par execution sur private/baseline-2.1.0/bob.db.2.1.0-snapshot (sha256 bee901ee..., integrity_check ok, 18 taches, 143 messages, 5 system prompts, dernier message 2026-09-19, schema deja en 011) ; criteres 2 a 4 par la page et les 102 verdicts regeneres de private/diff/anchors-verdicts.txt avec bundle_diff.py ameliore (27 SAME string, 10 IDENTICAL, 3 SAME LOGIC, 12 CHANGED, 6 EDITED, 19 MISSING in 2.2.0, 25 MISSING in 2.1.0), toute divergence avec le plan expliquee dans les notes ; criteres 5 et 6 par les sections nommees. Controles : aucun /Users/ ni nom dans la page, liens relatifs existants, py_compile de bundle_diff.py ok. Entrees transmises par notes datees a TASK-13.1 (template explore-premium.md casse par modelTier, re-ancrage agents_md, hooks, modele de securite) et TASK-13.2 (key_value_store = featureFlags.v1, configs de prompt par modele, tier security, tarifs).
<!-- SECTION:FINAL_SUMMARY:END -->
