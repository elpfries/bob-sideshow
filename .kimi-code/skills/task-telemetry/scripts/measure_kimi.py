#!/usr/bin/env python3
"""Télémétrie Kimi Code : fenêtre d'une tâche Backlog.md, ou vues globales.

Deux familles de commandes :

1. Mesure d'une tâche (tokens exacts, fenêtre temporelle) :

   measure_kimi.py task --task-id 12 [--project-dir PATH] [--end-ts ISO]
                        [--gap-threshold 120] [--locale fr|en] [--json]
   measure_kimi.py backfill --task-id 12 [--commit SHA ...]
                        [--id-pattern 'TASK-{id}'] [--json]

   ``task`` ouvre la fenêtre au marqueur « backlog task edit <id> -s "In
   Progress" » trouvé dans les appels d'outils Bash des wire.jsonl du projet,
   et la ferme au marqueur « -s Done » le plus récent (ou --end-ts, ou le
   dernier événement). ``backfill`` utilise la fenêtre (commit précédent,
   commit(s) de la tâche], comme le backfill.py Claude Code.

2. Vues globales (reprises de l'ancienne skill kimi-telemetry) :

   measure_kimi.py summary|sessions|calls|tools|context
                   [--session PREFIX] [--since YYYY-MM-DD] [--json]

Source de données : ~/.kimi-code/sessions/wd_<slug>_<sha>/session_<id>/agents/
<agent>/wire.jsonl (un wire.jsonl par agent : main, coder, explore…), indexé
par ~/.kimi-code/session_index.jsonl (sessionId, sessionDir, workDir). Les
sessions d'un projet sont retrouvées par workDir == répertoire du projet.

Consommation : une ligne {"type":"usage.record",...,"usage":{"inputOther",
"output","inputCacheRead","inputCacheCreation"},"usageScope":"turn",
"time":<epoch ms>} par tour — on les somme. Protocole vérifié : 1.5 (le
2026-09-19, sur des sessions live du CLI Kimi Code sous macOS) ; tout autre
protocole déclenche un avertissement sur stderr (--strict pour en faire une
erreur).

IMPORTANT — pas de prix côté Kimi : le schéma d'usage a un total_cost_usd
optionnel jamais rempli. Ce script rapporte des tokens exacts (avec le détail
cache read / creation, qui domine : ~95 % de l'input) et marque le coût comme
indisponible. Ne jamais inventer de tarif.

Read-only ; Python 3.8+, bibliothèque standard uniquement.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

VERIFIED_WIRE = "1.5"
DEFAULT_HOME = os.path.join(os.path.expanduser("~"), ".kimi-code")
USAGE_KEYS = ("input", "cacheRead", "cacheWrite", "output")


# ---------------------------------------------------------------- parsing ---

def load_index(home):
    """sessionId -> {sessionId, sessionDir, workDir} depuis session_index.jsonl."""
    idx = {}
    path = os.path.join(home, "session_index.jsonl")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("sessionId"):
                    idx[r["sessionId"]] = r
    return idx


def all_wire_files(home):
    return sorted(glob.glob(os.path.join(home, "sessions", "*", "*", "agents", "*", "wire.jsonl")))


def project_wire_files(home, project_dir):
    """wire.jsonl des sessions dont le workDir est le projet (via l'index)."""
    target = os.path.realpath(str(project_dir))
    files = []
    for _sid, rec in load_index(home).items():
        wd, sdir = rec.get("workDir"), rec.get("sessionDir")
        if wd and sdir and os.path.realpath(wd) == target:
            files.extend(glob.glob(os.path.join(sdir, "agents", "*", "wire.jsonl")))
    return sorted(files)


def parse_wire(path, since_ms=None):
    """Stream un wire.jsonl ; retourne (proto, usage, tools, context, stamps).

    usage   : {session, agent, model, ts, input, cacheRead, cacheWrite, output}
    tools   : {session, agent, ts, name, command}  (command = args.command Bash)
    context : {session, agent, ts, tokens, messages}
    stamps  : tous les instants (ms) d'activité, pour le calcul des pauses
    """
    parts = path.split(os.sep)
    agent = parts[-2]
    session = parts[-4]
    proto, usage, tools, context, stamps = None, [], [], [], []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"usage.record"' in line:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("type") != "usage.record" or not isinstance(r.get("usage"), dict):
                    continue
                t = r.get("time") or 0
                if since_ms and t < since_ms:
                    continue
                stamps.append(t)
                usage.append({"session": session, "agent": r.get("agentId") or agent,
                              "model": r.get("model") or "?", "ts": t,
                              "input": r["usage"].get("inputOther") or 0,
                              "cacheRead": r["usage"].get("inputCacheRead") or 0,
                              "cacheWrite": r["usage"].get("inputCacheCreation") or 0,
                              "output": r["usage"].get("output") or 0})
            elif '"tool.call"' in line:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                ev = r.get("event") or {}
                if r.get("type") == "context.append_loop_event" and ev.get("type") == "tool.call":
                    t = r.get("time") or 0
                    if since_ms and t < since_ms:
                        continue
                    stamps.append(t)
                    tools.append({"session": session, "agent": r.get("agentId") or agent,
                                  "ts": t, "name": ev.get("name") or "?",
                                  "command": (ev.get("args") or {}).get("command") or ""})
            elif '"token_counting.measured"' in line:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("type") == "token_counting.measured":
                    context.append({"session": session, "agent": r.get("agentId") or agent,
                                    "ts": r.get("time"), "tokens": r.get("tokens") or 0,
                                    "messages": r.get("length") or 0})
            elif proto is None and '"metadata"' in line:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("type") == "metadata":
                    proto = r.get("protocol_version")
    return proto, usage, tools, context, stamps


def load_files(files, since_ms=None):
    protos, usage, tools, context, stamps = set(), [], [], [], []
    for wf in files:
        proto, u, t, c, s = parse_wire(wf, since_ms)
        if proto:
            protos.add(proto)
        usage += u
        tools += t
        context += c
        stamps += s
    return protos, usage, tools, context, stamps


def check_protocol(protos, strict, quiet):
    if quiet:
        return
    if protos == {VERIFIED_WIRE}:
        print(f"[task-telemetry/kimi] protocole wire {VERIFIED_WIRE} — vérifié", file=sys.stderr)
    else:
        print(f"[task-telemetry/kimi] AVERTISSEMENT : protocole wire {sorted(protos) or 'inconnu'}, "
              f"vérifié sur {VERIFIED_WIRE} — les champs inconnus sont ignorés", file=sys.stderr)
        if strict:
            sys.exit(3)


# ---------------------------------------------------------------- helpers ---

def ts(ms):
    return dt.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S") if ms else "-"


def parse_iso_to_ms(value):
    v = value.strip().replace("Z", "+00:00")
    try:
        d = dt.datetime.fromisoformat(v)
    except ValueError:
        d = dt.datetime.strptime(v, "%Y-%m-%d")
    if d.tzinfo is None:
        d = d.astimezone()
    return int(d.timestamp() * 1000)


def tot(rows):
    return {k: sum(r[k] for r in rows) for k in USAGE_KEYS}


def cache_pct(t):
    inp = t["input"] + t["cacheRead"] + t["cacheWrite"]
    return (t["cacheRead"] / inp * 100) if inp else 0.0


def table(rows, cols):
    if not rows:
        print("  (aucune ligne)")
        return
    w = [max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols]
    print("  " + "  ".join(c.ljust(x) for c, x in zip(cols, w)))
    for r in rows:
        print("  " + "  ".join(str(r.get(c, "")).ljust(x) for c, x in zip(cols, w)))


def duration_stats(stamps_ms, gap_threshold_s):
    """(fenêtre_s, pauses [(a_ms, b_ms, gap_s)]) à partir d'instants epoch ms."""
    stamps = sorted(s for s in stamps_ms if s)
    if len(stamps) < 2:
        return 0.0, []
    window_s = (stamps[-1] - stamps[0]) / 1000.0
    pauses = []
    for a, b in zip(stamps, stamps[1:]):
        gap = (b - a) / 1000.0
        if gap > gap_threshold_s:
            pauses.append((a, b, gap))
    return window_s, pauses


def marker_res(task_id):
    """Regex des marqueurs Backlog dans les commandes Bash des tool.call."""
    norm = re.sub(r"^task-", "", task_id, flags=re.I)
    base = rf"backlog\s+task\s+edit\s+(task-)?{re.escape(norm)}\s+.*-s\s+.?"
    return (re.compile(base + r"In Progress", re.I),
            re.compile(base + r"Done", re.I))


def git_log(project_dir):
    """(sha court, epoch ms du commit, sujet), plus ancien d'abord."""
    out = subprocess.run(
        ["git", "log", "--reverse", "--format=%h\x1f%cI\x1f%s"],
        cwd=project_dir, capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"git log a échoué dans {project_dir} : {out.stderr.strip()}")
    commits = []
    for line in out.stdout.strip().splitlines():
        sha, iso, subject = line.split("\x1f", 2)
        commits.append((sha, parse_iso_to_ms(iso), subject))
    return commits


def match_commits(commits, task_id, id_pattern):
    """Indices des commits dont le sujet référence la tâche, bornes de mot."""
    token = id_pattern.replace("{id}", re.escape(task_id))
    rx = re.compile(rf"(?<![0-9A-Za-z]){token}(?![0-9.])", re.I)
    return [i for i, (_, _, subject) in enumerate(commits) if rx.search(subject)]


# ------------------------------------------------------- mesure d'une tâche ---

def measure_window(a, start_ms, end_ms, method_label):
    """Agrège usage + durées sur [start_ms, end_ms] et émet la note line."""
    files = project_wire_files(a.home, a.project_dir)
    if not files:
        print(f"aucune session Kimi Code pour {a.project_dir} dans "
              f"{a.home}/session_index.jsonl", file=sys.stderr)
        return 1
    protos, usage, tools, context, stamps = load_files(files)
    check_protocol(protos, a.strict, a.no_version_check)

    end_ms = end_ms if end_ms is not None else 10**15
    usage = [u for u in usage if start_ms <= (u["ts"] or 0) <= end_ms]
    stamps = [s for s in stamps if start_ms <= s <= end_ms]
    if not usage:
        print(f"aucun usage.record entre {ts(start_ms)} et "
              f"{ts(end_ms) if end_ms < 10**15 else 'maintenant'}",
              file=sys.stderr)
        return 1

    by_model = collections.defaultdict(
        lambda: {"input": 0, "cacheRead": 0, "cacheWrite": 0, "output": 0, "turns": 0})
    agents = collections.Counter()
    for u in usage:
        m = by_model[u["model"]]
        for k in USAGE_KEYS:
            m[k] += u[k]
        m["turns"] += 1
        agents[u["agent"]] += 1

    window_s, pauses = duration_stats(stamps, a.gap_threshold)
    pause_s = sum(g for _, _, g in pauses)
    active_s = window_s - pause_s
    grand = tot(usage)
    n_turns = len(usage)
    real_end = max(u["ts"] or 0 for u in usage)
    pct = cache_pct(grand)
    models_label = " + ".join(f"{m}: {s['turns']}" for m, s in sorted(by_model.items()))
    agents_label = ",".join(sorted(agents))

    if a.json:
        print(json.dumps({
            "task_id": getattr(a, "task_id", None),
            "source": "kimi-code",
            "method": method_label,
            "window": {"start": ts(start_ms), "end": ts(real_end)},
            "wire_files": len(files),
            "turns": n_turns,
            "agents": dict(agents),
            "usage_by_model": {m: s for m, s in sorted(by_model.items())},
            "usage_total": grand,
            "cache_read_share_pct": round(pct, 1),
            "window_min": round(window_s / 60, 1),
            "active_min": round(active_s / 60, 1),
            "pause_min": round(pause_s / 60, 1),
            "pauses": [{"from": ts(x), "to": ts(y), "seconds": round(g)}
                       for x, y, g in pauses],
            "cost": None,
            "cost_note": "Kimi Code n'enregistre aucun prix (total_cost_usd jamais rempli)",
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"tâche {a.task_id} — fenêtre {ts(start_ms)} -> {ts(real_end)} ({method_label})")
    print(f"  wire.jsonl : {len(files)} fichier(s), agents : {agents_label}")
    for model, s in sorted(by_model.items()):
        print(f"  {model}: {s['turns']} tours, sortie {s['output']:,}, "
              f"cache read {s['cacheRead']:,}, cache write {s['cacheWrite']:,}, "
              f"input hors cache {s['input']:,}")
    print(f"  TOTAL : {n_turns} tours, sortie {grand['output']:,}, "
          f"cache read {grand['cacheRead']:,} ({pct:.0f} % de l'input), "
          f"cache write {grand['cacheWrite']:,}, input hors cache {grand['input']:,}")
    print(f"  durée : fenêtre {window_s/60:.0f} min, effectif ≈ {active_s/60:.0f} min, "
          f"pauses ≈ {pause_s/60:.0f} min (écarts > {a.gap_threshold:.0f} s : {len(pauses)})")
    for x, y, g in pauses:
        print(f"    pause {g/60:5.1f} min  {ts(x)[11:]} -> {ts(y)[11:]}")
    print("  coût : indisponible — Kimi Code n'enregistre aucun prix "
          "(total_cost_usd jamais rempli) ; ne pas estimer de tarif")

    if a.locale == "fr":
        note = (
            f"Télémétrie (Kimi Code, {method_label}, tokens exacts) : {n_turns} tours LLM "
            f"({models_label}), {grand['output']:,} tokens de sortie, "
            f"{grand['cacheRead']:,} cache read ({pct:.0f} % de l'input), "
            f"{grand['cacheWrite']:,} cache write, {grand['input']:,} input hors cache. "
            f"Coût : indisponible (Kimi Code n'enregistre pas de prix local). "
            f"Fenêtre {window_s/60:.0f} min, temps effectif ≈ {active_s/60:.0f} min "
            f"(pauses ≈ {pause_s/60:.0f} min : <causes à compléter>)."
        )
    else:
        note = (
            f"Telemetry (Kimi Code, {method_label}, exact tokens): {n_turns} LLM turns "
            f"({models_label}), {grand['output']:,} output tokens, "
            f"{grand['cacheRead']:,} cache read ({pct:.0f}% of input), "
            f"{grand['cacheWrite']:,} cache write, {grand['input']:,} non-cached input. "
            f"Cost: unavailable (Kimi Code records no local price). "
            f"Window {window_s/60:.0f} min, effective ≈ {active_s/60:.0f} min "
            f"(pauses ≈ {pause_s/60:.0f} min: <fill in causes>)."
        )
    print("\nNOTE LINE (compléter les causes de pause, puis persister) :")
    print(note)
    return 0


def cmd_task(a):
    start_rx, done_rx = marker_res(a.task_id)
    files = project_wire_files(a.home, a.project_dir)
    if not files:
        print(f"aucune session Kimi Code pour {a.project_dir} dans "
              f"{a.home}/session_index.jsonl", file=sys.stderr)
        return 1
    _protos, _usage, tools, _context, _stamps = load_files(files)

    start_ms = None
    done_ms = None
    for t in tools:
        cmd = t["command"]
        if not cmd:
            continue
        if start_rx.search(cmd):
            start_ms = max(start_ms or 0, t["ts"])
        elif done_rx.search(cmd) and (start_ms is None or t["ts"] >= (start_ms or 0)):
            # on retient le Done le plus récent ; affiné après coup
            done_ms = max(done_ms or 0, t["ts"])
    if start_ms is None:
        print(f"aucun marqueur `backlog task edit {a.task_id} -s \"In Progress\"` "
              f"dans les appels Bash des wire.jsonl du projet", file=sys.stderr)
        return 1
    if done_ms is not None and done_ms < start_ms:
        done_ms = None
    end_ms = parse_iso_to_ms(a.end_ts) if a.end_ts else done_ms
    return measure_window(a, start_ms, end_ms, "marqueur In Progress")


def cmd_backfill(a):
    commits = git_log(a.project_dir)
    if not commits:
        print(f"aucun commit dans {a.project_dir}", file=sys.stderr)
        return 1
    if a.commit:
        wanted = {c[:7] for c in a.commit}
        idxs = [i for i, (sha, _, _) in enumerate(commits) if sha[:7] in wanted]
        missing = wanted - {commits[i][0][:7] for i in idxs}
        if missing:
            print(f"commit(s) introuvable(s) : {sorted(missing)}", file=sys.stderr)
            return 1
    else:
        idxs = match_commits(commits, a.task_id, a.id_pattern)
        if not idxs:
            print(f"aucun sujet de commit ne correspond à "
                  f"{a.id_pattern.format(id=a.task_id)!r} — passer --commit SHA, "
                  f"ou --id-pattern si le dépôt nomme les tâches autrement",
                  file=sys.stderr)
            return 1
    first, last = idxs[0], idxs[-1]
    if idxs != list(range(first, last + 1)):
        skipped = [commits[i][0] for i in range(first, last + 1) if i not in idxs]
        print(f"note : l'intervalle englobe aussi des commits non liés : {skipped}",
              file=sys.stderr)
    start_ms = commits[first - 1][1] + 1 if first > 0 else 0
    end_ms = commits[last][1]
    shas = ", ".join(commits[i][0] for i in idxs)
    print(f"commits : {commits[first - 1][0] if first > 0 else '(dépôt initial)'} "
          f"(exclus) -> {shas} (inclus)", file=sys.stderr)
    return measure_window(a, start_ms, end_ms,
                          "relevé reconstruit depuis les commits")


# ------------------------------------------------------------ vues globales ---

def workdir(idx, session):
    return (idx.get(session) or {}).get("workDir") or "-"


def cmd_summary(idx, usage, tools, context, a):
    by = collections.defaultdict(list)
    for u in usage:
        by[(u["model"], u["agent"])].append(u)
    rows = []
    for (model, agent), rl in sorted(by.items(), key=lambda kv: -sum(r["output"] for r in kv[1])):
        t = tot(rl)
        rows.append({"model": model, "agent": agent, "turns": len(rl),
                     "in": f"{t['input']:,}", "cacheR": f"{t['cacheRead']:,}",
                     "cacheW": f"{t['cacheWrite']:,}", "out": f"{t['output']:,}",
                     "cache": f"{cache_pct(t):.0f}%"})
    t = tot(usage)
    out = {"home": a.home, "sessions": len({u["session"] for u in usage}),
           "turns": len(usage),
           "tokensIn": t["input"] + t["cacheRead"] + t["cacheWrite"],
           "tokensOut": t["output"], "cacheReadShare": f"{cache_pct(t):.0f}%",
           "byModel": rows}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"{a.home} · {out['sessions']} sessions · {len(usage)} tours · "
          f"{out['tokensIn']:,} tokens en entrée / {out['tokensOut']:,} en sortie · "
          f"cache read {out['cacheReadShare']}")
    table(rows, ["model", "agent", "turns", "in", "cacheR", "cacheW", "out", "cache"])
    print("  tokens exacts ; aucun prix enregistré (total_cost_usd jamais rempli)")


def cmd_sessions(idx, usage, tools, context, a):
    by = collections.defaultdict(list)
    for u in usage:
        by[u["session"]].append(u)
    rows = []
    for sess, rl in by.items():
        t = tot(rl)
        rows.append({"session": sess.replace("session_", "")[:8],
                     "started": ts(min(r["ts"] for r in rl if r["ts"])),
                     "workdir": workdir(idx, sess),
                     "agents": ",".join(sorted({r["agent"] for r in rl})),
                     "models": ",".join(sorted({r["model"] for r in rl})),
                     "turns": len(rl),
                     "in": f"{t['input'] + t['cacheRead'] + t['cacheWrite']:,}",
                     "out": f"{t['output']:,}"})
    rows.sort(key=lambda r: r["started"])
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table(rows, ["session", "started", "workdir", "agents", "models", "turns", "in", "out"])


def cmd_calls(idx, usage, tools, context, a):
    rows = [{"time": ts(u["ts"])[5:], "session": u["session"].replace("session_", "")[:8],
             "agent": u["agent"], "model": u["model"],
             "in": f"{u['input']:,}", "cacheR": f"{u['cacheRead']:,}",
             "cacheW": f"{u['cacheWrite']:,}", "out": f"{u['output']:,}"}
            for u in sorted(usage, key=lambda u: u["ts"] or 0)
            if not a.session or u["session"].startswith(a.session)]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table(rows, ["time", "session", "agent", "model", "in", "cacheR", "cacheW", "out"])


def cmd_tools(idx, usage, tools, context, a):
    counts = collections.Counter((t["agent"], t["name"]) for t in tools
                                 if not a.session or t["session"].startswith(a.session))
    rows = [{"agent": k[0], "tool": k[1], "calls": v}
            for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table(rows, ["agent", "tool", "calls"])


def cmd_context(idx, usage, tools, context, a):
    peak = {}
    for c in context:
        if a.session and not c["session"].startswith(a.session):
            continue
        k = (c["session"], c["agent"])
        if k not in peak or (c["ts"] or 0) > (peak[k]["ts"] or 0):
            peak[k] = c
    rows = [{"session": k[0].replace("session_", "")[:8], "agent": k[1],
             "measured": ts(c["ts"]), "messages": c["messages"],
             "contextTokens": f"{c['tokens']:,}"}
            for k, c in sorted(peak.items())]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table(rows, ["session", "agent", "measured", "messages", "contextTokens"])
    print("  dernière mesure par agent ; le contexte grandit au fil d'une session")


VIEWS = {"summary": cmd_summary, "sessions": cmd_sessions, "calls": cmd_calls,
         "tools": cmd_tools, "context": cmd_context}


def cmd_view(a):
    if not os.path.isdir(os.path.join(a.home, "sessions")):
        sys.exit(f"home kimi-code introuvable : {a.home}")
    since_ms = parse_iso_to_ms(a.since) if a.since else None
    protos, usage, tools, context, _stamps = load_files(all_wire_files(a.home), since_ms)
    check_protocol(protos, a.strict, a.no_version_check)
    VIEWS[a.view](load_index(a.home), usage, tools, context, a)


# ------------------------------------------------------------------- main ---

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--home", default=DEFAULT_HOME)
        p.add_argument("--no-version-check", action="store_true",
                       help="taire la ligne de vérification du protocole")
        p.add_argument("--strict", action="store_true",
                       help="sortie 3 si le protocole wire diffère du vérifié")
        p.add_argument("--json", action="store_true")

    p = sub.add_parser("task", help="mesure la fenêtre In Progress -> Done d'une tâche")
    p.add_argument("--task-id", required=True, help="id de tâche Backlog (12, TASK-12…)")
    p.add_argument("--project-dir", default=os.getcwd())
    p.add_argument("--end-ts", default=None,
                   help="fin de fenêtre ISO (défaut : marqueur Done, sinon dernier événement)")
    p.add_argument("--gap-threshold", type=float, default=120.0,
                   help="seuil de pause en secondes")
    p.add_argument("--locale", choices=("fr", "en"), default="fr")
    common(p)
    p.set_defaults(func=cmd_task)

    p = sub.add_parser("backfill", help="fenêtre (commit précédent, commit(s) de la tâche]")
    p.add_argument("--task-id", required=True)
    p.add_argument("--project-dir", default=os.getcwd())
    p.add_argument("--commit", action="append", default=[],
                   help="sha du commit de la tâche (répétable) ; saute la recherche par sujet")
    p.add_argument("--id-pattern", default="TASK-{id}",
                   help="forme de l'id dans les sujets de commit (défaut : TASK-{id})")
    p.add_argument("--gap-threshold", type=float, default=120.0)
    p.add_argument("--locale", choices=("fr", "en"), default="fr")
    common(p)
    p.set_defaults(func=cmd_backfill)

    for name in sorted(VIEWS):
        p = sub.add_parser(name, help=f"vue globale « {name} » (toutes sessions)")
        p.add_argument("--session", help="préfixe d'id de session")
        p.add_argument("--since", help="enregistrements à partir de YYYY-MM-DD")
        common(p)
        p.set_defaults(func=cmd_view, view=name)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
