# Publication inventory

These are the reviewed source export and Sprint 001 additions. Existing repository documentation is separate.

| Path | Contents |
|---|---|
| `.gitignore` | Guardrails against adding local state or generated output. |
| `INVENTORY.md` | This exhaustive publication allowlist. |
| `LICENSE` | MIT notice from the pinned upstream commit. |
| `README.md` | Scope, publication target and development-only warning. |
| `docs/BUILD.md` | Disposable build and launch instructions and verification limits. |
| `docs/COMPATIBILITY.md` | Change rationale and intentionally excluded prototype shortcuts. |
| `docs/TEST-EVIDENCE.md` | Sanitised historical observations and Phase 1 test results. |
| `manifests/electron/package.json` | Exact prototype Electron npm dependency. |
| `manifests/electron/package-lock.json` | Historical Electron acquisition dependency lock, sanitised. |
| `manifests/native/package.json` | Exact prototype native-module dependencies. |
| `manifests/native/package-lock.json` | Historical native dependency lock, sanitised; not a release baseline. |
| `manifests/upstream.json` | Source commit, target, runtime versions and local archive digests. |
| `patches/0001-defer-build-only-msix-module.patch` | Minimal legacy-loader compatibility patch. |
| `scripts/launch.sh` | Isolated smoke/fake-boot launcher with fresh-state and Desktop receipt checks. |
| `scripts/runtime-smoke.cjs` | Static, sandboxed Electron window fixture. |
| `scripts/preflight.py` | Offline source/toolchain and Desktop receipt preflight. |
| `tests/test_preflight.py` | Offline preflight unit and CLI fixtures. |
| `docs/CATALINA-ACCEPTANCE.md` | Native, packaging, performance and publication gates. |
| `tests/verify-identity.cjs` | Loader and identity regression checks. |
| `tests/verify-launch.sh` | Launch-contract tests using a temporary stub executable. |

No hidden source checkout, Git metadata, binary artifacts, archive payloads, users' paths, logs, credentials, databases, profiles, or caches are part of the inventory.