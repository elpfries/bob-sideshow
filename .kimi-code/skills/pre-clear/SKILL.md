---
name: pre-clear
description: Auditer la conversation en cours avant un /clear, en supposant qu'elle s'arrête juste après — passe 0 sur ce qui tourne encore, passe 1 mécanique via un script (travail non commité, commits non poussés, tâches In Progress), passe 2 de capitalisation (« qu'est-ce que cette session sait que le dépôt ne sait pas ? »), puis annoncer si le /clear est sûr et donner le premier message à envoyer après. Utiliser sur « /pre-clear », « pré-clear », « je vais clear », « je change de conversation », « est-ce que je peux fermer », « qu'est-ce qui se perd si j'arrête là », « qu'est-ce qui n'est pas capitalisé », ou avant de rendre la main sur tout échange qui a produit un état (décision, fait vérifié, tâche écrite, fichier modifié, processus lancé).
---

# Avant que le fil ne s'arrête

Adapté d'un projet voisin (fusion de ses skills `pre-clear` et
`capitalize-learnings` en une seule). Trois passes, dans l'ordre : une passe 0
sur ce qui tourne encore, une passe mécanique sur ce qui a touché le disque,
une passe de capitalisation sur ce qui n'existe que dans le fil.

Cette skill part d'une hypothèse, et c'est toute sa valeur : **la conversation
s'arrête juste après ta réponse.** Pas « à la fin de la tâche » — maintenant.
Le porteur fait `/clear` et repart d'un contexte vide ; la session suivante ne
connaîtra que le dépôt et le backlog.

La question n'est donc pas « ai-je fini ». C'est :

> **Qu'est-ce qui disparaît si le fil s'arrête ici, et que la prochaine
> session referait, redemanderait, ou prendrait à contresens ?**

## Trois passes, dans cet ordre

### 0. Rien ne tourne encore

Avant de lire ou d'écrire quoi que ce soit :

- **Un sous-agent en cours** : attendre son retour et le traiter. Un `/clear`
  pendant qu'il tourne perd son rapport, et un commit fait pendant qu'il
  tourne fausse la fenêtre de mesure de la tâche en cours
  (`run-milestone`, phase 4).
- **Un processus lancé à la main pour une vérification** (un serveur local,
  un conteneur, une installation de test) : l'arrêter, ou dire explicitement
  qu'il continue et pourquoi.

### 1. La passe mécanique — ce qui a touché le disque

```bash
python3 .kimi-code/skills/pre-clear/scripts/pre-clear-audit.py --repo .
```

Le relevé montre le travail non commité, les commits non poussés, les tâches
laissées In Progress, les processus visant ce dépôt encore vivants, les
fichiers d'exécution laissés à la racine, et — si le runtime expose un
répertoire temporaire de session et qu'on le passe avec `--session-dir` — les
fichiers qui n'existent que là.

**Un relevé vide ne veut pas dire qu'un `/clear` est sûr.** Le script ne voit
que ce qui a touché le disque. Le plus précieux d'une conversation n'y a
justement jamais touché.

Un pid signalé vieux de quelques secondes, et absent quand on le relit
(`ps -p <pid> -ww`), vient souvent de l'éditeur, pas de la session — vérifier
qu'il a disparu avant de conclure ; ne jamais tuer un processus qu'on n'a pas
lancé soi-même.

Pour chaque fichier du répertoire de session, trancher : **jetable** (le
dire), **à recréer** (écrire dans les notes de la tâche comment le recréer),
ou **à verser** (un script de preuve ou de contrôle qui resservira va dans
`.kimi-code/skills/<skill>/scripts/` — ou dans `skills/<skill>/scripts/` s'il
documente une skill livrée — jamais laissé dans un répertoire temporaire).

### 2. La passe de capitalisation — ce qui n'existe que dans le fil

Celle-ci ne s'automatise pas. La question, une seule :

> **Qu'est-ce que cette session sait, que le dépôt ne sait pas ?**

Pas « qu'ai-je fait » — c'est dans les commits. Ce qui reste : ce qui a été
*appris en chemin*, plus ce qui n'a rien appris à personne mais **coûterait
cher à refaire** ou **ne se retrouverait pas du tout**. Relire l'échange en
cherchant ces choses, qui se perdent toutes en silence :

| Ce que la session sait | Pourquoi ça compte | Où ça se verse, ici |
| --- | --- | --- |
| **Une décision du porteur** — un arbitrage rendu en cours d'échange | C'est ce qui ne se redécouvre pas. La session suivante repartira du design écarté, et il faudra le redemander | Notes de la tâche concernée, datées, avec « cette note PRIME sur la description » ; si c'est une règle transversale du projet, `AGENTS.md` |
| **Un fait reverse-engineered** — vérifié sur un build précis de Bob ou d'un outil comparé | Une skill de ce dépôt affirme des faits sur des builds ; un fait nouveau ou corrigé qui reste dans le fil est une doc périmée en silence | La `SKILL.md` concernée, ou le `docs/*-vs-bob.md` concerné — **toujours avec le build vérifié et sa source** (règle `AGENTS.md`) |
| **Une règle de contribution nouvelle** — une convention que le dépôt doit tenir | Elle vaut pour toutes les contributions futures | `AGENTS.md` si elle est courte ; une skill de `.kimi-code/skills/` si elle a une procédure |
| **Une leçon de process** — sur la conduite d'une milestone, un piège de mesure, un bug d'outillage trouvé en l'utilisant | Elle vaut au-delà de la tâche | La `SKILL.md` de la skill de dev concernée dans `.kimi-code/skills/`, ou `calibration.md` de `run-milestone` si c'est un chiffre |
| **Un script jetable révélé réutilisable** | Il disparaît avec le répertoire temporaire | `.kimi-code/skills/<skill>/scripts/` (Python 3.8+, stdlib, read-only — règles `AGENTS.md`), et la skill qui le documente |
| **Une piste fermée** — « on a vérifié que X ne marche pas / n'est pas la cause » | Un échec ne laisse aucune trace. Sans ça, la piste est rouverte et refaite intégralement | La tâche, en toutes lettres : « à lire avant d'implémenter, ferme telle fausse piste » |
| **Une preuve réelle** — un script fait tourner contre une vraie installation, un comportement observé sur un vrai build | La refaire coûte à nouveau du temps ou une installation | Notes de la tâche : date, build, ce qui a été touché, ce qui a été observé, ce qui n'a **pas** été prouvé |
| **Un défaut vu et pas corrigé** | Il disparaît avec le fil | Une tâche de suivi, avec l'accord du porteur ; à défaut, une phrase au porteur en rendant la main |
| **Une question restée sans réponse** | Elle disparaît avec le fil, et personne ne sait qu'elle a été posée | Un commentaire de tâche, **et** une phrase au porteur en rendant la main |
| **Un état hors dépôt** — un réglage changé, une installation laissée en place | Rien dans le dépôt ne le montre, et il fausse la prochaine vérification | Notes de la tâche concernée, et une phrase au porteur s'il doit agir |
| **La reprise** — la prochaine action et ce qu'elle doit lire d'abord | C'est ce qui évite que la session suivante reconstruise l'état depuis le journal git | Notes de la prochaine tâche à traiter ; la milestone si c'est un ordre ou un blocage |

**Le test qui tranche** : est-ce que la prochaine session, sans ce fil,
referait l'erreur, referait le travail, redemanderait un arbitrage, ou
repartirait dans la mauvaise direction ? Si oui, ça se verse. Sinon, non.

**« Rien à verser » est une bonne réponse** — c'est même la plus fréquente, et
elle doit rester bon marché. Une tâche qui applique un mécanisme connu à un
cas de plus n'apprend rien au dépôt. Ce qui n'est **pas** une bonne réponse :
« c'est dans les notes de la tâche » pour une leçon qui vaut hors de cette
tâche. Personne ne relit les notes d'une tâche close.

Ce qui ne se verse **pas** : un résumé de la conversation, l'histoire que git
porte déjà, un chiffre déjà dans les notes, un secret, une donnée personnelle
(les exemples et fixtures de ce dépôt n'en contiennent jamais — règle
`AGENTS.md`).

## Verser, puis le dire

**Verser avant de rendre la main, pas le proposer.** « Veux-tu que je note
ça ? » est une question dont la réponse arrive après le `/clear`. Ce qui se
range se range ; ce sur quoi il y a un vrai doute se dit.

Deux exceptions :

- ne jamais écrire dans le dépôt une décision que le porteur n'a pas prise :
  un design proposé et pas encore validé se note comme une proposition, jamais
  comme un arbitrage ;
- ne jamais créer une tâche de suivi sans son accord : la noter comme défaut
  vu dans les notes de la tâche la plus proche, et le lui dire.

Règles d'écriture de ce dépôt, qui s'appliquent ici comme ailleurs :

- backlog uniquement par le CLI, jamais d'édition manuelle d'un markdown
  backlog ; `--append-notes` jamais `--notes` (qui efface l'historique) ;
- **pas de backticks** dans le texte des notes en shell double-quoté
  (substitution de commande silencieuse), pas de guillemets simples non plus
  (coupe sur la première apostrophe française) : passer par un petit script
  Python `subprocess.run([...], shell=False)` pour tout texte riche en
  apostrophes ou en noms de code, puis relire la note écrite ;
- si la passe touche une skill livrée (`skills/*/`), rejouer les contrôles
  d'`AGENTS.md` : `python3 -m py_compile skills/*/scripts/*.py`, le
  `node --check` du template de hook, et l'identité des copies de
  `_bobcheck.py` (`shasum skills/*/scripts/_bobcheck.py`) ;
- un commit par passe de capitalisation, message en français, puis push sans
  demander confirmation ;
- relancer l'audit mécanique après le commit : il doit revenir propre.

## La fin de réponse, obligatoire

En rendant la main, trois choses, dans cet ordre :

1. **Une phrase qui dit si le `/clear` est sûr**, et ce qui a été versé où —
   ou ce qui ne l'a pas été, et pourquoi.
2. **Ce que le porteur doit faire hors dépôt**, s'il y a quelque chose (un
   processus à arrêter de son côté, un réglage à vérifier).
3. **Le premier message à envoyer après le `/clear`**, prêt à coller, qui
   pointe vers ce qui a été versé plutôt que de le répéter.

```
Un /clear est sûr : la décision du porteur est dans les notes de TASK-3 et le
fait vérifié sur le build X est versé dans docs/kimi-code-vs-bob.md. Rien ne
tourne en arrière-plan.

Après le /clear : « Quelle est la prochaine tâche ? »
```

```
Un /clear perdrait la mesure de X : je ne l'ai pas versée parce qu'elle ne vaut
que si la question Y est tranchée, et elle ne l'est pas.
```

Sans ces phrases, l'audit retombe sur le porteur — et c'est exactement ce que
cette skill existe pour lui éviter.

## Pourquoi il n'y a pas de hook

Les autres disciplines d'un projet peuvent être gatées par des hooks parce
qu'elles s'accrochent à un événement observable. Il n'y a **aucun événement
`/clear`** à intercepter : quand il arrive, il est déjà trop tard, et rien ne
s'exécute entre lui et l'effacement.

La discipline tient donc à un seul endroit : la fin de réponse. C'est fragile,
et c'est pour ça qu'elle est obligatoire plutôt que polie.
