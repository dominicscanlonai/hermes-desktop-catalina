# Sanitised test evidence

## Phase 1 export verification

| Check | Result | Scope |
|---|---|---|
| Upstream identity | Local tag `v0.23.4` resolved to `8fc0374447313e276f6b9a2764bfc750190c966a`. | Local Git evidence, not a separate signature verification. |
| Legacy CJS failure | Unpatched identity test failed with `ERR_REQUIRE_ESM`. | Node 20.20.1 with `--no-experimental-require-module`, not Electron execution. |
| Patch application and identity | `git apply --check`, apply, and `git diff --check` passed in a disposable checkout. Three normal identities matched between loader modes; malformed channel input was rejected on the modern loader. | The test does not exercise real build-channel validation or packaged Electron. |
| Launcher | Stub executable verified flags, environment isolation, rejection of reused state, missing Desktop inputs and a Webapp receipt, and acceptance of a prepared Desktop fixture. Shell and smoke JS syntax checks passed. | No Electron GUI or backend was launched by Phase 1 tests. |

## Historical prototype observations (not rerun during Phase 1)

- Intel Catalina 10.15.8; Electron 32.3.3 used the compiled workspace with a GPU-disable flag. Native JS staging files matched their locally recorded SHA-256 digests. The renderer was stamped `webapp`.
- Launch evidence progressed from missing identity/module imports to `ERR_REQUIRE_ESM`, then three HTTP request timeouts. The latest captured launch log contained the GPU override but did not prove application readiness.
- During the prior audit, loopback health was successful. A status request timed out once and then succeeded on retry. This is not evidence of an authentication failure or a successful clean-install flow.
- Native package imports passed under host Node 20.20.1. Electron-side PTY spawn, native-helper execution, and permission handling were not verified.

No raw logs, response payloads, environment captures, command-line dumps, profile state, or personal identifiers are included. Real GUI, full Desktop build, backend, signing, and distribution tests are pending.