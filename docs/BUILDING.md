# Building the Catalina port

> **Status:** Development notes. The complete build scripts, patches and source archive have not yet been uploaded to this repository. Do not treat these notes as a runnable end-to-end guide.

## Development baseline

- Intel Mac running macOS Catalina 10.15.8.
- Official Hermes source checkout at v0.23.4 (development checkout commit recorded separately on the build Mac).
- Ubuntu build environment, Node 26.12.1 and pnpm 12.15.0.
- Browser renderer built using the original Hermes Vite pipeline.
- Electron main and preload built from official TypeScript entries with the Hermes esbuild script.
- A Catalina-compatible Electron 32.3.3 runtime was used as the native host.
- Native `node-pty@1.1.0` and `get-windows@9.3.0` were individually smoke-tested on the Mac.

## Known compatibility work

The experimental app encountered an ESM/CJS incompatibility when an Electron desktop identity module required `scripts/msix-shared.mjs`. A **staging-only** CommonJS variant and corresponding require-path adjustment resolved the immediate launch exception. This patch needs to be distilled, reviewed, tested and published.

The functioning launch also required an explicit `HERMES_HOME` to bind the native desktop to the existing Hermes profile rather than an isolated test-profile home. It should not be interpreted as permission to copy profile databases into Git.

## Next steps

1. Extract **only** the authored compatibility changes from the local project.
2. Compare them against the pinned upstream version.
3. Audit and publish the patch set and a minimal launcher.
4. Script dependency acquisition and reproducible builds with checksums.
5. Automate PTY, backend and UI smoke tests.
6. Validate signing, packaging and startup without the Ubuntu build VM.
7. Create a release only after security and operational review.

## Source of truth

- [Official Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [Upstream MIT license](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE)
- [Compatibility and test status](../COMPATIBILITY.md)

**Do not** commit `~/.hermes`, agent credentials, cached sessions, local profiles, generated `node_modules`, private logs, or entire upstream working trees.
