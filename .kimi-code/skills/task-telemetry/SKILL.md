---
name: task-telemetry
description: Mesurer et persister la télémétrie réelle d'une tâche Backlog.md (appels, tokens, coût USD/EUR quand il existe, temps effectif vs pauses) depuis les transcripts Claude Code, les wire.jsonl de Kimi Code ou l'usage Cursor. À utiliser au rituel de fin de tâche, ou quand on demande « combien a coûté cette tâche », « télémétrie », « temps passé sur la tâche », « tokens consommés », « task cost/tokens », ou pour les vues globales Kimi Code (tokens par modèle/session/agent, taux de cache, outils, contexte).
---

# Task telemetry

Adaptée de la skill `task-telemetry` d'un projet voisin. Mesure la
consommation réelle d'une tâche Backlog.md et produit une ligne de note à
persister dans les notes de la tâche (source de vérité unique, à côté de
l'estimation d'effort éventuelle).

**Skill de développement** : elle vit dans `.kimi-code/skills/` — active en
travaillant sur ce dépôt, elle n'est pas livrée dans `skills/` et `install.sh`
ne l'installe pas.

## Quel runtime, quel script

| Qui a fait le travail | Runtime | Script | Fenêtre |
| --- | --- | --- | --- |
| Session courante | **Kimi Code** | `measure_kimi.py task` | marqueur In Progress → Done |
| Tâche finie avant le rituel | **Kimi Code** | `measure_kimi.py backfill` | (commit précédent, commit(s) de la tâche] |
| Vue d'ensemble (pas une tâche) | **Kimi Code** | `measure_kimi.py summary/sessions/calls/tools/context` | toutes sessions, ou `--since` |
| Session courante | **Claude Code** | `measure.py` | marqueur In Progress → dernier message |
| Sous-agent / vieille tâche | **Claude Code** | `backfill.py` | (commit précédent, commit(s) de la tâche] |
| Une session d'une tâche multi-sessions | **Claude Code** | `measure_session.py` | un transcript, du début à la fin |
| Session Agent / Auto | **Cursor** | `measure_cursor.py` | timestamps des tours × événements `cursor-usage` |

## Comment la source est détectée

Le script se choisit selon **l'outil qui a réellement fait le travail** — pas
selon le projet :

- **Kimi Code** : la session courante est Kimi Code (ce CLI), ou le projet a
  des sessions sous `~/.kimi-code/sessions/` dont le `workDir` (dans
  `~/.kimi-code/session_index.jsonl`) est le répertoire du projet →
  `measure_kimi.py`. Les wire.jsonl ne contiennent aucun bloc `usage` de style
  Anthropic ni prix.
- **Claude Code** : transcripts avec blocs `usage` Anthropic sous
  `~/.claude/projects/<chemin-assaini>/` → `measure.py` / `backfill.py` /
  `measure_session.py`.
- **Cursor** : transcripts d'agent sous `~/.cursor/projects/…/agent-transcripts/`
  + événements `cursor-usage` → `measure_cursor.py`.

Ne jamais mélanger les lignes de note de runtimes différents sans étiqueter la
source : les chiffres Claude Code sont des équivalents tarif API Anthropic, les
chiffres Cursor des équivalents tarif liste Cursor, et Kimi Code ne fournit que
des tokens (pas de prix). Ils ne sont pas comparables en une seule moyenne.

## Procédure Kimi Code (`measure_kimi.py`)

Source : `~/.kimi-code/sessions/wd_<slug>_<sha>/session_<id>/agents/<agent>/wire.jsonl`
(un wire.jsonl par agent : main, coder, explore…), indexé par
`~/.kimi-code/session_index.jsonl`. Les sessions du projet sont retrouvées par
`workDir`. Consommation : une ligne `usage.record` par tour
(`usageScope: "turn"`, `time` en epoch ms) — on les somme. Protocole vérifié :
**1.5** (le 2026-09-19) ; tout autre `protocol_version` déclenche un
avertissement sur stderr (`--strict` pour en faire une erreur).

1. Après le résumé final de la tâche, depuis le répertoire du projet :

   ```bash
   python3 .kimi-code/skills/task-telemetry/scripts/measure_kimi.py task --task-id <id>
   ```

   La fenêtre s'ouvre au marqueur `backlog task edit <id> -s "In Progress"`
   trouvé dans les appels Bash des wire.jsonl, et se ferme au marqueur
   `-s "Done"` le plus récent (ou `--end-ts <ISO>`, ou le dernier événement).
   Options : `--end-ts`, `--gap-threshold 120`, `--locale en`, `--json`,
   `--home`, `--strict`.

2. Tâche finie sans rituel (ou marqueur posé au dernier moment) :

   ```bash
   python3 .kimi-code/skills/task-telemetry/scripts/measure_kimi.py backfill --task-id <id>
   ```

   Fenêtre = (commit précédent, commit(s) de la tâche] — les sujets de commit
   doivent référencer `TASK-<id>` (`--id-pattern` sinon, `--commit SHA` en
   secours). Garder la mention « reconstruit » dans la ligne.

3. **Ce que les chiffres veulent dire — pas de prix côté Kimi.** Le schéma
   d'usage a un `total_cost_usd` optionnel **jamais rempli**. La ligne rendue
   rapporte des **tokens exacts** — avec le détail cache read / cache write,
   qui domine (~95 % de l'input : c'est ce qui tient le coût réel bas) — et
   marque le **coût comme indisponible**. Ne jamais inventer de tarif. Le quota
   (fenêtre 5 h, total mensuel) est côté serveur : c'est le rôle de `/usage` et
   de la console Kimi Code, pas de ce script.

4. Vues globales (héritées de l'ancienne skill kimi-telemetry) :

   ```bash
   python3 .kimi-code/skills/task-telemetry/scripts/measure_kimi.py summary
   python3 .kimi-code/skills/task-telemetry/scripts/measure_kimi.py sessions --since 2026-09-01
   python3 .kimi-code/skills/task-telemetry/scripts/measure_kimi.py tools --session session_8646
   ```

   | vue | répond à |
   |---|---|
   | `summary` | tokens totaux, par modèle et agent, taux de cache |
   | `sessions` | coût en tokens par session, avec répertoire de travail |
   | `calls` | chaque tour : tokens in/out, cache, modèle |
   | `tools` | nombre d'appels d'outils par agent |
   | `context` | taille de fenêtre de contexte mesurée par agent |

5. Persister :

   ```bash
   backlog task edit <id> --append-notes "<NOTE LINE imprimée par le script>"
   ```

## Procédure Claude Code (`measure.py`, `backfill.py`, `measure_session.py`)

Scripts copiés tels quels depuis le projet source ; voir leurs docstrings pour
le détail. En bref :

```bash
python3 .kimi-code/skills/task-telemetry/scripts/measure.py --task-id <id>
python3 .kimi-code/skills/task-telemetry/scripts/measure_session.py
python3 .kimi-code/skills/task-telemetry/scripts/backfill.py --task-id <id>
```

Points clés : déduplication par `message.id` ; découverte récursive des
transcripts (sous-agents inclus) ; coût = équivalent tarif liste API (snapshot
`PRICING_DATE` dans `measure.py`, surcharge `--price`) ; modèle non tarifé =
arrêt, jamais 0,00 USD ; `measure_session.py` pour une tâche multi-sessions
entrecoupée d'autres tâches (une ligne mesurée par session, jamais de
soustraction de lignes publiées).

## Procédure Cursor (`measure_cursor.py`)

Prérequis une fois par machine : `pip install cursor-usage` (lit la session
Cursor connectée ; accorder le réseau complet — une erreur 403 de tunnel
signifie un appel sandboxé). Puis :

```bash
python3 .kimi-code/skills/task-telemetry/scripts/measure_cursor.py \
    --task-id <id> --until-commit
```

Tarifs dans `cursor-pricing.json` (date du snapshot dans le fichier ; source
https://cursor.com/docs/models-and-pricing) ; `auto`/`default` tarifés comme
Composer 2.5. La « valeur compute incluse » du dashboard n'est pas de l'argent
dû sur un plan Included : la rapporter en seconde clause, jamais en
substitut. Options : `--csv` (export hors-ligne), `--transcript`, `--end-ts`,
`--match-window`.

## Devise : la ligne porte toujours des euros (runtimes tarifés)

Ordre de conversion, partagé par les trois scripts Claude/Cursor via
`measure.resolve_usd_eur` : `--usd-eur <taux>`, puis taux BCE du jour
(frankfurter.dev), puis repli daté `usd-eur-fallback.json`. Un run qui atteint
la BCE réécrit le fichier de repli — le committer. Sans aucune des trois
sources, le script sort plutôt que d'émettre une ligne en USD seul. Sans objet
pour Kimi Code, qui n'a pas de prix.

## Persistance et conventions

- La note se persiste avec `backlog task edit <id> --append-notes "<ligne>"` —
  compléter d'abord le placeholder des causes de pause.
- Ce dépôt n'impose **pas** la convention de labels `model:` des projets
  sources ; si on l'adopte, un label par runtime (`model: kimi-code/k3`,
  `model: claude-opus-5`, …) permet de filtrer les lignes de télémétrie par
  moteur. Optionnel.
- Une tâche multi-sessions se totalise en **additionnant une ligne mesurée par
  session** ; ne jamais soustraire des lignes publiées entre elles.

## Notes de méthode

- **Claude Code** : dédup par `message.id` (obligatoire) ; découverte récursive ;
  coût = équivalent tarif liste API.
- **Kimi Code** : une ligne `usage.record` par tour, somme directe ; fenêtre
  par marqueurs Backlog trouvés dans les `tool.call` Bash, ou par commits git ;
  tokens exacts, coût indisponible.
- **Cursor** : jointure par timestamp seul (± `--match-window`) ; list-price et
  valeur incluse dashboard sont deux quantités différentes.
- **L'euro n'est jamais optionnel** quand un prix existe.
