#!/usr/bin/env bash
# Install bob-sideshow skills into a Bob skills root.
#
#   ./install.sh                     -> ~/.bob/skills/<skill>/           (global)
#   ./install.sh --workspace [DIR]   -> DIR/.bob/skills/<skill>/          (default DIR = .)
#   ./install.sh --root NAME ...     -> use another skills root (default .bob)
#   ./install.sh --link ...          -> symlink instead of copy (handy while developing)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_name=".bob"
mode="global"
target_dir=""
link=0

while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) mode="workspace"; if [ $# -gt 1 ] && [ "${2#-}" = "$2" ]; then target_dir="$2"; shift; fi ;;
    --root) root_name="$2"; shift ;;
    --link) link=1 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ "$mode" = "global" ]; then
  dest="$HOME/$root_name/skills"
else
  dest="$(cd "${target_dir:-.}" && pwd)/$root_name/skills"
fi
mkdir -p "$dest"

for skill in "$here"/skills/*/; do
  name="$(basename "$skill")"
  if ! printf '%s' "$name" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$'; then
    echo "skip $name: invalid skill name" >&2; continue
  fi
  rm -rf "$dest/$name"
  if [ "$link" = 1 ]; then
    ln -s "${skill%/}" "$dest/$name"
  else
    cp -R "${skill%/}" "$dest/$name"
  fi
  echo "installed $name -> $dest/$name"
done

echo
echo "Done. Bob loads skills at the start of the next task: open a new conversation, then type /bob-version."
