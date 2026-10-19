# Calibration — chiffres réels par milestone

Une section par milestone, une ligne par tâche. Lu par la phase 0 (annonce de
budget) et la phase 6 (ré-estimation à la frontière) de la skill
`run-milestone`. Ne jamais citer ici un chiffre venu d'un autre projet.

Convention : le coût est celui de la fenêtre de commits (commit précédent →
commit de la tâche), donc il **inclut l'orchestration de la session
principale** — brief, relecture du rapport, mesure. Le temps est le temps
effectif de traitement, pas le temps mur-à-mur.

Format d'une section :

```
## m-N — <titre de la milestone>

Chaîne conduite depuis <runtime et modèle de la session principale> ;
sous-agents sur <modèle(s)>. Le coût inclut l'orchestration.

| Tâche | Nature | Modèle | Coût | Temps effectif |
|---|---|---|---|---|
| TASK-N (…) | … | … | … | … |
| **Total** | N tâches | | … | … |

Estimation annoncée au lancement : … Enseignements chiffrés, à réutiliser pour
estimer la suite : …
```

## m-1 — v2.2.0 adaptations (close le 2026-09-29)

Chaîne conduite depuis Claude Code / Fable 5.1 (session principale) ;
sous-agents sur Fable (label `model:primaire`) et Sonnet (`model:secondaire`).
Coûts = équivalent tarif liste API Anthropic (script `backfill.py`, taux BCE
de repli 1 USD = 0,8610 EUR), pas une facture. Le coût inclut l'orchestration.

| Tâche | Nature | Modèle | Coût | Temps effectif |
|---|---|---|---|---|
| (hors tâche) création de la milestone et des 5 tâches | rédaction backlog, relevé 2.2.0 | Fable (session) | 3,00 EUR | 8 min |
| (hors tâche) arbitrages utilisateur, snapshot de la base | orchestration | Fable (session) | 0,80 EUR | 2 min |
| TASK-13.4 — analyse de conception (`analyze-task`, session principale) | conception + prototype de l'outil de diff, téléchargement du build 2.1.0 | Fable (session) | 14,92 EUR | 29 min |
| TASK-13.4 — implémentation (delta 2.1.0 → 2.2.0, page docs/) | reverse-engineering, doc publique, vérificateur indépendant | Fable (agent) | 22,60 EUR | 34 min |
| TASK-13.1 — faits et ancres 2.2.0, template réparé | relecture claim par claim de 3 notes, 193 littéraux vérifiés | Sonnet | 7,27 EUR | 18 min |
| TASK-13.2 — base et scripts sur trafic 2.2.0 réel | vérification + 2 scripts corrigés, vérificateur indépendant | Sonnet | 3,31 EUR | 15 min |
| TASK-13.3 — ré-étiquetage, `VERIFIED_*`, CHANGELOG | 20 fichiers, 1 coupure de session reprise sans travail refait | Sonnet | 6,62 EUR | 13 min |
| (hors tâche) clôture : TASK-13 prouvée et close, `install.sh` à froid, calibration | orchestration | Fable (session) | 2,50 EUR | 3 min |
| (hors tâche) réouverture : deux restes trouvés à froid, TASK-14 et TASK-15 créées | rédaction backlog | Fable (session) | 2,84 EUR | 4 min |
| TASK-14 — `premium-subagents.md` (`modelTier`), `rule_locations.py` sur les racines `plugins/` et la confiance 2.2.0 | correction ciblée, test sur dossier jetable | Sonnet | 1,70 EUR | 4 min |
| TASK-15 — procédure de re-vérification en huit étapes, 46 ancres durables, baseline 2.2.0, répétition à blanc | outillage privé + vérificateur indépendant | Sonnet | 3,31 EUR | 15 min |
| **Total** | 6 tâches + parente + orchestration | | **68,87 EUR** | **145 min** |

Deux critères ont exigé l'utilisateur (son Bob, son compte) : lancer une tâche
Bob 2.2.0 pour produire des appels tarifés et un prompt stocké, et charger le
template d'agent corrigé dans une tâche neuve. Coût nul, mais un arrêt de
chaîne chacun — à prévoir comme tel.

Estimation annoncée au lancement : aucune (fichier vide, première milestone
mesurée). Enseignements chiffrés, à réutiliser pour estimer la suite :

- **Une tâche `model:primaire` coûte ~5× une tâche secondaire** : 37,5 EUR
  (analyse + implémentation, 63 min) contre 3,3–7,3 EUR (13–18 min) pour les
  trois tâches Sonnet. L'analyse de conception seule (14,92 EUR) a coûté plus
  que n'importe quelle tâche secondaire entière — mais c'est elle qui a
  produit l'outil et la preuve dont les trois autres ont vécu.
- **Une tâche secondaire briefée sur un plan et des verdicts déjà établis
  tourne en 13–18 min pour 3–7 EUR**, vérificateur indépendant compris.
- **L'orchestration hors tâches** (création, arbitrages, mesures, clôture)
  pèse ~4 EUR sur la milestone, soit ~7 % — négligeable tant que la session
  principale n'implémente pas.
- **Le temps mur-à-mur ment** : 13.3 affiche 25 min de fenêtre pour 13 min de
  travail (coupure de session + attente de reprise) ; la création des tâches,
  25 min pour 8. Citer le temps effectif.
- **Compter un arrêt de chaîne par critère qui exige la machine de
  l'utilisateur**, et regrouper ces critères pour n'en faire qu'un.

## Hors milestone — TASK-16 : re-vérification sur Bob 2.2.3 (close le 2026-10-19)

Chaîne conduite depuis Claude Code / Fable 5.1 (session principale) ; sous-agents sur Sonnet
(`model:secondaire`). Coûts = équivalent tarif liste API (script `backfill.py`, taux de repli
1 USD = 0,8610 EUR), pas une facture. Le coût inclut l'orchestration.

| Tâche | Nature | Modèle | Coût | Temps effectif |
|---|---|---|---|---|
| (hors tâche) diff 2.2.0→2.2.1→2.2.3, création de TASK-16 et ses deux sous-tâches | relevé + rédaction backlog, sur deux sessions (2026-10-05, 2026-10-19) | Fable (session) | non mesuré (hors fenêtre de commit) | ≈ 20 min |
| TASK-16.1 — baselines 2.2.1/2.2.3 avec webview, récupération 2.2.0/2.2.1 depuis le serveur de mise à jour (lecture Range HTTP), étape 2 amendée | outillage privé + vérificateur indépendant | Sonnet | 3,59 EUR | 22 min |
| TASK-16.2 — étapes 6-8, bump `VERIFIED_*`, 13 fichiers ré-étiquetés, CHANGELOG 0.4 | ré-étiquetage guidé par une règle écrite dans le brief | Sonnet | 3,16 EUR (dont un lancement coupé par une erreur réseau, sans travail refait) | 16 min |
| (hors tâche) mesures, contrôles à froid (`install.sh`, cinq scripts), clôture du parent | orchestration | Fable (session) | ≈ 1 EUR | ≈ 5 min |
| **Total** | 2 sous-tâches + parente + orchestration | | **≈ 7,8 EUR** | **≈ 63 min** |

Estimation annoncée au lancement : 5–15 EUR, 20–35 min effectives pour les deux sous-tâches
(d'après les lignes Sonnet de m-1). Réalisé : 6,75 EUR et 38 min pour les deux — dans la
fourchette de coût, au-dessus en temps à cause de la récupération réseau de 16.1.

Enseignements chiffrés :

- **Un build Bob sans changement de bundle coûte quand même ~7 EUR à re-vérifier** : le coût
  est dans la preuve et le ré-étiquetage, pas dans le delta.
- **Un critère qui exige la machine de l'utilisateur** (lancer une tâche Bob sur le nouveau
  build) a de nouveau arrêté la chaîne une fois ; posé comme question unique avant le premier
  agent, il n'a rien coûté en attente.
- **Une coupure réseau d'un agent avant toute écriture coûte ~1 EUR** (le brief relu par un
  agent neuf) et zéro travail refait, si l'arbre est inventorié avant la relance.
