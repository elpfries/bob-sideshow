#!/usr/bin/env bash
# Vérifier que le build Bob installé correspond exactement aux pins gravés dans l'image.
# Échoue bruyamment (exit 1 + message clair) si l'un des trois ne correspond pas.
#
# Pins attendus — correspondent à private/baseline-2.3.0/ :
#   APP_VERSION   : version dans product.json ("bobideVersion" et "updateVersion")
#   BOBCODE_VER   : version dans bob-code/package.json
#   EXT_SHA1      : SHA-1 de extensions/bob-code/dist/extension.js
#
# Usage: ./assert-pins.sh [INSTALL_ROOT]
#   INSTALL_ROOT defaults to /usr/share/bobide/resources/app  (chemin Linux du .deb)
set -euo pipefail

INSTALL_ROOT="${1:-/usr/share/bobide/resources/app}"
PRODUCT_JSON="${INSTALL_ROOT}/product.json"
PKG_JSON="${INSTALL_ROOT}/extensions/bob-code/package.json"
EXT_JS="${INSTALL_ROOT}/extensions/bob-code/dist/extension.js"

# ---- Pins (épinglés au moment du build de l'image) ----
# SHA-1 du build Linux (IBM-Bob-linux-amd64-1.126.0+bob2.3.0.deb), établi par
# docker buildx build --platform linux/amd64 le 2026-11-05 (TASK-1).
# Le SHA-1 macOS est 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (baseline-2.3.0/).
PIN_APP_VERSION="2.3.0"
PIN_BOBCODE_VER="2.3.0"
PIN_EXT_SHA1="0b8ef4c68a3f0acd71f1f69e0d7e01070fa9c343"
# -------------------------------------------------------

FAIL=0

check_file() {
  local f="$1"
  if [ ! -f "$f" ]; then
    echo "ERROR [assert-pins] fichier manquant : $f" >&2
    FAIL=1
  fi
}

check_file "$PRODUCT_JSON"
check_file "$PKG_JSON"
check_file "$EXT_JS"
if [ "$FAIL" -ne 0 ]; then exit 1; fi

# 1. App version (bobideVersion dans product.json)
GOT_APP=$(python3 -c "import json; d=json.load(open('${PRODUCT_JSON}')); print(d['bobideVersion'])")
if [ "$GOT_APP" != "$PIN_APP_VERSION" ]; then
  echo "ERROR [assert-pins] app version mismatch" >&2
  echo "  attendu : ${PIN_APP_VERSION}" >&2
  echo "  obtenu  : ${GOT_APP}" >&2
  FAIL=1
fi

# 2. bob-code version (package.json)
GOT_BOBCODE=$(python3 -c "import json; d=json.load(open('${PKG_JSON}')); print(d['version'])")
if [ "$GOT_BOBCODE" != "$PIN_BOBCODE_VER" ]; then
  echo "ERROR [assert-pins] bob-code version mismatch" >&2
  echo "  attendu : ${PIN_BOBCODE_VER}" >&2
  echo "  obtenu  : ${GOT_BOBCODE}" >&2
  FAIL=1
fi

# 3. extension.js SHA-1
GOT_SHA1=$(sha1sum "${EXT_JS}" | awk '{print $1}')
if [ "$GOT_SHA1" != "$PIN_EXT_SHA1" ]; then
  echo "ERROR [assert-pins] extension.js SHA-1 mismatch" >&2
  echo "  attendu : ${PIN_EXT_SHA1}" >&2
  echo "  obtenu  : ${GOT_SHA1}" >&2
  FAIL=1
fi

if [ "$FAIL" -ne 0 ]; then
  echo "ERROR [assert-pins] build épinglé non conforme — arrêt du conteneur." >&2
  exit 1
fi

echo "[assert-pins] OK — Bob ${PIN_APP_VERSION}, bob-code ${PIN_BOBCODE_VER}, extension.js ${PIN_EXT_SHA1}"
