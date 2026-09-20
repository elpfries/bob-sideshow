---
name: analyze-task
description: Analyser la conception d'une tâche Backlog.md avant que quiconque l'implémente — charger tout son contexte backlog, cartographier les points d'extension du code existant, faire surveiller des implémentations de référence par des agents en arrière-plan, synthétiser une solution structurée, la faire valider par l'utilisateur, puis consigner le plan dans la tâche et mettre à jour chaque tâche voisine que l'analyse tranche. Utiliser sur « analyse la tâche N », « analyser TASK-N pour proposer une solution », « propose une solution élégante », « analyse de conception », « design analysis », ou quand une tâche difficile ou un arbitrage ouvert (« à trancher », « révisable ») doit être réglé avant l'implémentation. Écrit des plans/notes backlog et commite, mais seulement APRÈS validation par l'utilisateur — l'unique exception étant une chaîne de milestones dont les implémentations de référence convergent sur un design. N'implémente jamais, et le statut de la tâche ne change pas.
---

# Analyser la conception d'une tâche avant l'implémentation

Adapté d'un projet voisin, où la procédure a été établie sur plusieurs analyses
de conception ayant chacune produit un plan d'implémentation validé et consigné
dans la tâche, sans écrire une ligne de code de production.

**À quoi sert cette skill.** Aux tâches dont la *conception* est la partie
chère : descriptions nommant des questions ouvertes, décisions marquées
*révisable*, notes disant « à trancher à l'implémentation », ou deux stratégies
plausibles avec des rayons de blast différents. (Si le projet utilise des
labels `model:<tier>`, les tâches au tier le plus élevé sont les candidates
naturelles.) Le livrable est un plan assez bon pour que la session qui
implémente (souvent un sous-agent sur un modèle moins cher) n'ait jamais à
re-dériver la conception — et ne puisse jamais la rétrécir en silence.

**Ce qu'elle ne fait jamais.** Pas d'implémentation, pas de changement de
statut (la tâche reste To Do — une analyse n'est pas un démarrage), pas
d'écriture d'aucune sorte avant que l'utilisateur ait validé la proposition,
pas de chiffres inventés.

**Note runtime.** Pas de variante « Auto » ici : les deux runtimes de travail
sont Claude Code et Kimi Code. Sous **Claude Code**, les sous-agents se lancent
avec l'outil `Task` et le modèle se choisit par son paramètre `model`. Sous
**Kimi Code**, les sous-agents se lancent avec l'outil **`Agent`** (en
arrière-plan pour les recherches de la phase 2, suivis par `TaskList` /
`TaskOutput`), et le modèle se choisit par le paramètre `model` de l'appel ou,
à défaut, par la section `[secondary_model]` de `config.toml` — un agent lancé
sans choix explicite hérite du défaut de son profil, et rien dans sa sortie ne
le dit. Dans les deux cas, les agents de *recherche* de la phase 2 tournent sur
le petit modèle : la recherche est de la récupération, pas de la conception.

## Phase 1 — Charger le contexte backlog

1. `backlog instructions overview`, puis trouver la tâche si l'utilisateur l'a
   nommée approximativement (`backlog search`, `backlog task list --plain`).
2. `backlog task view TASK-N --plain` — lire **les notes d'abord** : les
   tâches antérieures y déposent les points d'extension exacts, les noms de
   fichiers, et parfois des corrections de la description.
3. Lire ce que la tâche référence : sa milestone, les décisions et documents
   qu'elle pointe (`backlog/decisions/`, `backlog/docs/`), et les **notes de
   ses dépendances** — ce qu'elles ont réellement livré, qui est rarement
   exactement ce qu'elles promettaient.
4. Une commande `backlog …` simple par appel — jamais de boucle, de pipe ni de
   `&&` autour (le mécanisme de permission évalue la commande composée
   entière).

## Phase 2 — Lancer la recherche de références D'ABORD (arrière-plan)

Lancer la recherche **avant** de lire le code : les agents prennent 10–20
minutes et tournent pendant que vous travaillez. Un agent généraliste en
arrière-plan par sujet ; deux tâches indépendantes peuvent faire tourner deux
agents en parallèle (sous Kimi Code : deux appels `Agent` en arrière-plan ; pas
besoin d'`AgentSwarm`).

**Ce dépôt n'a pas de roster de projets de référence.** Avant de briefer un
agent de recherche, **demander à l'utilisateur quels projets, dépôts ou
documentations il considère comme références** pour le problème analysé — et
consigner dans les notes de la tâche ce que chacun s'est révélé valoir, pour
que la prochaine analyse n'ait pas à redemander. À défaut de réponse, l'agent
cherche par mots-clés et on juge les sources trouvées à leur mérite (dépôts
officiels et documentation de première main d'abord).

La qualité du prompt décide de la qualité du rapport. Tout prompt doit porter :

- **Le problème énoncé concrètement**, dans le vocabulaire que les
  implémenteurs utilisent. Les agents trouvent du code en cherchant ces
  phrases exactes.
- **Nos contraintes**, pour que les trouvailles se mappent au lieu de flotter.
  Pour ce dépôt : scripts Python 3.8+ stdlib, read-only, offline ; skills
  nommées selon la règle d'`AGENTS.md` ; tout fait reverse-engineered énoncé
  avec le build et la source dont il provient ; aucune donnée personnelle dans
  les exemples.
- **Les projets à examiner, par nom, avec pourquoi** — ceux que l'utilisateur
  a indiqués, plus les sources officielles pertinentes (la documentation d'un
  produit analysé prime sur les suppositions de tout projet tiers).
- **Des mots-clés de recherche concrets** et la demande de **chemins de
  fichiers, noms de classes, courts extraits**, via raw.githubusercontent.com
  pour GitHub.

⚠️ **Lancer chaque agent de recherche explicitement sur le petit modèle** —
paramètre `model` sous Claude Code, modèle secondaire ou paramètre `model` de
l'outil `Agent` sous Kimi Code — quel que soit le modèle de la session. Une
recherche lit des dépôts tiers et de la documentation ; c'est de la
récupération, pas de la conception, et c'est le travail le moins cher qu'un
agent fasse. Le tier élevé qualifie la *conception* de la tâche que la
recherche alimente, jamais la lecture qui l'alimente. Un agent sans modèle
explicite hérite du défaut silencieusement ; rien dans la sortie ne le dit, et
la facture arrive en fin de milestone — erreur coûteuse constatée sur un
projet voisin (deux agents de recherche héritant du gros modèle ont fait d'une
phase de recherche 40 % du coût total de la tâche), ne pas la répéter ici.

- La demande de clôture : **une synthèse des 2–3 designs récurrents avec leurs
  compromis**, et « ton message final est le rapport lui-même — contenu brut,
  pas de préambule ».

Deux sortes de preuves valent d'être demandées explicitement, toutes deux
décisives :

- **L'historique des bugs** : un commit de correctif prouvant qu'une stratégie
  échoue vaut plus que n'importe quel argument.
- **La documentation du fournisseur** : pour tout ce qui touche un produit
  analysé par ce dépôt, la documentation officielle et le code livré arbitrent.
  Un design doit atterrir de leur côté, et une convergence entre projets tiers
  qui les contredit n'est pas utilisable.

## Phase 3 — Cartographier le code pendant que les agents tournent

1. Localiser les fichiers exacts que la tâche nomme et les lire en entier : le
   point d'extension, les invariants des commentaires, ce que les modules
   voisins supposent.
2. Construire **l'inventaire factuel dont l'arbitrage a besoin** — exhaustif,
   à coups de grep. Un arbitrage plaidé sans l'inventaire est une opinion.
3. Collecter les contraintes que toute solution doit respecter, avec
   `fichier:ligne` — les règles d'`AGENTS.md`, les conventions des skills
   existantes, les formats déjà livrés. **Les pièges vivent là où deux
   contraintes se rencontrent.**
4. Collecter les rapports (sous Kimi Code : `TaskOutput`, bloquant ; sous
   Claude Code : la notification de fin de tâche d'arrière-plan). Les lire avec
   esprit critique : les agents rapportent ce qui existe, pas ce qui convient —
   mapper sur cette codebase est le travail de cette session, pas le leur.

## Phase 4 — Synthétiser et présenter. Puis S'ARRÊTER.

Structurer la proposition pour que l'utilisateur puisse la valider en une
lecture :

1. **Ce que disent les références** — par projet, mécanisme et verdict, en
   gardant les preuves nommées (commits, sections de documentation, TODOs).
2. **Un principe structurel** énoncé d'abord — la phrase qui rend la solution
   sûre *par construction*, pas par discipline. S'il n'y a pas une telle
   phrase, le design n'est pas fini.
3. **Les étapes mappées sur des fichiers réels** (chemins cliquables), en
   réutilisant les motifs déjà dans la codebase plutôt qu'en inventant des
   parallèles. Quand l'analyse *dévie* d'une hypothèse des notes de la tâche
   ou d'un document de décision, le dire et dire pourquoi.
4. **Les pièges, chacun avec le contrôle qui le verrouillera** — et les
   critères d'acceptation vérifiés un à un contre les étapes. Nommer les
   critères qu'un contrôle local tranche hors ligne et ceux qui demandent une
   exécution contre une vraie installation.
5. **Les frontières** : ce qui appartient aux tâches voisines, nommées.

Présenter cela à l'utilisateur **et terminer le tour.** L'analyse est le
livrable ; la consigner est un acte séparé, validé. Si l'utilisateur amende,
plier l'amendement dedans — son arbitrage est final.

**Une exception, et seulement quand l'analyse a été lancée par une chaîne de
milestones** (`run-milestone` phase 3, où s'arrêter arrête toute la chaîne) :
quand les implémentations de référence trouvées sont **représentatives du
problème analysé** — elles résolvent ce problème, pas un voisin — et qu'elles
**convergent sur le même design**, consigner le plan et laisser la chaîne
continuer sans attendre. Rapporter le consensus, les projets et commits qui le
portent, et le fait que le plan est entré non validé. Une lignée partagée entre
deux projets fait un point de donnée, pas deux ; une convergence que la
documentation du fournisseur contredit n'est pas utilisable ; un design que
cette architecture ne peut pas porter n'a pas convergé sur notre problème.
L'exception ne couvre que le *design* — jamais une question de périmètre.
Invoquée directement par l'utilisateur, cette skill s'arrête toujours : il a
demandé une proposition à lire.

## Phase 5 — Consigner après validation, et mettre à jour les tâches tranchées

Seulement après validation explicite de l'utilisateur — ou, dans une chaîne de
milestones, sous l'exception de consensus de la phase 4 :

1. **Écrire le plan dans un fichier temporaire**, en français, autoportant :
   la solution validée, ses justifications (projets, commits, documentation),
   l'inventaire, les pièges avec leurs contrôles, les frontières hors
   périmètre. Le futur implémenteur ne doit avoir besoin de rien de cette
   conversation.
2. **Le pousser hors du shell** : un petit script Python appelant
   `subprocess.run(["backlog", "task", "edit", "N", "--plan", plan],
   shell=False)` — le contenu voyage comme un seul élément d'argv, donc
   accents, backticks et `$` ne rencontrent jamais de shell. Toutes les
   écritures backlog passent par le CLI : ne jamais éditer un markdown
   `backlog/` directement, quelle que soit la taille du changement.
3. **Mettre à jour chaque tâche voisine que l'analyse tranche — étape
   obligatoire.** Demander explicitement : *quelle autre tâche cette analyse
   vient-elle de fixer, dans ses critères d'acceptation ou sa conception ?*
   Chacune reçoit une note datée via `--append-notes` (JAMAIS `--notes` — ça
   efface l'historique accumulé) disant ce qui est tranché, où vit le plan qui
   fait autorité, et que la note prime sur tout document périmé. **Le futur
   implémenteur ne lit que sa propre tâche** — souvent une autre session, un
   autre modèle ; un plan dans une tâche voisine n'existe pas pour lui.
4. **Vérifier avant de commiter** : `backlog task view --plain` relit le plan ;
   `git diff --stat` confirme que seuls les fichiers de tâches voulus ont
   bougé ; une note ajoutée doit se situer *après* l'historique existant, rien
   d'effacé.
5. **Un commit** (message en français, comme le reste de l'historique de ce
   dépôt, disant ce qui a été tranché et sur quelle preuve), push sans
   demander. Le statut de la tâche n'a pas changé ; ne pas démarrer la tâche,
   ne pas choisir la suivante — dire que le plan est consigné et rendre la
   main.

## À quoi s'attendre

- Une analyse d'une tâche seule, c'est un agent de recherche plus la
  cartographie du code ; une demande à deux tâches parallélise les agents mais
  garde une synthèse chacune.
- La recherche de références se rembourse quand elle produit soit un *plan
  directeur*, soit un *contre-exemple avec un commit*, soit une *règle
  documentée* que le design doit respecter. Une recherche qui ne retourne rien
  de tout ça borne quand même la machinerie.
- La cartographie du code devrait trouver au moins un piège que les notes de
  la tâche ne nommaient pas. Si aucun n'a surfacé, la cartographie était trop
  superficielle.
