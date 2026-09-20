#!/usr/bin/env python3
"""Relève les traces mécaniques de ce qui disparaîtrait si le fil s'arrêtait ici.

Adapté d'un projet voisin. Ce script ne juge rien et ne verse rien. Il
rassemble les signaux qu'un agent oublie de regarder parce qu'ils ne sont pas
dans la conversation : un fichier modifié et jamais commité, un commit jamais
poussé, une tâche laissée In Progress, un processus de ce dépôt encore vivant,
un fichier d'exécution laissé à la racine du dépôt, un script qui n'existe que
dans le répertoire temporaire de la session.

Le jugement — « est-ce que ça compte ? où est-ce que ça se range ? » — est dans
SKILL.md, et il reste à la charge de qui lit. Un relevé vide ne veut pas dire
qu'un /clear est sûr : ce qui n'a jamais touché le disque n'a laissé aucune
trace ici, et c'est précisément le cas le plus dangereux.

Usage :
    pre-clear-audit.py [--repo <chemin>] [--session-dir <chemin>]

``--session-dir`` est le répertoire temporaire de travail de la session, si le
runtime en expose un. Sans lui, la section correspondante le dit simplement.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

#: Fichiers qu'on ne signale jamais comme « traces perdues » du répertoire de
#: session : du bruit d'exécution, jamais un travail à verser.
_BRUIT = {".DS_Store", "__pycache__"}

#: Fragments de ligne de commande qui identifient un processus que ce projet
#: (ou son outillage) peut avoir laissé tourner. Aucun spécifique pour
#: l'instant — étendre cette liste au premier besoin (ex. un serveur lancé à
#: la main pour une vérification, un conteneur de benchmark).
_MARQUEURS_PROCESSUS: tuple = ()

#: Processus qui portent le nom du dépôt dans leur ligne sans être une
#: exécution de ce projet (l'éditeur, ce script lui-même, le shell qui l'a
#: lancé).
_PROCESSUS_IGNORES = ("extension-host", "pre-clear-audit", "/bin/zsh -c", "grep ")

#: Fichiers d'exécution que ce projet écrit dans son répertoire de lancement
#: (jamais versionnés) — aucun connu pour l'instant, la liste s'enrichit au
#: premier besoin. Les trouver à la racine du dépôt signifie qu'un outil du
#: projet a été lancé depuis là pendant la session.
_FICHIERS_EXECUTION: tuple = ()


def _git(repo: Path, *args: str) -> str:
    """Une commande git, sortie nettoyée. Chaîne vide si git échoue —
    le script doit rester utile hors dépôt, pas s'arrêter.

    ``rstrip`` seulement : un ``strip()`` sur la sortie de ``git status
    --porcelain`` mange l'espace de tête de sa première ligne (format
    ``"XY chemin"``, ex. ``" M fichier"``) et décale ensuite tout
    ``ligne[3:]`` d'un caractère — le chemin affiché perd sa première lettre
    et peut manquer le bon préfixe de classement."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.rstrip("\n") if out.returncode == 0 else ""


def _titre(texte: str) -> None:
    print(f"\n## {texte}")


def _lignes(items: list, *, vide: str) -> None:
    if not items:
        print(f"  {vide}")
        return
    for item in items:
        print(f"  {item}")


def travail_non_commite(repo: Path) -> None:
    _titre("Travail non commité")
    brut = _git(repo, "status", "--porcelain")
    if not brut:
        _lignes([], vide="rien — l'arbre de travail est propre")
        return
    buckets = {
        "backlog (tâches, milestones, docs, décisions)": [],
        "skills livrées (skills/)": [],
        "outillage de dev (.kimi-code/)": [],
        "docs (docs/)": [],
        "reste": [],
    }
    for ligne in brut.splitlines():
        chemin = ligne[3:].strip().strip('"')
        if chemin.startswith("backlog/"):
            cle = "backlog (tâches, milestones, docs, décisions)"
        elif chemin.startswith("skills/"):
            cle = "skills livrées (skills/)"
        elif chemin.startswith(".kimi-code/"):
            cle = "outillage de dev (.kimi-code/)"
        elif chemin.startswith("docs/"):
            cle = "docs (docs/)"
        else:
            cle = "reste"
        buckets[cle].append(f"{ligne[:2].strip():<3} {chemin}")
    for label, items in buckets.items():
        if items:
            print(f"  — {label} :")
            _lignes([f"  {x}" for x in items], vide="")


def commits_non_pousses(repo: Path) -> None:
    _titre("Commits non poussés")
    branche = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    amont = _git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if not amont:
        print(f"  branche « {branche or '?'} » sans amont — rien n'est poussé nulle part")
        return
    devant = _git(repo, "log", "--oneline", f"{amont}..HEAD")
    if not devant:
        print(f"  aucun — {branche} est à jour avec {amont}")
        return
    print(f"  {len(devant.splitlines())} commit(s) d'avance sur {amont} :")
    _lignes([f"  {x}" for x in devant.splitlines()], vide="")


def taches_en_cours(repo: Path) -> None:
    _titre("Tâches laissées In Progress")
    try:
        out = subprocess.run(
            ["backlog", "task", "list", "--status", "In Progress", "--plain"],
            capture_output=True, text=True, timeout=60, cwd=str(repo),
        )
    except (OSError, subprocess.SubprocessError):
        print("  (backlog injoignable — à vérifier à la main)")
        return
    texte = (out.stdout or "").strip()
    if not texte or "No tasks" in texte:
        print("  aucune")
        return
    _lignes([f"  {l}" for l in texte.splitlines() if l.strip()], vide="")


def processus_vivants(repo: Path) -> None:
    _titre("Processus encore vivants")
    try:
        out = subprocess.run(
            ["ps", "-ax", "-o", "pid=,etime=,command="],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        print("  (ps injoignable — à vérifier à la main)")
        return
    moi = str(os.getpid())
    trouves = []
    for ligne in out.stdout.splitlines():
        pid = ligne.split(None, 1)[0] if ligne.strip() else ""
        if pid == moi or any(ignore in ligne for ignore in _PROCESSUS_IGNORES):
            continue
        # Une commande ne compte que si elle vise CE dépôt (un test, un
        # script lancé depuis sa racine), pas celle d'un autre projet ouvert
        # en parallèle — ou si elle correspond à un marqueur connu.
        notre_processus = str(repo) in ligne
        if notre_processus or any(marqueur in ligne for marqueur in _MARQUEURS_PROCESSUS):
            trouves.append(ligne.strip()[:160])
    _lignes(trouves, vide="aucun")
    if trouves:
        print(
            "  Un pid signalé vieux de quelques secondes, et absent quand on le "
            "relit (ps -p <pid> -ww), vient souvent de l'éditeur, pas de la "
            "session — vérifier qu'il a disparu avant de conclure ; ne jamais "
            "tuer un processus qu'on n'a pas lancé soi-même."
        )


def fichiers_execution_racine(repo: Path) -> None:
    _titre("Fichiers d'exécution à la racine du dépôt")
    trouves = []
    for nom in _FICHIERS_EXECUTION:
        p = repo / nom
        if p.is_file():
            trouves.append(f"{nom}  ({p.stat().st_size} o)")
    for p in sorted(repo.glob("*.db")) + sorted(repo.glob("*.sqlite3")):
        trouves.append(f"{p.name}  ({p.stat().st_size} o) — base SQLite à la racine")
    if not trouves:
        print("  aucun")
        return
    _lignes([f"  {x}" for x in trouves], vide="")
    print(
        "  Signale qu'un outil du projet a été lancé depuis la racine du dépôt "
        "pendant la session (ces fichiers sont en général gitignorés, jamais un "
        "travail à verser) — dire si le porteur doit les regarder avant qu'ils "
        "soient écrasés par le prochain lancement."
    )


def repertoire_session(chemin: str) -> None:
    _titre("Fichiers qui n'existent que dans le répertoire de session")
    if chemin is None:
        print(
            "  (non fourni — le passer avec --session-dir si le runtime expose "
            "un répertoire temporaire de session)"
        )
        return
    base = Path(chemin)
    if not base.is_dir():
        print(f"  (inexistant : {chemin})")
        return
    fichiers = [
        p for p in sorted(base.rglob("*"))
        if p.is_file() and not any(part in _BRUIT for part in p.parts)
    ]
    if not fichiers:
        print("  aucun")
        return
    print("  Chacun est perdu au prochain nettoyage. Trancher : jetable, à recréer, ou à verser :")
    for p in fichiers:
        taille = p.stat().st_size
        print(f"    {p.relative_to(base)}  ({taille} o)")


def main(argv=None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--repo", default=".")
    parseur.add_argument("--session-dir", dest="session_dir", default=None)
    args = parseur.parse_args(argv)

    repo = Path(args.repo).resolve()
    print(f"# Relevé pre-clear — {repo}")
    print(
        "\nCe relevé ne voit que ce qui a touché le disque. Ce qui n'est resté "
        "que dans la conversation\nn'y figure pas, et c'est là que se cache "
        "l'essentiel : voir SKILL.md."
    )
    travail_non_commite(repo)
    commits_non_pousses(repo)
    taches_en_cours(repo)
    processus_vivants(repo)
    fichiers_execution_racine(repo)
    repertoire_session(args.session_dir)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
