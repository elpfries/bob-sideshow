#!/usr/bin/env bash
# Point d'entrée du conteneur bob-bench.
# 1. Vérifie les pins (échoue bruyamment si mismatch).
# 2. Démarre Xvfb sur :99.
# 3. Lance bobide sous ce display virtuel sans input interactif.
# 4. Attend "Extension activated" dans les logs ; échoue si absent après timeout.
set -euo pipefail

DISPLAY_NUM=":99"
BOBIDE_LOG="/tmp/bobide.log"
XVFB_LOG="/tmp/xvfb.log"
WAIT_TIMEOUT="${BOB_STARTUP_TIMEOUT:-120}"

# ── 1. Assertion des pins ─────────────────────────────────────────────────────
echo "[entrypoint] Vérification des pins de build..."
/usr/local/bin/assert-pins.sh
echo "[entrypoint] Pins OK."

# ── 2. Xvfb ──────────────────────────────────────────────────────────────────
echo "[entrypoint] Démarrage Xvfb ${DISPLAY_NUM}..."
Xvfb "${DISPLAY_NUM}" -screen 0 1280x800x24 >"${XVFB_LOG}" 2>&1 &
XVFB_PID=$!
# Attendre que Xvfb soit prêt (max 10 s)
for i in $(seq 1 20); do
  xdpyinfo -display "${DISPLAY_NUM}" >/dev/null 2>&1 && break
  sleep 0.5
  if [ "$i" -eq 20 ]; then
    echo "ERROR [entrypoint] Xvfb n'a pas démarré en 10 s" >&2
    exit 1
  fi
done
echo "[entrypoint] Xvfb prêt."

# ── 3. bobide ─────────────────────────────────────────────────────────────────
echo "[entrypoint] Démarrage bobide..."
export DISPLAY="${DISPLAY_NUM}"
# --no-sandbox requis dans un conteneur sans user namespace.
# --disable-gpu évite les erreurs de rendu GPU sans carte physique.
# --disable-workspace-trust : contourne le dialogue de trust (workspace=/workspace).
# L'option --wait n'existe pas dans bobide ; on démarre en arrière-plan et on lit les logs.
/usr/share/bobide/bin/bobide \
  --no-sandbox \
  --disable-gpu \
  --disable-updates \
  --user-data-dir=/tmp/bob-userdata \
  /workspace \
  >"${BOBIDE_LOG}" 2>&1 &
BOBIDE_PID=$!

# ── 4. Attendre "Extension activated" ────────────────────────────────────────
echo "[entrypoint] Attente de 'Extension activated' (timeout ${WAIT_TIMEOUT} s)..."
ELAPSED=0
while true; do
  if grep -q "Extension activated" "${BOBIDE_LOG}" 2>/dev/null; then
    echo "[entrypoint] 'Extension activated' détecté — bobide prêt."
    break
  fi
  if ! kill -0 "${BOBIDE_PID}" 2>/dev/null; then
    echo "ERROR [entrypoint] bobide s'est arrêté avant d'atteindre 'Extension activated'" >&2
    cat "${BOBIDE_LOG}" >&2
    exit 1
  fi
  if [ "${ELAPSED}" -ge "${WAIT_TIMEOUT}" ]; then
    echo "ERROR [entrypoint] timeout (${WAIT_TIMEOUT} s) — 'Extension activated' jamais apparu" >&2
    echo "--- log bobide ---" >&2
    cat "${BOBIDE_LOG}" >&2
    exit 1
  fi
  sleep 1
  ELAPSED=$((ELAPSED + 1))
done

# ── Passer la main au CMD ou attendre ────────────────────────────────────────
if [ "$#" -gt 0 ]; then
  exec "$@"
else
  # Mode standalone : garder le processus vivant pour inspection.
  echo "[entrypoint] Mode standalone — PID bobide=${BOBIDE_PID}. Ctrl-C pour arrêter."
  wait "${BOBIDE_PID}"
fi
