#!/usr/bin/env python3
"""Measure per-task telemetry for Cursor Agent / Auto sessions.

Claude Code transcripts carry Anthropic-style ``usage`` blocks; Cursor Agent
transcripts do not. This script fills that gap:

1. Export usage events via ``cursor-usage --csv`` (local Cursor session →
   dashboard API), or reuse an existing CSV (``--csv``).
2. Find the Cursor agent transcript(s) that mention the task.
3. Match each user turn's ``<timestamp>`` to the nearest usage event
   (± ``--match-window`` seconds).
4. Price matched events at Cursor list rates
   (``.claude/skills/task-telemetry/cursor-pricing.json``).
   ``auto`` / ``default`` → Composer 2.5 (project rule).

Emits the same style of note line as ``measure.py``, labelled
« Cursor Auto / cursor-usage » so it is never confused with a Claude Code
API-list reading.

Requires: ``pip install cursor-usage`` (reads the signed-in Cursor session).
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("measure", Path(__file__).with_name("measure.py"))
measure = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(measure)

SKILL_DIR = Path(__file__).resolve().parent.parent
PRICING_PATH = SKILL_DIR / "cursor-pricing.json"

TS_LABEL_RE = re.compile(
    r"<timestamp>\s*([^<]+?)\s*</timestamp>",
    re.I,
)
USER_QUERY_RE = re.compile(
    r"<user_query>\s*(.*?)\s*</user_query>",
    re.S | re.I,
)
# Monday, Aug 31, 2026, 3:59 AM (UTC+2)
TS_PARSE_RE = re.compile(
    r"^(?P<weekday>\w+),\s+(?P<month>\w+)\s+(?P<day>\d{1,2}),\s+(?P<year>\d{4}),\s+"
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2})\s+(?P<ampm>AM|PM)\s+\(UTC(?P<off>[+-]\d{1,2})\)$",
    re.I,
)


def load_pricing() -> dict:
    with PRICING_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_model(raw: str, pricing: dict) -> str:
    key = (raw or "").strip().lower().replace("_", "-")
    aliases = {k.lower(): v for k, v in pricing.get("aliases", {}).items()}
    if key in aliases:
        return aliases[key]
    if key in pricing["models"]:
        return key
    remaps = {k.lower(): v for k, v in pricing.get("substring_to_model", {}).items()}
    models = pricing["models"]
    # Longer / more specific substrings first (order is load-bearing)
    for substr in pricing.get("substring_order", []):
        s = substr.lower()
        if s not in key:
            continue
        if s in remaps:
            return remaps[s]
        if s in models:
            return s
        stripped = s[len("cursor-"):] if s.startswith("cursor-") else s
        if stripped in models:
            return stripped
    return key


def rates_for(canonical: str, pricing: dict) -> tuple[float, float, float, float] | None:
    m = pricing["models"].get(canonical)
    if not m:
        return None
    return (
        float(m["input"]),
        float(m["output"]),
        float(m["cache_read"]),
        float(m.get("cache_write") or 0.0),
    )


def cursor_transcripts_dir(project_dir: Path) -> Path:
    """~/.cursor/projects/<sanitized>/agent-transcripts — same layout Cursor uses."""
    # Cursor drops the leading slash and replaces / with -
    sanitized = str(project_dir.resolve()).lstrip("/").replace("/", "-")
    return Path.home() / ".cursor" / "projects" / sanitized / "agent-transcripts"


def parse_ts_label(label: str) -> datetime | None:
    m = TS_PARSE_RE.match(label.strip())
    if not m:
        return None
    # Build a naive local then attach fixed offset
    try:
        dt = datetime.strptime(
            f"{m.group('month')} {m.group('day')} {m.group('year')} "
            f"{m.group('hour')}:{m.group('minute')} {m.group('ampm').upper()}",
            "%b %d %Y %I:%M %p",
        )
    except ValueError:
        return None
    off = int(m.group("off"))
    return dt.replace(tzinfo=timezone(timedelta(hours=off)))


def iter_user_turns(transcript: Path) -> list[tuple[datetime, str, Path]]:
    turns: list[tuple[datetime, str, Path]] = []
    with transcript.open(errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("role") != "user":
                continue
            text = ""
            content = (obj.get("message") or {}).get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text += block.get("text") or ""
            elif isinstance(content, str):
                text = content
            tm = TS_LABEL_RE.search(text)
            if not tm:
                continue
            dt = parse_ts_label(tm.group(1))
            if dt is None:
                continue
            qm = USER_QUERY_RE.search(text)
            query = (qm.group(1) if qm else text[:120]).strip().replace("\n", " ")
            turns.append((dt, query, transcript))
    return turns


def task_mention_re(task_id: str) -> re.Pattern:
    norm = re.sub(r"^task-", "", task_id, flags=re.I)
    # TASK-53, task 53, tâche 53, tache 53
    return re.compile(
        rf"(?:task[-\s]?{re.escape(norm)}\b|t[aâ]che\s*{re.escape(norm)}\b)",
        re.I,
    )


def find_task_transcripts(tdir: Path, task_id: str) -> list[Path]:
    rx = task_mention_re(task_id)
    hits: list[tuple[int, Path]] = []
    if not tdir.is_dir():
        return []
    for path in tdir.rglob("*.jsonl"):
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        n = len(rx.findall(text))
        if n:
            hits.append((n, path))
    hits.sort(key=lambda x: (-x[0], -x[1].stat().st_mtime))
    return [p for _, p in hits]


def run_cursor_usage_csv(start: datetime, end: datetime, out: Path) -> None:
    exe = shutil.which("cursor-usage")
    if exe is None:
        # Prefer project venv
        venv = Path.cwd() / ".venv" / "bin" / "cursor-usage"
        exe = str(venv) if venv.is_file() else None
    if exe is None:
        raise SystemExit(
            "cursor-usage not found — install with "
            "`pip install cursor-usage` (or `.venv/bin/pip install cursor-usage`)"
        )
    start_d = start.astimezone(timezone.utc).date().isoformat()
    # cursor-usage --end is inclusive calendar day; bump if end is late UTC
    end_d = end.astimezone(timezone.utc).date().isoformat()
    cmd = [exe, "--start", start_d, "--end", end_d, "--csv", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise SystemExit(
            f"cursor-usage failed ({proc.returncode}):\n{detail}\n"
            "Hint: needs the signed-in Cursor session + outbound HTTPS to "
            "cursor.com (disable sandbox / grant full network). "
            "Or pass --csv from a dashboard export / a prior cursor-usage run."
        )


def load_events(csv_path: Path) -> list[dict]:
    events = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Support both cursor-usage columns and dashboard export columns
            if "timestamp_ms" in row and row.get("timestamp_ms"):
                ms = int(float(row["timestamp_ms"]))
                dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
                model = row.get("model") or ""
                inp = int(float(row.get("input_tokens") or 0))
                out = int(float(row.get("output_tokens") or 0))
                cread = int(float(row.get("cache_read_tokens") or 0))
                cwrite = int(float(row.get("cache_write_tokens") or 0))
                value_cents = float(row.get("value_cents") or 0)
            elif "Date" in row:
                raw_in = (row.get("Input (w/o Cache Write)") or "").strip()
                raw_out = (row.get("Output Tokens") or "").strip()
                raw_cr = (row.get("Cache Read") or "").strip()
                raw_cw = (row.get("Input (w/ Cache Write)") or "").strip()
                if not raw_in and not raw_out and not raw_cr:
                    continue  # Free / empty rows
                dt = datetime.fromisoformat(row["Date"].replace("Z", "+00:00"))
                model = row.get("Model") or ""
                inp = int(float(raw_in or 0))
                out = int(float(raw_out or 0))
                cread = int(float(raw_cr or 0))
                cwrite = int(float(raw_cw or 0))
                value_cents = 0.0
            else:
                continue
            events.append(
                {
                    "dt": dt,
                    "model": model,
                    "input": inp,
                    "output": out,
                    "cache_read": cread,
                    "cache_write": cwrite,
                    "value_cents": value_cents,
                }
            )
    events.sort(key=lambda e: e["dt"])
    return events


def match_turns_to_events(
    turns: list[tuple[datetime, str, Path]],
    events: list[dict],
    window_s: float,
) -> list[tuple[datetime, str, dict, float]]:
    used: set[int] = set()
    matched = []
    for turn_dt, query, _path in turns:
        utc = turn_dt.astimezone(timezone.utc)
        best_i = None
        best_d = None
        for i, ev in enumerate(events):
            if i in used:
                continue
            d = abs((ev["dt"] - utc).total_seconds())
            if d <= window_s and (best_d is None or d < best_d):
                best_i, best_d = i, d
        if best_i is not None:
            used.add(best_i)
            matched.append((turn_dt, query, events[best_i], best_d))
    return matched


def git_task_commit_time(project_dir: Path, task_id: str) -> datetime | None:
    """Latest commit subject mentioning TASK-<id>, for --until-commit."""
    norm = re.sub(r"^task-", "", task_id, flags=re.I)
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cI", f"--grep=TASK-{norm}", "-E", "-i"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    if out.returncode != 0 or not out.stdout.strip():
        # fallback: subject contains task id
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", f"--grep={norm}", "-i"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
    iso = out.stdout.strip()
    if not iso:
        return None
    return datetime.fromisoformat(iso).astimezone(timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument(
        "--csv",
        type=Path,
        help="reuse an existing usage CSV (cursor-usage or dashboard export); "
        "skips calling cursor-usage",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        action="append",
        help="explicit agent transcript .jsonl (repeatable); default: auto-discover",
    )
    parser.add_argument(
        "--match-window",
        type=float,
        default=180.0,
        help="max seconds between user-turn timestamp and usage event (default 180)",
    )
    parser.add_argument(
        "--until-commit",
        action="store_true",
        help="drop matched events after the task's latest commit time (delivery window)",
    )
    parser.add_argument("--end-ts", help="ISO end cutoff (inclusive) for matched events")
    parser.add_argument("--usd-eur", type=float)
    parser.add_argument("--locale", choices=("fr", "en"), default="fr")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    pricing = load_pricing()
    pricing_date = pricing.get("pricing_date", "?")

    if args.transcript:
        transcripts = list(args.transcript)
    else:
        tdir = cursor_transcripts_dir(project_dir)
        transcripts = find_task_transcripts(tdir, args.task_id)
        if not transcripts:
            raise SystemExit(
                f"no Cursor agent transcript mentioning {args.task_id} under {tdir}"
            )

    turns: list[tuple[datetime, str, Path]] = []
    for path in transcripts:
        turns.extend(iter_user_turns(path))
    turns.sort(key=lambda t: t[0])
    if not turns:
        raise SystemExit("transcript(s) found but no user turns with <timestamp>")

    # Deduplicate turns that appear in multiple files (same second + query head)
    seen = set()
    uniq_turns = []
    for t in turns:
        key = (t[0].isoformat(), t[1][:80])
        if key in seen:
            continue
        seen.add(key)
        uniq_turns.append(t)
    turns = uniq_turns

    t0 = turns[0][0].astimezone(timezone.utc)
    t1 = turns[-1][0].astimezone(timezone.utc)

    if args.csv:
        csv_path = args.csv
        cleanup = None
    else:
        tmp = tempfile.NamedTemporaryFile(prefix="cursor-usage-", suffix=".csv", delete=False)
        tmp.close()
        csv_path = Path(tmp.name)
        cleanup = csv_path
        # Pad one day on each side for timezone edges
        run_cursor_usage_csv(t0 - timedelta(days=1), t1 + timedelta(days=1), csv_path)

    try:
        events = load_events(csv_path)
    finally:
        if cleanup is not None:
            cleanup.unlink(missing_ok=True)

    matched = match_turns_to_events(turns, events, args.match_window)
    if not matched:
        raise SystemExit(
            f"no usage events matched within ±{args.match_window:.0f}s of "
            f"{len(turns)} transcript turn(s) — check the CSV window / session"
        )

    end_cut: datetime | None = None
    if args.end_ts:
        end_cut = datetime.fromisoformat(args.end_ts.replace("Z", "+00:00"))
        if end_cut.tzinfo is None:
            end_cut = end_cut.replace(tzinfo=timezone.utc)
    if args.until_commit:
        commit_t = git_task_commit_time(project_dir, args.task_id)
        if commit_t is None:
            raise SystemExit("--until-commit set but no matching git commit found")
        end_cut = commit_t if end_cut is None else min(end_cut, commit_t)

    if end_cut is not None:
        matched = [m for m in matched if m[2]["dt"] <= end_cut.astimezone(timezone.utc)]
        if not matched:
            raise SystemExit("all matched events fell after the end cutoff")

    # Aggregate
    by_model: dict[str, dict[str, int]] = defaultdict(
        lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "events": 0}
    )
    unpriced: list[str] = []
    cost_usd = 0.0
    cursor_value_usd = 0.0
    for _dt, _q, ev, _d in matched:
        canonical = resolve_model(ev["model"], pricing)
        rates = rates_for(canonical, pricing)
        by_model[canonical]["input"] += ev["input"]
        by_model[canonical]["output"] += ev["output"]
        by_model[canonical]["cache_read"] += ev["cache_read"]
        by_model[canonical]["cache_write"] += ev["cache_write"]
        by_model[canonical]["events"] += 1
        cursor_value_usd += ev["value_cents"] / 100.0
        if rates is None:
            unpriced.append(f"{ev['model']}→{canonical}")
            continue
        pin, pout, pread, pwrite = rates
        cost_usd += (
            ev["input"] / 1e6 * pin
            + ev["output"] / 1e6 * pout
            + ev["cache_read"] / 1e6 * pread
            + ev["cache_write"] / 1e6 * pwrite
        )

    if unpriced:
        raise SystemExit(
            f"no Cursor list price for {sorted(set(unpriced))} in {PRICING_PATH} "
            f"(snapshot {pricing_date}) — add the model or pass a dashboard model id"
        )

    rate, rate_fr, rate_en = measure.resolve_usd_eur(args.usd_eur)
    cost_eur = cost_usd * rate

    grand = {
        k: sum(m[k] for m in by_model.values())
        for k in ("input", "output", "cache_read", "cache_write", "events")
    }
    window_start = matched[0][2]["dt"]
    window_end = matched[-1][2]["dt"]
    # Effective time from matched event timestamps + turn gaps
    stamps = [m[2]["dt"] for m in matched]
    window_s = (stamps[-1] - stamps[0]).total_seconds() if len(stamps) > 1 else 0.0
    # Plus a nominal active slice: we don't have per-event duration; report
    # span between first and last matched event and count of events.

    models_label = " + ".join(
        f"{name}: {stats['events']}" for name, stats in sorted(by_model.items())
    )

    if args.json:
        print(
            json.dumps(
                {
                    "task_id": args.task_id,
                    "source": "cursor-usage",
                    "pricing_date": pricing_date,
                    "transcripts": [str(p) for p in transcripts],
                    "matched": [
                        {
                            "turn": q,
                            "turn_ts": dt.isoformat(),
                            "event_ts": ev["dt"].isoformat(),
                            "delta_s": round(d),
                            "model_raw": ev["model"],
                            "model": resolve_model(ev["model"], pricing),
                            "input": ev["input"],
                            "output": ev["output"],
                            "cache_read": ev["cache_read"],
                            "cache_write": ev["cache_write"],
                            "value_cents": ev["value_cents"],
                        }
                        for dt, q, ev, d in matched
                    ],
                    "usage_by_model": dict(by_model),
                    "usage_total": grand,
                    "cost_usd_list": round(cost_usd, 4),
                    "cost_eur_list": round(cost_eur, 4),
                    "cursor_included_value_usd": round(cursor_value_usd, 4),
                    "usd_eur": rate,
                    "usd_eur_note": rate_en,
                    "window": {
                        "start": window_start.isoformat(),
                        "end": window_end.isoformat(),
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"task {args.task_id} — Cursor usage (cursor-usage × transcript)")
    print(f"transcripts: {len(transcripts)} file(s); matched {grand['events']} event(s)")
    print(f"window: {window_start.isoformat()} -> {window_end.isoformat()}")
    for name, stats in sorted(by_model.items()):
        rates = rates_for(name, pricing)
        print(
            f"  {name}: {stats['events']} events, out {stats['output']:,}, "
            f"cache read {stats['cache_read']:,}, fresh in {stats['input']:,}"
            + (
                f" → list $/M in/out/read/write = "
                f"{rates[0]}/{rates[1]}/{rates[2]}/{rates[3]}"
                if rates
                else ""
            )
        )
        for dt, q, ev, d in matched:
            if resolve_model(ev["model"], pricing) != name:
                continue
            print(f"    Δ{d:.0f}s  {ev['dt'].isoformat()}  «{q[:70]}»")
    print(
        f"  TOTAL list-price: {cost_usd:.2f} USD = {cost_eur:.2f} EUR ({rate_en})"
    )
    if cursor_value_usd:
        print(
            f"  Cursor included compute value (dashboard): "
            f"{cursor_value_usd:.2f} USD (not owed if Included)"
        )
    print(f"  pricing snapshot {pricing_date} — {PRICING_PATH.name}")
    print("  rule: auto/default priced as composer-2.5")

    if args.locale == "fr":
        note = (
            f"Télémétrie (Cursor Auto / cursor-usage) : {grand['events']} événement(s) "
            f"({models_label}), {grand['output']:,} tokens de sortie, "
            f"{grand['cache_read']:,} cache read, {grand['input']:,} input, "
            f"≈ {cost_usd:.2f} USD ≈ {cost_eur:.2f} EUR équivalent tarif liste Cursor "
            f"({pricing_date}, auto→composer-2.5) ({rate_fr})"
            + (
                f" ; valeur compute incluse dashboard ≈ {cursor_value_usd:.2f} USD"
                if cursor_value_usd
                else ""
            )
            + f". Fenêtre {window_start.strftime('%Y-%m-%d %H:%M')} → "
            f"{window_end.strftime('%H:%M')} UTC, jointure transcript ±"
            f"{args.match_window:.0f}s."
        )
    else:
        note = (
            f"Telemetry (Cursor Auto / cursor-usage): {grand['events']} event(s) "
            f"({models_label}), {grand['output']:,} output tokens, "
            f"{grand['cache_read']:,} cache read, {grand['input']:,} input, "
            f"≈ {cost_usd:.2f} USD ≈ {cost_eur:.2f} EUR Cursor list-rate equivalent "
            f"({pricing_date}, auto→composer-2.5) ({rate_en})"
            + (
                f"; dashboard included compute ≈ {cursor_value_usd:.2f} USD"
                if cursor_value_usd
                else ""
            )
            + f". Window {window_start.isoformat()} → {window_end.isoformat()}, "
            f"transcript join ±{args.match_window:.0f}s."
        )
    print()
    print("NOTE LINE:")
    print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
