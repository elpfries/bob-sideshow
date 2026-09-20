#!/usr/bin/env python3
"""Reconstruct per-task telemetry for a task finished before the ritual existed.

Same measurement engine as measure.py (dedup by message.id, list pricing,
gaps > threshold counted as pauses) but a different window: measure.py needs
an "In Progress" marker, which old tasks either lack or set moments before
finishing — it would report 3 minutes for an hour of work.

Window here = (previous commit, task's own commit]. Every deduplicated
assistant record in that interval is charged to the task. Since the project's
commits partition the timeline without overlap, non-task commits (planning,
tooling) absorb their own work instead of inflating a neighbour.

That window is also what makes this the right tool when a SUBAGENT did the
work: it spans the orchestration and the delegated session alike, however many
sessions were involved, and transcript discovery is recursive
(measure.transcript_paths) so the subagent's own file is read too.

Requires: a git repo whose commit subjects reference the task id (e.g.
"Implement the lobby (TASK-9)"). Override discovery with --commit when they
do not.

Usage:
  backfill.py --task-id 9 [--project-dir PATH] [--commit SHA ...]
              [--id-pattern 'TASK-{id}'] [--usd-eur RATE] [--gap-threshold 120]
              [--price SUBSTR=IN,OUT[,READ,WRITE]] [--locale fr|en] [--json]

The emitted note line labels itself as reconstructed. Keep that label: this
window is wider than measure.py's (it includes the exploration before the task
was started and the finalisation after its summary), so the two are not
directly comparable — on this skill's home project the In Progress window came
out ~1.5x lower than the commit-to-commit one.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_spec = importlib.util.spec_from_file_location("measure", Path(__file__).with_name("measure.py"))
measure = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(measure)

USAGE_KEYS = measure.USAGE_KEYS


def git_log(project_dir: Path) -> list[tuple[str, str, str]]:
    """(short sha, UTC ISO commit date, subject) oldest first."""
    out = subprocess.run(
        ["git", "log", "--reverse", "--format=%h\x1f%cI\x1f%s"],
        cwd=project_dir, capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"git log failed in {project_dir}: {out.stderr.strip()}")
    commits = []
    for line in out.stdout.strip().splitlines():
        sha, iso, subject = line.split("\x1f", 2)
        utc = datetime.fromisoformat(iso).astimezone(timezone.utc)
        commits.append((sha, utc.isoformat().replace("+00:00", "Z"), subject))
    return commits


def match_commits(commits, task_id: str, id_pattern: str) -> list[int]:
    """Indices of commits whose subject references the task, word-bounded.

    Word-bounded so --task-id 1 does not also match TASK-11 or TASK-1.2.
    """
    token = id_pattern.replace("{id}", re.escape(task_id))
    rx = re.compile(rf"(?<![0-9A-Za-z]){token}(?![0-9.])", re.I)
    return [i for i, (_, _, subject) in enumerate(commits) if rx.search(subject)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task-id", required=True, help="task id as it appears in commit subjects")
    ap.add_argument("--project-dir", type=Path, default=Path.cwd())
    ap.add_argument("--transcripts-dir", type=Path, default=None)
    ap.add_argument("--commit", action="append", default=[],
                    help="task commit sha (repeatable); skips subject matching")
    ap.add_argument("--id-pattern", default="TASK-{id}",
                    help="how the task id appears in commit subjects (default: TASK-{id})")
    ap.add_argument("--gap-threshold", type=float, default=120.0, help="pause threshold, seconds")
    ap.add_argument("--usd-eur", type=float, default=None, help="rate; default: fetch ECB")
    ap.add_argument("--price", action="append", default=[],
                    metavar="SUBSTR=IN,OUT[,READ,WRITE]",
                    help="override $/M pricing for models whose id contains SUBSTR")
    ap.add_argument("--locale", choices=("fr", "en"), default="fr")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    overrides = []
    for spec in args.price:
        substr, _, values = spec.partition("=")
        parts = tuple(float(v) for v in values.split(","))
        if len(parts) not in (2, 4):
            ap.error(f"--price {spec!r}: expected IN,OUT or IN,OUT,READ,WRITE")
        overrides.append((substr, parts))

    commits = git_log(args.project_dir)
    if not commits:
        print(f"no commits in {args.project_dir}", file=sys.stderr)
        return 1

    if args.commit:
        wanted = {c[:7] for c in args.commit}
        idxs = [i for i, (sha, _, _) in enumerate(commits) if sha[:7] in wanted]
        missing = wanted - {commits[i][0][:7] for i in idxs}
        if missing:
            print(f"commit(s) not found: {sorted(missing)}", file=sys.stderr)
            return 1
    else:
        idxs = match_commits(commits, args.task_id, args.id_pattern)
        if not idxs:
            print(
                f"no commit subject matches {args.id_pattern.format(id=args.task_id)!r} — "
                f"pass --commit SHA, or --id-pattern if this repo names tasks differently",
                file=sys.stderr,
            )
            return 1

    first, last = idxs[0], idxs[-1]
    if idxs != list(range(first, last + 1)):
        skipped = [commits[i][0] for i in range(first, last + 1) if i not in idxs]
        print(f"note: interval also spans non-matching commit(s): {skipped}", file=sys.stderr)

    start_ts = commits[first - 1][1] if first > 0 else ""
    end_ts = commits[last][1]
    task_shas = [commits[i][0] for i in idxs]
    prev_sha = commits[first - 1][0] if first > 0 else "(dépôt initial)"

    tdir = args.transcripts_dir or measure.transcripts_dir_for(args.project_dir)
    paths = measure.transcript_paths(tdir)
    if not paths:
        print(f"no transcripts in {tdir}", file=sys.stderr)
        return 1

    by_id: dict[str, dict] = {}
    stamps: list[datetime] = []
    for entry in measure.iter_entries(paths):
        ts = entry.get("timestamp")
        if not ts or ts <= start_ts or ts > end_ts:
            continue
        stamps.append(measure.parse_ts(ts))
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("usage"), dict):
            continue
        key = message.get("id") or entry.get("uuid") or ts
        # keep the earliest sighting: a resumed session can replay a message id
        if key not in by_id or ts < by_id[key]["ts"]:
            by_id[key] = {"ts": ts, "model": message.get("model", "?"), "usage": message["usage"]}

    if not by_id:
        print(f"no assistant activity between {start_ts or 'repo start'} and {end_ts} — "
              f"transcripts for that period are gone", file=sys.stderr)
        return 1

    totals = defaultdict(lambda: defaultdict(int))
    calls = defaultdict(int)
    for record in by_id.values():
        calls[record["model"]] += 1
        for k in USAGE_KEYS:
            totals[record["model"]][k] += record["usage"].get(k) or 0

    stamps.sort()
    window_s = (stamps[-1] - stamps[0]).total_seconds()
    pauses = [(a, b, (b - a).total_seconds()) for a, b in zip(stamps, stamps[1:])
              if (b - a).total_seconds() > args.gap_threshold]
    pause_s = sum(g for _, _, g in pauses)
    active_s = window_s - pause_s

    rate, rate_fr, rate_en = measure.resolve_usd_eur(args.usd_eur)
    cost_usd = 0.0
    per_model_cost = {}
    unpriced = []
    for model, usage in totals.items():
        p = measure.price_for(model, overrides)
        if p is None:
            unpriced.append(model)
            continue
        pin, pout, pread, pwrite = p
        cost = (usage["input_tokens"] / 1e6 * pin
                + usage["output_tokens"] / 1e6 * pout
                + usage["cache_read_input_tokens"] / 1e6 * pread
                + usage["cache_creation_input_tokens"] / 1e6 * pwrite)
        per_model_cost[model] = (cost, p)
        cost_usd += cost
    measure.fail_on_unpriced(unpriced)
    cost_eur = cost_usd * rate

    grand = {k: sum(t[k] for t in totals.values()) for k in USAGE_KEYS}
    n_calls = sum(calls.values())
    models_label = " + ".join(f"{m.replace('claude-', '')}: {calls[m]}"
                              for m in sorted(calls, key=lambda m: -calls[m]))
    shas_label = ", ".join(task_shas)

    if args.json:
        print(json.dumps({
            "task_id": args.task_id,
            "mode": "backfill",
            "window": {"start": start_ts, "end": end_ts,
                       "prev_commit": prev_sha, "task_commits": task_shas},
            "calls": dict(calls),
            "usage_by_model": {m: dict(u) for m, u in totals.items()},
            "usage_total": grand,
            "window_min": round(window_s / 60, 1),
            "active_min": round(active_s / 60, 1),
            "pause_min": round(pause_s / 60, 1),
            "pauses": [{"from": a.isoformat(), "to": b.isoformat(), "seconds": round(g)}
                       for a, b, g in pauses],
            "cost_usd": round(cost_usd, 2),
            "cost_eur": round(cost_eur, 2),
            "usd_eur": rate,
            "usd_eur_note": rate_en,
            "pricing_date": measure.PRICING_DATE,
        }, ensure_ascii=False))
        return 0

    print(f"task {args.task_id} — backfill window {start_ts or 'repo start'} -> {end_ts}")
    print(f"  commits: {prev_sha} (exclusive) -> {shas_label} (inclusive)")
    print(f"  transcripts: {len(paths)} file(s) in {tdir}")
    for model in sorted(totals):
        usage = totals[model]
        cost, p = per_model_cost.get(model, (None, None))
        line = (f"  {model}: {calls[model]} calls, out {usage['output_tokens']:,}, "
                f"cache read {usage['cache_read_input_tokens']:,}, "
                f"cache write {usage['cache_creation_input_tokens']:,}, "
                f"fresh in {usage['input_tokens']:,}")
        if cost is not None:
            line += f" -> {cost:.2f} USD (in/out/read/write $/M = {p[0]}/{p[1]}/{p[2]}/{p[3]})"
        print(line)
    print(f"  TOTAL: {n_calls} calls -> {cost_usd:.2f} USD = {cost_eur:.2f} EUR ({rate_en})")
    print(f"  duration: window {window_s/60:.0f} min, active ≈ {active_s/60:.0f} min, "
          f"pauses ≈ {pause_s/60:.0f} min (gaps > {args.gap_threshold:.0f}s: {len(pauses)})")
    print(f"  pricing snapshot {measure.PRICING_DATE} — verify current list prices (claude-api skill)")

    if args.locale == "fr":
        note = (
            f"Télémétrie (relevé reconstruit depuis les commits, script backfill.py) : "
            f"{n_calls} appels API ({models_label}), "
            f"{grand['output_tokens']:,} tokens de sortie, "
            f"{grand['cache_read_input_tokens']:,} cache read, "
            f"{grand['cache_creation_input_tokens']:,} cache write, "
            f"≈ {cost_usd:.2f} USD ≈ {cost_eur:.2f} EUR équivalent API ({rate_fr} ; tarifs de "
            f"liste, pas une facture). "
            f"Méthode : la fenêtre est l'intervalle entre le commit précédent ({prev_sha}) et "
            f"le(s) commit(s) de la tâche ({shas_label}) — toute l'activité des transcripts sur "
            f"cet intervalle, sessions de sous-agent comprises, est imputée à la tâche. "
            f"Fenêtre (premier → dernier événement) {window_s/60:.0f} min, temps effectif "
            f"≈ {active_s/60:.0f} min (pauses ≈ {pause_s/60:.0f} min sur les écarts "
            f"> {args.gap_threshold:.0f} s). Écart de convention assumé : cette fenêtre englobe "
            f"l'exploration amont et la finalisation aval, que les relevés In Progress → résumé "
            f"final excluent."
        )
    else:
        note = (
            f"Telemetry (reconstructed from the commits, backfill.py): "
            f"{n_calls} API calls ({models_label}), "
            f"{grand['output_tokens']:,} output tokens, "
            f"{grand['cache_read_input_tokens']:,} cache read, "
            f"{grand['cache_creation_input_tokens']:,} cache write, "
            f"≈ {cost_usd:.2f} USD ≈ {cost_eur:.2f} EUR API-equivalent ({rate_en}; list prices, "
            f"not an invoice). "
            f"Method: the window is the interval between the previous commit ({prev_sha}) and "
            f"the task's commit(s) ({shas_label}) — all transcript activity in that interval, "
            f"subagent sessions included, is charged to the task. Window (first -> last "
            f"event) {window_s/60:.0f} min, effective ≈ {active_s/60:.0f} min (pauses "
            f"≈ {pause_s/60:.0f} min on gaps > {args.gap_threshold:.0f}s). Known convention gap: "
            f"this window includes the exploration before and the wrap-up after, which the "
            f"In Progress -> final summary readings exclude."
        )
    print("\nNOTE LINE (keep the 'reconstructed' label, then persist):")
    print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
