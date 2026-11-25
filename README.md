<p align="center">
  <img src="https://raw.githubusercontent.com/NousResearch/hermes-agent/main/assets/banner.png" alt="Hermes Agent, upstream project by Nous Research" width="100%">
</p>

<h1 align="center">Hermes Desktop for macOS Catalina ☤</h1>

<p align="center">
  <strong>A community compatibility port of the official Hermes Desktop experience to Intel macOS 10.15.8.</strong><br>
  Preserve the original interface. Extend compatibility. Keep the build reproducible.
</p>

<p align="center">
  <a href="https://github.com/NousResearch/hermes-agent"><img alt="Based on Hermes Agent" src="https://img.shields.io/badge/Upstream-Hermes%20Agent-FFD700?style=for-the-badge"></a>
  <a href="COMPATIBILITY.md"><img alt="Platform" src="https://img.shields.io/badge/macOS-Catalina%2010.15.8-0088CC?style=for-the-badge&logo=apple&logoColor=white"></a>
  <a href="docs/ROADMAP.md"><img alt="Status" src="https://img.shields.io/badge/Status-Experimental-orange?style=for-the-badge"></a>
  <a href="SECURITY.md"><img alt="Security notes" src="https://img.shields.io/badge/Security-Review%20Pending-red?style=for-the-badge"></a>
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#compatibility-at-a-glance">Compatibility</a> ·
  <a href="#getting-started">Getting started</a> ·
  <a href="#feature-status">Feature status</a> ·
  <a href="#project-layout">Source layout</a> ·
  <a href="#documentation">Documentation</a>
</p>

> [!IMPORTANT]
> **Experimental development project.** The native desktop prototype has launched and completed a basic AI conversation on an Intel Mac running Catalina. This repository includes the reviewed source integration: a compatibility patch, isolated launcher, dependency records and sanitised evidence. It does not include a complete tested Desktop build, standalone `.app` or installer. Electron 32 is end-of-support and is not suitable for general distribution.

## Overview

[Hermes Agent](https://github.com/NousResearch/hermes-agent), created by [Nous Research](https://nousresearch.com), is a model-flexible AI agent with a desktop workspace, CLI, tools, skills, memory, sessions and automation capabilities. Its current official desktop build targets newer macOS releases.

**Hermes Desktop Catalina** is an independent compatibility effort to run the **official desktop interface** on an Intel Mac running **macOS Catalina 10.15.8**, without inventing a substitute interface or replacing Hermes itself.

| Project principle | Approach |
|---|---|
| **Original Hermes experience** | Preserve upstream React interface, desktop features and branding |
| **Catalina compatibility** | Investigate an older macOS-compatible Electron host and native dependencies |
| **Upstream-first** | Keep compatibility changes small, reviewable and traceable |
| **Reproducibility** | Capture pinned tooling, scripts, test evidence and rollback instructions |
| **Safe by default** | Keep credentials, profiles, session databases and private logs out of source control |

## Compatibility at a glance

| Component | Observed development baseline |
|---|---|
| Host OS | macOS Catalina 10.15.8, Intel x86_64 |
| Upstream Hermes source | v0.23.4 ([pinned commit](manifests/upstream.json)) |
| Desktop test host | Electron 32.3.3, Chromium 128, Node 20.18.1 |
| Renderer / desktop bundling host | Ubuntu VM, Node 26.12.1, pnpm 12.15.0 |
| Native desktop window | ✅ Launched on Catalina |
| Hermes backend | ✅ Connected in tested session |
| AI chat | ✅ Basic `hello` / response smoke test |
| Conversation history | ✅ Visible in tested session |
| Terminal PTY | 🧪 Host Node import verified; packaged Electron test pending |
| Window inspection helper | 🧪 Host Node import verified; packaged Electron test pending |
| Full application test suite | ⏳ Not completed |
| Standalone distributable `.app` | ⏳ Not packaged |
| Security and dependency review | ⚠️ Outstanding |

See [COMPATIBILITY.md](COMPATIBILITY.md) for scope and limitations.

## Getting started

### Option A: Use the official Hermes Agent

For **supported operating systems**, follow [Nous Research's installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation). The upstream general-purpose installation command is:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

**This is the upstream installer, not a Catalina-specific installer.** It is **not** verified here as a fresh-install solution for macOS 10.15.

### Option B: Help build the Catalina port

The reviewed source and isolated smoke/fake-boot harness are available. There is **no supported one-command Catalina installation**.

Clone the source and documentation:

```bash
git clone https://github.com/dominicscanlonai/hermes-desktop-catalina.git
cd hermes-desktop-catalina
```

Read the [build plan](docs/BUILDING.md), [compatibility notes](COMPATIBILITY.md) and [roadmap](docs/ROADMAP.md). See the [source build and isolated launch guide](docs/BUILD.md) for the unverified build procedure and verified offline checks.

## Feature status

The feature set below is **inherited from Hermes Agent**, not a claim that each item has passed Catalina testing.

| Desktop capability | Catalina status |
|---|---|
| Desktop UI and navigation | 🧪 Prototype smoke-tested with a Webapp-derived renderer; Desktop renderer parity pending |
| Model selection and provider connection | ✅ Tested with one configured provider |
| Interactive AI conversation | ✅ Basic response confirmed |
| Session history | ✅ Rendered |
| Terminal-backed tools | 🧪 Native PTY separately tested; end-to-end testing pending |
| Skills and capabilities | 🧪 Interface present; workflows pending |
| Artifacts and files | 🧪 Interface present; workflows pending |
| Scheduled jobs | 🧪 Interface present; execution pending |
| MCP integrations | ⏳ Pending |
| Subagents, memory and advanced automation | ⏳ Pending |
| Update and migration flows | ⏳ Pending; do not use upstream auto-update on the experimental port |
| Installer, signing and notarisation | ⏳ Pending |

Upstream feature documentation: [CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) · [Tools](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) · [Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) · [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) · [MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp).

## How the port works

```text
Official Nous Research Hermes source
                |
                +-- Linux build host (modern Node + pnpm)
                |         |
                |         +-- Upstream React/Vite Webapp renderer (prototype)
                |         +-- Bundled Electron main / preload
                |
                +-- Catalina-compatible Electron runtime
                |         |
                |         +-- Native macOS x86_64 dependencies
                |         +-- Minimal module compatibility patches
                |
                +-- Existing local Hermes backend
                          |
                          +-- Authenticated desktop interface
                          +-- Sessions, model provider and tools
```

The architecture above describes the **working development prototype**, not a packaged release. It currently relies on a separately installed and configured Hermes backend. All platform-specific paths and credentials remain outside the repository.

## Project layout

```text
hermes-desktop-catalina/
├── README.md                 # Project overview
├── COMPATIBILITY.md          # Hardware / operating-system results
├── SECURITY.md               # Dependency and security limitations
├── .gitignore                # Exclude local state and generated files
└── docs/
    ├── BUILDING.md           # Build process and prerequisites
    └── ROADMAP.md            # Prioritised engineering milestones

# Reviewed source additions:
# patches/                    # Minimal compatibility patch
# scripts/                    # Isolated smoke and fake-boot launchers
# tests/                      # Offline verification
# manifests/                  # Pinned provenance and dependency records
# INVENTORY.md                # Source integration allowlist
```

## Documentation

| Guide | Purpose |
|---|---|
| [Compatibility matrix](COMPATIBILITY.md) | Verified results versus untested features |
| [Build and development](docs/BUILDING.md) | Environment, upstream source and pending build automation |
| [Source build and launch](docs/BUILD.md) | Disposable build recipe and test launcher |
| [Compatibility changes](docs/COMPATIBILITY.md) | Patch rationale and omitted prototype shortcuts |
| [Test evidence](docs/TEST-EVIDENCE.md) | Sanitised results and verification limits |
| [Security](SECURITY.md) | Runtime risks, secrets handling and distribution limitations |
| [Roadmap](docs/ROADMAP.md) | Development priorities |
| [Upstream Hermes documentation](https://hermes-agent.nousresearch.com/docs/) | Official Hermes feature reference |
| [Upstream GitHub](https://github.com/NousResearch/hermes-agent) | Canonical project and issue tracker |

## Contributing

Compatibility reports, reproducible crash reports, test cases, packaging improvements and narrowly scoped upstream changes are welcome. Please identify the exact Catalina build and Electron version, and **remove secrets and personal information from logs** before submitting them.

For the current development baseline, see the [roadmap](docs/ROADMAP.md). Contributions must not weaken backend authentication, disable Electron isolation or silently upgrade the pinned runtime.

## Credits and license

Hermes Agent and the original desktop interface are by **[Nous Research](https://nousresearch.com)**. Their upstream repository uses the **MIT license**, included here as [LICENSE](LICENSE) from the [pinned upstream commit](manifests/upstream.json).

This compatibility project is independently maintained, **not an official Nous Research release or endorsement**. The upstream banner is linked for attribution, not copied into this repository. Before redistributing upstream code or binaries, preserve the applicable upstream license and attribution notices, and verify third-party dependency licenses.

---

<p align="center">
  <strong>Hermes, with a longer runway for older Macs. ☤</strong><br>
  <sub>Experimental compatibility engineering · Intel Catalina 10.15.8 · Upstream-first</sub>
</p>
