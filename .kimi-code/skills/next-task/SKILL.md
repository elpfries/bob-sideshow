---
name: next-task
description: Choisir la prochaine tâche Backlog.md à traiter — reprend la tâche In Progress s'il en existe une, sinon filtre les tâches To Do par dépendances résolues et trie les débloquées par priorité puis ordinal. Utiliser au rituel de fin de tâche (recommander la suite avant de rendre la main), sur « quelle est la prochaine tâche », « next task », « qu'est-ce que je fais après », ou pour prioriser le backlog. Lecture seule — ne fait que lister et lire des tâches, n'en modifie jamais une.
---

# Prochaine tâche Backlog.md

Procédure de décision en lecture seule. N'utilise que `backlog task list` /
`backlog task view` — jamais `task edit`, donc aucune permission
supplémentaire et aucune mutation. Choisir une tâche pour la *démarrer* est
une étape séparée : une fois le choix fait, suivre `backlog instructions
task-execution` (le passage In Progress fait partie de ce flux-là, pas de
celui-ci).

## Procédure

1. **Regarder d'abord le travail déjà commencé.**

   ```bash
   backlog task list --plain
   ```

   Cette commande groupe les tâches par statut en un appel. Une section
   « In Progress: » signifie que quelqu'un (ou une session antérieure) a déjà
   commencé cette tâche — la reprendre prime sur le démarrage d'une nouvelle.
   Ne passer aux étapes 2–4 que si cette section est vide, ou si l'utilisateur
   a explicitement demandé la prochaine tâche *non commencée*.

   Garder l'ensemble des tâches « Done » de cette même sortie — l'étape 3 en
   a besoin, et ça économise un second appel.

2. **Relever les dépendances de chaque candidate « To Do ».**

   ```bash
   backlog task view TASK-N --plain
   ```

   Lire `Dependencies:`, `Ordinal:`, `Priority:` (si présente) et `Labels:`.
   Pas de ligne `Dependencies:` = débloquée par défaut.

   Lancer chaque `view` comme sa propre commande `backlog …` simple (les
   appels parallèles sont acceptés). Ne jamais les enrouler dans une boucle
   shell ni les piper dans d'autres programmes (`for`, `| head`, `&& echo`,
   …) : selon le runtime, le mécanisme de permission évalue la commande
   composée entière, qui ne correspond plus à une éventuelle règle
   d'autorisation sur `backlog *` et déclenche une demande — ce qui détruit
   l'intérêt d'une skill à zéro permission.

3. **Filtrer sur les tâches débloquées.**

   Une candidate n'est débloquée que si chaque identifiant de sa ligne
   `Dependencies:` est dans l'ensemble « Done » de l'étape 1. Garder une note
   d'une ligne sur ce qui bloque les autres — ça vaut la peine de le montrer,
   pas seulement de l'écarter.

4. **Trier ce qui reste.**

   - Toute candidate débloquée avec une `Priority:` l'emporte sur une sans,
     High > Medium > Low.
   - Départager (ou trier quand rien n'a de priorité) par `Ordinal:` croissant.
     L'ordinal est la séquence réellement voulue par l'équipe — ce n'est *pas*
     équivalent à trier par numéro de TASK-ID, ne pas substituer l'un à
     l'autre.

5. **Label de modèle — convention active dans ce dépôt.**

   Chaque tâche porte `model:secondaire` (défaut, tourne sur
   `kimi-for-coding`) ou `model:primaire` (architecture difficile,
   concurrence, ordonnancement — tourne sur `k3`).

   - **Claude Code** (modèle de session explicite) : comparer le label de la
     tâche gagnante au modèle actif de la session. Écart → le dire et demander
     confirmation à l'utilisateur avant tout plan ou toute implémentation.
     Accord → le noter en une ligne et continuer.
   - **Kimi Code** : le choix du modèle d'un sous-agent passe par le paramètre
     `model` de l'outil `Agent` (`kimi-code/kimi-for-coding` pour
     `model:secondaire`, `kimi-code/k3` ou `"primary"` pour `model:primaire`)
     ou, à défaut, par le `default_model` de la section `[secondary_model]`
     de `config.toml` ; il n'y a pas de `/model` à demander au fil de l'eau.
     Rapporter le label comme **information seulement** — une indication
     coût/qualité à exploiter au moment du lancement, jamais un bloquant.
   - **Tâche gagnante sans label** : le signaler et proposer d'en ajouter un
     avec `backlog task edit` — la convention veut un label par tâche.

## Rendre le résultat

Commencer par la recommandation, puis la justifier :

- Tâche recommandée : identifiant, titre, raison en une ligne (reprise d'une
  In Progress / débloquée + plus haute priorité / débloquée + plus bas
  ordinal).
- Dauphines débloquées, s'il y en a, et pourquoi elles arrivent après.
- Tâches bloquées qui valent d'être mentionnées (en général celles à qui il
  manque le moins de dépendances) et ce qu'elles attendent.
- Résultat du contrôle du label de modèle (`model:primaire` /
  `model:secondaire`, ou son absence signalée).

S'arrêter là. Ne pas passer la tâche In Progress, ne pas esquisser de plan,
ne pas commencer l'implémentation — c'est le rôle de `backlog instructions
task-execution`, et ça demande d'abord le feu vert de l'utilisateur.
