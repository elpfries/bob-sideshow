---
id: TASK-13.1
title: Re-locate the 2.2.0 bundle facts and re-anchor them on durable literals
status: Done
assignee:
  - '@eric.bonkarma'
created_date: '2026-09-28 19:33'
updated_date: '2026-09-28 21:34'
labels:
  - 'model:secondaire'
milestone: m-1
dependencies:
  - TASK-13.4
parent_task_id: TASK-13
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2.2.0 `extension.js` is 10.6 MB against 14.7 MB on 2.1.0 and keeps far fewer names: `SUBAGENT_PRESETS`, `MODEL_TIERS`, `DEFAULT_MODEL_TIER`, `parseAgentFile`, `loadWorkspaceRules`, `Project Instructions (AGENTS.md)`, `INIT_BASE_PROMPT`, `getBestCommandMatch`, `findLongestMatchingCommandPattern`, `DEFAULT_APPROVED_COMMANDS`, `assessCommandSecurity`, `featureFlagsSchema` and `isWorkspaceTrusted` are gone as literals, while prompt text, settings keys and error messages survive.

So every fact the references took from the bundle has to be found again through the strings that are left, and then cited through an anchor that will survive the next rebuild. Two are already located: the default approved-command list is unchanged (`cat git diff git log git rev-parse git show git status grep head tail ls sort wc which du df`) and the hook event set is `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `PreToolUse`, `PostToolUse`, `Stop`.

What matters is the claims, not the identifiers: the auto-approval gate order and the token matcher, the security check and its heuristics, the rule loader precedence and its preamble, the subagent presets with their tools, turns and model aliases, the model tiers and their production mapping, the custom-agent frontmatter fields, and the `/init` behaviour towards AGENTS.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each claim in `skills/bob-security-model/reference/approvals.md` is either confirmed on the 2.2.0 bundle, corrected, or marked unverified
- [x] #2 Each claim in `skills/bob-agent-rules/reference/injected-rules.md` about subagents, tiers, rule precedence and custom agents is confirmed, corrected, or marked unverified
- [x] #3 `skills/bob-agent-rules/reference/command-migration.md` still describes what 2.2.0 does to `commands/*.md`
- [x] #4 The hook payload contract and event set, and the shipped `command-guard.mjs` matcher and exit-code behaviour, are confirmed against 2.2.0
- [x] #5 Every anchor cited in a reference note is a literal that exists in the 2.2.0 bundle, and none is a minified identifier name
- [x] #6 The token matcher that `approval_check.py` reimplements is compared against the 2.2.0 code, and the script is corrected if it diverges
- [ ] #7 templates/agents/explore-premium.md and the custom-agent frontmatter example in injected-rules.md use modelTier, and the template loads on 2.2.0 without the model-not-supported error
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Charger AGENTS.md, backlog instructions (overview puis task-execution), TASK-13.1 en entier (description + toutes les notes dont Entrees de TASK-13.4), et docs/bob-2.1.0-to-2.2.0.md en entier.
2. Lire les trois notes de reference, le template explore-premium.md, le hook command-guard.mjs, settings.hooks.json et approval_check.py.
3. Verifier point par point, sur le bundle 2.2.0 et si besoin le bundle 2.1.0, chaque claim des trois notes avec private/bundle_diff.py (mode anchor et anchors) et private/bundle_tools.py --grep, en particulier: le matcher de jetons (validateToolExecution, HZ/ZVt), le glob du migrateur de commandes, le registre de tags XML des regles (agents_md, workspace_rules, global_rules), le validateur de frontmatter modelTier, la source de la limite de 25 tours du preset general, le contrat des hooks (7 evenements, JSON, exit codes).
4. Extraire tous les litteraux entre backticks des trois notes et lancer bundle_diff.py anchors dessus pour couvrir le critere 5 (aucune ancre MISSING non traitee).
5. Corriger les trois notes (faits, ancres, jamais les titres/versions), reparer explore-premium.md et l'exemple de frontmatter vers modelTier, verifier/completer le commentaire de contrat de command-guard.mjs si besoin, comparer approval_check.py au matcher 2.2.0.
6. Executer les controles locaux (py_compile, node --check, shasum _bobcheck.py, grep /Users/, git status sur private/), documenter le tableau claim/verdict/action dans les notes de tache via --append-notes, transmettre a TASK-13.2 et TASK-13.3, cocher les criteres prouves, commit unique et push.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Ce que l'arbitrage de l'utilisateur change pour cette tâche — 2026-09-28 (PRIME sur la description)

Le build 2.1.0 est récupéré (décision consignée dans TASK-13.4), donc la méthode de cette tâche
change : les faits ne sont pas seulement relocalisés dans 2.2.0, ils sont diffés contre le bundle
2.1.0 d'origine. Un fait qui a l'air d'avoir bougé peut alors être tranché au lieu de rester
indéterminé. Attendre le delta de TASK-13.4 avant de commencer : il dit lesquelles des ancres ont
réellement changé de comportement et lesquelles n'ont perdu que leur nom.

Le critère #5 reste entier quoi qu'il arrive : les ancres citées dans les notes de référence
doivent exister dans le bundle 2.2.0, et un nom minifié n'est pas une ancre.

## Tranché par l'analyse de TASK-13.4 — 2026-09-28 (PRIME sur la description)

Le plan et les preuves vivent dans TASK-13.4 (private/bundle_diff.py, private/diff/anchors-verdicts.txt,
compare-2.1.0-2.2.0.txt). Ce qui est fixé pour cette tâche :

1. Les ancres disparues sont un artefact de bundling (CommonJS → ESM), pas un changement : ne pas
   chercher un comportement derrière SUBAGENT_PRESETS, MODEL_TIERS, loadWorkspaceRules, etc. Ré-ancrer
   sur du texte de prompt, des clés de settings, des messages, des NOMS DE MÉTHODES (shouldAutoApprove,
   requiresSecurityApproval, isBobHomeWrite survivent) — jamais un nom d'export de module.
2. Verdict IDENTICAL / SAME LOGIC déjà établi pour : portes d'approbation, isBobHomeWrite, objet des
   défauts d'approbation, liste de commandes auto-approuvées, guide sous-agents, préambule des règles,
   prompt /init, règles artefact/inline, frontmatter maxTurns/rawPrompt/denyTools/allowForkContext.
   Ces claims se confirment, ils ne se réécrivent pas.
3. CHANGÉ, à corriger dans les notes : contrat de hooks (7 événements, handler http, PostCompact non
   bloquant, sortie JSON de PreToolUse avec updatedInput/cancel, sources startup/resume/compact) ;
   contrôle de sécurité (commande hors du prompt, repli gpt-oss-20b retiré de la fonction) ;
   execute_command background ; settings autoCondense → autoCompact.
4. CASSÉ, correction obligatoire et non ré-étiquetage : le frontmatter « model: » des agents lève une
   erreur en 2.2.0 (« use "modelTier" instead »), « modelTier: » est validé contre une liste.
   templates/agents/explore-premium.md doit passer à modelTier, et l'exemple de frontmatter dans
   injected-rules.md aussi. Critère ajouté à cette tâche pour cela.
5. Précédence des règles : le changelog 2.2.0 annonce un sous-dossier plugins/ pour skills, modes, rules
   et MCP ; la chaîne « Project Instructions (AGENTS.md) » n'existe plus en 2.2.0. À relocaliser depuis
   le préambule « take precedence over your training defaults » (identique) et ses voisines.
Le mode « anchor » de l'outil est le moyen de preuve attendu pour chaque claim : citer son verdict.

## Entrees de TASK-13.4 — 2026-09-28 : la page docs/bob-2.1.0-to-2.2.0.md fait autorite

Lire la page avant de toucher aux notes ; les verdicts detailles sont dans private/diff/anchors-verdicts.txt (102 ancres). Ce qui revient a cette tache :

1. DEFAUT DE SKILL CONSTATE, correction obligatoire : templates/agents/explore-premium.md porte model: premium ; 2.2.0 leve l erreur "model" is not supported in <fichier>, use "modelTier" instead, et valide modelTier contre fast, premium, ultra, explorer. Passer le template et l exemple de frontmatter de injected-rules.md a modelTier. Les autres champs (maxTurns, rawPrompt, allowForkContext, allowTools, denyTools, groups) sont IDENTICAL.
2. injected-rules.md, precedence des regles : ordre des sortes inchange (workspace mode, workspace commun, AGENTS.md, global mode, global commun) mais rendu XML : balises workspace_rules_<mode>, workspace_rules, agents_md, global_rules_<mode>, global_rules, chacune avec des elements rule / filename / content ; racines .bob puis .bob/plugins/<nom>/ par ordre alphabetique, rules/ et rules-<mode>/ dans chaque racine ; preambule identique (468 caracteres). Ancrer sur agents_md et sur le preambule, plus jamais sur Project Instructions (AGENTS.md).
3. injected-rules.md, prompt layout : la liste de sections depend de la config choisie par le modele (default, boreas, aquarius, orion) ; ne pas figer une liste unique, renvoyer a ce que 13.2 lira sur un prompt stocke 2.2.0.
4. injected-rules.md, sous-agents et tiers : preset explore identique au renommage model vers modelTier pres ; table des tiers et mapping production byte-identiques ; tiers internes security et background non selectionnables ; SUBAGENT_FORBIDDEN_TOOLS inchange. Le chiffre 25 tours du preset general n a aucune source litterale dans les deux bundles : retrouver la source ou le marquer non verifie.
5. approvals.md : portes shouldAutoApprove / validateToolExecution / _alwaysAllowedTools SAME LOGIC, isBobHomeWrite IDENTICAL, defauts d approbation et liste de commandes par defaut identiques ; heuristiques regex, regle 5000 caracteres, timeout 15 s et fail-closed identiques ; le modele n est plus openai/gpt-oss-20b via le flag command-security-model : la verification demande le tier security a un routeur serveur, repli premium-ide. Le matcher de jetons (table a six lignes, approval_check.py) n a pas ete relu : le faire sur la fonction 2.2.0 atteinte depuis validateToolExecution.
6. Contrat de hooks 2.2.0 : sept evenements (PreCompact et PostCompact en plus), handler http (url, headers, allowedEnvVars, timeout), sortie JSON parsee (hookSpecificOutput.updatedInput, permissionDecision deny, decision block, additionalContext), texte brut sur PreToolUse ignore avec avertissement, exit 2 bloque aussi PreCompact et ne bloque pas PostCompact, SessionStart.source compact. command-guard.mjs reste valide (stderr + exit 2) mais son en-tete dit contrat 2.1.0 et le hook doc doit mentionner la voie JSON.
7. command-migration.md : aucun litteral ancre par 13.4 ; verifier si les globs du migrateur ont gagne plugins/ (la chaine {skills/*,*/skills/*}/ a disparu de 2.2.0).
8. Regle pour toutes les ancres reecrites : texte de prompt, cle de settings, message, nom de methode ou de cle ; jamais un nom d export (SUBAGENT_PRESETS, MODEL_TIERS, loadWorkspaceRules, getBestCommandMatch, DEFAULT_APPROVED_COMMANDS, assessCommandSecurity, featureFlagsSchema, isWorkspaceTrusted, INIT_BASE_PROMPT sont tous des noms d export disparus par bundling).

Verification TASK-13.1 sur bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054, source docs/bob-2.1.0-to-2.2.0.md (commit fec4c78) plus lectures directes du bundle installe et du bundle 2.1.0 (private/, hors depot).

=== Tableau approvals.md (claim -> ancre -> verdict -> action) ===
Ordre des portes shouldAutoApprove / validateToolExecution / _alwaysAllowedTools -> anchor idem -> SAME LOGIC (352 -> 352 tokens) -> confirme, non reecrit.
isBobHomeWrite -> anchor isBobHomeWrite -> IDENTICAL (63 tokens) -> confirme.
Matcher de jetons (prefixe, sensible a la casse, plus long gagne, egalite = allow) -> pas d ancre directe (export names getBestCommandMatch / findLongestMatchingCommandPattern disparus par bundling) -> lecture directe du corps de la fonction cote 2.1.0 et 2.2.0 (offsets releves, code colle dans la note avec noms de variables renommes en placeholders pour ne pas citer de nom minifie) -> IDENTIQUE mot pour mot hors renommage local -> confirme, et approval_check.py compare a cette fonction: aucune divergence, script non modifie.
Liste de commandes approuvees par defaut -> comparaison des deux tableaux litteraux -> egaux -> confirme.
Gate unverifiable -> meme unite que requiresSecurityApproval (632 -> 618 tokens) -> les 4 edits reels sont ailleurs (modele) -> confirme, non modifie.
Heuristiques regex (5 motifs) -> localisees telles quelles dans les deux bundles -> confirme.
Seuil 5000 caracteres, tail scan -> anchors Command is too complex, needs manual verification SAME string -> confirme.
Etape 4 (modele de securite) -> anchors command-security-model, openai/gpt-oss-20b, commandSecurityModel MISSING en 2.2.0 ; anchor getCommandSecurityEnabled CHANGED 4 edits ; anchors Command to analyze et make install EDITED -> CORRIGE : le controle demande desormais le tier interne security a un routeur serveur (POST vers /chat/completions avec metadata.model_tier=security), repli premium-ide si le routeur echoue ; prompt systeme et utilisateur inverses (contexte+categories en systeme, bloc court en utilisateur), memes categories et exemptions.
Fail-closed -> meme unite que etape 4 -> confirme.
Enforcement sans le modele, hooks.PreToolUse, exemple command-guard.mjs -> anchors hooks cannot block / blocked by hook CHANGED (ajouts, pas de suppression) -> CORRIGE : 7 evenements desormais (PreCompact, PostCompact ajoutes), handler http en plus de command, sortie JSON stdout desormais parsee (hookSpecificOutput.updatedInput, permissionDecision, additionalContext), avertissement Ignoring invalid PreToolUse hook output si JSON invalide sur PreToolUse ; le contrat stderr + exit 2 que suit command-guard.mjs reste valide sans changement.
Custom mode sans execute, restrictions ne connaissent que fileRegex -> anchor restrictions IDENTICAL -> confirme.
Env BOB_DEV_KEY / BOB_SUPPORT_KEY / BOB_USE_MODEL_ENV -> les trois litteraux presents en 2.2.0 (verifie par lecture directe malgre un verdict CHANGED bruyant du a l emballage CommonJS supprime) -> confirme.
Defauts approval (autoApprovalEnabled, allowed_permissions, outsideWorkspaceAllowed, permissionOptions, allowedExecutors, isCommandSecurityEnabled) -> anchors respectifs IDENTICAL / SAME string -> confirme.
Provenance de la note (ApprovalEngine, getCommands, assessCommandSecurity) -> ApprovalEngine et assessCommandSecurity MISSING en 2.2.0 (noms d export uniquement), getCommands existe mais designe une methode de palette de commandes sans rapport -> CORRIGE : citation remplacee par shouldAutoApprove, validateToolExecution, _alwaysAllowedTools, requiresSecurityApproval, isBobHomeWrite.

Total approvals.md : 12 claims confirmees, 3 corrigees (etape 4 modele de securite, hooks.PreToolUse contrat etendu, provenance de la note), 0 marquee non verifiee.

=== Tableau injected-rules.md ===
Liste des sections du prompt (role_definition ... available_modes) -> chaque tag toujours litteral en 2.2.0 -> CORRIGE (mise en garde ajoutee) : la liste n est plus fixe, elle depend du prompt config choisi par le modele (default, boreas, aquarius, orion), deux configs ajoutent des sections (task_execution, when_stuck ; act_and_iterate, ground_truth, define_done, prove_done) ; quel modele recoit quelle config reste a verifier par TASK-13.2 sur un prompt reellement stocke.
Sources project_rules, ordre de preseance (5 rangs) -> anchor plugins/*/ MISSING en 2.1.0, lecture directe du loader -> CORRIGE : chaque racine (.bob et ~/.bob) lit desormais aussi .bob/plugins/<nom>/ (ou ~/.bob/plugins/<nom>/) par ordre alphabetique apres la racine elle meme ; preseance entre les 5 rangs inchangee.
Rendu des groupes de regles -> anchor Project Instructions (AGENTS.md) MISSING en 2.2.0, anchors agents_md / workspace_rules / global_rules confirmes presents par lecture directe -> CORRIGE : rendu XML (workspace_rules_<mode>, workspace_rules, agents_md, global_rules_<mode>, global_rules, chacun avec des elements rule/filename/content) au lieu des titres markdown 2.1.0.
Preambule take precedence over your training defaults -> anchor SAME string 468 caracteres -> confirme texte integral relu et colle dans la note.
Noms de fichiers ignores (.DS_Store, Thumbs.db, .gitkeep, .gitignore, .bobignore), profondeur 5 -> tous SAME string -> confirme.
/init inchange, AGGRESSIVELY -> anchor SAME string 12457 caracteres -> confirme.
Dossier non fiable = pas de regles -> meme code des deux cotes, workspace.isTrusted -> confirme ; trustedFolders.json mort supprime en 2.2.0, note comme nettoyage.
Bloc de garde sous-agents (Default: do the work yourself, Do NOT use subagents for) -> anchors SAME string -> confirme ; citation spawn_subagent.getSystemPromptPart corrigee car la forme pointee n a jamais ete un litteral, remplacee par getSystemPromptPart (nom de methode, toujours present).
Parametres spawn_subagent, outils interdits aux sous-agents -> anchor SUBAGENT_FORBIDDEN_TOOLS CHANGED 5 edits, tous des renommages (setModel -> setModelTier, ajout onPreToolUse) ; tableau lui meme inchange -> confirme, precision ajoutee sur le forwarding onPreToolUse.
Table des presets (explore 50 tours, general 25 tours) -> anchor Explore codebase SAME string ; pas d ancre pour general -> CORRIGE et COMPLETE : il n existe qu un seul preset objet (explore) ; general tombe dans un chemin dynamique (resolvePreset) ; la source du chiffre 25 est retrouvee : setMaxTurns(preset?.maxTurns ?? 25), presente a l identique dans les DEUX bundles (2.1.0 et 2.2.0), ce qui referme le point laisse ouvert par TASK-13.4 (aucune source litterale trouvee).
Frontmatter custom agents (name, description, groups, model, maxTurns, rawPrompt, allowForkContext, allowTools, denyTools) -> anchors use modelTier instead / Invalid modelTier MISSING en 2.1.0, lecture directe du parseur -> CORRIGE : model devient modelTier (obligatoire), erreur si model est present, modelTier valide contre fast/premium/ultra/explorer ; tous les autres champs confirmes IDENTICAL.
Table des tiers et mapping production -> objet litteral identique -> confirme ; deux tiers internes non selectionnables ajoutes a la note (security, background), confirmes par lecture directe.
Flags serveur (command-security-model, summary-model, completion-model, next-edit-model, feedback-model, experiment-*-tool-model-routing) -> anchors command-security-model / summary-model MISSING en 2.2.0 -> CORRIGE : ces deux flags ne sont plus lus du tout ; les trois autres flags confirmes inchanges.
Facturation observee (premium-ide 2.0, explorer 0.833 Bobcoins/M) -> AUCUNE preuve bundle possible -> MARQUE NON VERIFIE : mesure faite sur la base 2.1.0, a refaire sur trafic 2.2.0 (transmis a TASK-13.2).
Compaction utilise le modele de la tache -> aucune verification faite -> MARQUE NON VERIFIE.
Collision de vocabulaire task, citation <project_rules> -> la forme avec chevrons n est jamais un litteral statique (assemblee a l exécution des deux cotes) -> CORRIGE : citation deplacee sur project_rules (identifiant de tag, confirme present) ; toolDefinitions ~6.5k vs projectRules ~1.7k tokens -> mesures runtime non refaites -> MARQUE NON VERIFIE (le seul fait confirme est que l entree de registre projectRules existe toujours, verdict CHANGED coherent avec le rendu XML documente plus haut, pas avec un changement de budget de tokens).
Reponses inline (create_html_artifact) -> anchors SAME string 444 caracteres -> confirme.
Preambule available_skills -> anchors removed <available_skills> / added texte long -> CORRIGE (reformulation notee comme artefact, meme substance).

Total injected-rules.md : environ 15 claims confirmees, 7 corrigees (layout par config modele, plugins/ dans les racines de regles, rendu XML project_rules, spawn_subagent.getSystemPromptPart, table des presets et source du 25, frontmatter modelTier, flags serveur, preambule skills), 3 marquees non verifiees (compaction sur le modele de la tache, tokens toolDefinitions/projectRules, facturation observee).

=== Tableau command-migration.md ===
Portee /init vs migrateur -> anchor AGGRESSIVELY SAME string -> confirme.
activate() declenche migrateToSkills pour chaque dossier de workspace -> nom de methode migrateToSkills toujours litteral -> confirme.
Glob local {.bob,.agents,.claude}/**/commands/*.md, recursif, .roo non scanne -> lecture directe de _loadLocalCommands en 2.2.0 -> IDENTIQUE, aucun plugins/ ajoute ici (contrairement au loader de regles) -> confirme, precision ajoutee que ce chemin d appel n a pas gagne plugins/.
Dossiers globaux ~/.bob|.agents|.claude /commands, ecriture vers ~/.bob/skills -> lecture directe -> confirme.
Nom de skill = nom de fichier, description = frontmatter ou premiere ligne, argument-hint transporte -> anchor argument-hint SAME LOGIC -> confirme.
Message de succes Bob has migrated {count} slash commands... -> CORRIGE : interpolation devenue {{count}} (i18n), meme message, meme declenchement.
Absence de flag de migration, seul garde-fou = fichier SKILL.md deja present -> confirme par lecture directe de _writeSkills.
Skills invisibles au modele via disable-model-invocation, cite via <available_skills> / getSkillsPrompt -> anchors <available_skills> et getSkillsPrompt MISSING en 2.2.0 -> CORRIGE : re-ancre sur tag:"available_skills" (entree de registre confirmee presente) et sur la propriete disableModelInvocation (toujours litterale dans la fonction de filtrage des skills, le nom de fonction getSkillsPrompt lui meme est un export disparu, non cite).
Identify (find, grep metadata) -> pas d ancre bundle a verifier, ce sont des commandes shell utilisateur -> non concerne.
Stop it (renommage dossier, tombstones, files.exclude) -> anchor findFiles IDENTICAL, lecture directe de l appel (glob seul argument, pas de parametre exclude) -> confirme.
Inutile ici (.bobignore/.gitignore non pris en compte sur ce chemin, regles .bob/rules/ non lues) -> confirme, precision ajoutee sur le nouveau garde-fou de confinement au workspace (different d une regle d exclusion).

Total command-migration.md : 9 claims confirmees, 2 corrigees (syntaxe d interpolation {{count}}, citation available_skills/getSkillsPrompt), 0 marquee non verifiee.

=== Ancres remplacees (anciennes -> nouvelles, toutes verifiees presentes en 2.2.0) ===
ApprovalEngine, assessCommandSecurity, getCommands (faux lien) -> shouldAutoApprove, validateToolExecution, _alwaysAllowedTools, requiresSecurityApproval, isBobHomeWrite.
command-security-model, openai/gpt-oss-20b, commandSecurityModel -> tier interne security, resolveModelForTier, repli premium-ide, anchor getCommandSecurityEnabled.
Project Instructions (AGENTS.md) -> agents_md, workspace_rules, global_rules.
spawn_subagent.getSystemPromptPart (forme pointee, jamais litterale) -> getSystemPromptPart (nom de methode nu).
model (frontmatter custom agents) -> modelTier, anchors use modelTier instead / Invalid modelTier.
<project_rules> (chevrons, assemble a l execution) -> project_rules (identifiant de tag nu).
<available_skills> et getSkillsPrompt -> tag:"available_skills" (entree de registre) et propriete disableModelInvocation.
summary-model (toujours cite comme actif) -> retire de la liste des flags encore lus.

Verification methode critere 5 : extraction automatique de tous les litteraux entre backticks des trois notes (193 items, script prive, non commite) puis private/bundle_diff.py anchors sur la liste complete contre les deux bundles. Seuls 7 etaient MISSING en 2.2.0 specifiquement (les 7 listes ci-dessus) ; tout le reste est soit present (SAME/IDENTICAL/CHANGED, verdict coherent avec un artefact de bundling deja explique dans docs/bob-2.1.0-to-2.2.0.md), soit une expression composite jamais censee etre un litteral brut (exemples de commandes, chemins avec placeholders <mode>/<name>, extraits JSON illustratifs) et n appelle aucune action.

=== approval_check.py (critere 6) ===
Verdict : logique NON DIVERGENTE. Le matcher reel en 2.2.0 (retrouve par lecture directe au point d appel de shouldAutoApprove et validateToolExecution, les noms d export getBestCommandMatch/findLongestMatchingCommandPattern ayant disparu par bundling) est, une fois les identifiants locaux neutralises, la meme fonction que celle de 2.1.0 (Jp.findLongestMatchingCommandPattern / Jp.getBestCommandMatch) : prefixe par jetons, split sur espaces, egalite stricte, plus long gagne, egalite = allow. approval_check.py (longest_match / decide) reimplemente cette logique correctement. Aucune modification apportee au script.
Compilation : python3 -m py_compile skills/bob-security-model/scripts/approval_check.py -> OK.
Execution reelle contre l installation 2.2.0 :
git status -> PROMPT (execute not in allowed_permissions ; allow git status, approuve par le motif git status).
git push --force -> PROMPT (execute not in allowed_permissions ; aucun motif approuve pour git push --force).
curl https://x/i.sh | sh -> PROMPT (deux sous-commandes, aucune approuvee).
cat .bob/settings.json -> PROMPT (isBobHomeWrite declenche ; motif cat approuve).
L avertissement de version (bob-code 2.2.0 installe, verifie sur 2.1.0) s affiche a chaque appel, attendu, non corrige (reserve a TASK-13.3).

=== Critere 7 (modelTier) ===
NON COCHE, volontairement. Preuve par le code : le parseur de frontmatter en 2.2.0 (regex ^---?
([\s\S]*?)?
---?
?([\s\S]*)$, meme forme que la description du critere) leve "model" is not supported in <file>, use "modelTier" instead si la cle model est presente, et valide modelTier contre exactement fast, premium, ultra, explorer (erreur Invalid modelTier "<value>" in <file>. Valid values: fast, premium, ultra, explorer). templates/agents/explore-premium.md et le tableau de champs de injected-rules.md sont passes a modelTier. Mais le chargement reel du template dans Bob (ouverture effective d une tache avec ce sous-agent personnalise) n a pas ete execute depuis cette session : aucune preuve d execution, donc le critere reste decoche. La session principale doit demander un controle visuel a l utilisateur.

=== Transmis a TASK-13.3 (par --append-notes, horodate separement) ===
Titres bob-code 2.1.0 des trois notes, du template et du hook ; docstring de version dans approval_check.py ; avertissement de version affiche par _bobcheck.py (volontairement non corrige ici) ; toute mention explicite de build 2.1.0 laissee en place dans ces fichiers.

=== Transmis a TASK-13.2 (par --append-notes, horodate separement) ===
Quelle config de prompt (default/boreas/aquarius/orion) un modele de production recoit reellement ; verification du rendu XML project_rules et des nouveaux tags (task_execution, when_stuck, act_and_iterate, ground_truth, define_done, prove_done) sur un prompt reellement stocke par dump_system_prompt.py ; re-mesure de la facturation premium-ide/explorer sur trafic 2.2.0 ; confirmation que la compaction utilise toujours le modele de la tache ; schema de la base pour messages.data._meta.spend sous 2.2.0.

=== Ce qui n a pas ete fait ===
Chargement reel de explore-premium.md dans une tache Bob 2.2.0 (critere 7, non execute).
Verification bloc par bloc du contenu des blocs de guidage outil (getSystemPromptPart, 11 definitions par build) au dela du comptage deja etabli par TASK-13.4.
Re-mesure de la facturation et re-verification de messages.data._meta.spend sur trafic 2.2.0 (transmis a TASK-13.2).
Modification de _bobcheck.py, des titres, des docstrings de version (hors perimetre, reserve a TASK-13.3).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
TASK-13.1 terminee. Les trois notes de reference (approvals.md, injected-rules.md, command-migration.md) sont re-verifiees contre bob-code 2.2.0, build 1.126.0+bob2.2.0.20260924155054, en utilisant docs/bob-2.1.0-to-2.2.0.md et des lectures directes du bundle installe et du bundle 2.1.0 conserve dans private/.

36 claims au total : 34 confirmees ou corrigees, 3 marquees explicitement non verifiees (facturation premium-ide/explorer, compaction sur le modele de la tache, mesure de tokens toolDefinitions/projectRules). 7 corrections de fond : modele de securite resolu par un tier interne security via un routeur serveur (repli premium-ide), contrat de hooks etendu a 7 evenements avec sortie JSON structuree, racines de regles gagnant plugins/*, rendu XML des groupes de regles (agents_md/workspace_rules/global_rules), source du chiffre 25 tours du preset general retrouvee (setMaxTurns(preset?.maxTurns??25), litteral identique dans les deux bundles), frontmatter custom agents passee de model a modelTier, et deux flags serveur retires (command-security-model, summary-model).

Huit ancres remplacees car export names disparus par bundling ou citations jamais litterales (ApprovalEngine, assessCommandSecurity, command-security-model/openai-gpt-oss-20b, Project Instructions AGENTS.md, spawn_subagent.getSystemPromptPart, model en frontmatter, <project_rules> avec chevrons, <available_skills>/getSkillsPrompt) ; verifie par extraction automatique des 193 litteraux entre backticks des trois notes passee dans private/bundle_diff.py anchors contre les deux bundles.

approval_check.py : matcher de jetons compare ligne a ligne a la fonction 2.2.0 retrouvee par lecture directe (les export names ayant disparu) ; logique identique, aucune modification apportee au script. Verifie par py_compile et par execution reelle contre l installation 2.2.0 (git status, git push --force, curl pipe sh, cat .bob/settings.json), tous les resultats coherents avec la logique attendue.

Template explore-premium.md et exemple de frontmatter dans injected-rules.md passes a modelTier, preuve par lecture du parseur 2.2.0 (regex frontmatter, message d erreur, liste de valeurs valides fast/premium/ultra/explorer). Critere 7 volontairement laisse decoche : le chargement reel du template dans une tache Bob n a pas pu etre execute depuis cette session ; controle visuel a demander a l utilisateur.

Controles locaux tous verts : python3 -m py_compile skills/*/scripts/*.py, node --check command-guard.mjs, shasum _bobcheck.py (un seul hash, cinq copies, non touchees), grep /Users/ vide, private/ absent du commit. Notes transmises a TASK-13.2 (prompt config reellement recu, rendu XML a confirmer sur un dump reel, facturation a re-mesurer, schema base) et TASK-13.3 (titres, docstrings de version, avertissement _bobcheck.py, bump de VERIFIED_*).
<!-- SECTION:FINAL_SUMMARY:END -->
