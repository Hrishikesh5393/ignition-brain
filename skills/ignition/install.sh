#!/bin/sh
# Install the Ignition skills: create or refresh symlinks in ~/.claude/skills
#   ignition          ->  <repo>/skill          (core + selector + shared payload)
#   ignition-<name>   ->  <repo>/skills/<name>   (thin focused skills, one per dir)
# Any agent that reads Agent Skills folders: pass a target dir (or set SKILLS_TARGET):
#   sh skill/install.sh --target ~/.agents/skills
# Idempotent. Refuses to touch a pre-existing path that is not our symlink.
set -eu

# Resolve the directory this script lives in (that IS the skill dir).
script_path=$0
case $script_path in
  /*) : ;;
  *) script_path=$(pwd)/$script_path ;;
esac
SKILL_DIR=$(cd "$(dirname "$script_path")" && pwd -P)
SKILLS_DIR=$(cd "$SKILL_DIR/../skills" 2>/dev/null && pwd -P || true)

DEST_DIR="${SKILLS_TARGET:-${HOME}/.claude/skills}"
while [ $# -gt 0 ]; do
  case $1 in
    -t|--target) [ $# -ge 2 ] || { echo "usage: install.sh [--target DIR]" >&2; exit 2; }; DEST_DIR=$2; shift 2 ;;
    *) echo "usage: install.sh [--target DIR]" >&2; exit 2 ;;
  esac
done
mkdir -p "$DEST_DIR"
rc=0

# link <target-dir> <dest-name>
link() {
  target=$1
  dest="${DEST_DIR}/$2"
  if [ -L "$dest" ]; then
    old_target=$(readlink "$dest" 2>/dev/null || echo '?')
    resolved=$(cd "$dest" 2>/dev/null && pwd -P || true)
    if [ "$resolved" = "$target" ]; then
      echo "ok: ${dest} already points to ${target}"
    else
      ln -sfn "$target" "$dest"
      echo "updated: ${dest} -> ${target} (was ${old_target})"
    fi
  elif [ -e "$dest" ]; then
    echo "refused: ${dest} exists and is not a symlink we manage; remove it by hand and re-run" >&2
    rc=1
  else
    ln -s "$target" "$dest"
    echo "installed: ${dest} -> ${target}"
  fi
}

DEST="${DEST_DIR}/ignition"
link "$SKILL_DIR" "$(basename "$DEST")"
if [ -n "$SKILLS_DIR" ]; then
  for d in "$SKILLS_DIR"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    d=${d%/}
    link "$d" "$(basename "$d")"
  done
fi
exit $rc
