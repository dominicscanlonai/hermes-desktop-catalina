# Roadmap

Experimental compatibility project. Electron 32 is unsupported; general binary distribution remains blocked.

| Milestone | Status |
|---|---|
| Sprint 001 source integration | Submitted in [PR #4](https://github.com/dominicscanlonai/hermes-desktop-catalina/pull/4); 20 preflight tests reported passing |
| Sprint 002 genuine Desktop compilation | Completed locally using pinned build tooling |
| Sprint 003 Catalina live acceptance | Desktop launch, AI response and existing history confirmed; full feature matrix pending |
| Sprint 004 protected build | Compiled and integrity verified locally; no standalone candidate assembled or launched |
| Sprint 005 release candidate | Pending verified completion; startup isolation, Darwin dependencies and runtime execution assessment remain gates |
| CUA on Catalina | Proposed research; native API feasibility and permission-aware testing welcome |
| Release readiness | Blocked pending runtime security, packaging, signing and acceptance |

## Next priorities

1. Verify fail-closed startup isolation before backend discovery or live state access.
2. Validate Darwin native dependencies and runtime under normal macOS security policy.
3. Assemble a separate relocatable desktop bundle and test Finder launch, IPC, GUI, shutdown and performance.
4. Validate authenticated backend integration and broader feature parity.
5. Investigate Catalina-native CUA capabilities and document limitations.

Contributions and reproducible Intel Mac test reports are welcome. Local sprint results are not claims that corresponding source has already been published. No production-ready release is available.
