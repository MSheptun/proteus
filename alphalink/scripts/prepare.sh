#!/usr/bin/env bash
# Prepare a patched (AlphaLink) source tree from upstream RustDesk.
#
#   prepare.sh <target-dir>
#
# Fetches upstream RustDesk at the pinned tag (see ../UPSTREAM) into <target-dir>
# (which may already contain other files), applies the AlphaLink patches and
# generates the branded icon set.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUS="$(dirname "$HERE")"
TARGET="${1:?usage: prepare.sh <target-dir>}"
# shellcheck disable=SC1091
source "$PLUS/UPSTREAM"

mkdir -p "$TARGET"
cd "$TARGET"
if [ ! -d .git ]; then
  git init -q .
fi
git remote remove upstream 2>/dev/null || true
git remote add upstream "$UPSTREAM_URL"
git fetch -q --depth 1 upstream "refs/tags/$UPSTREAM_TAG:refs/tags/$UPSTREAM_TAG"
git checkout -q -f "tags/$UPSTREAM_TAG"
git submodule update -q --init --recursive --depth 1

git apply --whitespace=nowarn "$PLUS"/patches/rustdesk/*.patch
(cd libs/hbb_common && git apply --whitespace=nowarn "$PLUS"/patches/hbb_common/*.patch)

python3 "$PLUS/scripts/rebrand.py" "$TARGET"
python3 -m pip install --quiet pillow 2>/dev/null || true
python3 "$PLUS/scripts/gen_icons.py" "$TARGET"
echo "AlphaLink source ready in $TARGET"
