# Hướng dẫn Phát triển Addon — OZPanel v9.1.4 (SDK 5.0.0)

> **Phiên bản SDK:** `5.0.0` · **Tương thích OZPanel:** `v9.1.4+` (Linux x86_64 & ARM64)  
> **Động cơ bảo mật:** `OZV8-Fortress+` (`OZV8-SES/2` + Cloud Lease `21600s` little-endian `<Q`)  
> **Hệ sinh thái:** CLI `[15]` · Web GUI `[27]` · Enterprise API `[31]` (`125` resources / `932` operations) · AI Config Surgeon `[32]` · MCP 8-Tool (`register_mcp_v914.sh`) · OzonFS `9.1.4`

---

## Mục lục

1. [Tổng quan kiến trúc Addon SDK 5.0.0 trên OZPanel v9.1.4](#1-tổng-quan-kiến-trúc-addon-sdk-500-trên-ozpanel-v914)
2. [Bắt đầu nhanh trong 5 phút (Quickstart)](#2-bắt-đầu-nhanh-trong-5-phút-quickstart)
3. [Cấu trúc thư mục một Addon chuẩn `.ozaddon`](#3-cấu-trúc-thư-mục-một-addon-chuẩn-ozaddon)
4. [Đặc tả đầy đủ `manifest.json` (Schema 1)](#4-đặc-tả-đầy-đủ-manifestjson-schema-1)
5. [Vòng đời 5 Hooks chuẩn & Biến môi trường](#5-vòng-đời-5-hooks-chuẩn--biến-môi-trường)
6. [Hệ thống Quyền hạn & Kiểm toán Bảo mật `OZV8-Fortress+`](#6-hệ-thống-quyền-hạn--kiểm-toán-bảo-mật-ozv8-fortress)
7. [Tích hợp Web GUI `[27]` (`[15]` SDK Workbench & `OZ_GUI_FORM=1`)](#7-tích-hợp-web-gui-27-15-sdk-workbench--oz_gui_form1)
8. [Thư viện Runtime `ozaddon.sh` & `ozaddon.py` (v9.1.4)](#8-thư-viện-runtime-ozaddonsh--ozaddonpy-v914)
9. [Tích hợp REST API `[31]` (932 ops), AI Config Surgeon `[32]` & MCP 8-Tool](#9-tích-hợp-rest-api-31-932-ops-ai-config-surgeon-32--mcp-8-tool)
10. [Đóng gói, Ký số Ed25519, SBOM & Kiểm thử Tự động](#10-đóng-gói-ký-số-ed25519-sbom--kiểm-thử-tự-động)
11. [Xuất bản lên Kho Tiện ích `[15]` hoặc GitHub Raw URL](#11-xuất-bản-lên-kho-tiện-ích-15-hoặc-github-raw-url)
12. [Checklist Kiểm duyệt trước khi phát hành](#12-checklist-kiểm-duyệt-trước-khi-phát-hành)

---

## 1. Tổng quan kiến trúc Addon SDK 5.0.0 trên OZPanel v9.1.4

OZPanel v9.1.4 hỗ trợ **2 định dạng Addon** chạy thống nhất trên cả SSH Terminal `[15]` lẫn Web Admin GUI `[27]`:

| Định dạng | Đuôi tệp | Khuyên dùng | Đặc điểm |
| :--- | :--- | :--- | :--- |
| **Native Package (Khuyên dùng)** | `.ozaddon` (`tar.gz`) | Production / Store | Có `manifest.json` Schema 1, 5 lifecycle hooks, đa ngôn ngữ `vi/en`, tương thích 100% GUI Workbench (`OZ_GUI_FORM=1`), kiểm tra SHA-256 từng tệp & chữ ký Ed25519 (`manifest.sig`), hỗ trợ rollback & cách ly tự động. |
| **Classic Script** | `.sh` / `.bin` | Script nội bộ nhẹ | 1 tệp Bash/ELF duy nhất (xem `examples/classic/addon_demo_9001.sh`, hỗ trợ `OZ_GUI_FORM=1` & `OZ_ACTION_KEY`). |

### Những điểm đồng bộ quan trọng trên OZPanel v9.1.4
- **Tự động cài Runtime khi build:** Lệnh `build.sh` tự động sao chép `ozsdk.py`, `lib/ozaddon.{py,sh}` và trust pin mẫu vào `/usr/local/lib/ozpanel/sdk/` (kèm symlink `/usr/local/bin/ozsdk`), giúp `.ozaddon` chạy ngay sau khi triển khai.
- **Đọc chuẩn `runtime.lease` 72-byte (`<Q` little-endian, TTL 6h = `21600s`):** `inspect_lease_status()` và `Context.lease_status()` giải mã chính xác định dạng native `<Q` do Rust launcher và `ozbackend` ghi xuống đĩa (giữ tương thích ngược `>Q`).
- **Tích hợp trực tiếp `[15] → [6]` & Web GUI `[27] → [15]`:** Hàm lõi `oz_local_addon` trong `panel.sh` trực tiếp giải nén an toàn, kiểm tra SHA-256 + Ed25519, chạy `hooks/install.sh` và quản lý qua `addon.sdk_list`, `addon.sdk_run`, `addon.sdk_import_url`, `addon.sdk_health`.
- **Full CLI Parity trong `ozsdk.py`:** Hỗ trợ đầy đủ `init --category`, `keygen --out <dir>`, `pack --sign-key`, `verify --pub-key`, `trust --publisher --pub-key --confirm`, cùng chuẩn hóa CPU `amd64`/`arm64`.

---

## 2. Bắt đầu nhanh trong 5 phút (Quickstart)

```bash
# 1. Kiểm tra phiên bản & khả năng môi trường SDK (932 ops / 125 resources)
python3 ozsdk.py --version
python3 ozsdk.py doctor

# 2. Khởi tạo dự án Addon mới (ID 9010, publisher của bạn)
python3 ozsdk.py init ./my-addon --id 9010 --publisher my-studio --name "My Super Addon" --category automation

# 3. Kiểm tra manifest, hooks, quyền hạn & rà soát bảo mật OZV8-Fortress+
python3 ozsdk.py validate ./my-addon
python3 ozsdk.py audit ./my-addon

# 4. Tạo cặp khóa ký số Ed25519 cho nhà phát triển (giữ kín publisher-private.pem!)
python3 ozsdk.py keygen --out ./keys

# 5. Đóng gói & ký số tạo tệp .ozaddon + .sha256
python3 ozsdk.py pack ./my-addon --out ./dist/addon_9010.ozaddon --sign-key ./keys/publisher-private.pem

# 6. Xác minh chữ ký độc lập trực tiếp bằng khóa công khai
python3 ozsdk.py verify ./dist/addon_9010.ozaddon --pub-key ./keys/publisher-public.pem

# 7. Tin cậy publisher & cài thử trên máy chủ Linux OZPanel v9.1.4
sudo python3 ozsdk.py trust --publisher my-studio --pub-key ./keys/publisher-public.pem --confirm
sudo python3 ozsdk.py install ./dist/addon_9010.ozaddon --confirm
sudo python3 ozsdk.py run 9010
```

---

## 3. Cấu trúc thư mục một Addon chuẩn `.ozaddon`

```text
my-addon/
├── manifest.json          # Khai báo định danh, phiên bản, quyền hạn, hooks, GUI Workbench
├── bin/
│   └── main.sh            # Entrypoint chính (chmod 700 trong archive)
├── hooks/
│   ├── install.sh         # Chạy khi cài mới lần đầu
│   ├── upgrade.sh         # Chạy khi nâng cấp phiên bản
│   ├── health.sh          # Chạy khi kiểm tra sức khỏe (ozsdk.py health <id>)
│   ├── rollback.sh        # Chạy khi khôi phục phiên bản trước
│   └── uninstall.sh       # Chạy khi gỡ cài đặt
├── locales/
│   ├── vi.json            # Chuỗi tiếng Việt
│   └── en.json            # Chuỗi tiếng Anh
└── lib/                   # (Tùy chọn) Thư viện runtime riêng: ozaddon.sh & ozaddon.py
```

---

## 4. Đặc tả đầy đủ `manifest.json` (Schema 1)

```json
{
  "schema": 1,
  "id": 9010,
  "publisher": "my-studio",
  "name": "My Super Addon (OZPanel v9.1.4)",
  "version": "1.0.0",
  "min_panel_version": "9.1.4",
  "category": "automation",
  "entrypoint": "bin/main.sh",
  "architectures": ["any"],
  "permissions": ["system.read", "ssl.read", "ai.read"],
  "hooks": {
    "install": "hooks/install.sh",
    "upgrade": "hooks/upgrade.sh",
    "health": "hooks/health.sh",
    "rollback": "hooks/rollback.sh",
    "uninstall": "hooks/uninstall.sh"
  },
  "locales": {
    "vi": "locales/vi.json",
    "en": "locales/en.json"
  },
  "platforms": [
    "ubuntu:20.04", "ubuntu:22.04", "ubuntu:24.04",
    "debian:11", "debian:12", "debian:13"
  ],
  "gui_workbench": {
    "actions": [
      { "key": "1", "label": "Kiểm tra thông tin hệ điều hành & OZPanel v9.1.4" },
      { "key": "3", "label": "Kiểm tra Core v9.1.4 & OZV8-Fortress+" },
      { "key": "5", "label": "Kiểm tra Health JSON (<30ms) & AI Watchdog" }
    ]
  }
}
```

### Bảng trường bắt buộc

| Trường | Kiểu | Quy tắc hợp lệ |
| :--- | :--- | :--- |
| `schema` | `int` | Bắt buộc bằng `1` |
| `id` | `int` | Số nguyên dương `1..999999` (khuyên dùng `9000+` hoặc `900000+` cho addon nội bộ) |
| `publisher` | `string` | Slug `a-z0-9-`, độ dài `2..48` ký tự |
| `name` | `string` | Tên hiển thị ngắn gọn trên CLI `[15]` và Web GUI `[27]` |
| `version` | `string` | SemVer `X.Y.Z` (VD: `1.0.0`, `5.0.0`) |
| `min_panel_version` | `string` | Phiên bản OZPanel tối thiểu (VD: `9.0.0` hoặc `9.1.4`) |
| `category` | `string` | `web`, `database`, `mail`, `security`, `backup`, `monitoring`, `automation`, `ai`, `network`, `system`, `general` |
| `entrypoint` | `string` | Đường dẫn tương đối bên trong gói (VD: `bin/main.sh`) |
| `architectures` | `array` | `["any"]`, `["x86_64"]` (hoặc `"amd64"`), `["aarch64"]` (hoặc `"arm64"`) |
| `permissions` | `array` | Danh sách quyền khai báo theo quy tắc tối thiểu |

---

## 5. Vòng đời 5 Hooks chuẩn & Biến môi trường

Mỗi hook phải **idempotent** (chạy lại nhiều lần vẫn an toàn, timeout `300s`), không sửa file bên trong `$OZ_SDK_RELEASE` (nếu sửa sẽ bị từ chối vì sai SHA-256), và thoát `0` khi thành công:

1. **`hooks/install.sh`**: Khởi tạo cấu hình mặc định trong `$OZ_ADDON_DATA` (`0600`). Không hỏi `read` tương tác để tương thích cài tự động từ Web GUI `[27]`.
2. **`hooks/upgrade.sh`**: Di trú dữ liệu khi nâng cấp phiên bản, giữ nguyên cấu hình người dùng.
3. **`hooks/health.sh`**: Kiểm tra nhanh sức khỏe tiến trình/cấu hình (`exit 0` = khỏe mạnh).
4. **`hooks/rollback.sh`**: Khôi phục trạng thái trước đó nếu bản mới gặp lỗi.
5. **`hooks/uninstall.sh`**: Dọn sạch cron/service do Addon tạo; giữ `$OZ_ADDON_DATA` trừ khi chỉ định `--purge-data`.

### Biến môi trường được truyền vào Addon

| Biến môi trường | Ý nghĩa |
| :--- | :--- |
| `OZ_ADDON_ID` | ID số của Addon (VD: `9002` hoặc `900000`) |
| `OZ_ADDON_VERSION` | Phiên bản hiện tại |
| `OZ_ADDON_DATA` | Thư mục dữ liệu riêng (`$OZON_ROOT_DIR/addon-data/<id>`, `chmod 700`) |
| `OZ_SDK_RELEASE` | Thư mục gói đã giải nén chứa `manifest.json` & `lib/ozaddon.*` |
| `OZ_SDK_CLI` | Đường dẫn `/usr/local/lib/ozpanel/sdk/ozsdk.py` |
| `OZ_SDK_VERSION` / `OZ_PANEL_BASELINE` | `5.0.0` / `9.1.4` |
| `OZ_SHIELD_ENGINE` | `OZV8-Fortress+` |
| `OZON_ROOT_DIR` / `OZON_ADDON_DIR` | `/etc/ozon` và `/etc/ozon/addons` |
| `OZON_LICENSE_FILE` | Đường dẫn file khóa Addon `license_<id>.key` |
| `OZ_GUI_FORM` / `OZ_ACTION_KEY` | `1` khi chạy từ Web GUI `[27]`, kèm mã thao tác người dùng chọn (VD: `1`, `3`, `5`) |

---

## 6. Hệ thống Quyền hạn & Kiểm toán Bảo mật `OZV8-Fortress+`

Lệnh `ozsdk.py audit <dir>` kiểm tra tĩnh tự động mã nguồn để chặn mọi hành vi vi phạm ranh giới bảo mật `OZV8-Fortress+` (`--native-source`, `--ozv7-helper`, `--ozv7-bg-lease-refresh`, đọc trực tiếp `/etc/ozon/native/runtime.lease`, inject `LD_PRELOAD`/`LD_AUDIT`/`PYTHONINSPECT`, import lậu `/etc/ozon/(gui|core-api|license-v2)/*.py`), đồng thời kiểm tra cú pháp toàn bộ `.sh` (`bash -n`) và `.py` (`ast.parse`).

---

## 7. Tích hợp Web GUI `[27]` (`[15]` SDK Workbench & `OZ_GUI_FORM=1`)

Trên Web GUI `[27]` mục **`[15] Kho tiện ích`**, OZPanel v9.1.4 cung cấp sẵn 4 thao tác tương tác trực tiếp bằng form (không cần SSH):
- `addon.sdk_list`: Liệt kê Addon đã cài kèm các `gui_workbench.actions`.
- `addon.sdk_import_url`: Cài đặt trực tiếp URL `.ozaddon` hoặc `.sh` với kiểm tra SHA-256.
- `addon.sdk_run`: Khởi chạy Addon ở chế độ không tương tác với `OZ_GUI_FORM=1` và `OZ_ACTION_KEY`.
- `addon.sdk_health`: Kiểm tra SHA-256 payload và chạy `hooks/health.sh`.

```bash
if oz_is_gui_form; then
    case "${OZ_ACTION_KEY:-1}" in
        1) oz_os ;;
        3) python3 "${OZ_SDK_CLI:?}" --root "${OZON_ROOT_DIR:-/etc/ozon}" core-status ;;
        5) oz_health_json ;;
    esac
    exit 0
fi
```

---

## 8. Thư viện Runtime `ozaddon.sh` & `ozaddon.py` (v9.1.4)

| Hàm Bash (`source "${OZ_SDK_RELEASE:?}/lib/ozaddon.sh"`) | Phương thức Python (`lib/ozaddon.py`) | Chức năng |
| :--- | :--- | :--- |
| `oz_get` / `oz_set` | `ctx.get` / `ctx.set` | Đọc/ghi cấu hình JSON atomic + `flock` (`chmod 600`) |
| `oz_health_json` *(v9.1.4)* | `ctx.health_json()` | Gọi nhanh `/usr/bin/oz --health-json` (<30ms) có fallback SDK |
| `oz_shield_status` / `oz_lease_status` | `ctx.shield_status()` / `ctx.lease_status()` | Trạng thái `OZV8-Fortress+` & Cloud Lease 72-byte `<Q` (6h TTL) |
| `oz_api_call <res> <act>` | `ctx.api_call(res, act)` | Gọi REST API `[31]` tự động định tuyến GET/POST & query string |
| `oz_ai_cache_stats` *(v9.1.4)* | `ctx.ai_cache_stats(clear=False)` | Đọc/xóa telemetry cache LLM (`llm_cache.json`) của AI `[32]` |
| `oz_config_inspect <path>` *(v9.1.4)* | `ctx.ai_config_inspect(path)` | Đọc an toàn cấu hình dịch vụ & danh sách backup `.ozbak` |
| `oz_app_pulse` *(v9.1.4)* | `ctx.app_pulse()` | Telemetry CPU/RAM/Disk chi phí <2ms từ `/api/v1/app/pulse` |
| `oz_webhooks <act>` *(v9.1.4)* | `ctx.webhooks_action(act)` | Quản lý Outbound Webhooks ký số HMAC-SHA256 |
| `oz_db_tables <db> [engine]` *(v9.1.4)* | `ctx.db_tables_list(name, engine)` | Kiểm tra bảng/engine/dung lượng của Database MySQL/PostgreSQL |
| `oz_ai_shift_report` | `ctx.api_call('ai','shift_report')` | Lấy Báo cáo Ca trực DevOps AI `[32]` (HTTP `GET`) |
| `oz_panel_groups` | `ctx.api_call('panel','groups')` | Lấy danh mục 46 nhóm chức năng OZPanel (HTTP `GET`) |
| `oz_loadbalancer` / `oz_cloudflare` / `oz_fleet` | `ctx.api_call(...)` | Tương tác Cân bằng tải `[33]`, Cloudflare `[38]`, Multi-Server `[39]` |
| `oz_gui_sso` / `oz_sso_link` | `ctx.sso_link(...)` | Tạo link 1-Click SSO vào Web GUI, OzonFS, AdminNeo, Webmail |
| `oz_log` / `oz_t` | `ctx.log` / `ctx.t` | Ghi log vào `$OZ_ADDON_DATA/addon.log` & đa ngôn ngữ `vi/en` |

---

## 9. Tích hợp REST API `[31]` (932 ops), AI Config Surgeon `[32]` & MCP 8-Tool

OZPanel v9.1.4 cung cấp Gateway API tại `/api/v1` (tổng cộng **125 resources / 932 operations**, kèm Postman Collection v2.1 & `X-RateLimit-*` tại `/api_docs`) và **MCP Server 8-Tool** cài tự động qua `register_mcp_v914.sh`:
`panel_status`, `panel_groups`, `panel_execute`, `panel_api`, `panel_ai_surgeon`, `panel_config_surgeon`, `panel_shift_report`, `panel_sso`.

```bash
# Xem tóm tắt toàn bộ 125 resources / 932 operations
python3 ozsdk.py api-catalog --summary

# Lọc chỉ nhóm ai hoặc cli_bridge (46 hàm)
python3 ozsdk.py api-catalog --resource ai
python3 ozsdk.py api-catalog --group cli_bridge
```

---

## 10. Đóng gói, Ký số Ed25519, SBOM & Kiểm thử Tự động

```bash
# Kiểm toán bảo mật tĩnh
python3 ozsdk.py audit ./my-addon

# Xuất hóa đơn phần mềm SBOM JSON
python3 ozsdk.py sbom ./my-addon --out ./dist/addon_9010.sbom.json

# Đóng gói có chữ ký Ed25519
python3 ozsdk.py pack ./my-addon --out ./dist/addon_9010.ozaddon --sign-key ./keys/publisher-private.pem

# Đóng gói dạng 1 tệp Bash wrapper (.sh) kế thừa
python3 ozsdk.py pack ./my-addon --out ./dist/addon_9010.sh --sign-key ./keys/publisher-private.pem --legacy

# Chạy toàn bộ bộ unit test SDK 5.0.0 (Rev 9.1.4)
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 11. Xuất bản lên Kho Tiện ích `[15]` hoặc GitHub Raw URL

1. **Phân phối trực tiếp qua GitHub Raw URL:**
   - Đẩy `addon_<ID>.ozaddon`, `addon_<ID>.ozaddon.sha256` và `publisher-public.pem` lên nhánh `main` của repo public.
   - Người dùng dán thẳng URL `https://raw.githubusercontent.com/<owner>/<repo>/main/addon_<ID>.ozaddon` vào **SSH `[15] → [6]`** hoặc **Web GUI `[27] → [15]` (`addon.sdk_import_url`)**.
2. **Xuất bản lên Kho Chính thức OZPanel Store:**
   - Tạo payload chuẩn API & SQL bằng `python3 ozsdk.py store-payload <dir> --download-url https://...` và kiểm tra 10 trường `catalog.txt` bằng `ozsdk.py catalog`.

---

## 12. Checklist Kiểm duyệt trước khi phát hành

- [ ] `python3 ozsdk.py validate <dir>` đạt **0 lỗi**
- [ ] `python3 ozsdk.py audit <dir>` trả về `compatible: true`
- [ ] Đủ 5 lifecycle hooks idempotent (`install`, `upgrade`, `health`, `rollback`, `uninstall`)
- [ ] Hỗ trợ chạy không tương tác `OZ_GUI_FORM=1` & `OZ_ACTION_KEY` trên Web GUI `[27]`
- [ ] Không chứa mật khẩu/private key, không symlink thoát thư mục, không tải mã chưa kiểm SHA-256
- [ ] Đã ký Ed25519 (`manifest.sig`), kèm `.sha256` và `publisher-public.pem` để người dùng xác minh
