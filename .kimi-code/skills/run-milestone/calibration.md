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

(Aucune milestone mesurée pour l'instant — ce fichier se remplit à la clôture
de chaque milestone, phase 5.)
