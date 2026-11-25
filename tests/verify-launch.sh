#!/bin/bash
set -eu
root=$(cd "$(dirname "$0")/.." && pwd -P)
base=$(/usr/bin/mktemp -d "${TMPDIR:-/tmp}/catalina-test.XXXXXXXX")
trap '/bin/rm -rf -- "$base"' EXIT
mkdir "$base/fake.app" "$base/app"
cat > "$base/electron" <<'STUB'
#!/bin/bash
set -eu
[[ $1 == --disable-gpu && ( -f $2 || -d $2 ) ]]
[[ -d "$HOME" && -d "$HERMES_HOME" && -d "$HERMES_DESKTOP_USER_DATA_DIR" ]]
[[ $HERMES_DESKTOP_BOOT_FAKE == 1 && -z ${PHASE1_SENTINEL+x} ]]
printf 'controlled launch\n'
STUB
chmod +x "$base/electron"
mkdir -p "$base/fake.app/Contents/MacOS"
cp "$base/electron" "$base/fake.app/Contents/MacOS/Electron"
PHASE1_SENTINEL=discard-me /bin/bash "$root/scripts/launch.sh" smoke "$base/fake.app" "$base/new-state" | grep -qx 'controlled launch'
if /bin/bash "$root/scripts/launch.sh" smoke "$base/fake.app" "$base/new-state" >/dev/null 2>&1; then
  printf 'FAIL: existing state reused\n' >&2; exit 1
fi
if /bin/bash "$root/scripts/launch.sh" desktop "$base/fake.app" "$base/untouched" "$base/app" >/dev/null 2>&1; then
  printf 'FAIL: unprepared desktop app accepted\n' >&2; exit 1
fi
[[ ! -e "$base/untouched" ]]
mkdir "$base/app/dist"
printf '%s\n' '{"main":"dist/electron-main.mjs"}' > "$base/app/package.json"
touch "$base/app/dist/"{electron-main.mjs,electron-preload.js,preview-guest-preload.js,index.html}
printf '%s\n' '{"product":"webapp"}' > "$base/app/dist/hermes-build.json"
if /bin/bash "$root/scripts/launch.sh" desktop "$base/fake.app" "$base/untouched" "$base/app" >/dev/null 2>&1; then
  printf 'FAIL: Webapp renderer accepted\n' >&2; exit 1
fi
[[ ! -e "$base/untouched" ]]
printf '%s\n' '{"product":"desktop"}' > "$base/app/dist/hermes-build.json"
/bin/bash "$root/scripts/launch.sh" desktop "$base/fake.app" "$base/desktop-state" "$base/app" | grep -qx 'controlled launch'
printf 'PASS: launch environment, GPU flag, state isolation and missing Desktop receipt rejection\n'
