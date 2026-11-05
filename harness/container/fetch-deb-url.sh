#!/usr/bin/env bash
# Obtenir une URL pré-signée (60 s) pour IBM-Bob-linux-amd64-1.126.0+bob2.3.0.deb.
# Usage: ./fetch-deb-url.sh
# Requis: curl
set -euo pipefail

VERSION="1.126.0+bob2.3.0"
ARCH="amd64"

LOCATION=$(curl -s -o /dev/null -D - -X POST \
  "https://bob.ibm.com/api/download/bobide" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "platform=linux" \
  --data-urlencode "version=${VERSION}" \
  --data-urlencode "architecture=${ARCH}" \
  --data-urlencode "packageType=deb" \
  | grep -i "^location:" | tr -d '\r' | awk '{print $2}')

if [ -z "$LOCATION" ]; then
  echo "ERROR: impossible d'obtenir l'URL de téléchargement" >&2
  exit 1
fi
echo "$LOCATION"
