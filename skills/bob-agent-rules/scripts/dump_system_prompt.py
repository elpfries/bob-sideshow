#!/usr/bin/env python3
"""Extract the system prompt IBM Bob actually used, from ~/.bob/db/bob.db.

  dump_system_prompt.py [--db PATH] [--task PREFIX] [--list | --section NAME | --guidance NAME | --grep REGEX | --all]

Sections are the top-level <tag>…</tag> blocks of the prompt; guidance blocks are the "# name — …"
tool guides that follow <environment_info>. Read-only; standard library only.
"""
import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bobcheck  # noqa: E402

DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".bob", "db", "bob.db")


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


def latest_prompt(con, task_prefix):
    q = "select task_id, data, created_at from messages where role='system'"
    args = []
    if task_prefix:
        q += " and task_id like ?"
        args.append(task_prefix + "%")
    q += " order by created_at desc limit 1"
    row = con.execute(q, args).fetchone()
    if not row:
        sys.exit("no system message found" + (f" for task {task_prefix}" if task_prefix else ""))
    d = json.loads(row[1])
    c = d.get("content")
    text = c if isinstance(c, str) else "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return row[0], row[2], text


def split(text):
    sections = []
    for m in re.finditer(r"^<([a-z_]+)>\n(.*?)^</\1>", text, re.S | re.M):
        sections.append((m.group(1), m.group(2).strip(), m.start()))
    guidance = []
    tail_start = text.find("</environment_info>")
    tail = text[tail_start:] if tail_start >= 0 else text
    heads = list(re.finditer(r"^# ([^\n]+)$", tail, re.M))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(tail)
        title = h.group(1).strip()
        name = title.split(" — ")[0].strip()
        guidance.append((name, title, tail[h.end():end].strip()))
    return sections, guidance


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--task", help="task id prefix")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--list", action="store_true", help="list sections and guidance blocks with sizes (default)")
    g.add_argument("--section", help="print one <section>")
    g.add_argument("--guidance", help="print one tool guidance block (e.g. Subagents, create_html_artifact)")
    g.add_argument("--grep", help="regex; print matching lines with their section")
    g.add_argument("--all", action="store_true", help="print the whole prompt")
    _bobcheck.add_arguments(ap)
    a = ap.parse_args()
    _bobcheck.check("dump_system_prompt", db_path=a.db, quiet=a.no_version_check, strict=a.strict)

    con = open_db(a.db)
    task, created, text = latest_prompt(con, a.task)
    sections, guidance = split(text)
    import datetime as dt
    stamp = dt.datetime.fromtimestamp(created / 1000).strftime("%Y-%m-%d %H:%M:%S")
    print(f"# task {task[:8]} · {stamp} · {len(text):,} chars", file=sys.stderr)

    if a.all:
        print(text)
        return
    if a.section:
        for name, body, _ in sections:
            if name == a.section:
                print(body)
                return
        sys.exit(f"no section {a.section}; available: {', '.join(n for n, _, _ in sections)}")
    if a.guidance:
        for name, title, body in guidance:
            if name.lower() == a.guidance.lower():
                print(f"# {title}\n{body}")
                return
        sys.exit(f"no guidance {a.guidance}; available: {', '.join(n for n, _, _ in guidance)}")
    if a.grep:
        rx = re.compile(a.grep, re.I)
        hits = 0
        for m in rx.finditer(text):
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line_end = len(text) if line_end < 0 else line_end
            where = "?"
            for name, _, pos in sections:
                if pos <= m.start():
                    where = name
            for name, _, _ in guidance:
                idx = text.find(f"# {name}")
                if 0 <= idx <= m.start():
                    where = f"guidance:{name}"
            print(f"[{where}] {text[line_start:line_end].strip()}")
            hits += 1
        print(f"\n{hits} match(es)")
        return
    for name, body, _ in sections:
        print(f"  section   {name:<28} {len(body):>7,} chars")
    for name, title, body in guidance:
        print(f"  guidance  {name:<28} {len(body):>7,} chars")


if __name__ == "__main__":
    main()
