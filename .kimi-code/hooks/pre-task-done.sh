#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash), DUAL-PROTOCOLE Claude Code / Kimi Code.
# Fires BEFORE a `backlog task edit ... -s Done` runs, and refuses it unless
# the task's implementation notes already carry a "Vérification de livraison"
# section answering two questions — what integrity checks were run on any
# assets the task produced or modified, and whether the processing hit any
# incident — plus, when an incident is declared, the report of an independent
# verifier.
#
# Adapted from a sibling project (Sentinelle), where this gate was adopted
# after repeated premature closures on unverified deliverables. Differences
# with the original:
#   - dual-protocol (Claude Code JSON deny / Kimi Code exit 2 + stderr) ;
#   - no-op (exit 0) outside a Backlog.md project (no backlog/tasks/ dir), so
#     the Kimi user-level config can declare it globally without side effects;
#   - the sabotage `--check` battery and the required "Témoins" line only
#     apply when tests/sabotages/*.json exist in the project;
#   - no `model:` label convention in the reminders (not used in this repo).
#
# Runtime detection: BACKLOG_HOOK_RUNTIME (set in the hook declaration) wins;
# otherwise the stdin JSON is sniffed (client_type => kimi, transcript_path /
# permission_mode => claude); default kimi.
#
# Blocking output per protocol:
#   kimi   : reason on stderr, exit 2
#   claude : {"hookSpecificOutput":{...,"permissionDecision":"deny",...}} on
#            stdout, exit 0
# Allow is exit 0 with no output in both protocols.
#
# The section is matched accent-insensitively (notes are often written
# without accents). Expected shape, in the task's implementation notes:
#
#   ## Vérification de livraison
#   Assets : aucun asset produit ou modifié
#        ou : <contrôles exécutés et leur résultat>
#   Incidents : aucun
#        ou : <interruptions, bugs corrigés dans l'outillage, contournements,
#              interventions manuelles, durée >2x l'estimation, réouverture>
#   Capitalisation : rien à verser
#        ou : <ce qui a été versé et OÙ>
#   Vérificateur indépendant : <rapport cité>   (requis si Incidents ≠ aucun)

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
  emit_deny() {
    jq -n --arg reason "$1" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
  }
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
  emit_deny() {
    python3 - "$1" <<'PYEOF'
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": sys.argv[1]}}, ensure_ascii=False))
PYEOF
  }
fi

block() {
  if [ "$runtime" = "claude" ]; then
    emit_deny "$1"
    exit 0
  fi
  printf '%s\n' "$1" >&2
  exit 2
}

command="$(json_get '.tool_input.command')"
[ -n "$command" ] || exit 0

# Racine du projet : le cwd fourni par le runtime (les deux protocoles
# l'envoient), sinon repli. Hors d'un projet Backlog.md : no-op.
proj="$(json_get '.cwd')"
{ [ -n "$proj" ] && [ -d "$proj" ]; } || proj="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$proj/backlog/tasks" ] || exit 0

# Only a status change to Done is gated. Accept -s/--status, with or without
# quotes, anywhere in the command; "In Progress"/"To Do" never match.
printf '%s' "$command" | grep -Eq '(^|[;&|]) *backlog +task +edit ' || exit 0
printf '%s' "$command" | grep -Eq -- '(-s|--status) +"?Done"?( |$)' || exit 0

# Les identifiants de sous-tâche sont décimaux (TASK-7.1, TASK-10.2) : sans la
# partie `(\.[0-9]+)*`, un identifiant comme `TASK-7.1` serait tronqué en `7`
# et le gate inspecterait la tâche PARENTE — donc refuserait toute clôture de
# sous-tâche, quelles que soient ses notes.
task_id="$(printf '%s' "$command" | sed -nE 's/.*backlog +task +edit +(TASK-)?([0-9]+(\.[0-9]+)*).*/\2/p' | head -n1)"
[ -n "$task_id" ] || exit 0

cd "$proj" || exit 0
view="$(backlog task view "TASK-$task_id" --plain 2>/dev/null)" || exit 0

has_section=0
printf '%s' "$view" | grep -Eiq '^#+ *V[ée]rification de livraison' && has_section=1
has_assets=0
printf '%s' "$view" | grep -Eiq '^ *-? *\**Assets\** *:' && has_assets=1
has_incidents=0
printf '%s' "$view" | grep -Eiq '^ *-? *\**Incidents\** *:' && has_incidents=1
# Une connaissance apprise en cours de tâche et perdue au /clear suivant ne
# fait rien tomber : rien ne signale l'oubli.
has_capitalisation=0
printf '%s' "$view" | grep -Eiq '^ *-? *\**Capitalisation\** *:' && has_capitalisation=1
# La ligne Témoins (batterie de sabotage) n'est exigée que si le projet porte
# des batteries : ce dépôt n'en a pas, l'exigence serait sans objet.
sabotage_present=0
ls tests/sabotages/*.json >/dev/null 2>&1 && sabotage_present=1
has_witnesses=0
printf '%s' "$view" | grep -Eiq '^ *-? *\**T[ée]moins\** *:' && has_witnesses=1

if [ "$has_section" -eq 0 ] || [ "$has_assets" -eq 0 ] || [ "$has_incidents" -eq 0 ] || [ "$has_capitalisation" -eq 0 ] \
  || { [ "$sabotage_present" -eq 1 ] && [ "$has_witnesses" -eq 0 ]; }; then
  witnesses_line=""
  if [ "$sabotage_present" -eq 1 ]; then
    witnesses_line="Témoins : sans objet (aucun test livré) — OU — le résultat de la batterie de sabotage, obtenu par la batterie tests/sabotages/<sujet>.json, qui casse un mécanisme de production à la fois et exige qu'un test tombe. Un test qui passe encore alors que ce qu'il prétend vérifier est mort est un faux témoin : il se présente comme une preuve et n'en est pas une.
"
  fi
  block "Passage en Done REFUSÉ pour TASK-$task_id : les notes de la tâche n'ont pas de section « Vérification de livraison » complète. Avant de clore, ajoute-la avec \`backlog task edit TASK-$task_id --append-notes\` (jamais --notes), sous cette forme exacte :

## Vérification de livraison
Assets : aucun asset produit ou modifié — OU — la liste des contrôles d'intégrité exécutés sur les assets produits/modifiés, avec leur résultat (adaptés à la nature de la tâche — ex. intégrité des fichiers produits, cohérence des métadonnées, total confronté à la source).
Incidents : aucun — OU — la liste : interruption/relance d'une étape, bug trouvé et corrigé dans l'outillage en cours de tâche, contournement appliqué, intervention manuelle sur le résultat, durée effective > 2x l'estimation, tâche rouverte après Done.
${witnesses_line}Capitalisation : rien à verser — tout ce qui compte est déjà dans le code, les tests et les notes — OU — ce qui a été versé et OÙ (skill, docstring, AGENTS.md, hook, doc, tâche de suivi créée), plus ce qui a été délibérément laissé et pourquoi. La question à se poser est « qu'est-ce que cette session sait, que le dépôt ne sait pas ? » — pas « qu'ai-je fait », qui est dans les commits. Sans cette étape, un /clear perd ce que la session a appris, et une connaissance perdue ne fait rien tomber.
Vérificateur indépendant : <rapport cité> — OBLIGATOIRE dès que Incidents ≠ aucun : un agent frais (pas celui qui a produit), briefé avec les critères d'acceptation, la checklist et le rapport du producteur, qui réexécute lui-même les contrôles pour tenter de réfuter la conformité.

Ce hook ne juge pas le contenu : il rend seulement impossible de clore sans avoir répondu."
fi

# --------------------------------------------------------------------------- #
# Aucun critère coché sans preuve nommée                                      #
# --------------------------------------------------------------------------- #
# Une case cochée est une affirmation, et elle ne porte aucune trace de ce qui
# l'établit. Ce gate ne lit pas la preuve et ne la juge pas : il exige qu'une
# preuve soit NOMMÉE pour chaque case cochée, ce qui transforme une omission
# silencieuse en ligne manquante. Un critère qu'on ne peut pas prouver se
# décoche — c'est une réponse légitime, et le refus est le moment où ce choix
# se fait sciemment plutôt que par défaut.
#
# Les critères sont lus dans le SEUL bloc « Acceptance Criteria » : un `- [x]`
# recopié dans les notes ne doit pas créer une exigence fantôme. Le numéro est
# ancré sur le « : » qui suit, sinon une ligne « AC #1 : » satisferait le
# critère #10.
checked_acs="$(printf '%s' "$view" \
  | awk '/^Acceptance Criteria:/{inac=1;next} inac && /^[A-Za-z].*:$/{inac=0} inac' \
  | grep -oE '^- \[[xX]\] #[0-9]+' | grep -oE '[0-9]+' || true)"
missing_ac=""
for n in $checked_acs; do
  if ! printf '%s' "$view" | grep -Eiq "^ *-? *\**AC *#?${n}\** *: *[^[:space:]]"; then
    missing_ac="$missing_ac #$n"
  fi
done
if [ -n "$missing_ac" ]; then
  block "Passage en Done REFUSÉ pour TASK-$task_id : critère(s) d'acceptation coché(s) sans preuve nommée :$missing_ac

Une case cochée affirme ; elle ne dit pas ce qui l'établit. Pour chaque critère coché, ajoute une ligne qui nomme sa preuve, avec \`backlog task edit TASK-$task_id --append-notes\` (jamais --notes) :

AC #1 : <ce qui l'établit — commande et son résultat, extrait de fichier ou de réponse, doc produit, mesure>

Si un critère ne peut pas être prouvé, ne fabrique pas de ligne : décoche-le (\`backlog task edit TASK-$task_id --uncheck-ac <n>\`) et dis dans les notes ce qui manque et pourquoi. Un critère décoché et assumé vaut mieux qu'une case que rien ne soutient.

Ce hook ne lit pas la preuve et ne la juge pas : il rend seulement impossible de cocher sans en nommer une."
fi

# --------------------------------------------------------------------------- #
# Aucun témoin périmé : `--check` sur toutes les batteries                    #
# --------------------------------------------------------------------------- #
# Sans objet dans ce dépôt tant qu'il n'y a ni script sabotage ni batteries :
# le bloc ne s'arme que si les DEUX existent.
sabotage_script=".claude/skills/verify-delivery/scripts/sabotage.py"
if [ -f "$sabotage_script" ] && ls tests/sabotages/*.json >/dev/null 2>&1; then
  sabotage_py="python3"
  [ -x .venv/bin/python ] && sabotage_py=".venv/bin/python"
  stale=""
  for cfg in tests/sabotages/*.json; do
    if ! "$sabotage_py" "$sabotage_script" --config "$cfg" --check >/dev/null 2>&1; then
      stale="$stale
  - $cfg"
    fi
  done
  if [ -n "$stale" ]; then
    block "Passage en Done REFUSÉ pour TASK-$task_id : au moins une batterie de sabotage porte un motif introuvable ou ambigu, donc ne peut plus être jouée telle quelle :$stale

Un motif \`find\` qui ne s'applique plus laisse le code intact : la suite reste verte et le témoin se lit comme une preuve alors qu'il n'en est plus une.

Diagnostic entrée par entrée :
  $sabotage_py $sabotage_script --config <batterie> --check

Puis, pour chaque motif signalé : soit le mécanisme visé existe encore ailleurs (réécrire le motif contre le code actuel, à intention identique), soit il a disparu avec la tâche en cours (supprimer l'entrée). Rejouer ensuite la batterie complète avant de clore."
  fi
fi

# An incident declared without an independent verifier is the exact failure
# mode this gate exists for. "aucun"/"none"/"RAS" on the Incidents line
# means no incident.
#
# TOUTES les lignes Incidents sont lues, pas seulement la première : une tâche
# rouverte après Done garde sa première section « Vérification de livraison »,
# dont la ligne dit « aucun » — et l'incident déclaré par la reprise ne serait
# jamais vu. Une seule ligne qui déclare quelque chose suffit.
declared_incident=""
while IFS= read -r incidents_line; do
  [ -n "$incidents_line" ] || continue
  incidents_value="$(printf '%s' "$incidents_line" | sed -E 's/^[^:]*: *//' | tr '[:upper:]' '[:lower:]')"
  case "$incidents_value" in
    aucun*|none*|ras*|néant*|neant*|"") : ;;
    *) declared_incident="$incidents_value" ;;
  esac
done <<EOF
$(printf '%s' "$view" | grep -Ei '^ *-? *\**Incidents\** *:')
EOF
case "$declared_incident" in
  "") : ;;
  *)
    incidents_value="$declared_incident"
    # Le motif DOIT être une ligne de champ ("Vérificateur indépendant :
    # <rapport>"), pas une mention quelconque dans les notes. Une forme plus
    # permissive s'ouvrirait sur une simple mention en passant — par exemple
    # une note qui cite le vérificateur d'une AUTRE tâche.
    # Limite assumée : ce hook ne sait pas si la ligne se trouve DANS la
    # section « Vérification de livraison » de CETTE exécution, ni si le
    # rapport cité est vrai. Il vérifie une forme, pas un fait.
    if ! printf '%s' "$view" | grep -Eiq '^ *-? *\**V[ée]rificateur +ind[ée]pendant[^:]*:'; then
      block "Passage en Done REFUSÉ pour TASK-$task_id : la section « Vérification de livraison » déclare des incidents (« ${incidents_value:0:120} ») mais ne cite aucun « Vérificateur indépendant : … ». Règle du projet : dès qu'un traitement a connu une interruption, un incident ou une anomalie, la conformité du résultat est vérifiée par un agent FRAIS et indépendant de celui qui a produit — que la tâche ait été déléguée ou traitée en session. Lance-le (sous-agent dédié), brief = critères d'acceptation + checklist d'intégrité + rapport du producteur, mission = réexécuter les contrôles et tenter de réfuter ; cite son rapport dans la section, puis repasse en Done."
    fi
    ;;
esac

exit 0
