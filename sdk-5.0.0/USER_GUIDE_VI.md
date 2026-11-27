# Hướng dẫn Sử dụng Addon (Tiện ích Mở rộng) — Dành cho Người dùng OZPanel v9.1.4

> **Áp dụng cho:** OZPanel Linux v9.1.4+ (Ubuntu 18.04–26.04 · Debian 10–14 · AlmaLinux/Rocky/RHEL/CentOS-Stream/Oracle/CloudLinux 7–10)  
> **Quản lý qua:** Menu SSH `[15] Kho tiện ích` · Web Admin GUI `[27]` (`[15]` SDK Workbench) · Trợ lý AI DevOps `[32]`

---

## 1. Addon trên OZPanel là gì?

**Addon (Tiện ích mở rộng)** là các mô-đun chức năng độc lập chuẩn **SDK 5.0.0** giúp mở rộng OZPanel (tự động hóa, bảo mật, giám sát, tích hợp bên thứ ba...) mà **không can thiệp vào lõi hệ thống `OZV8-Fortress+`**.

Mỗi Addon chuẩn `.ozaddon` đều được:
- Kiểm tra toàn vẹn **SHA-256** cho mọi tệp trước khi giải nén và chặn tuyệt đối path traversal / symlink.
- Xác thực **chữ ký số Ed25519** (`manifest.sig`) khi nhà phát triển được tin cậy (`sdk-trust/<publisher>/public.pem`).
- Lưu dữ liệu cấu hình tách biệt trong thư mục riêng (`chmod 700`) và hỗ trợ **khôi phục (Rollback) / tự động cách ly** khi gặp lỗi.

---

## 2. Mở Trung tâm Quản lý Addon `[15]`

### Cách 1: Qua SSH Terminal
1. Kết nối SSH vào VPS và gõ lệnh:
   ```bash
   oz
   ```
2. Chọn mục **`15`** (**Quản lý Kho Tiện ích**).

### Cách 2: Qua Web Admin GUI `[27]`
1. Đăng nhập giao diện **Web GUI OZPanel** (cổng `8443`, dùng link SSO 1-Click hoặc tài khoản quản trị).
2. Chọn nhóm **`[15] Kho tiện ích`**.
3. Bạn có thể thao tác trực tiếp bằng form nút bấm cho toàn bộ vòng đời Addon:
   - **`addon.sdk_list`**: Xem tất cả Addon đã cài, các thao tác Workbench và trạng thái SDK Runtime (`/usr/local/lib/ozpanel/sdk`).
   - **`addon.sdk_import_url`**: Cài trực tiếp gói `.ozaddon` hoặc `.sh` từ URL HTTPS (tùy chọn kiểm tra SHA-256).
   - **`addon.sdk_run`**: Khởi chạy Addon / thực thi từng nút Workbench (`OZ_ACTION_KEY`) trực tiếp trên trình duyệt.
   - **`addon.sdk_health`**: Kiểm tra toàn vẹn SHA-256 và chạy `hooks/health.sh`.

### Cách 3: Qua Trợ lý AI DevOps `[32]` hoặc MCP Server
Bạn có thể nhắn tự nhiên trên Telegram / Zalo / Web GUI `[32]` hoặc qua Claude/Codex/Gemini CLI (đã cài sẵn qua `register_mcp_v914.sh`):
- `"kiểm tra sức khỏe hệ thống và danh sách addon"`
- `"chạy kiểm tra cấu hình nginx qua config surgeon"`

---

## 3. Các thao tác hàng ngày trên Menu SSH `[15]`

| Phím | Chức năng | Khi nào dùng |
| :---: | :--- | :--- |
| **`1`** | **Tải xuống Addon / Nhập License** | Cài Addon chính thức từ Kho OZPanel theo số `ID`. Nếu là Addon trả phí, hệ thống sẽ hỏi nhập mã License Key. |
| **`2`** | **Cập nhật Addon** | Khi cột Trạng thái báo có phiên bản mới; cấu hình cũ trong `addon-data` được bảo toàn qua hook `upgrade.sh`. |
| **`3`** | **Khởi chạy Addon đã tải** | Mở giao diện/menu của Addon (hỗ trợ cả `.ozaddon`, `.sh` và `.bin`). |
| **`4`** | **Gỡ cài đặt / Xóa License** | Gỡ sạch Addon (tự động chạy `hooks/uninstall.sh` cho gói `.ozaddon` và giữ lại dữ liệu/log an toàn). |
| **`5`** | **Làm mới danh sách Chợ** | Đồng bộ danh mục Addon mới nhất từ Kho. |
| **`6`** | **Thêm Addon nội bộ từ URL** | Cài trực tiếp `.ozaddon`, `.sh` hoặc `.bin` từ link **GitHub Raw** (`https://raw.githubusercontent.com/...`) hoặc máy chủ riêng (tự cấp ID `900000+`). |
| **`7`** | **Xem nhật ký lỗi / chạy theo ID** | Đọc JSONL log (`logs/<ID>.jsonl`) khi cần chẩn đoán lỗi. |
| **`8`** | **Xem / Khôi phục Addon bị cách ly** | Nếu Addon lỗi 3 lần liên tiếp hoặc hỏng chữ ký, OZPanel tự cách ly — bạn có thể kiểm tra và khôi phục tại đây. |

---

## 4. Cài đặt Addon `.ozaddon` từ GitHub Raw URL

Nếu nhà phát triển gửi cho bạn tệp `.ozaddon` hoặc link GitHub Raw:

1. Mở `oz` → chọn **`15`** → chọn **`6) Thêm addon nội bộ từ URL`** (hoặc dùng **`addon.sdk_import_url`** trên Web GUI `[27]`).
2. Dán đường dẫn HTTPS trực tiếp (khuyên dùng `https://raw.githubusercontent.com/<user>/<repo>/main/addon_9002.ozaddon`).
3. Chọn loại **`[3] Gói SDK (.ozaddon)`** (mục `[6]` tự gợi ý `[3]` nếu URL kết thúc bằng `.ozaddon`).
4. Hệ thống tự tải, giải nén an toàn, kiểm tra SHA-256 (+ Ed25519 nếu có trust pin), chạy `hooks/install.sh` và cấp ID tự động.
5. Chọn **`3) Khởi chạy Addon`** hoặc mở từ **Web GUI `[27] → [15]`**.

> **Mẹo xác minh bảo mật trước khi cài:**
> ```bash
> sha256sum -c addon_9002.ozaddon.sha256
> python3 /usr/local/lib/ozpanel/sdk/ozsdk.py verify addon_9002.ozaddon --pub-key publisher-demo-public.pem
> ```

---

## 5. Xử lý sự cố thường gặp (FAQ)

| Triệu chứng | Nguyên nhân & Cách xử lý nhanh |
| :--- | :--- |
| **Báo thiếu `/usr/local/lib/ozpanel/sdk/ozsdk.py`** | Chạy `cd /var/www/ozhub/html && bash build.sh` (bản v9.1.4 tự cài SDK Runtime), hoặc chạy `sudo python3 ozsdk.py runtime-install --confirm` từ thư mục SDK. |
| **Báo `min_panel_version` không tương thích** | Addon yêu cầu OZPanel mới hơn. Mở **`[44] Cập nhật hệ thống`** để nâng cấp OZPanel lên `v9.1.4`. |
| **Addon bị cách ly / sai chữ ký** | Mở **`[15] → [7]`** xem log chi tiết, xác minh lại SHA-256, rồi dùng **`[15] → [8]`** để khôi phục. |
| **Lỗi tải URL từ GitHub Release bị redirect** | Dùng URL **`https://raw.githubusercontent.com/...`** trực tiếp thay cho link `/releases/download/...`. |
| **Muốn cập nhật giao diện Web GUI `[27]` sau khi cài Addon** | Bấm nút tải lại trang trên Web GUI hoặc chạy `systemctl restart ozon-gui`. |

---

## 6. Kênh Hỗ trợ Chính thức

- **Kho công khai OZPanel Linux:** https://github.com/chuongminhofficial/ozPanel
- **Kho công khai OZPanel Windows:** https://github.com/chuongminhofficial/ozPanel-win
- **Phát triển bởi:** Chương Minh Studio
