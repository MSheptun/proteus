#!/usr/bin/env bash
# Clones HeliBoard at the pinned commit and applies the AlphaKeys patch.
# usage: prepare.sh <workdir>
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
. "$here/UPSTREAM"
work="${1:?usage: prepare.sh <workdir>}"
rm -rf "$work"
git clone "$UPSTREAM_URL" "$work"
git -C "$work" checkout "$UPSTREAM_COMMIT"
git -C "$work" apply --index "$here"/patches/*.patch
echo "patched HeliBoard is in $work"
