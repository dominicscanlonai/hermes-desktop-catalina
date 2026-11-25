#!/bin/bash
# Isolated smoke/fake-boot launcher. Does not configure or contact a real backend.
set -eu
fail() { printf '%s\n' "$*" >&2; exit 1; }
root=$(cd "$(dirname "$0")/.." && pwd -P)
[[ $# == 3 || $# == 4 ]] || fail 'Usage: launch.sh smoke|desktop ELECTRON_APP NEW_STATE_DIR [PREPARED_DESKTOP_APP_DIR]'
mode=$1
runtime=$(cd "$2" && pwd -P)/Contents/MacOS/Electron
[[ -x $runtime ]] || fail 'Missing Electron executable'
case $mode in
  smoke) [[ $# == 3 ]] || fail 'Smoke mode does not take an app directory'; app=$root/scripts/runtime-smoke.cjs ;;
  desktop)
    [[ $# == 4 ]] || fail 'Desktop mode needs a prepared app directory'
    app=$(cd "$4" && pwd -P)
    for name in package.json dist/hermes-build.json dist/electron-main.mjs dist/electron-preload.js dist/preview-guest-preload.js dist/index.html; do
      [[ -f $app/$name && ! -L $app/$name ]] || fail "Missing or linked Desktop input: $name"
    done
    grep -Eq '"product"[[:space:]]*:[[:space:]]*"desktop"' "$app/dist/hermes-build.json" || fail 'Expected Desktop renderer receipt, not Webapp output'
    grep -Eq '"main"[[:space:]]*:[[:space:]]*"dist/electron-main.mjs"' "$app/package.json" || fail 'Unexpected app entry point'
    [[ ! -L $app/dist && ! -L $app/dist/node_modules ]] || fail 'Linked Desktop dist or node_modules is not supported'
    ;;
  *) fail 'Choose smoke or desktop' ;;
esac
parent=$(cd "$(dirname "$3")" && pwd -P)
leaf=$(basename "$3")
[[ $leaf != . && $leaf != .. && $leaf != / ]] || fail 'Choose a new state directory under an existing parent'
state=$parent/$leaf
umask 077
mkdir "$state" || fail 'State must be a new directory; never reuse your existing profile'
mkdir "$state/home" "$state/tmp" "$state/hermes" "$state/user-data"
exec /usr/bin/env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=en_US.UTF-8 \
  HOME="$state/home" TMPDIR="$state/tmp" HERMES_HOME="$state/hermes" \
  HERMES_DESKTOP_USER_DATA_DIR="$state/user-data" HERMES_DESKTOP_BOOT_FAKE=1 \
  "$runtime" --disable-gpu "$app"
