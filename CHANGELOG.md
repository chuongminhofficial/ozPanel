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


### ✨ Cập nhật bổ sung v9.1.2 (GUI [27], Pure-FTPd & AI SRE [32])
- **Chau chuốt giao diện Web GUI [27]**: Nâng cấp chi tiết Dashboard, 46 thẻ công cụ, Workbench (.cp-card, .cp-wb-toolbar, .cp-input, .cp-btn), các màn hình chuyên biệt WHM ([18]/[22]/[31]/[32]/[33]/[37]), Dark/Light Mode & Responsive — **giữ nguyên hoàn toàn giao diện trang đăng nhập gốc**.
- **Sửa triệt để lỗi Pure-FTPd**: Chuẩn hóa STANDALONE_OR_INETD=standalone, xác thực IPv4 chặt trước khi ghi ForcePassiveIP, tự tạo pureftpd.passwd/PureDB & bảo vệ chứng chỉ TLS, tự động vá lỗi trong SRE Patrol.
- **Nâng cấp Trợ lý AI DevOps [32]**: Giảm tần suất báo cáo mặc định (12h + nhiễu thời gian ngẫu nhiên -20p..+45p), chống spam cảnh báo theo cooldown, 5 mẫu bản tin điều hành xoay vòng ngẫu nhiên chuyên nghiệp, và 8 tác vụ SRE tự động (tự hồi phục dịch vụ, cắt log >120MB/dọn đĩa 2 tầng, thu hồi RAM PageCache >=88%, tự gia hạn SSL <=14 ngày, kiểm tra cú pháp Nginx, dọn temp/đếm Zombie, ping MariaDB/Redis, giám sát Backup).
- **Hỗ trợ gọi trực tiếp qua Raw URL (aw.githubusercontent.com)**: Toàn bộ tệp thành phẩm (install.sh, oz_installer_vi, oz_installer_vi-arm64, elease.json, elease.manifest.json, elease.manifest.sig, *.sha256) đều nằm sẵn tại nhánh main.
