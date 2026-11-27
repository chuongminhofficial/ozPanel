# Changelog — OZPanel

All notable releases of **OZPanel Cloud & OzonFS** are documented in this file.

## [9.1.4] — Addon SDK 5.0.0, 932-Operation API Gateway, 8-Tool MCP & OZV8-Fortress+
- **Addon Developer Kit & SDK 5.0.0 (`[15]`)**: Published public Addon Developer Kit (`sdk-5.0.0/`) with Ed25519-signed `.ozaddon` packaging (`addon_9002.ozaddon`), interactive developer documentation (`GUIDE_9.1.4_SDK_5.0.0.html`), and public key verification workflow.
- **Enterprise API Gateway `[31]` (932 Operations / 125 Resources)**: Expanded OpenAPI 3.1 gateway catalog (`125` resources / `932` operations) for third-party and mobile/desktop app integration, complete batch/DAG orchestration, DNS/Cloudflare, SSL, Database, FileOps, and IAM RBAC endpoints.
- **Autonomous AI DevOps Engineer `[32]` & 8-Tool MCP Server**: Deeper log + configuration file inspection to auto-diagnose and remediate system errors, single-prompt compound task execution minimizing redundant AI API calls, load-aware urgent alerting without spam, and upgraded **8-Tool MCP** registration (`register_mcp_v914.sh`).
- **Standalone Web Admin GUI `[27]` Polish & SSO Responsiveness**: Complete 100% standalone control surface (full button/input/form coverage independent of CLI) plus noticeably faster SSO handoff and `oz` launch responsiveness.
- **Security & Proprietary Hardening (`OZV8-Fortress+` + Native v3)**: Strengthened anti-reverse-engineering, tamper resistance, and lightweight client caching to cut license server round-trips while keeping runtime integrity intact.
- **Verified Signed Raw Artifacts (`main`)**: Published `oz_installer_vi` (`x86_64`, `9,146,552` bytes), `oz_installer_vi-arm64` (`ARM64`, `8,637,104` bytes), `install.sh` (`15,566` bytes), `release.manifest.json` (`sequence: 1795816267586`), and `release.manifest.sig` for direct GitHub Raw installation.

## [9.1.3] — Enterprise Standalone GUI, 854-Endpoint API, Multi-Task AI DevOps & OZV8-Fortress
- **Standalone Web Admin GUI `[27]`**: 100% standalone execution without CLI dependency (0 `/usr/bin/oz` calls in backend), OZM Studio executive layout (preserving original Login UI), `Ctrl+K` global command palette, live `services_matrix` & `1m/5m/15m` load telemetry, `Quick Exec` vs `Live PTY` terminal switcher, integrated API Live Tester `[31]`, and AI DevOps Studio `[32]`.
- **Enterprise API Gateway `[31]` (854 Endpoints / 119 Resources)**: Full headless server administration without SSH or GUI — added `panel:batch`, `panel:dag`, `cloudflare:*` full zone/record/SSL/cache CRUD, `domains:alias_*` & `docroot_set`, `ssl:inspect_cert` & `generate_csr`, `database:tables_list` & `query_readonly`, `fileops:trash_list` & `trash_restore`, `monitor:service_*`, real IAM RBAC `effective_permissions`, `DELETE` query parameter + confirmation support, and automatic Nginx `/api/v1/` reverse proxy sync.
- **Autonomous AI DevOps Engineer `[32]` & 7-Tool MCP Server**: Compound 1-prompt multi-task DevOps orchestration, unified 7-tool MCP server, and Gemini/Ollama/OpenCode CLI adapters.
- **Security & Anti-Reverse-Engineering (`OZV8-Fortress`)**: Domain-separated `HMAC-SHA256` key schedule, `<1.5ms` self-wiping `memfd` bootstrapper, `sys.addaudithook` anti-trace protection, ChatOps webhook authentication + SSRF protection.
- **Direct GitHub Raw Distribution**: Signed release artifacts published directly on `main` for 1-line `raw.githubusercontent.com` installation.

## [9.1.1] — Zero-Gap Cross-Layer Parity
- Completed top-level CLI flags (`--gui-sso`, `--license-status`, `--malware-scan-auto`) and 830/830 REST operations across 118 resources.
- Dedicated Web Admin GUI views for Resource Monitor `[18]`, Load Balancer Studio `[33]`, and Backup Vault `[37]`.

## [9.1.0] — Autonomous AI DevOps Engineer & Multi-Task DAG
- Added Multi-Task DAG Orchestrator and proactive SRE Shift Reporting across Telegram/Zalo/Slack/WhatsApp/Discord.

## [9.0.9] — Performance, Security & API/GUI Overhaul
- Hardened API broker against path traversal, arbitrary log reads, SQL/shell injection, and heartbeat replay; added metrics caching and HSTS.
