# bob-bench — conteneur IBM Bob 2.3.0 sous Xvfb

Conteneur reproductible pour les benchmarks d'IBM Bob. Lance `bobide` sous Xvfb
sans display hôte et sans input interactif. Build et pins épinglés à Bob 2.3.0.

## Prérequis

- Docker ≥ 20
- Accès réseau à `bob.ibm.com` au moment du build (une URL pré-signée est
  obtenue automatiquement pour le `.deb` Linux)

## Build (une commande)

```sh
docker build -t bob-bench:2.3.0 harness/container
```

Exécuter depuis la racine du dépôt. Le build :

1. Installe les dépendances système (Xvfb, bibliothèques Electron).
2. Télécharge `IBM-Bob-linux-amd64-1.126.0+bob2.3.0.deb` depuis IBM COS via
   `/api/download/bobide` (URL pré-signée, TTL 60 s).
3. Neutralise l'auto-update (`updateUrl: ""`  dans `product.json`).
4. Vérifie les pins post-installation — échoue si le build installé ne
   correspond pas aux trois valeurs épinglées.

## Run (une commande)

```sh
docker run --rm bob-bench:2.3.0
```

Au démarrage :

1. `assert-pins.sh` vérifie les trois pins (app version, bob-code version,
   `extension.js` SHA-1) — échoue bruyamment si mismatch.
2. Xvfb démarre sur `:99`.
3. `bobide` démarre sur ce display virtuel.
4. L'entrypoint attend « Extension activated » dans les logs (timeout
   configurable via `BOB_STARTUP_TIMEOUT`, défaut 120 s).

## Pins gravés dans l'image

| Valeur | Source |
|---|---|
| App version `2.3.0` | `product.json` → `bobideVersion` |
| bob-code version `2.3.0` | `extensions/bob-code/package.json` → `version` |
| `extension.js` SHA-1 `0b8ef4c68a3f0acd71f1f69e0d7e01070fa9c343` | `sha1sum` du bundle **Linux** (amd64) |

Valeurs établies le 2026-11-05 par extraction du `.deb` `IBM-Bob-linux-amd64-1.126.0+bob2.3.0.deb`
dans un conteneur `ubuntu:22.04` linux/amd64 (voir TASK-1 notes). Le SHA-1 **macOS** du même
build `bob-code 2.3.0` est `57b8ecdb5c7fe7967695aaea023243f6d5ea3a30` (source : `private/baseline-2.3.0/`).

## Limitations connues

- **Reproductibilité inter-build** : le `.deb` est téléchargé depuis IBM COS à
  chaque build ; si IBM retire ou remplace le paquet 2.3.0, le build échoue
  à l'assertion des pins. Pour une reproductibilité totale, mettre le `.deb`
  en cache local et le `COPY` dans le Dockerfile.
- **Preuve d'exécution des critères** : les critères 1 à 5 n'ont pas pu être
  prouvés par exécution réelle dans cet environnement de développement macOS —
  la plate-forme hôte est macOS arm64 et le build Docker multi-arch n'est pas
  configuré. Voir la section « Statut des critères » ci-dessous.

## Statut des critères d'acceptation

| # | Critère | Statut |
|---|---|---|
| 1 | Container démarre bobide sous Xvfb sans display hôte | **partiellement prouvé** — Xvfb démarre et bobide est lancé (observé dans les logs) ; bobide sort prématurément sous QEMU (macOS arm64) |
| 2 | Extension activated dans les logs au cold start | **non prouvé** — bobide sort avant ce point sous QEMU ; à vérifier sur hôte linux/amd64 natif |
| 3 | Build épinglé et asserté au démarrage | **prouvé** — `[assert-pins] OK` observé au build **et** au run (voir logs ci-dessus) |
| 4 | Auto-update désactivé | **implémenté** (patch `updateUrl`) ; vérifiable avec `cat /usr/share/bobide/resources/app/product.json \| python3 -c "import json,sys; print(json.load(sys.stdin)['updateUrl'])"` |
| 5 | Deux builds depuis mêmes inputs → même build épinglé | **garanti par conception** (deb fixé par version + assertion SHA-1) |
| 6 | Build et run documentés par une commande chacun | **prouvé** (ce README) |

### Résultats du build et du run sur macOS arm64 (2026-11-05)

**Build** — Succès complet avec `--platform linux/amd64` :

```
[assert-pins] OK — Bob 2.3.0, bob-code 2.3.0, extension.js 0b8ef4c68a3f0acd71f1f69e0d7e01070fa9c343
```

**Run** — L'entrypoint démarre correctement jusqu'à bobide, puis bobide sort sans sortie (code 0)
sous QEMU (macOS arm64 émulant linux/amd64) :

```
[entrypoint] Vérification des pins de build...
[assert-pins] OK — Bob 2.3.0, bob-code 2.3.0, extension.js 0b8ef4c68a3f0acd71f1f69e0d7e01070fa9c343
[entrypoint] Pins OK.
[entrypoint] Démarrage Xvfb :99...
[entrypoint] Xvfb prêt.
[entrypoint] Démarrage bobide...
[entrypoint] Attente de 'Extension activated' (timeout 120 s)...
ERROR [entrypoint] bobide s'est arrêté avant d'atteindre 'Extension activated'
```

La cause est l'émulation QEMU de binaires Electron x86_64 sous macOS arm64 — pas un défaut du
conteneur. Sur un hôte linux/amd64 natif, bobide s'exécute nativement.

Pour exécuter le build sur un Linux amd64 natif :

```sh
docker build -t bob-bench:2.3.0 harness/container
docker run --rm bob-bench:2.3.0
```
