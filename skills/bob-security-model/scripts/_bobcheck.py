#!/usr/bin/env python3
"""Version guard for bob-sideshow scripts. Identical copy in every skill's scripts/ folder.

check() compares the installed bob-code extension (and the bob.db schema when a database path is
given) with the build the scripts were verified on, prints one line on stderr and returns a dict.
It exits 3 only with strict=True.
"""
import json
import os
import platform
import shutil
import sqlite3
import sys

VERIFIED_EXTENSION = "2.1.0"
VERIFIED_SCHEMA = "010_pending_approvals"
HOME = os.path.expanduser("~")


def app_candidates():
    system = platform.system()
    c = [os.environ["BOB_SIDESHOW_APP"]] if os.environ.get("BOB_SIDESHOW_APP") else []
    if system == "Darwin":
        c += ["/Applications/IBM Bob.app/Contents/Resources/app",
              os.path.join(HOME, "Applications/IBM Bob.app/Contents/Resources/app")]
    elif system == "Windows":
        for base in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles", ""),
                     os.environ.get("ProgramFiles(x86)", "")):
            if base:
                c += [os.path.join(base, "Programs", "IBM Bob", "resources", "app"),
                      os.path.join(base, "IBM Bob", "resources", "app")]
    else:
        c += ["/usr/share/ibm-bob/resources/app", "/usr/share/bobide/resources/app",
              "/opt/IBM Bob/resources/app", "/opt/ibm-bob/resources/app", "/opt/bobide/resources/app",
              os.path.join(HOME, ".local/share/ibm-bob/resources/app")]
    for exe in ("bobide", "ibm-bob"):
        p = shutil.which(exe)
        if p:
            p = os.path.realpath(p)
            c += [os.path.join(os.path.dirname(p), "resources", "app"),
                  os.path.join(os.path.dirname(os.path.dirname(p)), "resources", "app")]
    out = []
    for x in c:
        if x not in out and os.path.isfile(os.path.join(x, "product.json")):
            out.append(x)
    return out


def installed_extension_version():
    for app in app_candidates():
        try:
            with open(os.path.join(app, "extensions", "bob-code", "package.json"), encoding="utf-8") as f:
                return json.load(f).get("version")
        except Exception:
            continue
    return None


def db_last_migration(db_path):
    if not db_path or not os.path.isfile(db_path):
        return None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        row = con.execute("select name from _migrations order by applied_at desc, name desc limit 1").fetchone()
        con.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def check(script, db_path=None, quiet=False, strict=False, logic_from_bundle=False):
    ext = installed_extension_version()
    schema = db_last_migration(db_path) if db_path else None
    problems = []
    if ext is None:
        problems.append("IBM Bob IDE not found (set BOB_SIDESHOW_APP to its resources/app folder)")
    elif ext != VERIFIED_EXTENSION:
        problems.append(f"bob-code {ext} installed, verified on {VERIFIED_EXTENSION}")
    if schema and schema != VERIFIED_SCHEMA:
        problems.append(f"schema {schema}, verified on {VERIFIED_SCHEMA}")
    status = {"script": script, "extension": ext, "schema": schema, "verifiedExtension": VERIFIED_EXTENSION,
              "verifiedSchema": VERIFIED_SCHEMA, "match": not problems, "problems": problems}
    if not quiet:
        if problems:
            hint = "matcher logic comes from the 2.1.0 bundle" if logic_from_bundle else "unknown fields are ignored"
            print("[bob-sideshow] WARNING: " + "; ".join(problems) + f" — {hint}", file=sys.stderr)
        else:
            print(f"[bob-sideshow] bob-code {ext}" + (f", schema {schema}" if schema else "") + " — verified build",
                  file=sys.stderr)
    if strict and problems:
        sys.exit(3)
    return status


def add_arguments(parser):
    parser.add_argument("--no-version-check", action="store_true", help="silence the version line")
    parser.add_argument("--strict", action="store_true", help="exit 3 if the installed Bob differs from the verified build")
