#!/usr/bin/env python3
"""Would IBM Bob (bob-code 2.3.0) auto-approve this shell command?

  approval_check.py "<command line>" [--settings PATH] [--workspace DIR] [--approved PAT ...]
                    [--denied PAT ...] [--json]

Reproduces the token-prefix matcher, the allow/deny resolution, the always-on regex heuristics, the
.bob-settings detection and, as an APPROXIMATION, the ignored-path write gate that 2.3.0 added to the
command security check (read in build 1.126.0+bob2.3.0.20261026121409, dist/extension.js, functions
around the anchor "Command attempts to write to a path blocked by .gitignore or .bobignore.").

That gate flags a command whose text redirects (> >>), tee's, dd's (of=), cp/mv's or PowerShell-writes
(Set-Content, Add-Content, Out-File) to a path matched by the workspace ignore patterns. Bob takes the
patterns from <workspace>/.bobignore, plus <workspace>/.gitignore only when the setting
session.respectGitIgnore is true (default false); it ignores empty lines, comments and "!" lines and
strips trailing slashes; it matches with the node-ignore library (case-insensitive). This script reads
the same files from --workspace (default: the current directory) and matches them with a small
gitignore-to-regex translation, which is an approximation of node-ignore: exotic patterns (escapes,
character-class corner cases, nested negation) may differ. Paths containing "$" and paths outside the
workspace are skipped, as in Bob. The gate runs before the isCommandSecurityEnabled test, so it applies
with command security off; like Bob's, it needs no model call.

It cannot run Bob's model-based check, and it splits the line with a regex approximation of
tree-sitter (quoted separators and subshells are not handled; Bob's parse-error "unverifiable" case
is not reproduced).
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


# Ignored-path write gate (2.3.0). Group 2 of every pattern is the written path. Ported from the seven
# regexes of the bundle (JS "$" = end of string, hence \\Z here).
WRITE_TARGETS = [
    re.compile(r"""(?<![<>])>{1,2}\s*(['"]?)([^\s|&;'"]+)\1"""),
    re.compile(r"""\btee\s+(?:-a\s+)?(['"]?)([^\s|&;'"]+)\1"""),
    re.compile(r"""\bdd\b[^|&;]*?\bof=(['"]?)([^\s|&;'"]+)\1"""),
    re.compile(r"""\b(?:cp|mv)\b[^|&;]*?\s+(?:-t\s+|--target-directory=)(['"]?)([^\s|&;'"]+)\1"""),
    re.compile(r"""\b(?:cp|mv)\b(?:[ \t]+-[a-zA-Z0-9_-]+)*(?:[ \t]+(?!--)(?:'[^']*'|"[^"]*"|\S+))+[ \t]+(['"]?)([^\s|&;'"]+)\1(?=[ \t]*(?:[|&;\r\n]|\Z))"""),
    re.compile(r"""\b(?:Set-Content|Add-Content|Out-File)\b[^|&;]*?\s+-(?:Path|FilePath|LiteralPath)\s+(['"]?)([^\s|&;'"]+)\1""", re.I),
    re.compile(r"""\b(?:Set-Content|Add-Content|Out-File)\b(?:[ \t]+-[a-zA-Z0-9]+)*[ \t]+(['"]?)([^\s|&;'"-][^\s|&;'"]*)\1""", re.I),
]
IGNORE_REASON = "Command attempts to write to a path blocked by .gitignore or .bobignore."


def read_ignore_patterns(workspace, respect_gitignore):
    """User patterns as Bob builds them: .bobignore always, .gitignore only if respectGitIgnore."""
    pats, files = [], []
    for name in ((".gitignore",) if respect_gitignore else ()) + (".bobignore",):
        try:
            with open(os.path.join(workspace, name), encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        got = 0
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!"):
                pats.append((re.sub(r"/+$", "", line), name))
                got += 1
        files.append(f"{name} ({got})")
    return pats, files


def _glob_to_regex(pat):
    out, i, n = [], 0, len(pat)
    while i < n:
        c = pat[i]
        if pat.startswith("**/", i) and (i == 0 or pat[i - 1] == "/"):
            out.append("(?:.*/)?")
            i += 3
        elif pat.startswith("/**", i) and i + 3 == n:
            out.append("/.*")
            i += 3
        elif c == "*":
            j = i
            while j < n and pat[j] == "*":
                j += 1
            out.append(".*" if j - i > 1 else "[^/]*")
            i = j
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c == "[":
            j = pat.find("]", i + 2)
            if j < 0:
                out.append(re.escape(c))
                i += 1
            else:
                body = pat[i + 1:j]
                out.append("[" + ("^" if body[:1] in "!^" and body else "") + body.lstrip("!^").replace("\\", "\\\\") + "]")
                i = j + 1
        elif c == "\\" and i + 1 < n:
            out.append(re.escape(pat[i + 1]))
            i += 2
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


def ignored_by(rel, patterns):
    """First (pattern, file) whose gitignore rule ignores the workspace-relative path or a parent dir."""
    parts = [p for p in rel.split("/") if p]
    for pat, src in patterns:
        anchored = "/" in pat
        body = pat[1:] if pat.startswith("/") else pat
        try:
            rx = re.compile(_glob_to_regex(body) + r"\Z", re.I)
        except re.error:
            continue
        for k in range(1, len(parts) + 1):
            if rx.match("/".join(parts[:k]) if anchored else parts[k - 1]):
                return pat, src
    return None


def ignored_write(command, workspace, patterns):
    """Return (written path, pattern, file) for the first write target that Bob's gate would flag."""
    if not patterns:
        return None
    ws = os.path.normpath(workspace)
    for rx in WRITE_TARGETS:
        for m in rx.finditer(command):
            target = m.group(2)
            if not target or "$" in target:
                continue
            if target == "~" or target.startswith("~/"):
                target = os.path.expanduser(target)
            full = os.path.normpath(os.path.join(ws, target))
            rel = os.path.relpath(full, ws)
            if rel == "." or rel == ".." or rel.startswith(".." + os.sep) or os.path.isabs(rel):
                continue  # outside the workspace: Bob skips it (~/.bob and the terminal-history dir not modelled)
            hit = ignored_by(rel.replace(os.sep, "/"), patterns)
            if hit:
                return target, hit[0], hit[1]
    return None


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
    ap.add_argument("--workspace", default=os.getcwd(), help="workspace root whose .bobignore/.gitignore feed the ignored-path write gate")
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
    respect_git = bool((st.get("session") or {}).get("respectGitIgnore", False))
    ignore_pats, ignore_files = read_ignore_patterns(a.workspace, respect_git)
    ignore_hit = None if heur else ignored_write(a.command, a.workspace, ignore_pats)
    if heur:
        reasons.append("requiresSecurityApproval by heuristic: " + "; ".join(heur))
    elif ignore_hit:
        reasons.append(f'requiresSecurityApproval (ignored-path write, {ignore_hit[2]}): writes "{ignore_hit[0]}", '
                       f'pattern "{ignore_hit[1]}" - {IGNORE_REASON}')
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
                          "isCommandSecurityEnabled": security_on, "settings": a.settings if st else None,
                          "ignoredPathGate": {"modelled": "approximation", "workspace": a.workspace, "files": ignore_files,
                                              "hit": list(ignore_hit) if ignore_hit else None}}, indent=2, ensure_ascii=False))
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
    print("ignored-path write gate (approximation): " + (", ".join(ignore_files) if ignore_files else "no ignore file read, not applied")
          + f" in {a.workspace}" + ("" if respect_git else " (.gitignore not read: session.respectGitIgnore is not true)"))


if __name__ == "__main__":
    main()
