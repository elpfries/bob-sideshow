#!/usr/bin/env python3
"""Would IBM Bob (bob-code 2.1.0) auto-approve this shell command?

  approval_check.py "<command line>" [--settings PATH] [--approved PAT ...] [--denied PAT ...] [--json]

Reproduces the token-prefix matcher, the allow/deny resolution, the always-on regex heuristics and
the .bob-settings detection. It cannot run Bob's model-based check, and it splits the line with a
regex approximation of tree-sitter (quoted separators and subshells are not handled).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bobcheck  # noqa: E402

DEFAULT_APPROVED = ["cat", "git diff", "git log", "git rev-parse", "git show", "git status", "grep",
                    "head", "tail", "ls", "sort", "wc", "which", "du", "df"]
DEFAULT_SETTINGS = os.path.join(os.path.expanduser("~"), ".bob", "settings", "settings.json")
HEURISTICS = [
    (re.compile(r"\$\{[^}]*@[PQEAa][^}]*\}"), "${var@P|Q|E|A|a} transformation"),
    (re.compile(r"\$\{[^}]*[=+\-?][^}]*\\[0-7]{3}[^}]*\}"), "octal escape in ${…}"),
    (re.compile(r"\$\{[^}]*[=+\-?][^}]*\\x[0-9a-fA-F]{2}[^}]*\}"), "hex escape in ${…}"),
    (re.compile(r"\$\{[^}]*[=+\-?][^}]*\\u[0-9a-fA-F]{4}[^}]*\}"), "unicode escape in ${…}"),
    (re.compile(r"\$\{![^}]+\}"), "indirect expansion ${!name}"),
    (re.compile(r"<<<\s*(\$\(|`)"), "here-string fed by command substitution"),
    (re.compile(r"[*?+@!]\(e:[^:]+:\)"), "extglob obfuscation"),
]
TAIL = [re.compile(r"\|\s*(bash|sh|zsh|fish|python\d*|perl|ruby)\b", re.I),
        re.compile(r"\|\s*sudo\s+(bash|sh)", re.I), re.compile(r"base64\s+-d\s*\|\s*(bash|sh)", re.I)]
BOB_SETTINGS = re.compile(r"""(?:^|[\\/\s"'=<>])\.bob[\\/](?:settings[\\/])?settings\.json(?=$|[\s"';&|<>()])""", re.I)


def split_commands(line):
    return [p for p in (x.strip() for x in re.split(r"\s*(?:\|\||&&|\||;|\n)\s*", line.strip())) if p]


def longest_match(command, patterns):
    words = command.split()
    best, best_len = None, -1
    for pat in patterns:
        toks = pat.split()
        if toks and len(toks) <= len(words) and all(t == words[i] for i, t in enumerate(toks)) and len(toks) > best_len:
            best, best_len = pat, len(toks)
    return best


def decide(command, approved, denied):
    a, d = longest_match(command, approved), longest_match(command, denied)
    if not a and not d:
        return "none", a, d
    if not d:
        return "allow", a, d
    if not a:
        return "deny", a, d
    return ("allow" if len(a.split()) >= len(d.split()) else "deny"), a, d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command")
    ap.add_argument("--settings", default=DEFAULT_SETTINGS)
    ap.add_argument("--approved", action="append", default=[], help="extra approved pattern")
    ap.add_argument("--denied", action="append", default=[], help="extra denied pattern")
    ap.add_argument("--json", action="store_true")
    _bobcheck.add_arguments(ap)
    a = ap.parse_args()
    _bobcheck.check("approval_check", quiet=a.no_version_check, strict=a.strict, logic_from_bundle=True)

    try:
        with open(a.settings, encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        st = {}
    approval = st.get("approval") or {}
    ex = next((e for e in approval.get("allowedExecutors") or [] if e.get("toolId") == "execute_command"), None) \
        or {"approvedCommands": DEFAULT_APPROVED, "deniedCommands": []}
    approved = list(ex.get("approvedCommands") or []) + a.approved
    denied = list(ex.get("deniedCommands") or []) + a.denied
    allowed = approval.get("allowed_permissions", ["read"])

    reasons = []
    if not approval.get("autoApprovalEnabled", True):
        reasons.append("autoApprovalEnabled is false")
    if "execute" in (approval.get("forbiddenApprovalGroups") or []):
        reasons.append("execute is forbidden for auto-approval")
    heur = [why for rx, why in HEURISTICS if rx.search(a.command)]
    if heur:
        reasons.append("requiresSecurityApproval by heuristic: " + "; ".join(heur))
    if len(a.command) > 5000 and any(rx.search(a.command[5000:]) for rx in TAIL):
        reasons.append("requiresSecurityApproval: too long, shell pipe in truncated tail")
    if BOB_SETTINGS.search(a.command):
        reasons.append("isBobHomeWrite: references .bob settings")
    if "execute" not in allowed:
        reasons.append("execute not in allowed_permissions")
    subs = [dict(zip(("command", "verdict", "approvedMatch", "deniedMatch"), (c, *decide(c, approved, denied)))) for c in split_commands(a.command)]
    if not subs:
        reasons.append("unverifiable: no command found")
    denied_hits = [s for s in subs if s["verdict"] == "deny"]
    unmatched = [s for s in subs if s["verdict"] == "none"]
    if denied_hits:
        reasons.append("deny list: " + ", ".join(f'"{s["deniedMatch"]}"' for s in denied_hits))
    elif unmatched:
        reasons.append("no approved pattern: " + ", ".join(f'"{s["command"]}"' for s in unmatched))
    security_on = st.get("isCommandSecurityEnabled", True)
    outcome = ("BLOCKED by deny list" if denied_hits else "PROMPT" if reasons
               else "AUTO-APPROVED" + (" unless the model check flags it" if security_on else ""))

    if a.json:
        print(json.dumps({"command": a.command, "outcome": outcome, "reasons": reasons, "subcommands": subs,
                          "isCommandSecurityEnabled": security_on, "settings": a.settings if st else None}, indent=2, ensure_ascii=False))
        return
    print(f"{a.command} → {outcome}")
    for r in reasons:
        print(f"  {r}")
    for s in subs:
        if len(subs) == 1 and s["verdict"] == "none":
            break
        match = s["approvedMatch"] and f'approved "{s["approvedMatch"]}"'
        deny = s["deniedMatch"] and f'denied "{s["deniedMatch"]}"'
        print(f"  {s['verdict']:<5} {s['command']}" + (f"  ({', '.join(x for x in (match, deny) if x)})" if match or deny else ""))
    print(f"model check {'on' if security_on else 'off'} · {len(approved)} approved · {len(denied)} denied · allowed_permissions {', '.join(allowed)}"
          + ("" if st else " · settings not found, defaults used"))


if __name__ == "__main__":
    main()
