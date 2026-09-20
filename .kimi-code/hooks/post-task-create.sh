#!/usr/bin/env bash
# PostToolUse hook (matcher: Bash), DUAL-PROTOCOLE Claude Code / Kimi Code.
# Fires after `backlog task create` so the task-quality rules (description
# claire, critères d'acceptation, découpage) can't be silently skipped. This
# script only detects the event and forces the reminder back into context —
# it can't judge task content itself.
#
# Adapted from a sibling project. Differences with the original:
#   - dual-protocol : Claude Code reçoit {"decision":"block","reason":...} sur
#     stdout ; Kimi Code (PostToolUse observation-only) reçoit le rappel en
#     clair sur stdout, exit 0 dans les deux cas ;
#   - no-op (exit 0) hors d'un projet Backlog.md (pas de backlog/tasks/), la
#     config Kimi étant utilisateur-globale ;
#   - rappel adapté : labels de complexité `model:primaire`/`model:secondaire`
#     (k3 / kimi-for-coding), critères d'acceptation, découpage si la tâche
#     dépasse une session ou mêle les deux tiers.
#
# Le rappel se déclenche sur un EFFET, pas sur un texte de commande. Le motif
# ci-dessous n'est qu'un pré-filtre bon marché : il lit une chaîne, pas un
# shell. Il voit un séparateur là où il n'y a qu'un `&&` entre quotes, et il
# ne sait pas distinguer une création d'un `--help` ou d'une erreur d'usage —
# trois façons de mentionner `backlog task create` sans rien créer.
#
# Runtime detection : BACKLOG_HOOK_RUNTIME (posé dans la déclaration du hook)
# l'emporte ; sinon sniffing du JSON stdin (client_type => kimi,
# transcript_path / permission_mode => claude) ; défaut kimi.

input="$(cat)"

runtime="${BACKLOG_HOOK_RUNTIME:-}"
if [ -z "$runtime" ]; then
  case "$input" in
    *'"client_type"'*) runtime=kimi ;;
    *'"transcript_path"'*|*'"permission_mode"'*) runtime=claude ;;
    *) runtime=kimi ;;
  esac
fi

# --- Extraction JSON : jq, avec repli python3 --------------------------------
if command -v jq >/dev/null 2>&1; then
  json_get() { printf '%s' "$input" | jq -r "$1 // empty"; }
  emit_block() { jq -n --arg reason "$1" '{decision: "block", reason: $reason}'; }
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
  emit_block() {
    python3 - "$1" <<'PYEOF'
import json, sys
print(json.dumps({"decision": "block", "reason": sys.argv[1]}, ensure_ascii=False))
PYEOF
  }
fi

command="$(json_get '.tool_input.command')"
[ -n "$command" ] || exit 0

# Racine du projet : cwd du JSON, sinon repli. Hors d'un projet Backlog.md :
# no-op, pour que la config Kimi globale reste sans effet de bord.
proj="$(json_get '.cwd')"
{ [ -n "$proj" ] && [ -d "$proj" ]; } || proj="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$proj/backlog/tasks" ] || exit 0

# Le `tool_response` d'un Bash porte stdout/stderr/interrupted — il n'a pas de
# champ `success`.
out="$(json_get '.tool_response.stdout')"
interrupted="$(json_get '.tool_response.interrupted')"
duration_ms="$(json_get '.duration_ms')"
case "$duration_ms" in ''|*[!0-9.]*) duration_ms=0 ;; esac

printf '%s' "$command" | grep -Eq '(^|[;&|]) *backlog +task +create( |$)' || exit 0
[ "$interrupted" = "true" ] && exit 0

# Deux témoins indépendants qu'une tâche a bien été écrite.
# 1. La sortie de Backlog.md : « Created task TASK-n » en mode normal, la seule
#    ligne « File: » sous --plain.
created=false
printf '%s' "$out" | grep -Eq '^Created task |^File: .*/tasks/.*\.md$' && created=true

# 2. Un .md modifié dans backlog/tasks/ pendant l'appel. Ce témoin-là survit à
#    un changement de format de sortie de Backlog.md : sans lui, une mise à
#    jour de l'outil éteindrait le rappel en silence. En cas de doute (dossier
#    illisible, python3 absent), on rappelle plutôt que de se taire.
if [ "$created" = "false" ]; then
  created="$(python3 - "$proj/backlog/tasks" "$duration_ms" 2>/dev/null <<'PYEOF' || echo true
import os, sys, time

tasks_dir, duration_ms = sys.argv[1], float(sys.argv[2])
cutoff = time.time() - (duration_ms / 1000.0) - 5.0  # marge pour le hook lui-meme
try:
    names = os.listdir(tasks_dir)
except OSError:
    print("true")  # on ne peut pas conclure : rappeler pour rien coûte moins cher
    sys.exit(0)
print("true" if any(
    n.endswith(".md") and os.path.getmtime(os.path.join(tasks_dir, n)) >= cutoff
    for n in names
) else "false")
PYEOF
)"
fi

[ "$created" = "true" ] || exit 0

reason="Tâche Backlog créée : avant de continuer, (1) vérifie que la description dit clairement ce qu'il faut livrer et pourquoi — complète-la avec \`backlog task edit\` si elle se résume au titre ; (2) pose des critères d'acceptation vérifiables — une tâche sans critères ne peut pas être prouvée finie, et le passage en Done exigera une preuve nommée par critère coché ; (3) pose le label de complexité : \`model:secondaire\` par défaut (tourne sur kimi-for-coding), \`model:primaire\` réservé à l'architecture difficile, la concurrence ou l'ordonnancement (tourne sur k3) ; (4) si la tâche dépasse une session de travail — ou mêle une partie primaire et une partie standard — découpe-la en sous-tâches (\`backlog task create -p <ID> ...\`) plutôt que de la laisser monolithique."
if [ "$runtime" = "claude" ]; then
  emit_block "$reason"
else
  # Kimi Code : PostToolUse est observation-only, le rappel part sur stdout.
  printf '%s\n' "$reason"
fi
exit 0
