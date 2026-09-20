---
name: quota-check
description: Relever le quota d'abonnement Kimi Code (fenêtre 5 h, mensuel, Extra Usage) sans le TUI, via le serveur local de l'app Desktop ou de `kimi web`. À utiliser quand l'utilisateur demande « où en est mon quota », « usage », « pourcentage du quota », « temps avant reset », « burn rate » ou « vais-je tenir jusqu'à la fin du mois ».
---

# Quota check

`python3 "<skill-dir>/scripts/quota_check.py" [--json]`

Le quota d'abonnement est calculé côté serveur : aucun fichier local ne le reflète. Mais l'app
Desktop et `kimi web` exposent localement la route que la commande `/usage` du CLI interroge :

```
GET http://127.0.0.1:<port>/api/v1/oauth/usage
Authorization: Bearer <~/.kimi-code/server.token>
```

Le script découvre port et token tout seuls (`~/.kimi-code/server/instances/*.json` + heartbeat
récent) et affiche, pour la fenêtre 5 h et le quota mensuel : pourcentage consommé, temps restant
avant reset, et **burn rate** = % du quota consommé ÷ % de la période écoulée. 100 % =
dans les temps ; 200 % = épuisement deux fois trop vite. Si le burn rate dépasse 100 %, la date
d'épuisement projetée est affichée.

Prérequis : l'app Kimi Code Desktop ou `kimi web` doit tourner (sinon pas de serveur local).
Le port et le token changent au redémarrage — le script les relit à chaque appel. Attention en
sondant le serveur à la main : il sert la SPA du web UI avec un code 200 sur toute route
inconnue — seule une réponse JSON avec `code == 0` prouve que la route existe.

En expliquant les chiffres :
- `limit5h` : fenêtre glissante de 5 heures (rate limit).
- `monthTotal` : quota mensuel global, partagé entre Kimi web et Kimi Code.
- `monthCode` : sous-compteur coding du mois.
- En début de période (moins de ~5 % écoulée), le burn rate est très instable : le dire plutôt
  que d'alarmer sur un chiffre énorme.

Vérifié le 2026-09-20 contre le serveur local de Kimi Code Desktop 2.0.1 (host_version du fichier
d'instance), route trouvée dans `dist/main.mjs` du formulaire Homebrew `kimi-code` 2.0.1.
Tokens exacts par session : c'est la skill `task-telemetry` (wire.jsonl), pas celle-ci.
