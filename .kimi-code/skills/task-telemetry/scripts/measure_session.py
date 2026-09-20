#!/usr/bin/env python3
"""Télémétrie d'UNE session Claude Code, pas d'une fenêtre de tâche.

Pourquoi ce script existe, à côté de ``measure.py``
---------------------------------------------------
``measure.py`` ouvre sa fenêtre au marqueur « In Progress » de la tâche et
compte **tout** ce qui a tourné dedans, tous journaux confondus. C'est le bon
comportement pour une tâche traitée d'un trait, y compris déléguée à des
sous-agents : leur coût appartient bien à la tâche.

Ça devient faux dès qu'une tâche s'étale sur plusieurs sessions **entrecoupées
d'autres tâches**. Mesuré sur un projet voisin : le marqueur datait de la
première session, la fenêtre couvrait plusieurs heures, et le total incluait
deux autres tâches traitées entre-temps. Publier ce chiffre aurait attribué
à une tâche le coût de deux autres.

``measure.py`` n'a pas de symétrique à ``--end-ts`` : on ne peut pas lui
imposer un début. D'où ce script, qui garde **exactement** sa méthode —
déduplication par ``message.id``, même table de tarification, même seuil de
pause, même résolution du taux USD/EUR — et change seulement le périmètre :
un journal, celui de la session qui mesure.

Ne pas obtenir ce chiffre par **soustraction** de lignes publiées : les
fenêtres se recouvrent, les sessions non mesurées manquent, et une soustraction
de deux totaux arrondis n'est pas une mesure.

Usage
-----
    python3 .claude/skills/task-telemetry/scripts/measure_session.py            # session courante, devinée
    python3 .claude/skills/task-telemetry/scripts/measure_session.py --transcript <fichier.jsonl>
    python3 .claude/skills/task-telemetry/scripts/measure_session.py --json

Sans ``--transcript``, le journal le plus récemment modifié du projet est
retenu — c'est celui de la session en cours quand on lance le script depuis
elle. Le script imprime le chemin retenu : le vérifier avant de recopier la
ligne.

La ligne rendue porte le suffixe « — session <id> » pour qu'on ne la confonde
jamais avec un total de tâche. Une tâche multi-sessions se totalise en
additionnant une ligne par session, chacune mesurée.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure as M  # noqa: E402  (le sys.path doit être posé avant)


def pick_transcript(project_dir: Path) -> Path:
    """Le journal le plus récemment écrit du projet — la session en cours."""
    tdir = M.transcripts_dir_for(project_dir)
    paths = sorted(tdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not paths:
        raise SystemExit(f"aucun journal dans {tdir}")
    return paths[-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--transcript", type=Path, default=None)
    ap.add_argument("--project-dir", type=Path, default=Path("."))
    ap.add_argument("--gap-threshold", type=float, default=120.0)
    ap.add_argument("--usd-eur", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = args.transcript or pick_transcript(args.project_dir.resolve())

    by_id: dict[str, dict] = {}
    stamps = []
    for entry in M.iter_entries([path]):
        ts = entry.get("timestamp")
        if not ts:
            continue
        stamps.append(M.parse_ts(ts))
        if entry.get("type") != "assistant":
            continue
        msg = entry.get("message")
        if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
            continue
        by_id[msg.get("id") or entry.get("uuid") or ts] = {
            "model": msg.get("model", "?"),
            "usage": msg["usage"],
        }
    if not stamps:
        raise SystemExit(f"journal vide ou illisible : {path}")

    totals: dict = defaultdict(lambda: defaultdict(int))
    calls: dict = defaultdict(int)
    for record in by_id.values():
        calls[record["model"]] += 1
        for key in M.USAGE_KEYS:
            totals[record["model"]][key] += record["usage"].get(key) or 0

    stamps.sort()
    window_s = (stamps[-1] - stamps[0]).total_seconds()
    pauses = [
        (a, b, (b - a).total_seconds())
        for a, b in zip(stamps, stamps[1:])
        if (b - a).total_seconds() > args.gap_threshold
    ]
    pause_s = sum(g for _, _, g in pauses)

    rate, rate_fr, rate_en = M.resolve_usd_eur(args.usd_eur)
    cost_usd = 0.0
    unpriced = []
    for model, usage in totals.items():
        priced = M.price_for(model, [])
        if priced is None:
            unpriced.append(model)
            continue
        pin, pout, pread, pwrite = priced
        cost_usd += (
            usage["input_tokens"] / 1e6 * pin
            + usage["output_tokens"] / 1e6 * pout
            + usage["cache_read_input_tokens"] / 1e6 * pread
            + usage["cache_creation_input_tokens"] / 1e6 * pwrite
        )
    M.fail_on_unpriced(unpriced)

    grand = {k: sum(t[k] for t in totals.values()) for k in M.USAGE_KEYS}
    n_calls = sum(calls.values())
    models = " + ".join(f"{m.replace('claude-', '')}: {calls[m]}" for m in sorted(calls))
    session_id = path.stem

    if args.json:
        print(json.dumps({
            "transcript": str(path),
            "session_id": session_id,
            "window": {"start": stamps[0].isoformat(), "end": stamps[-1].isoformat()},
            "calls": dict(calls),
            "usage_total": grand,
            "window_min": round(window_s / 60, 1),
            "active_min": round((window_s - pause_s) / 60, 1),
            "pause_min": round(pause_s / 60, 1),
            "pauses": [{"from": a.isoformat(), "to": b.isoformat(),
                        "seconds": round(g)} for a, b, g in pauses],
            "cost_usd": round(cost_usd, 2),
            "cost_eur": round(cost_usd * rate, 2),
            "usd_eur": rate,
            "usd_eur_note": rate_en,
            "pricing_date": M.PRICING_DATE,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"journal   : {path}")
    print(f"fenêtre   : {stamps[0]} -> {stamps[-1]}")
    print(f"pricing snapshot {M.PRICING_DATE} — vérifier les tarifs courants (skill claude-api)")
    print("pauses > seuil :")
    for a, b, g in pauses:
        print(f"   {g / 60:6.1f} min  {a:%H:%M:%S} -> {b:%H:%M:%S}")
    print()
    print("NOTE LINE (compléter les causes de pause, puis persister) :")
    print(
        f"Télémétrie — session {session_id} : {n_calls} appels API ({models}), "
        f"{grand['output_tokens']:,} tokens de sortie, "
        f"{grand['cache_read_input_tokens']:,} cache read, "
        f"{grand['cache_creation_input_tokens']:,} cache write, "
        f"≈ {cost_usd:.2f} USD ≈ {cost_usd * rate:.2f} EUR équivalent API ({rate_fr}). "
        f"Fenêtre {window_s / 60:.0f} min, temps effectif ≈ {(window_s - pause_s) / 60:.0f} min "
        f"(pauses ≈ {pause_s / 60:.0f} min : <causes à compléter>)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
