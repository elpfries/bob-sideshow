#!/usr/bin/env python3
"""Measure per-task session telemetry from Claude Code transcripts.

Sums real API usage (deduplicated by message.id — one API response spanning
several content blocks is written as several transcript entries that repeat
the same usage), computes wall-clock window vs effective processing time
(gaps > threshold are counted as pauses), prices the usage at API list
rates, and emits a ready-to-persist note line.

Task window: from the most recent Backlog.md "In Progress" transition of the
task (`backlog task edit <id> -s "In Progress"` tool call found in any
transcript of the project) to the last assistant message seen (or --end-ts).

Transcript discovery is recursive: subagent sessions live in
<session-id>/subagents/, so a task delegated to a subagent is measurable from
the orchestrating session and its total covers both (see transcript_paths).

Usage:
  measure.py --task-id 16.1 [--project-dir PATH] [--usd-eur RATE]
             [--price SUBSTR=IN,OUT[,READ,WRITE]] [--gap-threshold 120]
             [--end-ts ISO] [--locale fr|en] [--json]

Pricing defaults are a dated snapshot (see PRICING_DATE) — verify against
current Anthropic list prices (claude-api skill) and override with --price
if they changed. Cache read defaults to 0.1x input, cache write to 2x input
(the 1h TTL Claude Code sessions use). A model the table does not price is a
hard error, never a 0.00 total (see fail_on_unpriced).

EUR conversion uses the ECB daily rate, falling back to the dated rate
committed next to this script (usd-eur-fallback.json) when the ECB cannot be
reached. A line never goes out in USD only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PRICING_DATE = "2026-08"
# $/M tokens: (input, output). Matched by substring against message.model.
# Order matters: first match wins.
# Checked against the claude-api skill's pricing table on 2026-08-07.
DEFAULT_PRICING = [
    # Harness-generated placeholder, not a model: Claude Code writes an
    # assistant record with model "<synthetic>" when a turn dies mid-response
    # (API error, lost connection). Its usage block is all zeros — there is no
    # API call behind it — so pricing it at zero is exact, not the silent zero
    # `fail_on_unpriced` exists to prevent. Verified on this project
    # 2026-08-18: both such records carried zero input, output and cache
    # tokens. Kept FIRST so it can never be shadowed by another substring.
    ("<synthetic>", (0.0, 0.0, 0.0, 0.0)),
    ("fable-5", (10.0, 50.0)),
    ("mythos-5", (10.0, 50.0)),
    # Opus 5 serves its 1M window as both the default AND the maximum, with no
    # long-context premium — so the extended-window variant Claude Code reports
    # as `claude-opus-5[1m]` bills exactly like plain `claude-opus-5`, and one
    # substring entry covering both is correct rather than a shortcut.
    # (Fast mode — `speed: "fast"` — is the one Opus 5 rate that differs, at
    # 10/50; it is not what a Claude Code session runs on. Should a model id
    # ever carry it, give it its own entry ABOVE this one, since the first
    # substring match wins.)
    ("opus-5", (5.0, 25.0)),
    ("opus-4-8", (5.0, 25.0)),
    ("opus-4-7", (5.0, 25.0)),
    ("opus-4-6", (5.0, 25.0)),
    # Sonnet 5 launch pricing through 2026-08-31 (standard: 3.0 / 15.0).
    ("sonnet-5", (2.0, 10.0)),
    ("sonnet-4-6", (3.0, 15.0)),
    ("haiku-4-5", (1.0, 5.0)),
]
CACHE_READ_FACTOR = 0.1
CACHE_WRITE_FACTOR = 2.0  # 1h TTL; 5m TTL would be 1.25x

# Dated USD->EUR rate committed with the skill, used when the ECB is
# unreachable (sandboxed sessions often are). Refreshed automatically by any
# run that does reach the ECB — see save_fallback_rate.
FALLBACK_RATE_PATH = Path(__file__).resolve().parent.parent / "usd-eur-fallback.json"

USAGE_KEYS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def transcripts_dir_for(project_dir: Path) -> Path:
    sanitized = str(project_dir.resolve()).replace("/", "-")
    return Path.home() / ".claude" / "projects" / sanitized


def transcript_paths(tdir: Path) -> list[Path]:
    """Every transcript under the project directory, subagent sessions included.

    Claude Code writes a subagent's transcript to <session-id>/subagents/
    (workflow agents one level deeper). A non-recursive glob therefore sees
    only the orchestrating session: a task delegated to a subagent measures as
    near-zero from the main session, and cannot be measured at all from the
    subagent without --transcripts-dir. Reading both together is safe because
    usage is deduplicated by message.id.
    """
    return sorted(tdir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)


def iter_entries(paths):
    for path in paths:
        with path.open(errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def tool_commands(entry) -> str:
    message = entry.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "tool_use":
            command = item.get("input", {}).get("command")
            if command:
                parts.append(str(command))
    return "\n".join(parts)


def find_start(paths, task_id: str) -> str | None:
    """Timestamp of the most recent `backlog task edit <id> -s "In Progress"`."""
    norm = re.sub(r"^task-", "", task_id, flags=re.I)
    marker = re.compile(
        rf"backlog\s+task\s+edit\s+(task-)?{re.escape(norm)}\s+.*-s\s+.?In Progress",
        re.I,
    )
    latest = None
    for entry in iter_entries(paths):
        ts = entry.get("timestamp")
        if not ts:
            continue
        if marker.search(tool_commands(entry)):
            if latest is None or ts > latest:
                latest = ts
    return latest


def fetch_usd_eur() -> tuple[float, str] | None:
    """(rate, ECB quotation date) from frankfurter.dev, or None if unreachable."""
    try:
        with urllib.request.urlopen(
            "https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR", timeout=6
        ) as resp:
            payload = json.load(resp)
            return float(payload["rates"]["EUR"]), str(payload["date"])
    except Exception:
        return None


def load_fallback_rate() -> tuple[float, str] | None:
    """(rate, date) read from the rate committed alongside the skill."""
    try:
        data = json.loads(FALLBACK_RATE_PATH.read_text())
        return float(data["usd_eur"]), str(data["date"])
    except Exception:
        return None


def save_fallback_rate(rate: float, date: str) -> bool:
    """Refresh the committed fallback from a live ECB reading. True if it changed."""
    current = load_fallback_rate()
    if current is not None and current[1] == date and abs(current[0] - rate) < 1e-9:
        return False
    payload = {
        "usd_eur": rate,
        "date": date,
        "source": "ECB daily reference rate via frankfurter.dev",
        "note": (
            "Fallback used by measure.py and backfill.py when the ECB cannot be "
            "reached. Rewritten automatically by any run that does reach it — "
            "commit the change so the next offline run uses a fresh rate."
        ),
    }
    try:
        FALLBACK_RATE_PATH.write_text(json.dumps(payload, indent=2) + "\n")
        return True
    except OSError:
        return False


def resolve_usd_eur(explicit: float | None) -> tuple[float, str, str]:
    """(rate, French mention, English mention) for the emitted note line.

    Order: --usd-eur, then the ECB daily rate, then the dated fallback committed
    with the skill. Exits rather than let a line go out in USD only.
    """
    if explicit is not None:
        return (
            explicit,
            f"taux fourni en argument : 1 USD = {explicit:.4f} EUR",
            f"rate given on the command line: 1 USD = {explicit:.4f} EUR",
        )
    live = fetch_usd_eur()
    if live is not None:
        rate, date = live
        if save_fallback_rate(rate, date):
            print(
                f"fallback rate refreshed to {rate} ({date}) in {FALLBACK_RATE_PATH}"
                f" — commit it",
                file=sys.stderr,
            )
        return (
            rate,
            f"taux BCE du {date} : 1 USD = {rate:.4f} EUR",
            f"ECB rate of {date}: 1 USD = {rate:.4f} EUR",
        )
    stored = load_fallback_rate()
    if stored is not None:
        rate, date = stored
        print(f"ECB unreachable — falling back on the rate of {date} ({rate})", file=sys.stderr)
        return (
            rate,
            f"taux de repli figé du {date} : 1 USD = {rate:.4f} EUR, BCE injoignable",
            f"frozen fallback rate of {date}: 1 USD = {rate:.4f} EUR, ECB unreachable",
        )
    raise SystemExit(
        f"no USD/EUR rate: the ECB is unreachable and {FALLBACK_RATE_PATH} is missing or "
        f"unreadable. Pass --usd-eur RATE — a telemetry line must never go out in USD only."
    )


def price_for(model: str, overrides) -> tuple[float, float, float, float] | None:
    """(input, output, cache_read, cache_write) $/M for a model id."""
    for substr, values in overrides + DEFAULT_PRICING:
        if substr in model:
            if len(values) == 4:
                return values
            inp, out = values
            return (inp, out, inp * CACHE_READ_FACTOR, inp * CACHE_WRITE_FACTOR)
    return None


def fail_on_unpriced(unpriced) -> None:
    """Exit rather than let an unpriced model be reported as free.

    A model missing from the table used to cost 0.00 USD behind a one-line `!!`
    warning, and that zero would then be persisted verbatim into a task's notes
    — where it is the single source of truth for what the task cost, and where
    nothing distinguishes it from a genuinely cheap task. Same stance as
    resolve_usd_eur: a reading that cannot be trusted must not be emitted at
    all. Call this BEFORE printing anything, note line included.
    """
    if not unpriced:
        return
    raise SystemExit(
        f"no pricing for {sorted(unpriced)} at the {PRICING_DATE} snapshot — refusing to "
        f"report a cost that would silently read as 0.00 USD. Get the current list prices "
        f"(claude-api skill, never from memory) and either pass "
        f"--price <model-substr>=IN,OUT[,READ,WRITE] or add the model to DEFAULT_PRICING in "
        f"{Path(__file__).resolve()}."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-id", required=True, help="Backlog task id (12, 16.1, TASK-12…)")
    ap.add_argument("--project-dir", type=Path, default=Path.cwd())
    ap.add_argument("--transcripts-dir", type=Path, default=None)
    ap.add_argument("--end-ts", default=None, help="ISO end of window (default: last entry)")
    ap.add_argument("--gap-threshold", type=float, default=120.0, help="pause threshold, seconds")
    ap.add_argument("--usd-eur", type=float, default=None, help="rate; default: fetch ECB")
    ap.add_argument(
        "--price",
        action="append",
        default=[],
        metavar="SUBSTR=IN,OUT[,READ,WRITE]",
        help="override $/M pricing for models whose id contains SUBSTR",
    )
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

    tdir = args.transcripts_dir or transcripts_dir_for(args.project_dir)
    paths = transcript_paths(tdir)
    if not paths:
        print(f"no transcripts in {tdir}", file=sys.stderr)
        return 1

    start_ts = find_start(paths, args.task_id)
    if start_ts is None:
        print(f'no `task edit {args.task_id} -s "In Progress"` marker found', file=sys.stderr)
        return 1
    end_ts = args.end_ts or "9999"

    # --- usage, deduplicated by API message id ---
    by_id: dict[str, dict] = {}
    stamps: list[datetime] = []
    last_assistant = None
    for entry in iter_entries(paths):
        ts = entry.get("timestamp")
        if not ts or ts < start_ts or ts > end_ts:
            continue
        stamps.append(parse_ts(ts))
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("usage"), dict):
            continue
        last_assistant = max(last_assistant or ts, ts)
        key = message.get("id") or entry.get("uuid") or ts
        by_id[key] = {"model": message.get("model", "?"), "usage": message["usage"]}

    totals = defaultdict(lambda: defaultdict(int))
    calls = defaultdict(int)
    for record in by_id.values():
        calls[record["model"]] += 1
        for k in USAGE_KEYS:
            totals[record["model"]][k] += record["usage"].get(k) or 0

    # --- duration ---
    stamps.sort()
    window_s = (stamps[-1] - stamps[0]).total_seconds() if stamps else 0.0
    pauses = []
    for a, b in zip(stamps, stamps[1:]):
        gap = (b - a).total_seconds()
        if gap > args.gap_threshold:
            pauses.append((a, b, gap))
    pause_s = sum(g for _, _, g in pauses)
    active_s = window_s - pause_s

    # --- cost ---
    rate, rate_fr, rate_en = resolve_usd_eur(args.usd_eur)
    cost_usd = 0.0
    per_model_cost = {}
    unpriced = []
    for model, usage in totals.items():
        p = price_for(model, overrides)
        if p is None:
            unpriced.append(model)
            continue
        pin, pout, pread, pwrite = p
        cost = (
            usage["input_tokens"] / 1e6 * pin
            + usage["output_tokens"] / 1e6 * pout
            + usage["cache_read_input_tokens"] / 1e6 * pread
            + usage["cache_creation_input_tokens"] / 1e6 * pwrite
        )
        per_model_cost[model] = (cost, p)
        cost_usd += cost
    fail_on_unpriced(unpriced)
    cost_eur = cost_usd * rate

    grand = {k: sum(t[k] for t in totals.values()) for k in USAGE_KEYS}
    n_calls = sum(calls.values())
    models_label = " + ".join(f"{m.replace('claude-', '')}: {calls[m]}" for m in sorted(calls))

    if args.json:
        print(
            json.dumps(
                {
                    "task_id": args.task_id,
                    "window": {"start": start_ts, "end": last_assistant},
                    "calls": dict(calls),
                    "usage_by_model": {m: dict(u) for m, u in totals.items()},
                    "usage_total": grand,
                    "window_min": round(window_s / 60, 1),
                    "active_min": round(active_s / 60, 1),
                    "pause_min": round(pause_s / 60, 1),
                    "pauses": [
                        {"from": a.isoformat(), "to": b.isoformat(), "seconds": round(g)}
                        for a, b, g in pauses
                    ],
                    "cost_usd": round(cost_usd, 2),
                    "cost_eur": round(cost_eur, 2),
                    "usd_eur": rate,
                    "usd_eur_note": rate_en,
                    "pricing_date": PRICING_DATE,
                },
                ensure_ascii=False,
            )
        )
        return 0

    print(f"task {args.task_id} — window {start_ts} -> {last_assistant}")
    print(f"transcripts: {len(paths)} file(s) in {tdir}")
    for model in sorted(totals):
        usage = totals[model]
        cost, p = per_model_cost.get(model, (None, None))
        line = (
            f"  {model}: {calls[model]} calls, out {usage['output_tokens']:,}, "
            f"cache read {usage['cache_read_input_tokens']:,}, "
            f"cache write {usage['cache_creation_input_tokens']:,}, "
            f"fresh in {usage['input_tokens']:,}"
        )
        if cost is not None:
            line += f" -> {cost:.2f} USD (in/out/read/write $/M = {p[0]}/{p[1]}/{p[2]}/{p[3]})"
        print(line)
    print(
        f"  TOTAL: {n_calls} calls, out {grand['output_tokens']:,}, "
        f"cache read {grand['cache_read_input_tokens']:,}, "
        f"cache write {grand['cache_creation_input_tokens']:,} -> {cost_usd:.2f} USD"
        f" = {cost_eur:.2f} EUR ({rate_en})"
    )
    print(
        f"  duration: window {window_s/60:.0f} min, active ≈ {active_s/60:.0f} min, "
        f"pauses ≈ {pause_s/60:.0f} min (gaps > {args.gap_threshold:.0f}s: {len(pauses)})"
    )
    for a, b, g in pauses:
        print(f"    pause {g/60:5.1f} min  {a.strftime('%H:%M:%S')} -> {b.strftime('%H:%M:%S')}")
    print(f"  pricing snapshot {PRICING_DATE} — verify current list prices (claude-api skill)")

    if args.locale == "fr":
        note = (
            f"Télémétrie : {n_calls} appels API ({models_label}), "
            f"{grand['output_tokens']:,} tokens de sortie, "
            f"{grand['cache_read_input_tokens']:,} cache read, "
            f"{grand['cache_creation_input_tokens']:,} cache write, "
            f"≈ {cost_usd:.2f} USD ≈ {cost_eur:.2f} EUR équivalent API ({rate_fr}). "
            f"Fenêtre {window_s/60:.0f} min, temps effectif ≈ {active_s/60:.0f} min "
            f"(pauses ≈ {pause_s/60:.0f} min : <causes à compléter>)."
        )
    else:
        note = (
            f"Telemetry: {n_calls} API calls ({models_label}), "
            f"{grand['output_tokens']:,} output tokens, "
            f"{grand['cache_read_input_tokens']:,} cache read, "
            f"{grand['cache_creation_input_tokens']:,} cache write, "
            f"≈ {cost_usd:.2f} USD ≈ {cost_eur:.2f} EUR API-equivalent ({rate_en}). "
            f"Window {window_s/60:.0f} min, effective ≈ {active_s/60:.0f} min "
            f"(pauses ≈ {pause_s/60:.0f} min: <fill in causes>)."
        )
    print("\nNOTE LINE (complete the pause causes, then persist):")
    print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
