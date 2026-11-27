# Changelog — OZPanel Addon Developer Kit

## [5.0.0 — Rev 9.1.4] — Đồng bộ Toàn diện OZPanel v9.1.4 (2026)
### Nâng cấp kiến trúc, vá lỗi tương thích & đồng bộ Web GUI / MCP
- **Đồng bộ nền tảng v9.1.4 (`OZV8-Fortress+`):**
  - Cập nhật `PANEL = '9.1.4'`, `OZONFS_VERSION = '9.1.4'`, `SHIELD_ENGINE = 'OZV8-Fortress+'`, `SHIELD_STACK = ['OZV8-Fortress+', 'OZV7-Fortress', 'OZV6-ZeroTrust-CloudSplit', 'OZV5-Shield']`, `LEASE_TTL_SECONDS = 21600` (6 giờ).
  - Mở rộng `audit_project()` chặn thêm cờ nội bộ `--ozv7-bg-lease-refresh` của v9.1.4.
- **Vá lỗi đọc `runtime.lease` (Little-Endian `<Q`) & định tuyến HTTP GET:**
  - Sửa `inspect_lease_status()` (`ozsdk.py`) và `Context.lease_status()` (`lib/ozaddon.py`) đọc chuẩn 64-bit unsigned little-endian `<Q` do Rust launcher & `ozbackend` ghi ra tại byte `[32:40]` (giữ fallback an toàn cho fixture big-endian `>Q`).
  - Bổ sung nhóm action đọc mới (`shift_report`, `groups`, `group_status`, `providers`, `selftest`, `cache_stats`, `config_inspect`, `bootstrap`, `pulse`, `deliveries`, `packages`, `usage`, `tables_list`, `health_probe`, `inspect_cert`, `aliases_list`, `zones_list`, `records_list`, `banned_list`, `ext_list`, `client_config`, `service_journal`) vào tập GET auto-detection của `Context.api_call()`.
- **Đồng bộ `API_V914_CATALOG` đầy đủ (`125` resources / `932` operations):**
  - Bao gồm toàn bộ endpoint mới của v9.1.4 (`app/{bootstrap,pulse}`, `webhooks/*`, `billing/*`, `ozonfs/*`, `sso/*`, `panel/{groups,execute,batch,dag}`, `ai/{config_inspect,config_repair,cache_stats,shift_report,multitask,auto_policy}`, `database/{tables_list,query_readonly}`, `ssl/{inspect_cert,generate_csr}`) và danh sách `MCP_TOOLS_V914` (8 tool).
- **Mở rộng Helper v9.1.4 trong `lib/ozaddon.py` & `lib/ozaddon.sh`:**
  - Thêm `oz_health_json`, `oz_ai_cache_stats`, `oz_config_inspect`, `oz_app_pulse`, `oz_webhooks`, `oz_db_tables` (cùng phương thức Python tương ứng).
- **Đồng bộ CLI flags `ozsdk.py` khớp 100% tài liệu:**
  - Hỗ trợ `init --category`, `keygen --out <dir>`, `pack --sign-key`, `verify --pub-key`, `trust --publisher --pub-key`, và chuẩn hóa kiến trúc `amd64`/`arm64`.
- **Tích hợp trực tiếp vào lõi `panel.sh` & `build.sh` v9.1.4:**
  - `[15] → [6]` hỗ trợ tải & cài trực tiếp `.ozaddon` (kiểm tra path traversal, SHA-256, Ed25519 signature, chạy `hooks/install.sh` & tạo wrapper sạch).
  - Web GUI `[27] → [15]` bổ sung `addon.sdk_list`, `addon.sdk_run`, `addon.sdk_import_url`, `addon.sdk_health`.
  - `build.sh` tự động triển khai SDK Runtime vào `/usr/local/lib/ozpanel/sdk/`.
- **Khắc phục lỗi hiển thị UTF-8, ký lại `addon_9002.ozaddon` & nâng cấp tài liệu:**
  - Khôi phục toàn bộ chuỗi tiếng Việt UTF-8 sạch trong `manifest.json`, `locales/vi.json`, `ozsdk.py`, `lib/ozaddon.sh`; ký lại gói `addon_9002.ozaddon` bằng Ed25519 (`OpenSSL 3.5.9`), cập nhật `.sha256`, `catalog*.txt` và phát hành `GUIDE_9.1.4_SDK_5.0.0.html`.

## [5.0.0] — OZPanel v9.1.2 (2026)
- Đồng bộ `SDK VERSION = 5.0.0`, `PANEL = 9.1.2`, bảo vệ `fcntl` đa nền tảng Linux/macOS/Windows.
- Bổ sung 6 hàm helper (`oz_ai_shift_report`, `oz_loadbalancer`, `oz_cloudflare`, `oz_fleet`, `oz_panel_groups`, `oz_gui_sso`) và lưu trữ `GUIDE_9.1.2_SDK_5.0.0.html` vào `archive/`.

## [4.0.0] — OZPanel Cloud 8.6.0
- Hỗ trợ OZV7-Fortress, Omni-Channel AI ChatOps 46-Function Engine và OzonFS 8.6.0.
- Thêm `ai-watchdog-status`, `chatops-simulate`, `api-catalog`, `sbom`, `audit`.

## [3.0.0] — OZPanel 7.3.2
- Bổ sung Web GUI Workbench actions (`gui_workbench.actions`), 72-Byte Boot-Bound Cloud Lease và đa ngôn ngữ `locales/vi.json` & `en.json`.

## [1.0.0 – 2.0.0] — OZPanel 7.2.x
- Ra mắt định dạng `.ozaddon`, 5 lifecycle hooks, ký số Ed25519 và `ozsdk.py`.
