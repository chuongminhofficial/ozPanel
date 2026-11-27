# OZPanel Addon Developer Kit — v9.1.4 (SDK 5.0.0)

Bộ công cụ phát triển và tài liệu đầy đủ cho **Nhà phát triển Addon** và **Người dùng cuối** của **OZPanel v9.1.4** (Linux x86_64 & ARM64 — `OZV8-Fortress+` · `OZV8-SES/2` · 125 API Resources / 932 Operations `[31]` · Web GUI `[27]` · AI Config Surgeon `[32]` · MCP 8-Tool · OzonFS `9.1.4`).

---

## Tài liệu trong bộ Kit

| Tài liệu | Đối tượng | Mô tả |
| :--- | :--- | :--- |
| **[`GUIDE_9.1.4_SDK_5.0.0.html`](GUIDE_9.1.4_SDK_5.0.0.html)** | Developer & User | **Tài liệu Web tương tác toàn diện** (mở ngoại tuyến bằng trình duyệt, chuyển chế độ Developer/User/Tất cả, tìm kiếm tức thì, copy code 1-click, Light/Dark mode) |
| **[`DEVELOPER_GUIDE_VI.md`](DEVELOPER_GUIDE_VI.md)** | Nhà phát triển Addon | Hướng dẫn chi tiết từ A–Z: `manifest.json`, 5 hooks, quyền hạn, Web GUI `[27]` (`[15]` Workbench), API `[31]` (932 ops), AI `[32]`, MCP 8-Tool, ký số Ed25519 & xuất bản |
| **[`USER_GUIDE_VI.md`](USER_GUIDE_VI.md)** | Người dùng cuối | Hướng dẫn cài đặt, chạy, cập nhật, kiểm tra chữ ký, xem log, khôi phục & gỡ Addon trên CLI `[15]`, Web GUI `[27]` và AI `[32]` |
| **[`README_EN.md`](README_EN.md)** | International Dev | English quickstart & SDK 5.0.0 reference synced with OZPanel v9.1.4 |
| **[`TEST_REPORT.md`](TEST_REPORT.md)** | QA & DevOps | Báo cáo kiểm định tự động & xác thực toàn vẹn v9.1.4 · SDK 5.0.0 |
| **[`CHANGELOG.md`](CHANGELOG.md)** | Tất cả | Lịch sử nâng cấp từ SDK 1.0.0 → 5.0.0 (OZPanel v9.1.4) |

---

## Thành phần kỹ thuật chính

- **`ozsdk.py` (SDK 5.0.0 — Rev 9.1.4):** Công cụ CLI đa nền tảng (**Linux, macOS, Windows**) với `API_V914_CATALOG` (**125 resources / 932 operations**), `SHIELD_ENGINE = 'OZV8-Fortress+'`, đọc chuẩn `runtime.lease` little-endian `<Q` (TTL `21600s` — 6 giờ), hỗ trợ đầy đủ `--category`, `keygen --out`, `pack --sign-key`, `verify --pub-key`, `trust --publisher --pub-key`.
- **`lib/ozaddon.sh` & `lib/ozaddon.py`:** Thư viện Runtime cho Addon Bash/Python kèm đầy đủ helper v9.1.4 (`oz_health_json`, `oz_ai_cache_stats`, `oz_config_inspect`, `oz_app_pulse`, `oz_webhooks`, `oz_db_tables`, `oz_ai_shift_report`, `oz_loadbalancer`, `oz_cloudflare`, `oz_fleet`, `oz_panel_groups`, `oz_gui_sso`).
- **Tích hợp lõi OZPanel v9.1.4 (`panel.sh` & `build.sh`):**
  - Chạy `bash build.sh` tự động cài đặt SDK Runtime vào `/usr/local/lib/ozpanel/sdk/`.
  - SSH Menu `[15] → [6]` và Web GUI `[27] → [15]` (`addon.sdk_list`, `addon.sdk_run`, `addon.sdk_import_url`, `addon.sdk_health`) hỗ trợ cài đặt & vận hành trực tiếp cả `.ozaddon`, `.sh`, `.bin`.
- **`examples/native/` & `addon_9002.ozaddon`:** Addon mẫu chuẩn Native `.ozaddon` đã đóng gói & ký Ed25519 kèm `.sha256` và khóa công khai `publisher-demo-public.pem`.
- **`examples/classic/` & `addon_demo_9001.sh`:** Addon mẫu 1 tệp Bash truyền thống hỗ trợ cả CLI & `OZ_GUI_FORM=1`.
- **`tests/test_sdk.py`:** Bộ kiểm thử tự động vòng đời SDK, bảo mật Ed25519, little-endian lease & v9.1.4 API helpers.

---

## Bắt đầu nhanh (30 giây)

```bash
python3 ozsdk.py --version
python3 ozsdk.py doctor
python3 ozsdk.py init ./demo-addon --id 9010 --publisher my-studio --name "Demo Addon" --category automation
python3 ozsdk.py validate ./demo-addon
python3 ozsdk.py audit ./demo-addon
python3 ozsdk.py keygen --out ./keys
python3 ozsdk.py pack ./demo-addon --out ./dist/addon_9010.ozaddon --sign-key ./keys/publisher-private.pem
python3 ozsdk.py verify ./dist/addon_9010.ozaddon --pub-key ./keys/publisher-public.pem
```
