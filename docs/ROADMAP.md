# Roadmap

> [!IMPORTANT]
> This is an experimental compatibility project. Electron 32 is unsupported; general binary distribution remains blocked.

| Milestone | Status | Evidence / acceptance gate |
|---|---|---|
| Catalina prototype | ✅ Smoke-tested | Window, backend, conversation and session history observed |
| Agent Collective | ✅ Development workflow demonstrated | Two native subagents, independent review, shared Obsidian vault with manual Git sync |
| Sprint 001 source integration | ✅ Submitted for review | [PR #4](https://github.com/dominicscanlonai/hermes-desktop-catalina/pull/4); 20 Python tests reported passing |
| Sprint 002 Desktop build | 🧪 Next | Pinned Node 26.12.1 and pnpm 12.15.0; genuine Desktop receipt and verified producer inputs |
| Catalina acceptance | ⏳ Pending | Offline GUI, native preload and helper tests on Intel Catalina |
| Backend and feature parity | ⏳ Pending | Isolated authenticated testing, reconnect, streaming, terminal, files and performance |
| Relocatable test bundle | ⏳ Pending | No absolute development paths, validated x64 native dependencies, rollback |
| Release readiness | ⚠️ Blocked | Runtime security decision, dependency provenance, signing and notarisation |

## Sprint 002: compile, verify, then package

1. Restore the existing pinned build host and validate the clean upstream checkout.
2. Build the genuine Desktop renderer and matching Electron bundles, distinguishing Linux compilation from macOS native staging.
3. Verify build freshness, receipt, hashes and native compatibility.
4. Exercise the isolated offline Catalina acceptance harness.
5. Document actual results and remaining blockers before progressing to backend tests or packaging.

No release is production-ready yet.
