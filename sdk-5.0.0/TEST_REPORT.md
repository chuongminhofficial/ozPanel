# Báo cáo Kiểm định Toàn diện — OZPanel SDK 5.0.0 (Đồng bộ OZPanel v9.1.4 · `OZV8-Fortress+`)

- **Phiên bản đồng bộ**: `OZPanel v9.1.4` (`OZV8-Fortress+` / `OZV8-SES/2` / `OzonFS 9.1.4`) · `Addon SDK 5.0.0` (`schema: 1`)
- **Bộ kiểm thử tự động**: `tests/test_sdk.py` (`python3 -m unittest discover -s tests -p "test_*.py" -v`)
- **Kiểm tra cú pháp Bash (`bash -n`), chữ ký Ed25519 (`OpenSSL 3.5.9`), SHA-256 Sidecars & Giao diện Web (`consistency.mjs`)**: Đạt 100%.

## Danh mục Kiểm định & Khắc phục Kỹ thuật (Rev 9.1.4)

1. **Sửa lỗi Endianness `runtime.lease` (`<Q` Little-Endian) & TTL 6h (`21600s`):**
   - `ozsdk.py:inspect_lease_status()` và `lib/ozaddon.py:Context.lease_status()` đã chuyển sang giải mã chuẩn little-endian `<Q` do Rust `launcher.rs` & `ozbackend` ghi xuống `runtime.lease[32:40]` (giữ fallback `>Q` cho test fixture cũ).
   - Đồng bộ `LEASE_TTL_SECONDS = 21600` (6 giờ), `SHIELD_ENGINE = 'OZV8-Fortress+'`, `PANEL = '9.1.4'`.
2. **Đồng bộ `API_V914_CATALOG` đầy đủ `125` Resources / `932` Operations & sửa định tuyến `GET`:**
   - Trích xuất trực tiếp từ `EOF_ROUTES` + `PY_API_AUGMENT` của `panel.sh` v9.1.4 (gồm `app`, `webhooks`, `billing`, `ozonfs`, `sso`, `panel/{groups,execute,batch,dag}`, `ai/{config_inspect,config_repair,cache_stats,shift_report,multitask}`, `database/{tables_list,query_readonly}`, `ssl/{inspect_cert,generate_csr}`).
   - Bổ sung nhóm read-only actions mới vào `_GET_ACTIONS` của `Context.api_call()` để gửi đúng phương thức `GET` kèm query string.
   - Bổ sung 6 helpers mới cho `lib/ozaddon.py` & `lib/ozaddon.sh`: `oz_health_json`, `oz_ai_cache_stats`, `oz_config_inspect`, `oz_app_pulse`, `oz_webhooks`, `oz_db_tables`.
3. **Đồng bộ 100% cờ CLI của `ozsdk.py` với Tài liệu & Hỗ trợ `amd64`/`arm64`:**
   - Bổ sung `init --category`, `keygen --out <dir>`, `pack --sign-key`, `verify --pub-key`, `trust --publisher --pub-key`, và bảo vệ `--ozv7-bg-lease-refresh` trong `audit_project()`.
4. **Ký số Ed25519 & Toàn vẹn Gói Mẫu `addon_9002.ozaddon`:**
   - Khôi phục toàn bộ chuỗi tiếng Việt UTF-8 sạch trong `manifest.json`, `locales/vi.json`, `ozsdk.py`, `lib/ozaddon.sh`.
   - Đóng gói USTAR deterministic + `gzip (mtime=0)`, ký `manifest.sig` (64-byte Ed25519) bằng `OpenSSL 3.5.9`, xác thực `Signature Verified Successfully` với `publisher-demo-public.pem`, và cập nhật khớp 100% các tệp `.sha256` & `catalog*.txt`.
5. **Tích hợp Lõi `panel.sh` & `build.sh` v9.1.4 (CLI `[15]` + Web GUI `[27]`):**
   - `oz_local_addon` hỗ trợ cài đặt trực tiếp `.ozaddon` (kiểm path traversal, SHA-256, Ed25519 signature, chạy `hooks/install.sh` và gỡ sạch qua `hooks/uninstall.sh`).
   - Web GUI `[27] → [15]` bổ sung `addon.sdk_list`, `addon.sdk_run`, `addon.sdk_import_url`, `addon.sdk_health`.
   - `build.sh` tự động cài đặt SDK Runtime vào `/usr/local/lib/ozpanel/sdk/`.
6. **Phạm vi Unit Test Mới (`test_v914_*` trong `tests/test_sdk.py`):**
   - `test_v914_lease_little_endian_and_6h_policy`
   - `test_v914_cli_ergonomic_flags_keygen_init_pack_verify_trust`
   - `test_v914_audit_blocks_bg_lease_refresh_and_allows_clean_example`
   - `test_v914_api_catalog_and_helpers_get_routing`
   - `test_v914_bash_extended_helpers_and_health_json`
