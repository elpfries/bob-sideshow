#!/usr/bin/env python3
"""Quota d'abonnement Kimi Code via le serveur local (app Desktop ou `kimi web`).

  quota_check.py [--json] [--home PATH]

Lit le port dans ~/.kimi-code/server/instances/*.json (instance vivante au heartbeat le plus
récent) et le token dans ~/.kimi-code/server.token, puis appelle GET /api/v1/oauth/usage.
Read-only; Python 3.8+, bibliothèque standard uniquement. Vérifié le 2026-09-20 contre Kimi
Code Desktop 2.0.1.
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_HOME = os.path.join(os.path.expanduser("~"), ".kimi-code")
ROUTE = "/api/v1/oauth/usage"
HEARTBEAT_MAX_AGE_S = 300


def parse_ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def human_delay(delta):
    s = max(0, int(delta.total_seconds()))
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m = s // 60
    if d:
        return f"{d} j {h} h" if h else f"{d} j"
    if h:
        return f"{h} h {m:02d} min"
    return f"{m} min"


def month_start(reset):
    y, m = (reset.year, reset.month - 1) if reset.month > 1 else (reset.year - 1, 12)
    day = min(reset.day, 28)
    return reset.replace(year=y, month=m, day=day)


def find_token(home):
    path = os.path.join(home, "server.token")
    if not os.path.isfile(path):
        sys.exit(f"token introuvable : {path}")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def fetch_usage(home, token):
    inst = sorted(glob.glob(os.path.join(home, "server", "instances", "*.json")),
                  key=os.path.getmtime, reverse=True)
    if not inst:
        sys.exit("aucune instance de serveur local — lance l'app Kimi Code Desktop ou `kimi web`")
    errors = []
    now_ms = dt.datetime.now(dt.timezone.utc).timestamp() * 1000
    for path in inst:
        try:
            with open(path, encoding="utf-8") as f:
                meta = json.load(f)
        except (ValueError, OSError) as e:
            errors.append(f"{path}: {e}")
            continue
        age_s = (now_ms - (meta.get("heartbeat_at") or 0)) / 1000
        if age_s > HEARTBEAT_MAX_AGE_S:
            errors.append(f"{meta.get('host')}:{meta.get('port')} — heartbeat vieux de {int(age_s)} s")
            continue
        url = f"http://{meta['host']}:{meta['port']}{ROUTE}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                                   "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                body = json.load(r)
        except (urllib.error.URLError, ValueError, OSError) as e:
            errors.append(f"{meta['host']}:{meta['port']} — {e}")
            continue
        if isinstance(body, dict) and body.get("code") == 0:
            return body["data"], meta
        errors.append(f"{meta['host']}:{meta['port']} — réponse inattendue : {str(body)[:120]}")
    sys.exit("aucune instance n'a répondu sur " + ROUTE + " :\n  " + "\n  ".join(errors))


def pace_line(name, u, now, period_start):
    """Ligne d'une fenêtre de quota : % utilisé, reset, burn rate mensuel."""
    used = (u.get("usedRatio") or 0) * 100
    reset = parse_ts(u["resetAt"])
    left = human_delay(reset - now)
    line = {"name": name, "usedPct": round(used, 2), "resetAt": u["resetAt"],
            "resetIn": left}
    if period_start is None:
        return line, f"{name:14} {used:5.1f} % utilisés · reset dans {left}"
    total = (reset - period_start).total_seconds()
    elapsed = min(max((now - period_start).total_seconds(), 0), total)
    elapsed_pct = elapsed / total * 100 if total else 0
    pace = used / elapsed_pct * 100 if elapsed_pct > 0 and used > 0 else 0.0
    line.update({"periodElapsedPct": round(elapsed_pct, 2), "pacePct": round(pace)})
    txt = f"{name:14} {used:5.1f} % utilisés · période écoulée à {elapsed_pct:.1f} % · reset dans {left}"
    if used <= 0 or elapsed_pct <= 0:
        return line, txt + " · burn rate n/a"
    txt += f" · burn rate {pace:.0f} %"
    if elapsed_pct < 5:
        txt += " — début de période, peu significatif"
    elif pace > 100 and used > 0:
        end = period_start + dt.timedelta(seconds=elapsed / (used / 100))
        line["projectedExhaustion"] = end.strftime("%Y-%m-%d")
        txt += f" — à ce burn rate, épuisement vers le {end.strftime('%d/%m')}"
    else:
        txt += " — dans les temps"
    return line, txt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", default=DEFAULT_HOME)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    data, meta = fetch_usage(a.home, find_token(a.home))
    if data.get("kind") != "ok":
        sys.exit(f"réponse inattendue du serveur : kind={data.get('kind')!r} "
                 "(compte non géré ? l'endpoint ne couvre que l'abonnement)")
    now = dt.datetime.now(dt.timezone.utc)
    usages = (data.get("quota") or {}).get("usages") or {}
    lines, texts = [], []
    if "limit5h" in usages:
        line, txt = pace_line("fenêtre 5 h", usages["limit5h"], now, None)
        lines.append(line); texts.append(txt)
    for key, label, with_pace in (("monthCode", "mois (code)", True), ("monthTotal", "mois (total)", True)):
        if key in usages:
            reset = parse_ts(usages[key]["resetAt"])
            line, txt = pace_line(label, usages[key], now, month_start(reset))
            lines.append(line); texts.append(txt)
    extra = (data.get("quota") or {}).get("extraUsage")
    out = {"server": f"{meta.get('host')}:{meta.get('port')}", "hostVersion": meta.get("host_version"),
           "quotas": lines, "extraUsage": extra}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"quota Kimi Code · serveur local {out['server']} (app {out['hostVersion']})")
    for t in texts:
        print("  " + t)
    print(f"  extra usage    {'activé' if extra else 'non activé'}")
    print("  burn rate = % du quota consommé ÷ % de la période écoulée (100 % = dans les temps)")


if __name__ == "__main__":
    main()
