# Changelog — OZPanel

All notable releases of **OZPanel Cloud & OzonFS** are documented in this file.

## [9.1.2] — Commercial Product Certification
- **Web Admin GUI `[27]`**: 100% parameter parity across all 312 actions, real live server telemetry across all 46 features, Cloudflare Grey/Orange proxy selector, execution latency (`elapsed_ms`) reporting, and refined WHM UI polish.
- **Production Hardening**: Private `0700` `mktemp` staging in API broker, auto-hardening directory permissions in build pipeline, clean commercial help menus.

## [9.1.1] — Zero-Gap Cross-Layer Parity
- **CLI & Non-Interactive Actions**: Completed top-level flags (`--gui-sso`, `--license-status`, `--malware-scan-auto`) and full subcommand parity across Domain, SSL, Database, OzonFS, FTP, PHP, SSH, Mail, Docker, and System File dispatchers.
- **API Gateway `[31]`**: 830/830 REST operations across 118 resources with zero unhandled routes.
- **Web Admin GUI `[27]`**: Eliminated all remaining stubs across all 46 modules; added dedicated WHM views for Resource Monitor `[18]`, Load Balancer Studio `[33]`, and Backup Vault `[37]`.

## [9.1.0] — Autonomous AI DevOps Engineer & Multi-Task DAG
- **Multi-Task DAG Orchestrator**: Executes compound DevOps instructions in dependency order (e.g. Add Domain -> Cloudflare Grey/Orange Proxy -> SSL -> DB/App/LB/WAF/Malware/Backup).
- **Proactive SRE Shift Reporting**: Scheduled DevOps shift briefings via Zalo/Telegram/Slack/WhatsApp/Discord with RAM/Disk shift deltas, SSL auto-renewal (<14d), disk auto-hygiene (>=85%), and service self-heal.
- **6-Tool MCP Server**: Added `panel_shift_report`, `panel_file_op`, and `panel_chatops` alongside `panel_list_actions`, `panel_check_status`, and `panel_execute`.

## [9.0.9] — Performance, Security & API/GUI Overhaul
- Hardened API broker against path traversal, arbitrary log reads, SQL/shell injection, and heartbeat replay.
- Added 3s metrics caching, HSTS, TLS SNI cache cap, and Go rate-limiter periodic cleanup.
