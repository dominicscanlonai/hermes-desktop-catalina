# Compatibility baseline

Reported working prototype: Intel macOS 10.15.8, Hermes v0.23.4, Electron 32.3.3 (Node 20.18.1, Chromium 128). Linux build host used Node 26.12.1 and pnpm 12.15.0.

| Capability | Evidence / status |
|---|---|
| Desktop window and navigation | Prototype smoke-tested; Webapp-derived renderer, genuine Desktop parity pending |
| Backend and AI conversation | Basic response and existing session history observed; intermittent status timeouts require investigation |
| Native PTY and window inspection | Historical module smoke tests; packaged-app execution pending |
| Skills and project tools | Local engineering workflows exercised |
| Native subagents | Two parallel specialists with separate contexts completed Sprint 001 assignments |
| Shared project memory | Obsidian Markdown vault and manual private Git sync established; reverse-direction test pending |
| Multi-agent engineering | Implementation, independent review and integration demonstrated; manual continuation required |
| Source preflight | 20 Python tests and launcher regression reported passing in Sprint 001 |
| Genuine Desktop build | Pending pinned-host compilation and producer verification |
| Offline GUI acceptance and packaging | Pending |
| Distribution security | Blocked by unsupported Electron 32 and outstanding dependency review |

See [PR #4](https://github.com/dominicscanlonai/hermes-desktop-catalina/pull/4) for reviewed source and test harness changes. Source regression results do not establish packaged native functionality, build provenance or full feature parity.
