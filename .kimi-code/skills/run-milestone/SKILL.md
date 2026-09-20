---
name: run-milestone
description: Mener une milestone Backlog.md — ou une chaîne de plusieurs, l'une après l'autre — à son terme par une chaîne de sous-agents — résoudre l'ordre de traitement par les dépendances, faire trancher à l'utilisateur les arbitrages qui lui reviennent AVANT de lancer quoi que ce soit, briefer un sous-agent par tâche (jamais en parallèle), mesurer et commiter chaque retour, puis clore la milestone et franchir la frontière vers la suivante. Utiliser sur « traite la milestone m-N », « boucle m-N », « boucle m-0 puis m-1 », « traite les milestones restantes », « quelles tâches pour atteindre m-N », « implémente la milestone », ou quand l'utilisateur demande de traiter plusieurs tâches du backlog dans l'ordre. Écrit — modifie des tâches, commite et pousse.
---

# Mener une milestone

Adapté d'un projet voisin, où la procédure a été établie sur une milestone de
18 tâches traitées de bout en bout par une chaîne de sous-agents. Ce qui suit
est la mécanique qui a marché, plus les erreurs qui ont coûté le plus cher.
**Aucune table de coûts n'est portée** — ces chiffres appartenaient à un autre
domaine et induiraient en erreur ici. Ce projet repart avec un
`calibration.md` vide (à côté de ce fichier) ; le remplir fait partie de la
clôture de chaque milestone (phase 5).

La session principale **n'implémente jamais**. Elle résout l'ordre, fait
trancher les arbitrages par l'utilisateur, briefe un sous-agent par tâche et
consigne les résultats. Un agent à la fois — jamais en parallèle, ils se
battraient pour les mêmes fichiers.

Les phases 1 à 5 tournent **une fois par milestone**. Quand l'utilisateur en
demande plusieurs, la phase 0 monte la chaîne et la phase 6 franchit chaque
frontière pour revenir en phase 1 ; les phases intermédiaires ne chevauchent
jamais deux milestones.

## Runtime gate — Claude Code vs Kimi Code

Cette règle gouverne chaque décision de modèle de cette skill.

**Convention de labels, active dans ce dépôt** : chaque tâche backlog porte un
seul label reflétant sa complexité réelle —

- `model:secondaire` — **le défaut** : implémentations guidées par un plan,
  éditions localisées, scripts, docs. Tourne sur le modèle secondaire
  (`kimi-for-coding`).
- `model:primaire` — réservé à l'architecture difficile, la concurrence, les
  cas simultanés ou l'ordonnancement. Tourne sur le modèle primaire (`k3`).

Une tâche qui mêle une partie difficile et une partie standard se découpe en
sous-tâches (`backlog task create -p <ID> ...`) pour isoler la partie primaire
dans une sous-tâche dédiée. Le hook `post-task-create` rappelle cette règle
après chaque création de tâche.

- **Claude Code** : les sous-agents se lancent avec l'outil `Task`, et le
  label `model:primaire`/`model:secondaire` de la tâche choisit le modèle du
  sous-agent — voir phase 3.
- **Kimi Code** : les sous-agents se lancent avec l'outil **`Agent`** (pas
  `Task`), en avant-plan et un à la fois. **`AgentSwarm` est proscrit ici** :
  il parallélise, et la règle d'or est un agent à la fois. Le label choisit le
  modèle via le **paramètre `model` de l'outil `Agent`** :
  `model:secondaire` → `model="kimi-code/kimi-for-coding"`,
  `model:primaire` → `model="kimi-code/k3"` (ou `"primary"`). À défaut de
  paramètre explicite, un sous-agent tombe sur le `default_model` de la
  section `[secondary_model]` de `config.toml` — configurée ici avec
  `kimi-for-coding` en défaut et les deux modèles en pool — et rien dans sa
  sortie ne le dit. Les skills de travail de ce dépôt sont dans
  `.kimi-code/skills/`.

La règle de découpage du backlog (isoler une partie difficile dans sa propre
sous-tâche) vaut sous les deux runtimes ; seul le *forçage* du modèle dépend
du runtime.

## Phase 0 — Cadrer la chaîne

Passer directement en phase 1 quand l'utilisateur a nommé exactement une
milestone. Faire cette phase quand il en a nommé plusieurs, a dit « le reste »,
ou demandé quelque chose qu'une milestone active seule ne peut pas livrer.

1. **Voir l'ensemble actif**, milestones closes comprises quand une dépendance
   pointe en arrière.

   ```bash
   backlog milestone list --plain
   ```

2. **Ordonner les milestones.** Elles ne portent **pas de champ de
   dépendance** — `backlog milestone` ne fait que lister, ajouter, renommer,
   retirer, archiver. L'ordre vient de deux sources, dans cet ordre :

   - **Les dépendances de tâches qui franchissent une frontière de
     milestone.** Une tâche d'une milestone tardive dépendant d'une tâche
     d'une milestone plus tôt ordonne la paire. C'est la seule preuve dure.
   - **La description de chaque milestone.** Une milestone qui valide ou
     construit sur ce qu'une autre livre vient après elle, même sans
     dépendance enregistrée.

   La numérotation est un indice, jamais une preuve. Dire pour chaque paire
   laquelle des deux sources a servi.

3. **Annoncer le budget cumulé avant que quoi que ce soit commence.** Par
   milestone : le nombre de tâches restantes, leurs natures, et une
   fourchette — lire d'abord `calibration.md` (à côté de ce fichier) plutôt
   que citer de mémoire ; il démarre vide et se remplit à mesure que les
   milestones se closent. Tant qu'il est vide, les seuls repères sont les
   attentes générales de la section « À quoi s'attendre », et tout montant en
   USD n'y vaut qu'à titre d'exemple d'ordre de grandeur.

   Puis le total de la chaîne, en fourchette, et la phrase qui compte :
   **c'est un ordre de grandeur, pas un devis**, surtout avant que ce projet
   ait ses propres données de calibration. Énoncer séparément le coût de la
   première milestone : c'est elle l'engagement que l'utilisateur prend
   réellement maintenant.

4. **Proposer les points d'arrêt.** Le défaut est de rendre la main à chaque
   frontière : la milestone est close, ses chiffres rapportés, et l'utilisateur
   dit s'il faut franchir. Continuer sans arrêt est un choix que l'utilisateur
   fait explicitement, et il reste révocable — la phase 5 rapporte à chaque
   frontière quand même.

   ⚠️ **Une frontière de milestone est le seul arrêt prévu. Rien d'autre
   n'arrête la chaîne qu'un arbitrage qui revient genuinement à
   l'utilisateur.** L'heure, la fatigue présumée de l'utilisateur, le souhait
   qu'il soit réveillé pour lire un résultat, la longueur de la session — rien
   de tout cela n'est une raison. Ce sont des décisions prises à sa place, sur
   des choses qui ne regardent pas la chaîne, et elles transforment un run
   autonome en attente. Une tâche qui peut avancer sans l'utilisateur avance.

   Ce qui *arrête* la chaîne, et doit être nommé comme tel plutôt que déguisé
   en circonstance : une question de périmètre, un critère impossible à prouver
   sans lui (sa machine, ses yeux, son compte), un fork de conception, un coût
   qui a dépassé la fourchette annoncée. Pour ce dernier, la phase 6 étape 5
   dit déjà quoi faire — énoncer le chiffre et la fourchette promise, puis
   **continuer sauf objection**, plutôt qu'attendre un feu vert. Rapporter
   n'est pas s'arrêter.

5. **Ne pas ramasser maintenant les arbitrages de toute la chaîne.** La phase
   2 tourne par milestone, au moment où celle-ci démarre. La plupart des forks
   d'une milestone lointaine sont invisibles tant que la précédente n'a pas
   livré ; demander aujourd'hui, c'est demander à l'utilisateur de décider
   aveuglément. Ne signaler que les forks *transverses* — ceux dont la réponse
   change quelle milestone tourne en premier, ou si une milestone a encore un
   sens.

## Phase 1 — Établir l'ordre

1. **Voir les milestones.**

   ```bash
   backlog milestone list --plain
   ```

2. **Lister ses tâches.**

   ```bash
   backlog task list -m "<milestone>" --plain
   ```

   ⚠️ Le filtre matche la milestone la *plus proche*, et il peut ne **rien
   retourner du tout** pour une milestone qui existe. Une liste vide n'est
   jamais la preuve qu'une milestone est vide : réessayer avec le titre complet
   de la milestone.

   ⚠️ **Un listing plus court que `backlog/tasks/` signifie qu'une autre
   lignée existe.** Constaté sur un projet voisin : le listing montrait une
   fraction des tâches, et les compteurs de milestones bougeaient sans que rien
   soit supprimé. Cause établie : `checkActiveBranches: true` fusionne les
   tâches des branches actives par identifiant, et une branche non fusionnée
   portait une *version parallèle de la même milestone* dont les identifiants
   désignaient d'autres tâches — ses copies masquaient celles de main. Cette
   branche avait déjà produit les décisions que la chaîne a alors réécrites
   de zéro.

   Donc, **avant la phase 1, lancer `git branch -a`** et inspecter toute
   branche non fusionnée qui touche `backlog/`. Une tâche marquée To Do sur
   main n'est pas la preuve que personne ne l'a faite. Croiser le listing avec
   `ls backlog/tasks/*.md | wc -l` avant de citer un compte à l'utilisateur ;
   s'ils divergent, trouver la branche plutôt que contourner le symptôme.

3. **Ouvrir chaque tâche restante.**

   ```bash
   backlog task view TASK-N --plain
   ```

   Lire quatre choses, dans cet ordre d'importance :

   - **Les notes** — les plus précieuses et les plus souvent sautées. Les
     tâches antérieures y déposent les noms exacts de ce qu'elles ont livré,
     et parfois *corrigent la description*.
   - **Les dépendances** — celles déjà Done ne comptent plus.
   - **L'ordinal** — la séquence voulue, *pas* l'ordre des identifiants.
   - **Les labels** — le `model:primaire`/`model:secondaire` de la convention
     (voir le runtime gate) ; une tâche sans label est un défaut à signaler.

   Une commande `backlog …` simple par appel. Jamais de boucle, de pipe ni de
   `&&` autour : selon le runtime, le mécanisme de permission évalue la
   commande composée entière et demande confirmation.

4. **Construire l'ordre.** D'abord les débloquées ; parmi elles, ordinal
   croissant. Puis deux règles locales :

   - **Une tâche parente se clôt après ses sous-tâches**, jamais avant. Ses
     propres critères sont en général le câblage plus « les sous-tâches sont
     faites ».
   - **Les tâches d'interface en dernier dans une milestone.** Un installeur
     ou un point d'entrée qui consomme tout ce que les autres tâches exposent
     se traite une fois qu'ils existent, sinon il s'écrit contre une cible
     mouvante.

   Puis vérifier le résultat contre la description de la milestone **et contre
   tout document ou décision de référence** (`backlog/docs/`,
   `backlog/decisions/`). Si l'un d'eux s'avère périmé, le corriger devient
   une tâche — dans cette milestone, pas une suivante.

5. **Montrer l'ordre à l'utilisateur avant de rien lancer**, avec ce qui
   bloque quoi. Dire sur quel modèle chaque tâche tournera (phase 3) :
   `model:secondaire` → `kimi-for-coding`, `model:primaire` → `k3`. Signaler
   les tâches sans label (elles tourneront sur le défaut, phase 3) et ceux que
   les tâches précédentes donnent lieu de douter.

## Phase 2 — Faire trancher les arbitrages d'abord

**C'est la phase qui se rembourse.** La sauter est l'erreur la plus coûteuse
que ce workflow puisse faire.

En lisant chaque tâche en phase 1, signaler tout ce qui est une **décision,
pas une technique** : un périmètre que la description laisse ouvert, une
décision marquée *révisable*, un conflit entre un document de référence et les
notes d'une tâche, une dépendance à un outil tiers dont le comportement peut
avoir changé entre deux builds.

Puis demander à l'utilisateur, **avant de lancer un seul agent**, en un
message : quel est le fork, ce que coûte chaque branche, et une
recommandation.

> **Le mode d'échec que cette phase existe pour empêcher.** Non questionné, un
> agent à qui on demande de livrer une tâche la rétrécira presque toujours
> quand le travail devient coûteux, et il plaidera bien sa cause. Ce n'est pas
> une faute de l'agent ; c'est une question qui n'a jamais été la sienne.
> Défaire un rétrécissement de périmètre fait en silence coûte plus cher que
> demander ne l'aurait coûté — nouvelles tâches, réécriture d'un document, et
> une décision à re-plaider.

Règles que tout brief doit porter, adaptées à ce projet :

- **Un critère ne se coche jamais sur un raisonnement.** Ceux qui demandent
  une exécution réelle — un script fait tourner contre une vraie installation,
  une skill réellement chargée par le produit cible — sont prouvés ainsi ou
  pas du tout. Un agent qui ne peut pas y arriver doit **le dire**, pas
  raisonner jusqu'au cochage.
- **Les règles de contribution d'`AGENTS.md` ne sont pas négociables** :
  scripts Python 3.8+ stdlib, read-only, offline ; copies de `_bobcheck.py`
  identiques dans toutes les skills livrées ; tout fait reverse-engineered
  énoncé avec le build et la source dont il provient ; aucune donnée
  personnelle dans les exemples. Ce sont des décisions actées, pas des défauts
  qu'un agent peut assouplir en silence parce que l'alternative semblait moins
  chère.
- **Les arbitrages appartiennent à l'utilisateur.** Rapporter tout
  rétrécissement de périmètre qu'un agent fait, même quand la justification
  semble solide.

Quand l'utilisateur tranche un fork, écrire la décision dans les tâches
concernées tout de suite (`--append-notes`), et dire en toutes lettres dans
chacune que la note **PRIME** sur tout document disant encore le contraire.
Les documents sont corrigés par leur propre tâche ; les notes sont ce que le
prochain agent lit réellement.

## Phase 3 — Trancher la conception, puis briefer un sous-agent

### Toute tâche `model:primaire` reçoit d'abord une analyse de conception

C'est la règle qui justifie le label : une tâche assez difficile pour le
modèle primaire est assez difficile pour qu'on tranche sa conception avant
d'écrire du code. Lancer la skill `analyze-task` dessus **avant** de briefer
un agent — pas au début de la milestone, mais quand la tâche arrive. Lancée
plus tôt, l'analyse manquerait ce que les tâches intermédiaires viennent de
livrer, et c'est exactement de là que viennent ses points d'extension.

La lancer depuis la session principale : elle porte déjà l'ordre de la
milestone, les arbitrages de l'utilisateur et les notes. Son livrable est un
plan consigné dans la tâche, et c'est ce plan qui permet à l'implémentation de
tourner sur un sous-agent — souvent un moins cher, puisque la conception n'a
plus à être dérivée. C'est aussi la meilleure défense contre le mode d'échec
de la phase 2 : un agent fait bien plus difficilement descendre un *plan* en
prix qu'une *description*.

**La chaîne s'arrête pour la validation de l'utilisateur.** C'est la règle
propre de la skill d'analyse, et la leçon de la phase 2 s'applique inchangée.

**Une exception.** Quand l'analyse a trouvé des implémentations de référence
**représentatives du problème analysé** — elles résolvent ce problème, pas un
voisin — et que ces références **convergent sur le même design**, consigner le
plan et briefer l'agent sans attendre. Le dire dans le rapport qui suit : quel
était le consensus, quels projets et commits le portent, et que le plan est
entré non validé, pour que l'utilisateur puisse objecter après coup. Pas de
pause ne veut pas dire pas de rapport.

Quatre choses ressemblent à un consensus et n'en sont pas :

- **Des références qui partagent une lignée.** Deux projets d'accord parce que
  l'un est le fork de l'autre font un point de donnée, pas deux.
- **Une convergence que la documentation officielle du fournisseur
  contredit.** Le fournisseur gagne.
- **Un design qui converge ailleurs mais ne peut pas tenir ici** — parce
  qu'elle casse une règle du dépôt (stdlib seule, read-only, offline). Un
  consensus que cette architecture ne peut pas porter n'est pas un consensus
  sur notre problème.
- **Des références qui résolvent le problème voisin.**

Et l'exception ne couvre jamais une question de **périmètre**. Les références
montrent comment une chose se construit ; elles ne peuvent pas dire s'il faut
la construire. Cela reste à l'utilisateur, toujours.

### Le brief

Un agent par tâche, lancé **synchrone** — attendre son retour avant de lancer
le suivant (outil `Task` sous Claude Code, outil `Agent` en avant-plan sous
Kimi Code ; jamais `AgentSwarm`).

Le choix du modèle : le label de la tâche choisit le modèle de l'agent, pas
celui de la session. Les deux directions ne sont **pas** symétriques, parce
qu'une seule dépense le quota de l'utilisateur :

- **`model:secondaire` dans une chaîne conduite sur k3** — l'appliquer,
  silencieusement : sous Kimi Code, passer `model="kimi-code/kimi-for-coding"`
  à l'outil `Agent` (sous Claude Code, le tier moins cher de `Task`).
  Conduire la chaîne depuis le modèle primaire n'est **pas** une demande de
  traiter chaque tâche avec ce modèle. Pas de confirmation ; demander à chaque
  fois serait faire re-décider à l'utilisateur quelque chose de déjà tranché.
- **`model:primaire` dans une chaîne conduite sur le secondaire** — **demander
  avant de lancer**, avec ce qu'est la tâche et ce que coûte la montée de
  gamme (k3 consomme nettement plus de quota ; vérifier avec la skill
  `quota-check`). La réponse vaut pour le reste de la chaîne s'il le dit ;
  sinon redemander à la prochaine tâche concernée.

Puis les cas que le label ne tranche pas :

- **Pas de label `model:`** — tourner sur le modèle de la session, ou sur le
  secondaire (`kimi-for-coding`) si la tâche est visiblement standard, et le
  dire dans l'ordre montré en phase 1. Proposer au passage d'ajouter le label
  manquant avec `backlog task edit`.
- **L'utilisateur a demandé un modèle pour ce run** — son instruction l'emporte
  sur tout label, pour toute la chaîne. Nommer les tâches que ça déplace et ce
  que ça ajoute au budget, puis lancer.
- **Un label semble faux** à la lumière de ce que les tâches précédentes ont
  révélé — c'est un arbitrage, pas une technique : le soumettre à
  l'utilisateur avec la raison et le coût. Ne jamais monter en gamme en
  silence ; le label est aussi une estimation de difficulté à laquelle le
  prochain lecteur se fierait.

La session principale garde son propre modèle tout du long — elle lit les
rapports, arbitre et écrit les briefs.

Sept blocs. Les deux premiers et les trois derniers sont toujours les mêmes ;
les blocs 3 à 5 sont ce qu'on écrit réellement à chaque fois.

1. **Dépôt et mission.** Quelle tâche, et « intégralement, jusqu'au commit et
   au push ».

2. **Contexte à charger d'abord.** `AGENTS.md` ; les guides backlog
   (`backlog instructions overview`, puis `task-execution` avant de toucher un
   statut, puis `task-finalization` avant de clore) ; la tâche elle-même,
   **notes comprises** ; le document ou la décision de référence qu'elle
   pointe.

3. **Ce qui vient d'atterrir.** Les tâches terminées juste avant, avec leurs
   SHA de commit et les **noms exacts** des fichiers, skills et conventions
   qu'elles ont introduits. Sans ça, l'agent re-dérive ce qui existe déjà, ou
   pire, en construit une version parallèle.

4. **Ce qui est déjà tranché.** Les arbitrages de l'utilisateur, énoncés comme
   non négociables, et le plan consigné quand la tâche en a un — l'agent
   l'implémente, il ne le rouvre pas. Et quand un document dit encore le
   contraire, le dire explicitement : *« le document dit X, il est périmé, les
   notes de la tâche priment »*. Un agent qui lit un document périmé agit
   dessus.

5. **Périmètre et comment le prouver.** Le périmètre fonctionnel, plus le
   standard de preuve. Nommer les critères que la tâche doit satisfaire et
   comment chacun se prouve — lesquels un contrôle local tranche hors ligne
   (`python3 -m py_compile`, `node --check`, `shasum` des copies de
   `_bobcheck.py`), et lesquels demandent une exécution contre une vraie
   installation (règle d'`AGENTS.md` : chaque script est testé contre une
   installation réelle avant une PR). Dire à l'agent que s'il ne peut pas y
   arriver, il doit **le dire** plutôt que cocher le critère sur un
   raisonnement.

6. **Rituel de fin de tâche.** Formaliser dans le dépôt tout ce qui n'existe
   que dans la conversation ; transmettre aux tâches aval par leur nom ;
   vérifier chaque critère avec une preuve objective ; **ne pas se mesurer
   soi-même** (phase 4) ; un commit, message en français comme le reste de
   l'historique de ce dépôt, push sans demander ; ne pas choisir la tâche
   suivante.

7. **Contraintes d'outillage.** Pas de commandes composées autour de commandes
   autorisées ; `git` nu depuis la racine du dépôt ; `--append-notes` jamais
   `--notes` ; ne jamais éditer un markdown backlog à la main — toujours le
   CLI `backlog` ; relire `git status` avant de stager.

   ⚠️ **Jamais de backticks dans le texte passé à `--append-notes`.** Dans une
   chaîne shell double-quotée, ils déclenchent une substitution de commande :
   le nom backtické est remplacé par la sortie (vide) d'une commande qui
   n'existe pas, et la note s'écrit en silence avec des trous là où les
   identifiants devraient être. Utiliser du gras ou des guillemets français
   pour les noms de code — et relire la note après l'avoir écrite, parce que
   le CLI `backlog` rapporte un succès dans les deux cas.

   ⚠️ **Ne pas « corriger » ça en mettant l'argument entre apostrophes.** Les
   apostrophes shell arrêtent bien la substitution, mais elles se ferment à la
   première apostrophe — et la prose française en est pleine, donc la note
   arrive avec chaque `'` silencieusement perdu. Le remède qui marche pour
   tout caractère est de sortir le texte **du shell**, avec un petit script
   Python appelant `subprocess.run(["backlog", "task", "edit", …],
   shell=False)`, pour que le contenu voyage comme un seul élément d'argv et
   ne rencontre jamais de shell.

Conclure par **ce que le rapport final doit contenir** : des chiffres réels,
ce qui a été effectivement observé, et — dit explicitement — ce qui n'a *pas*
été fait.

## Phase 4 — Prendre le retour de l'agent

1. **Établir ce qui s'est passé avant de croire le rapport.** Le commit de la
   tâche dans `git log`, ce que `git status` montre qu'il a laissé derrière
   lui, et les contrôles du projet contre les chiffres que le brief a donnés.
   Un rapport est une affirmation ; ces trois-là sont des preuves, et tout ce
   qui suit suppose que le commit existe.

2. **Mesurer depuis la session principale, après le commit.** Un sous-agent ne
   peut pas se mesurer correctement lui-même. Utiliser la skill
   `task-telemetry` dans sa forme fenêtre-de-commits : la fenêtre va du commit
   précédent au commit de la tâche, donc elle capture l'orchestration *et* le
   travail de l'agent. Sous Kimi Code, la lecture des consommations par session
   et par agent se fait avec la skill `kimi-telemetry` (tokens exacts depuis
   les `wire.jsonl` locaux ; l'argent n'est rapporté que si le fournisseur le
   remplit). Vérifier la fenêtre affichée par l'outil avant de croire un total
   — un commit qui mentionne l'identifiant de la tâche peut se faire prendre
   pour le commit de clôture et déplacer la borne.

3. **Ajouter la ligne aux notes de la tâche**, en nommant honnêtement la cause
   de toute pause — un long batch de tests compté comme une pause est du
   traitement, pas de l'attente.

4. **Commiter cette ligne à part.** Elle devient la borne de fenêtre de la
   tâche suivante. Garder le sujet libre de tout ce qui pourrait matcher une
   autre tâche.

   ⚠️ **Ne jamais commiter quoi que ce soit pendant qu'un sous-agent tourne.**
   Le commit tombe dans la fenêtre de cet agent et en devient la borne basse
   exclusive, tronquant silencieusement la mesure. Retenir les commits
   d'orchestration jusqu'au retour de l'agent ; entre deux tâches ce sont des
   bornes légitimes, pendant une tâche c'est de la corruption.

   **Vérifier chaque lecture contre la durée rapportée par l'agent lui-même**
   avant de la persister. Cet écart est le seul indice — la fenêtre affichée
   a l'air parfaitement ordinaire dans les deux cas.

5. **Résumer à l'utilisateur** : ce qui a été livré, ce qui a été
   effectivement observé, le coût, et tout ce que l'agent a signalé comme non
   fait. Puis lancer la suivante.

Lire le rapport avec esprit critique. Les agents rapportent honnêtement mais
optimistement : un critère « vérifié par raisonnement » n'est pas vérifié, et
une tâche qui a ouvert de nouvelles tâches vous dit quelque chose sur le
périmètre réel de la milestone.

### Quand l'agent revient avec un problème

Quatre mauvais retours, et ils ne sont pas interchangeables — la réponse
diffère pour chacun. Ce qu'ils partagent : **aucun ne se résout en relançant
le même brief en espérant.**

- **Pas de commit, ou un arbre laissé sale.** Inventaire avant toute chose :
  ce qui est stagé, ce qui compile, ce que disent les contrôles. Ne jamais
  briefer un second agent par-dessus un arbre à moitié fait non inventorié —
  il ne peut pas voir la forme de ce sur quoi il construit, et il dupliquera
  ou enterrera. Ou bien l'état est assez propre pour continuer, et le brief
  suivant le dit explicitement en le nommant ; ou bien on le réverte
  délibérément, en disant à l'utilisateur quel travail est jeté.
- **Un critère que l'agent n'a pas pu prouver.** Il n'est pas vérifié, et il
  ne le devient pas parce que l'agent a raisonné dessus. Ou bien la chaîne le
  prouve maintenant, ou bien elle ouvre une tâche dans la même milestone.
  Jamais le cocher.
- **Un périmètre rétréci.** Le rapporter et s'arrêter. C'est toute la leçon
  de la phase 2 : la justification semblera solide et l'est peut-être, et
  c'est quand même une réponse à une question qui n'a jamais été la sienne.
- **Un fork de conception rencontré en cours de tâche.** Pas un retry — une
  analyse. Lancer `analyze-task` sur la tâche avec ce que l'agent a appris
  comme entrée, puis re-briefer contre le plan consigné. Un agent qui a échoué
  sur une question de conception échoue de nouveau sur la même question, un
  tier de modèle au-dessus inclus.

Un cinquième retour n'est pas un mauvais retour, seulement un interrompu :
**l'agent a été coupé en pleine tâche par une erreur d'API** (le résultat
d'outil le dit, avec une sortie partielle). Son travail est sur le disque et
son contexte intact — reprendre le MÊME agent avec un message (son identifiant
est dans le résultat d'outil ; sous Kimi Code, `TaskOutput`/`Agent` permettent
de suivre et reprendre un agent d'arrière-plan), en lui disant exactement où
il s'est arrêté et ce qui reste, plutôt que de briefer un nouvel agent
par-dessus son arbre à moitié fait. Inventorier `git status` d'abord, comme
ci-dessus, pour que le message nomme ce qui existe déjà.

Un **sixième** retour ressemble au cinquième et n'en est pas un : **l'agent
s'arrête de lui-même, en attente d'un travail d'arrière-plan qu'il a lancé
lui-même.** Son dernier message dit qu'il attend ; rien n'a échoué. Ne pas
briefer un nouvel agent : confirmer ce qui tourne réellement (`ps aux`,
`TaskList` sous Kimi Code), attendre que ce processus finisse, lire son
résultat, puis **reprendre le MÊME agent** avec un message citant le résultat
et listant ce qui reste. Son contexte est intact ; un agent neuf relirait
tout. Le correctif pour la prochaine fois est dans le brief, pas dans la
récupération : dire à l'agent de lancer ce genre de travail **au premier
plan** et d'accepter un appel d'outil qui dure.

**Un retry au plus, puis l'utilisateur décide.** Un second échec sur la même
tâche vous parle de la tâche, pas de l'agent — le plus souvent qu'elle est en
fait deux tâches, ou que sa conception n'a jamais été tranchée.

Le coût d'une tentative ratée n'est pas perdu : la fenêtre du commit final
démarre au commit précédent et l'absorbe. Dire dans la note que le chiffre
couvre N tentatives ratées — une tâche qui a coûté le double parce qu'elle a
été faite deux fois ne doit pas se lire comme une tâche simplement chère.

## Phase 5 — Clore la milestone

- Confirmer avec `backlog milestone list --plain` qu'elle a quitté l'ensemble
  actif.
- Passer la **porte de sortie** de la milestone si elle en a une, et rapporter
  ses chiffres.
- **Exécuter le livrable soi-même, à froid, avant de déclarer la milestone
  close.** Pas les contrôles — la chose réelle qu'un utilisateur invoquerait
  (ici : `install.sh` sur une installation propre, ou chaque script livré
  contre une vraie installation, comme l'exige `AGENTS.md`), sur la machine en
  l'état, sans l'environnement que la chaîne s'est arrangé. L'agent producteur
  prouve ses critères dans l'état qu'il a construit ; cet état lui est
  invisible et il ne peut pas savoir de quoi il en est venu à dépendre.

  Un défaut trouvé ainsi est normal, pas un signe que la chaîne a échoué —
  c'est exactement le genre de chose qui vit *entre* deux tâches dont les
  critères étaient chacun honnêtement tenus. Ouvrir une tâche pour lui, dire
  clairement si la porte tient encore et pourquoi, et ne rouvrir la milestone
  que si un critère de porte est réellement non prouvé.
- **Mettre à jour `calibration.md`** (à côté de ce fichier) avec les chiffres
  réels de la milestone : une section par milestone, une ligne par tâche
  (nature, modèle, coût, temps effectif). C'est ce que la phase 0 et la phase
  6 lisent au lieu de citer de mémoire — le tenir à jour fait partie de la
  clôture d'une milestone.
- Totaliser le coût, et le convertir en estimation pour ce qui reste.
- Lister toutes les tâches que la chaîne a créées en chemin, et celles qui
  attendent encore l'utilisateur.

## Phase 6 — Franchir la frontière

Seulement quand le run couvre plusieurs milestones. Une frontière est un
**checkpoint, pas une couture** : tout ce que la phase 0 a décidé est réexaminé
ici avec ce que la milestone vient d'enseigner.

1. **Rapporter, puis demander.** Donner les chiffres de clôture de la milestone
   qui s'achève, le coût réestimé de la suivante, et attendre l'utilisateur —
   sauf s'il a demandé en phase 0 d'enchaîner. Même alors, s'arrêter et
   demander quand la milestone s'est terminée avec un critère non prouvé, une
   tâche qu'elle n'a pas pu clore, ou un coût de plus de moitié au-dessus de
   l'estimation.

2. **Rejouer la phase 1 et la phase 2 en entier pour la milestone suivante.**
   Ses tâches portent maintenant des notes écrites par la chaîne qui vient de
   tourner, et ces notes corrigent couramment les descriptions que la phase 0
   a lues. Ne jamais réutiliser l'ordre esquissé au départ ; le reconstruire.

3. **Rejouer les arbitrages.** Les forks de cette milestone se demandent
   maintenant, pas avant — c'est la raison d'être de la frontière. Et rouvrir
   tout arbitrage antérieur que la dernière milestone a falsifié : une
   décision prise sur une estimation de coût qui s'est révélée fausse est une
   décision à re-soumettre à l'utilisateur, pas une décision acquise à
   reporter.

4. **Revérifier les tâches que la chaîne a créées.** Les tâches ouvertes en
   cours de milestone atterrissent souvent dans la suivante. Elles peuvent y
   être bloquantes, et elles sont absentes du compte que la phase 0 a annoncé.
   Dire comment le total a bougé.

5. **Recalibrer le budget** avec les chiffres réels de la milestone qui
   s'achève, et réénoncer le total restant. L'utilisateur s'est engagé sur une
   fourchette en phase 0 ; si le run la dépasse, c'est un fait dont il a
   besoin avant que la prochaine tâche commence, pas après.

6. **Une milestone qui en valide une autre a besoin d'un prédécesseur
   réellement fini**, pas seulement marqué Done. Avant de franchir, confirmer
   que les critères dont elle dépend ont été prouvés par exécution et non par
   raisonnement.

## À quoi s'attendre

Les chiffres mesurés vivent **à côté de ce fichier, dans `calibration.md`** —
une section par milestone, une ligne par tâche (nature, modèle, coût, temps
effectif). Il démarre vide. Le lire quand on annonce un budget (phase 0 étape
3) ou qu'on réestime à une frontière (phase 6 étape 5) ; ne jamais citer un
chiffre venu de l'historique d'un autre projet. Le tenir à jour fait partie de
la clôture d'une milestone (phase 5).

Quelques attentes générales, vraies sur les projets où cette skill a tourné,
utiles tant que ce projet n'a pas ses propres données (les montants USD sont
des exemples d'ordre de grandeur, pas des prédictions) :

- **Compter d'abord les tâches `model:primaire` dans un budget** — elles
  coûtent plusieurs fois une tâche secondaire (modèle plus cher, analyse de
  conception préalable, vérificateur indépendant plus souvent nécessaire). Une
  milestone de dix tâches secondaires peut coûter moins qu'une seule primaire.
- **Un compte de tâches annoncé est un plancher.** Les milestones ouvrent
  couramment une ou deux tâches supplémentaires en chemin, sur un défaut trouvé
  ou un arbitrage rendu — pas du scope creep, juste la vérité qui remonte.
- **Budgéter le monde réel comme une tâche en plus, pas comme un
  multiplicateur.** Un critère qui demande une vraie installation ne rend pas
  l'implémentation plus chère — il ajoute une tâche de preuve.
- **Le temps mur-à-mur est un très mauvais proxy du coût.** Citer le temps de
  traitement effectif, pas le temps calendaire que la fenêtre d'une tâche
  couvre.
- **Déléguer même tard dans une chaîne.** Une tâche conduite dans la session
  principale coûte plus cher que la même tâche déléguée, parce que chaque tour
  relit le contexte accumulé de la chaîne.
- **Un agent de recherche de références tourne sur le modèle secondaire,
  toujours** — un agent lancé sans choix de modèle explicite hérite
  silencieusement du défaut (sous Kimi Code : le `default_model` de
  `[secondary_model]`, configuré ici sur `kimi-for-coding` ; sous Claude Code :
  le modèle du parent), et rien dans sa sortie ne le dit. La recherche est bon
  marché, c'est la synthèse qui coûte.
