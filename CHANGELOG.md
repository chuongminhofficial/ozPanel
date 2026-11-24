# Changelog — OZPanel

All notable releases of **OZPanel Cloud & OzonFS** are documented in this file.

## [9.1.3] — Enterprise Standalone GUI, 854-Endpoint API, Multi-Task AI DevOps & OZV8-Fortress
- **Standalone Web Admin GUI `[27]`**: 100% standalone execution without CLI dependency (0 `/usr/bin/oz` calls in backend), OZM Studio executive layout (preserving original Login UI), `Ctrl+K` global command palette, live `services_matrix` & `1m/5m/15m` load telemetry, `Quick Exec` vs `Live PTY` terminal switcher, integrated API Live Tester `[31]`, and AI DevOps Studio `[32]`.
- **Enterprise API Gateway `[31]` (854 Endpoints / 119 Resources)**: Full headless server administration without SSH or GUI — added `panel:batch`, `panel:dag`, `cloudflare:*` full zone/record/SSL/cache CRUD, `domains:alias_*` & `docroot_set`, `ssl:inspect_cert` & `generate_csr`, `database:tables_list` & `query_readonly`, `fileops:trash_list` & `trash_restore`, `monitor:service_*`, real IAM RBAC `effective_permissions`, `DELETE` query parameter + confirmation support, and automatic Nginx `/api/v1/` reverse proxy sync.
- **Autonomous AI DevOps Engineer `[32]` & 7-Tool MCP Server**: Compound 1-prompt multi-task DevOps orchestration (Domain + Cloudflare Grey-to-Orange staging + SSL + Force HTTPS; 5-tier deleted file recovery + syntax-verified new file synthesis; deep Domain DNS/HTTP/SSL inspection + live API Gateway & AI Provider discovery), unified 7-tool MCP server (`panel_api_discover` added) with `Content-Length` + JSONL framing, and Gemini/Ollama/OpenCode CLI adapters.
- **Security & Anti-Reverse-Engineering (`OZV8-Fortress`)**: Domain-separated `HMAC-SHA256` key schedule eliminating Two-Time-Pad correlation, zero cleartext keys or S-Boxes across all 43 encrypted Python modules, `<1.5ms` self-wiping `memfd` bootstrapper, `sys.addaudithook` anti-trace protection, ChatOps webhook authentication + SSRF protection, and isolated `/var/ozon_backups` (`0600`) storage.
- **Native CLI Performance & >95% Request Reduction**: Sub-15ms `draw_menu` with stale-while-revalidate caching, session-memoized `verify_license`, O(1) streaming SSH log parser, automated `logrotate` provisioning, and >95% reduction in background sync requests.
- **Direct GitHub Raw Distribution**: All signed release artifacts (`install.sh`, `oz_installer_vi`, `oz_installer_vi-arm64`, `release.manifest.json`, `release.manifest.sig`, `*.sha256`, `version.txt`) published directly on `main` for 1-line `raw.githubusercontent.com` installation.

## [9.1.1] — Zero-Gap Cross-Layer Parity
- **CLI & Non-Interactive Actions**: Completed top-level flags (`--gui-sso`, `--license-status`, `--malware-scan-auto`) and full subcommand parity across Domain, SSL, Database, OzonFS, FTP, PHP, SSH, Mail, Docker, and System File dispatchers.
- **API Gateway `[31]`**: 830/830 REST operations across 118 resources with zero unhandled routes.
- **Web Admin GUI `[27]`**: Dedicated views for Resource Monitor `[18]`, Load Balancer Studio `[33]`, and Backup Vault `[37]`.

## [9.1.0] — Autonomous AI DevOps Engineer & Multi-Task DAG
- **Multi-Task DAG Orchestrator**: Executes compound DevOps instructions in dependency order.
- **Proactive SRE Shift Reporting**: Scheduled DevOps shift briefings via Zalo/Telegram/Slack/WhatsApp/Discord with SSL auto-renewal (<14d), disk auto-hygiene (>=85%), and service self-heal.

## [9.0.9] — Performance, Security & API/GUI Overhaul
- Hardened API broker against path traversal, arbitrary log reads, SQL/shell injection, and heartbeat replay.
- Added 3s metrics caching, HSTS, TLS SNI cache cap, and Go rate-limiter periodic cleanup.
