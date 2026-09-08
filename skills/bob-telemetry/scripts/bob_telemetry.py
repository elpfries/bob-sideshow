#!/usr/bin/env python3
"""IBM Bob usage from the local task database (~/.bob/db/bob.db).

  bob_telemetry.py summary|tasks|calls|tools|security|changes|context [--task PREFIX] [--since YYYY-MM-DD]
                   [--db PATH] [--json]

Read-only; Python 3.8+, standard library only. Verified on the bob-code 2.1.0 schema.
"""
import argparse
import collections
import datetime as dt
import json
import os
import shutil
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bobcheck  # noqa: E402

DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".bob", "db", "bob.db")


def ts(ms):
    return dt.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S") if ms else "-"


def open_db(path):
    if not os.path.isfile(path):
        sys.exit(f"database not found: {path}")
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        con.execute("select count(*) from sqlite_master")
        return con
    except sqlite3.OperationalError:
        tmp = tempfile.mkdtemp(prefix="bob-sideshow-")
        for suf in ("", "-wal", "-shm"):
            if os.path.exists(path + suf):
                shutil.copy2(path + suf, os.path.join(tmp, "bob.db" + suf))
        return sqlite3.connect(os.path.join(tmp, "bob.db"))


def load(con, since_ms):
    con.row_factory = sqlite3.Row
    tasks = {}
    for r in con.execute("select * from tasks order by created_at"):
        t = dict(r)
        if since_ms and (t["updated_at"] or 0) < since_ms:
            continue
        for k in ("env", "costs"):
            try:
                t[k] = json.loads(t[k]) if t[k] else {}
            except Exception:
                t[k] = {}
        tasks[t["id"]] = t
    msgs = collections.defaultdict(list)
    for r in con.execute("select * from messages order by created_at"):
        m = dict(r)
        if m["task_id"] not in tasks:
            continue
        try:
            m["data"] = json.loads(m["data"])
        except Exception:
            continue
        msgs[m["task_id"]].append(m)
    try:
        attrib = [dict(r) for r in con.execute("select * from attribution_logs order by created_at")]
    except sqlite3.Error:
        attrib = []
    return tasks, msgs, attrib


def spend(sp):
    g = lambda k: sp.get(k) or 0  # noqa: E731
    tok = g("input") + g("output")
    return {"input": g("input"), "output": g("output"), "cacheRead": g("cacheRead"), "cacheWrite": g("cacheWrite"),
            "cost": g("cost"), "rate": (g("cost") / tok * 1e6) if tok else None}


def model_class(rate):
    if rate is None:
        return "n/a"
    if rate >= 1.5:
        return "standard"
    if rate >= 0.5:
        return "economy"
    return f"other {rate:.3f}/M"


def iter_calls(tasks, msgs):
    for tid, ml in msgs.items():
        for m in ml:
            d, meta = m["data"], m["data"].get("_meta") or {}
            nested = d.get("messages") or []
            if meta.get("spend") and not nested:
                yield {"task": tid, "who": "agent", "ts": meta.get("timestamp") or m["created_at"], **spend(meta["spend"])}
            for sm in nested:
                s2 = (sm.get("_meta") or {}).get("spend")
                if s2:
                    yield {"task": tid, "who": f"subagent {meta.get('agentType') or '?'}",
                           "ts": (sm.get("_meta") or {}).get("timestamp") or m["created_at"], **spend(s2)}


def iter_tool_calls(msgs):
    for tid, ml in msgs.items():
        for m in ml:
            d, meta = m["data"], m["data"].get("_meta") or {}
            for tc in d.get("toolCalls") or []:
                yield {"who": "agent", "name": tc.get("name")}
            if m["role"] == "tool" and meta.get("durationMs") is not None:
                yield {"who": "agent", "duration": meta["durationMs"]}
            for sm in d.get("messages") or []:
                for tc in sm.get("toolCalls") or []:
                    yield {"who": f"subagent {meta.get('agentType') or '?'}", "name": tc.get("name")}
                sme = sm.get("_meta") or {}
                if sm.get("role") == "tool" and sme.get("durationMs") is not None:
                    yield {"who": "subagent", "duration": sme["durationMs"]}


def iter_command_uses(msgs):
    for tid, ml in msgs.items():
        for m in ml:
            d, meta = m["data"], m["data"].get("_meta") or {}
            sources = [("agent", d, meta.get("timestamp") or m["created_at"])]
            sources += [(f"subagent {meta.get('agentType') or '?'}", sm, (sm.get("_meta") or {}).get("timestamp") or m["created_at"])
                        for sm in d.get("messages") or []]
            for who, src, when in sources:
                cu = (src.get("toolUsage") or {}).get("commandUse")
                if cu:
                    yield {"task": tid, "who": who, "ts": when, **cu}


def iter_changes(msgs):
    for tid, ml in msgs.items():
        for m in ml:
            for src in [m["data"]] + (m["data"].get("messages") or []):
                meta = src.get("_meta") or {}
                for uri, c in (meta.get("changes") or {}).items():
                    lines = (c.get("patch") or "").splitlines()
                    yield {"task": tid, "ts": meta.get("timestamp") or m["created_at"], "uri": uri,
                           "added": sum(1 for l in lines if l.startswith("+") and not l.startswith("+++")),
                           "removed": sum(1 for l in lines if l.startswith("-") and not l.startswith("---")),
                           "undo": bool(meta.get("notAi"))}


def table(rows, cols):
    if not rows:
        print("  (none)")
        return
    w = [max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols]
    print("  " + "  ".join(c.ljust(x) for c, x in zip(cols, w)))
    for r in rows:
        print("  " + "  ".join(str(r.get(c, "")).ljust(x) for c, x in zip(cols, w)))


def cmd_summary(tasks, msgs, attrib, a):
    roots = [t for t in tasks.values() if not t.get("parent_id")]
    root_cost = sum((t["costs"] or {}).get("cost", 0) for t in roots)
    calls = list(iter_calls(tasks, msgs))
    call_cost = sum(c["cost"] for c in calls)
    by = collections.defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "cost": 0.0})
    for c in calls:
        b = by[(model_class(c["rate"]), c["who"])]
        b["calls"] += 1
        b["input"] += c["input"]
        b["output"] += c["output"]
        b["cost"] += c["cost"]
    rows = [{"class": k[0], "who": k[1], **v, "share": f"{(v['cost'] / call_cost * 100) if call_cost else 0:.0f}%"}
            for k, v in sorted(by.items(), key=lambda kv: -kv[1]["cost"])]
    out = {"db": a.db, "latest": ts(max([t["updated_at"] for t in tasks.values()] or [0])), "rootTasks": len(roots),
           "subagentTasks": len(tasks) - len(roots), "llmCalls": len(calls), "tokensIn": sum(c["input"] for c in calls),
           "tokensOut": sum(c["output"] for c in calls), "bobcoins": root_cost, "bobcoinsPerCall": call_cost, "byClass": rows}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"{a.db} · latest {out['latest']} · {len(roots)} root tasks, {out['subagentTasks']} subagents · "
          f"{len(calls)} LLM calls · {out['tokensIn']:,} tokens in / {out['tokensOut']:,} out")
    print(f"Bobcoins {root_cost:.4f}" + ("" if abs(root_cost - call_cost) < 1e-6 else f"  (per-call sum {call_cost:.4f})"))
    table([{"class": r["class"], "who": r["who"], "calls": r["calls"], "in": f"{r['input']:,}", "out": f"{r['output']:,}",
            "Bobcoins": f"{r['cost']:.4f}", "share": r["share"]} for r in rows],
          ["class", "who", "calls", "in", "out", "Bobcoins", "share"])


def cmd_tasks(tasks, msgs, attrib, a):
    own = collections.Counter(c["task"] for c in iter_calls(tasks, msgs) if c["who"] == "agent")
    rows = [{"task": t["id"][:8], "type": t["task_type"], "status": t["status"], "created": ts(t["created_at"])[5:16],
             "calls": own[t["id"]], "in": f"{(t['costs'] or {}).get('input', 0):,}", "out": f"{(t['costs'] or {}).get('output', 0):,}",
             "Bobcoins": f"{(t['costs'] or {}).get('cost', 0):.4f}",
             "title": (t.get("title") or t.get("first_message") or "").strip().replace("\n", " ")[:40]} for t in tasks.values()]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table(rows, ["task", "type", "status", "created", "calls", "in", "out", "Bobcoins", "title"])
    print("  root task Bobcoins include subagents; tokens do not")


def cmd_calls(tasks, msgs, attrib, a):
    rows = [{"time": ts(c["ts"])[5:], "task": c["task"][:8], "who": c["who"], "in": f"{c['input']:,}", "cacheR": f"{c['cacheRead']:,}",
             "cacheW": f"{c['cacheWrite']:,}", "out": f"{c['output']:,}", "Bobcoins": f"{c['cost']:.4f}",
             "rate/M": "-" if c["rate"] is None else f"{c['rate']:.3f}", "class": model_class(c["rate"])}
            for c in sorted(iter_calls(tasks, msgs), key=lambda c: c["ts"] or 0) if not a.task or c["task"].startswith(a.task)]
    print(json.dumps(rows, indent=2) if a.json else "", end="")
    if not a.json:
        table(rows, ["time", "task", "who", "in", "cacheR", "cacheW", "out", "Bobcoins", "rate/M", "class"])


def cmd_tools(tasks, msgs, attrib, a):
    counts, durations = collections.Counter(), collections.defaultdict(list)
    for t in iter_tool_calls(msgs):
        if t.get("name"):
            counts[(t["who"], t["name"])] += 1
        else:
            durations[t["who"]].append(t["duration"])
    rows = [{"who": k[0], "tool": k[1], "calls": v} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    if a.json:
        print(json.dumps({"calls": rows, "durationsMs": durations}, indent=2))
        return
    table(rows, ["who", "tool", "calls"])
    for who, ds in durations.items():
        print(f"  {who}: {len(ds)} tool runs, {sum(ds) / 1000:.1f} s total, max {max(ds) / 1000:.1f} s")


def cmd_security(tasks, msgs, attrib, a):
    rows = [{"time": ts(cu["ts"])[5:], "task": cu["task"][:8], "who": cu["who"],
             "flagged": "YES" if cu.get("requiresSecurityApproval") else "-", "unverifiable": "YES" if cu.get("unverifiable") else "-",
             "commands": " ⏵ ".join(cu.get("commands") or [])[:80], "reason": (cu.get("securityReason") or "")[:60]}
            for cu in iter_command_uses(msgs) if not a.task or cu["task"].startswith(a.task)]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    table(rows, ["time", "task", "who", "flagged", "unverifiable", "commands", "reason"])
    print(f"  {len(rows)} commands · {sum(r['flagged'] == 'YES' for r in rows)} flagged · {sum(r['unverifiable'] == 'YES' for r in rows)} unverifiable")


def cmd_changes(tasks, msgs, attrib, a):
    rows = [{"time": ts(c["ts"])[5:], "task": c["task"][:8], "file": c["uri"].replace("file://", ""), "+": c["added"], "-": c["removed"],
             "note": "undo" if c["undo"] else ""} for c in iter_changes(msgs) if not a.task or c["task"].startswith(a.task)]
    logs = [{"time": ts(x["created_at"])[5:], "task": (x.get("task_id") or "")[:8], "tool": x.get("tool_name"),
             "file": str(x.get("file_uri")).replace("file://", ""), "lines": f"{x.get('start_line')}-{x.get('end_line')}"}
            for x in attrib if not a.task or str(x.get("task_id", "")).startswith(a.task)]
    if a.json:
        print(json.dumps({"changes": rows, "attributionLogs": logs}, indent=2, ensure_ascii=False))
        return
    print("edits (_meta.changes)")
    table(rows, ["time", "task", "file", "+", "-", "note"])
    print("attribution logs")
    table(logs, ["time", "task", "tool", "file", "lines"])


def cmd_context(tasks, msgs, attrib, a):
    out = [{"task": t["id"][:8], **(t["costs"] or {}).get("contextWindowBreakdown", {})}
           for t in tasks.values() if (t["costs"] or {}).get("contextWindowBreakdown") and (not a.task or t["id"].startswith(a.task))]
    if a.json:
        print(json.dumps(out, indent=2))
        return
    for o in out:
        print(f"{o['task']}  context {o.get('reportedTotal', 0):,} tokens, static prompt {o.get('total', 0):,}")
        print("  " + ", ".join(f"{k} {v:,}" for k, v in sorted((o.get("breakdown") or {}).items(), key=lambda kv: -kv[1]) if v))
    if not out:
        print("  (none)")


VIEWS = {"summary": cmd_summary, "tasks": cmd_tasks, "calls": cmd_calls, "tools": cmd_tools,
         "security": cmd_security, "changes": cmd_changes, "context": cmd_context}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("view", choices=sorted(VIEWS))
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--task", help="task id prefix")
    ap.add_argument("--since", help="tasks updated on/after YYYY-MM-DD")
    ap.add_argument("--json", action="store_true")
    _bobcheck.add_arguments(ap)
    a = ap.parse_args()
    _bobcheck.check("bob_telemetry", db_path=a.db, quiet=a.no_version_check, strict=a.strict)
    since_ms = int(dt.datetime.strptime(a.since, "%Y-%m-%d").timestamp() * 1000) if a.since else None
    VIEWS[a.view](*load(open_db(a.db), since_ms), a)


if __name__ == "__main__":
    main()
