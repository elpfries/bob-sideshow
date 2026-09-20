#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash), DUAL-PROTOCOLE Claude Code / Kimi Code.
# Fires BEFORE a `backlog task edit ... -s "In Progress"` runs and, under the
# Kimi Code runtime only, gates the start of a backlog task on the 5-hour
# subscription quota window: if more than BACKLOG_QUOTA_GATE_PCT percent
# (default 80) of the window is consumed, the start is REFUSED and the agent
# is instructed to schedule a one-shot CronCreate at the window reset, so the
# task resumes by itself — the user never has to relaunch anything.
#
# Symmetric to pre-task-done.sh (which gates `-s Done`). Differences:
#   - enforcement is Kimi-only: the 5h window is a Kimi Code subscription
#     notion, so a claude runtime exits 0 immediately;
#   - fail-open: if the local quota server (Kimi Code Desktop app or
#     `kimi web`) is unreachable, the start is allowed with a stderr warning —
#     a gate that cannot measure must not block work;
#   - BACKLOG_QUOTA_GATE_PCT overrides the 80% threshold (used by tests to
#     force the block path), BACKLOG_QUOTA_HOME overrides the Kimi home the
#     quota script reads (used by tests to simulate an absent server).
#
# Runtime detection: BACKLOG_HOOK_RUNTIME (set in the hook declaration) wins;
# otherwise the stdin JSON is sniffed (client_type => kimi, transcript_path /
# permission_mode => claude); default kimi.
#
# Blocking output per protocol:
#   kimi   : reason on stderr, exit 2
#   claude : {"hookSpecificOutput":{...,"permissionDecision":"deny",...}} on
#            stdout, exit 0
# Allow is exit 0 with no output in both protocols (a stderr warning may still
# be emitted on the fail-open path; it does not block).

input="$(cat)"

runtime="${BACKLOG_HOOK_RUNTIME:-}"
if [ -z "$runtime" ]; then
  case "$input" in
    *'"client_type"'*) runtime=kimi ;;
    *'"transcript_path"'*|*'"permission_mode"'*) runtime=claude ;;
    *) runtime=kimi ;;
  esac
fi

# The 5h quota window only exists under Kimi Code.
[ "$runtime" = "kimi" ] || exit 0

# --- Extraction JSON : jq, avec repli python3 --------------------------------
if command -v jq >/dev/null 2>&1; then
  json_get() { printf '%s' "$input" | jq -r "$1 // empty"; }
else
  _json_tmp="$(mktemp -t backlog-hook)"
  printf '%s' "$input" > "$_json_tmp"
  trap 'rm -f "$_json_tmp"' EXIT
  json_get() {
    python3 - "$_json_tmp" "$1" <<'PYEOF'
import json, sys
tmp, path = sys.argv[1], sys.argv[2]
try:
    with open(tmp) as f:
        cur = json.load(f)
except Exception:
    sys.exit(0)
for key in path.lstrip('.').split('.'):
    if isinstance(cur, dict) and key in cur:
        cur = cur[key]
    else:
        sys.exit(0)
if cur is None:
    sys.exit(0)
if isinstance(cur, bool):
    print('true' if cur else 'false')
elif isinstance(cur, (dict, list)):
    print(json.dumps(cur, ensure_ascii=False))
else:
    print(cur)
PYEOF
  }
fi

block() {
  # Ce hook ne s'exécute que sous le runtime kimi (voir garde plus haut) :
  # raison sur stderr, exit 2. La branche claude est conservée pour le jour
  # où un équivalent de quota y existerait.
  if [ "$runtime" = "claude" ]; then
    python3 - "$1" <<'PYEOF'
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": sys.argv[1]}}, ensure_ascii=False))
PYEOF
    exit 0
  fi
  printf '%s\n' "$1" >&2
  exit 2
}

command="$(json_get '.tool_input.command')"
[ -n "$command" ] || exit 0

# Racine du projet : le cwd fourni par le runtime, sinon repli. Hors d'un
# projet Backlog.md : no-op.
proj="$(json_get '.cwd')"
{ [ -n "$proj" ] && [ -d "$proj" ]; } || proj="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$proj/backlog/tasks" ] || exit 0

# Seule la transition vers In Progress est gatée. Accepte -s/--status, avec ou
# sans guillemets ; "Done"/"To Do" ne matchent jamais.
printf '%s' "$command" | grep -Eq '(^|[;&|]) *backlog +task +edit ' || exit 0
printf '%s' "$command" | grep -Eq -- '(-s|--status) +"?In Progress"?( |$)' || exit 0

task_id="$(printf '%s' "$command" | sed -nE 's/.*backlog +task +edit +(TASK-)?([0-9]+(\.[0-9]+)*).*/\2/p' | head -n1)"
[ -n "$task_id" ] || exit 0

# --- Relevé de quota via la skill quota-check --------------------------------
quota_script="$proj/.kimi-code/skills/quota-check/scripts/quota_check.py"
[ -f "$quota_script" ] || quota_script="$proj/.claude/skills/quota-check/scripts/quota_check.py"
if [ ! -f "$quota_script" ]; then
  printf 'avertissement pre-task-start : script quota-check introuvable, démarrage de TASK-%s autorisé sans contrôle de quota\n' "$task_id" >&2
  exit 0
fi
quota_home="${BACKLOG_QUOTA_HOME:-$HOME/.kimi-code}"
quota_json="$(python3 "$quota_script" --json --home "$quota_home" 2>/dev/null)"
if [ $? -ne 0 ] || [ -z "$quota_json" ]; then
  printf 'avertissement pre-task-start : serveur local de quota injoignable (app Kimi Code Desktop ou `kimi web` non lancée ?), démarrage de TASK-%s autorisé sans contrôle de quota\n' "$task_id" >&2
  exit 0
fi

_quota_tmp="$(mktemp -t backlog-quota)"
printf '%s' "$quota_json" > "$_quota_tmp"
trap 'rm -f "$_quota_tmp"' EXIT

# python3 écrit le message de blocage complet sur stdout et sort 3 quand le
# seuil est dépassé ; sort 0 (silencieux) sinon. Toute autre sortie non nulle
# est un défaut de parsing -> fail-open avec avertissement.
block_msg="$(python3 - "$_quota_tmp" "$task_id" "${BACKLOG_QUOTA_GATE_PCT:-80}" <<'PYEOF'
import datetime as dt
import json
import sys

tmp, task_id, threshold = sys.argv[1], sys.argv[2], float(sys.argv[3])
with open(tmp, encoding="utf-8") as f:
    data = json.load(f)
win = None
for q in data.get("quotas", []):
    if q.get("name") == "fenêtre 5 h":
        win = q
        break
if win is None:
    sys.exit(0)
used = float(win.get("usedPct") or 0)
if used <= threshold:
    sys.exit(0)
reset_utc = dt.datetime.strptime(win["resetAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
reset_local = reset_utc.astimezone()
retry_at = reset_local + dt.timedelta(minutes=1)
cron = f"{retry_at.minute} {retry_at.hour} {retry_at.day} {retry_at.month} *"
print(f"""Démarrage de TASK-{task_id} DIFFÉRÉ : la fenêtre de quota 5 h de Kimi Code est consommée à {used:.1f} % (seuil : {threshold:g} %). Reset à {win['resetAt']} ({reset_local.strftime('%H:%M')} heure locale), {win.get('resetIn', '?')} restantes.

Ne relance PAS la commande maintenant : elle serait refusée à nouveau. Procédure d'attente automatique :

1. Planifie un CronCreate one-shot juste après le reset :
   cron: "{cron}"  (heure locale), recurring: false,
   prompt: « Le quota de la fenêtre 5 h est réinitialisé. Reprends le traitement de TASK-{task_id} : passe-la In Progress (backlog task edit TASK-{task_id} -s "In Progress") puis continue son exécution. »
2. Termine ton tour en annonçant à l'utilisateur : quota 5 h à {used:.1f} %, reprise automatique prévue à {retry_at.strftime('%H:%M')} heure locale.
3. Au déclenchement du cron, la commande passera : la fenêtre sera réinitialisée et ce hook laissera passer.

Limite assumée : la reprise automatique exige que cette session reste ouverte — le scheduler ne tire que sur une session vivante. Si la session est fermée avant le reset, la tâche devra être relancée à la main.""")
sys.exit(3)
PYEOF
)"
rc=$?
if [ "$rc" -eq 3 ]; then
  block "$block_msg"
fi
if [ "$rc" -ne 0 ]; then
  printf 'avertissement pre-task-start : réponse de quota inexploitable, démarrage de TASK-%s autorisé sans contrôle de quota\n' "$task_id" >&2
fi

exit 0
