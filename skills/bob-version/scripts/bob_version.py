#!/usr/bin/env python3
"""Which IBM Bob is installed: app, extension build, Bob Shell, database schema, server model flags.

  python3 bob_version.py [--json] [--app PATH_TO_resources/app]

Read-only; Python 3.8+, standard library only.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bobcheck  # noqa: E402

HOME = os.path.expanduser("~")
SYSTEM = platform.system()
FLAG_KEYS = ("command-security-model", "summary-model", "completion-model", "next-edit-model", "feedback-model",
             "command-security-enabled")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def app_info(app):
    info = {"path": app}
    prod = read_json(os.path.join(app, "product.json")) or {}
    for k in ("nameLong", "version", "commit", "quality", "updateUrl", "dataFolderName"):
        if k in prod:
            info[k] = prod[k]
    if SYSTEM == "Darwin":
        try:
            import plistlib
            with open(os.path.join(os.path.dirname(os.path.dirname(app)), "Info.plist"), "rb") as f:
                pl = plistlib.load(f)
            info["bundleVersion"] = pl.get("CFBundleShortVersionString")
            info["bundleBuild"] = pl.get("CFBundleVersion")
        except Exception:
            pass
    ext = os.path.join(app, "extensions", "bob-code")
    pkg = read_json(os.path.join(ext, "package.json")) or {}
    bundle = os.path.join(ext, "dist", "extension.js")
    e = {"version": pkg.get("version")}
    if os.path.isfile(bundle):
        st = os.stat(bundle)
        e.update(bundleBytes=st.st_size, bundleModified=dt.date.fromtimestamp(st.st_mtime).isoformat(), bundleSha1=sha1(bundle))
    info["extension"] = e
    return info


def shell_info():
    exe = shutil.which("bob")
    if not exe:
        return {"installed": False}
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=5)
        ver = (out.stdout or out.stderr).strip()
    except Exception as ex:  # noqa: BLE001
        ver = f"error: {ex}"
    return {"installed": True, "path": exe, "version": ver}


def data_info():
    bob = os.path.join(HOME, ".bob")
    d = {"bobHome": bob}
    for name, rel in (("settings", "settings/settings.json"), ("database", "db/bob.db"), ("rules", "rules"),
                      ("skills", "skills"), ("agents", "agents")):
        p = os.path.join(bob, rel)
        d[name] = p if os.path.exists(p) else None
    d["ideDataFolder"] = {"Darwin": os.path.join(HOME, "Library/Application Support/IBM Bob"),
                          "Windows": os.path.join(os.environ.get("APPDATA", ""), "IBM Bob")}.get(
        SYSTEM, os.path.join(HOME, ".config/IBM Bob"))
    return d


def db_info(path):
    if not path:
        return {"present": False}
    r = {"present": True, "path": path}
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        r["migrations"] = [row[0] for row in con.execute("select name from _migrations order by applied_at")]
        for t in ("tasks", "messages", "attribution_logs"):
            r[t] = con.execute(f"select count(*) from {t}").fetchone()[0]
        con.close()
    except sqlite3.Error as ex:
        r["error"] = str(ex)
    return r


def flags_info(ide_folder):
    p = os.path.join(ide_folder, "User", "globalStorage", "state.vscdb")
    if not os.path.isfile(p):
        return {"path": p}
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        row = con.execute("select value from ItemTable where key='IBM.bob-code'").fetchone()
        con.close()
        cache = json.loads(row[0]).get("bob.featureFlags.cache", {}) if row else {}
    except Exception:
        return {"path": p}
    return {"path": p, "count": len(cache),
            "flags": {k: v for k, v in cache.items() if k in FLAG_KEYS or k.startswith("experiment-")}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--app", help="path to the app's resources/app directory")
    a = ap.parse_args()
    if a.app:
        os.environ["BOB_SIDESHOW_APP"] = a.app

    apps = [app_info(x) for x in _bobcheck.app_candidates()]
    data = data_info()
    report = {"system": f"{SYSTEM} {platform.release()} {platform.machine()}", "apps": apps, "shell": shell_info(),
              "data": data, "database": db_info(data["database"]), "serverFlags": flags_info(data["ideDataFolder"]),
              "reference": _bobcheck.check("bob_version", db_path=data["database"], quiet=True)}
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if not apps:
        print("IBM Bob      not found — pass --app <path to resources/app>")
    for app in apps:
        e = app["extension"]
        print(f"IBM Bob      {app.get('bundleVersion') or app.get('version', '?')}  build {app.get('bundleBuild') or app.get('version', '?')}  {app['path']}")
        print(f"bob-code     {e.get('version', '?')}  extension.js {e.get('bundleBytes', 0):,} B  sha1 {str(e.get('bundleSha1', '?'))[:12]}  {e.get('bundleModified', '')}"
              + (f"  updates {app['updateUrl']}" if app.get("updateUrl") else ""))
    sh = report["shell"]
    print(f"Bob Shell    {sh['version'] + '  ' + sh['path'] if sh.get('installed') else 'not on PATH'}")
    present = [k for k in ("settings", "rules", "skills", "agents") if data[k]]
    print(f"~/.bob       {', '.join(present) or 'absent'}")
    db = report["database"]
    if db.get("present") and not db.get("error"):
        mig = db.get("migrations") or []
        print(f"bob.db       schema {mig[-1] if mig else '?'} ({len(mig)} migrations) · {db['tasks']} tasks · {db['messages']} messages · {db['attribution_logs']} attribution logs")
    else:
        print(f"bob.db       {db.get('error') or 'absent'}")
    fl = report["serverFlags"].get("flags") or {}
    if fl:
        print("server flags " + "  ".join(f"{k}={json.dumps(v)}" for k, v in sorted(fl.items())))
    ref = report["reference"]
    print("reference    " + ("MATCH — verified on bob-code " + ref["verifiedExtension"] + " / " + ref["verifiedSchema"]
                             if ref["match"] else "DIFFERENT — " + "; ".join(ref["problems"]) + " — reference notes may be stale"))


if __name__ == "__main__":
    main()
