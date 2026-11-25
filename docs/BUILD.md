# Build and launch

Phase 1 is a source export and an isolated launch harness. It does not claim a reproducible Catalina Desktop build yet. Use a new work area outside this export and outside any existing Hermes installation. Commands below are for a later build, not a request to run them against the live prototype.

## Modern build host

Use upstream's Node 26 and pnpm toolchain, preserving the upstream lockfile. Pin exact toolchain builds and the macOS SDK before promoting this recipe to CI. Use a disposable checkout:

```sh
EXPORT=/absolute/path/to/hermes-desktop-catalina
git clone https://github.com/NousResearch/hermes-agent.git upstream
cd upstream
git checkout --detach 8fc0374447313e276f6b9a2764bfc750190c966a
test "$(git rev-parse 'v0.23.4^{}')" = "$(git rev-parse HEAD)"
git apply --check "$EXPORT/patches/0001-defer-build-only-msix-module.patch"
git apply "$EXPORT/patches/0001-defer-build-only-msix-module.patch"
pnpm install --frozen-lockfile
pnpm --dir apps/desktop run build
```

This is the upstream **Desktop** entry point, not `build:webapp`. Use a modern macOS x64 builder or independently verified x64 native inputs for a Catalina candidate; never transfer an arm64-only native tree. The build command above has not been exercised in this export. Before accepting its output, validate the receipt (`product: desktop`), Electron 32 APIs and Chromium 128 syntax/CSS, and every x64 native module/helper against macOS 10.15. Confirm the preloads, JS, and native tree came from the same build. A completed Desktop build, signing, and a clean-host package remain later milestones.

## Catalina test host

Use a separately acquired, independently verified Electron **32.3.3 darwin-x64** app. The Electron lock tracks the npm package, not an independent checksum of the downloaded Electron distribution. The two manifest directories are reviewed records of the prototype's dependency resolutions; **do not run `npm ci` from inside this export**. The historical native lock contains vulnerable optional `tar@6.2.1`; it is not a release install prescription. Prepare any test dependencies in a disposable directory after reviewing install scripts and trusted binaries. Neither lockfile was reinstalled in Phase 1.

```sh
# Each invocation needs a fresh, nonexistent state path under an existing parent.
bash "$EXPORT/scripts/launch.sh" smoke /path/to/test/Electron.app /path/to/test/smoke-state
bash "$EXPORT/scripts/launch.sh" desktop /path/to/test/Electron.app /path/to/test/desktop-state /path/to/upstream/apps/desktop
```

`smoke` opens a local static fixture. `desktop` requires a prepared Desktop distribution and sets upstream fake-boot mode. It intentionally has no real-backend switch and does not perform network isolation at the OS level. If testing the full renderer, use a disposable offline Catalina test account or VM and do not sign in, configure a gateway, or open remote pages. The harness is not an application sandbox or security boundary. Run neither command against the working checkout or existing state. Dispose of test state outside the export; never publish it.

## Offline checks

Use Node 20.20.1 for the identity regression (it accepts `--no-experimental-require-module` to simulate the older loader). Run against the patched disposable checkout, not against the working prototype:

```sh
node "$EXPORT/tests/verify-identity.cjs" /path/to/patched/upstream
bash "$EXPORT/tests/verify-launch.sh"
```

Before committing, compare the exact staged file set with `INVENTORY.md` and repeat the content review. Do not add raw test output, generated directories, or a remote until publication is authorised.
