<div align="center">

# ⚡ OZPanel Cloud & OzonFS — v9.1.2

**Next-Generation Linux Control Panel · Standalone Web Admin GUI · Autonomous AI DevOps Engineer · 854 Enterprise REST API Endpoints**

[![Version](https://img.shields.io/badge/version-v9.1.2-2563eb?style=for-the-badge)](https://github.com/chuongminhofficial/ozPanel)
[![Platform](https://img.shields.io/badge/Linux-x86__64%20%7C%20ARM64-10b981?style=for-the-badge)](https://github.com/chuongminhofficial/ozPanel)
[![Security](https://img.shields.io/badge/Security-OZV8--Fortress%20Ed25519-f59e0b?style=for-the-badge)](SECURITY.md)
[![Modules](https://img.shields.io/badge/Modules-46%20Groups%20%C2%B7%20312%2B%20Actions-7c3aed?style=for-the-badge)](docs/FEATURES.md)
[![API](https://img.shields.io/badge/OpenAPI%203.1-854%20Endpoints-0ea5e9?style=for-the-badge)](docs/FEATURES.md)

*Phát triển bởi **Chương Minh® Studio** · Commercial Production Edition*

</div>

---

## Tổng quan (Overview)

**OZPanel v9.1.2** là nền tảng quản trị máy chủ Linux tốc độ Native (Ubuntu / Debian / AlmaLinux / Rocky / CentOS / RHEL — hỗ trợ **x86_64 & ARM64**), kết hợp **46 nhóm chức năng cốt lõi**, giao diện **Web Admin GUI `[27]` hoạt động độc lập 100% không phụ thuộc CLI**, cổng **Enterprise API Gateway `[31]` chuẩn OpenAPI 3.1 (854 endpoints / 119 resources)**, trình quản lý tệp & IDE **OzonFS `[5]`**, và **Kỹ sư Trưởng AI DevOps tự hành `[32]`** tích hợp **7-Tool MCP Server** cho Claude Code CLI, OpenAI Codex CLI, Gemini CLI & Ollama.

---

## Cài đặt nhanh 1 dòng trực tiếp qua GitHub Raw (Direct Raw Install)

Yêu cầu: Máy chủ Linux (`root` / `sudo`), kiến trúc `x86_64` hoặc `ARM64`.

```bash
curl -fsSL https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh | sudo OZ_RELEASE_BASE_URL="https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main" bash
```

Hoặc cài đặt qua CDN mặc định / GitHub Releases kèm kiểm tra băm SHA-256:

```bash
curl -fsSLO https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh
curl -fsSLO https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh.sha256
sha256sum -c install.sh.sha256 && sudo OZ_RELEASE_BASE_URL="https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main" bash install.sh
```

Sau khi cài đặt hoàn tất, mở Control Panel bằng lệnh:
```bash
oz
```

---

## Tải trực tiếp tệp thành phẩm dạng Raw (`raw.githubusercontent.com`)

Toàn bộ gói cài đặt nhị phân đã biên dịch và chữ ký số nằm trực tiếp trên nhánh `main` để tải thẳng bằng `curl` / `wget`:

| Tệp thành phẩm | Kiến trúc / Vai trò | Link tải trực tiếp (Direct Raw URL) |
| :--- | :--- | :--- |
| `install.sh` | Trình cài đặt & xác thực chữ ký Ed25519 tự động | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh` |
| `oz_installer_vi` | Binary Native Launcher (`Linux x86_64 / amd64`) | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi` |
| `oz_installer_vi-arm64` | Binary Native Launcher (`Linux ARM64 / aarch64`) | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi-arm64` |
| `release.manifest.json` | Manifest kích thước, SHA-256 & `sequence` chống rollback | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/release.manifest.json` |
| `release.manifest.sig` | Chữ ký số **Ed25519 (64-byte)** của Publisher | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/release.manifest.sig` |
| `oz_installer_vi.sha256` | Checksum SHA-256 cho bản `x86_64` | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi.sha256` |
| `oz_installer_vi-arm64.sha256` | Checksum SHA-256 cho bản `ARM64` | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi-arm64.sha256` |
| `version.txt` | Phiên bản phát hành hiện hành (`9.1.2`) | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/version.txt` |

---

## Điểm nổi bật phiên bản v9.1.2

| Trụ cột | Tính năng nổi bật |
| :--- | :--- |
| **🖥️ Web Admin GUI `[27]` (Độc lập 100% CLI)** | Hoạt động độc lập hoàn toàn với giao diện OZM Studio cao cấp, tìm kiếm lệnh nhanh `Ctrl+K`, ma trận sức khỏe dịch vụ thời gian thực, bộ chuyển đổi Terminal (`Quick Exec` & `Live PTY`), tích hợp sẵn **AI DevOps Studio**, **API Live Tester**, **Load Balancer Studio**, **Backup Vault**, và **1-Click SSO**. |
| **🤖 Kỹ sư AI DevOps `[32]` & 7-Tool MCP** | Thực thi tự động các yêu cầu khó, **đa tác vụ trong 1 prompt duy nhất** (*VD: thêm tên miền + đẩy Cloudflare Xám/Cam + cấp SSL + ép HTTPS; khôi phục file bị xóa 5 tầng + viết thêm file mới có kiểm tra cú pháp; kiểm tra sâu DNS/HTTP/SSL tên miền + rà soát toàn bộ API khả dụng*); chuẩn hóa **7-Tool MCP Server** và Báo cáo Ca trực Hạ tầng định kỳ (12h). |
| **🔌 Enterprise API Gateway `[31]`** | Viết bằng Go hiệu năng cao với **854 operations / 119 resources**, chuẩn **OpenAPI 3.1**, điều phối chuỗi `panel:batch` & `panel:dag`, quản trị Cloudflare/SSL/DB/Trash/Systemd/IAM RBAC không cần truy cập Terminal hay GUI. |
| **🌐 Webserver & App Hosting** | Hỗ trợ **Nginx, OpenLiteSpeed, Apache2, Multi (Nginx ➔ OLS)**; PHP 7.4–8.5; **Node.js `[14]`**, **Go Auto-Build `[23]`**, **Python ASGI/WSGI `[24]`**, **Docker & Compose Studio `[10]`**, **Reverse Proxy `[22]`**, **L7 Load Balancer `[33]`**, tự hồi phục **Pure-FTPd `[6]`**. |
| **🛡️ Bảo mật OZV8-Fortress & Anti-RE** | Ký số **Ed25519** chống hạ cấp, tách miền khóa độc lập `HMAC-SHA256`, mã hóa toàn bộ 43 module không lưu khóa/S-Box rõ trên đĩa, xóa trắng FD bộ nhớ `<1.5ms`, chống hook/trace thời gian thực, chặn SSRF & xác thực chặt Webhook ChatOps. |
| **⚡ Hiệu năng Native & Giảm >95% Request** | Khởi chạy CLI phản hồi tức thì (`<15ms`), cơ chế *Stale-While-Revalidate* telemetry, xử lý streaming log `O(1)` bộ nhớ, tự động xoay vòng `logrotate`, cắt giảm >95% lượng request đồng bộ nền về máy chủ trung tâm. |

---

## Xác thực tính toàn vẹn gói phát hành (Release Verification)

Mọi bản phát hành trên nhánh `main` và [GitHub Releases](https://github.com/chuongminhofficial/ozPanel/releases) đều đi kèm:
- `release.manifest.json` — Danh sách tệp, kích thước byte chính xác, mã băm SHA-256 và số thứ tự `sequence` chống hạ cấp (anti-rollback).
- `release.manifest.sig` — Chữ ký số **Ed25519 (64-byte)** do Publisher ký.
- `*.sha256` — Mã băm SHA-256 riêng cho từng binary (`oz_installer_vi`, `oz_installer_vi-arm64`, `install.sh`).

Xem chi tiết 46 nhóm tính năng tại [docs/FEATURES.md](docs/FEATURES.md) và chính sách bảo mật tại [SECURITY.md](SECURITY.md).

---

<div align="center">
Copyright © Chương Minh® Studio. All rights reserved.
</div>
