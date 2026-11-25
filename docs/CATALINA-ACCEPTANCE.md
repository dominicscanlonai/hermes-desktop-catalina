# Catalina acceptance gates

> [!IMPORTANT]
> This is a source-only engineering checklist, not release approval. Electron 32 is unsupported. Do not distribute binaries or bypass macOS security protections.

## Candidate milestones

| Milestone | Required evidence |
|---|---|
| Local launcher with an external backend | Separate, explicit fixture configuration; boot and clean shutdown without touching the existing backend |
| Relocatable desktop runtime | Real Desktop renderer and both preloads, verified Electron archive, relative resource lookup, clean Intel Catalina acceptance |
| Standalone app with backend | Relocatable Python runtime and dependencies, isolated per-user state, signed bundle, clean installation and rollback |

## Offline gates

1. Record the upstream commit, patch set, exact Node/pnpm, compiler, SDK, and independently verified Electron archive digest. Confirm `product: desktop`, use the upstream freshness check with expected producer and prepared inputs, and record native file hashes and modes separately. The six-file preflight inventory does not certify freshness or provenance.
2. Inspect each final Mach-O `x86_64` slice and minimum OS (`LC_BUILD_VERSION` or `LC_VERSION_MIN_MACOSX`). Check dynamic library loads and symbols against Catalina, not just SDK version. Keep `pty.node` paired with executable `spawn-helper`; keep `get-windows/main` executable and native resources outside ASAR where required. Verify bundle-relative resource paths and in-bundle framework links.
3. Gate the upstream HUD and command screenshot helpers. Stock compiler probes produced macOS 11.0 minimums. Independent x86_64 probes compiled the same sources with a 10.15 target and availability diagnostics; that is static evidence only. Omit or gate either feature until its alternate helper runs correctly in disposable Catalina state.
4. Test actual Electron ABI, preload handshake, PTY spawn/resize/exit, permission denial, guest lifecycle, and navigation policy. Use a disposable offline account or VM. Fake boot is not OS-level isolation. Check sandbox, context isolation, and certificate validation remain enabled.
5. Separately qualify fixture backend startup, health, status latency, WebSocket readiness, reconnect, and session recovery. Capture stage timings rather than increasing timeouts. Measure cold/warm boot, idle CPU, peak memory, and recovery after closing previews. Do not profile the working backend as part of candidate testing.
6. Use a distinct bundle identifier, icon attribution, version metadata, and per-user state directories. Avoid the upstream update feed. Verify signing, notarization, Gatekeeper, clean install and rollback before any distribution decision. Do not ship build-only dependencies or declare the old runtime safe merely because an optional dependency was removed.

## Media and contributor evidence

Use genuine screenshots from a disposable profile: hero workspace, Catalina version proof, synthetic chat, terminal, and optionally a short demo. Redact usernames, serials, paths, notifications, and private sessions. Suggested paths: `docs/media/screenshots/` and `docs/media/demos/`. Keep the existing banner, badges and attribution; do not restyle the application. Label every screenshot with the exact feature and what was actually tested. External community announcements and binary installation remain outside this sprint's published changes.
