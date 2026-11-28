<div align="center">

# ⚡ OZPanel Cloud & OzonFS — v9.1.4

**Next-Generation Linux Control Panel · Standalone Web Admin GUI · Autonomous AI DevOps Engineer · 932 Enterprise REST API Operations · Addon SDK 5.0.0**

[![Version](https://img.shields.io/badge/version-v9.1.4-2563eb?style=for-the-badge)](https://github.com/chuongminhofficial/ozPanel)
[![Platform](https://img.shields.io/badge/Linux-x86__64%20%7C%20ARM64-10b981?style=for-the-badge)](https://github.com/chuongminhofficial/ozPanel)
[![Security](https://img.shields.io/badge/Security-OZV8--Fortress%2B%20Ed25519-f59e0b?style=for-the-badge)](SECURITY.md)
[![Modules](https://img.shields.io/badge/Modules-46%20Groups%20%C2%B7%20312%2B%20Actions-7c3aed?style=for-the-badge)](docs/FEATURES.md)
[![API](https://img.shields.io/badge/OpenAPI%203.1-932%20Operations-0ea5e9?style=for-the-badge)](docs/FEATURES.md)

*Phát triển bởi **Chương Minh® Studio** · Commercial Production Edition*

</div>

---

## Tổng quan (Overview)

**OZPanel v9.1.4** là nền tảng quản trị máy chủ Linux tốc độ Native (Ubuntu / Debian / AlmaLinux / Rocky / CentOS / RHEL — hỗ trợ **x86_64 & ARM64**), kết hợp **46 nhóm chức năng cốt lõi**, giao diện **Web Admin GUI `[27]` hoạt động độc lập 100% không phụ thuộc CLI**, cổng **Enterprise API Gateway `[31]` chuẩn OpenAPI 3.1 (932 operations / 125 resources)**, trình quản lý tệp & IDE **OzonFS `[5]`**, **Kỹ sư Trưởng AI DevOps tự hành `[32]`** tích hợp **8-Tool MCP Server**, và bộ phát triển mở rộng **OZPanel Addon SDK 5.0.0** ký số Ed25519.

---

## Cài đặt nhanh 1 dòng trực tiếp qua GitHub Raw (Direct Raw Install)

Yêu cầu: Máy chủ Linux (`root` / `sudo`), kiến trúc `x86_64` hoặc `ARM64`.

```bash
curl -fsSL https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh | sudo OZ_RELEASE_BASE_URL="https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main" bash
```

Hoặc tải về và tự xác minh mã băm SHA-256 trước khi chạy:

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

| Tệp thành phẩm | Kiến trúc / Vai trò | Link tải trực tiếp (Direct Raw URL) | SHA-256 |
| :--- | :--- | :--- | :--- |
| `install.sh` | Trình cài đặt & xác thực chữ ký Ed25519 tự động | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh` | `855a9691e4bb4c9772bb9ecc1d8c759dfd3f4f2199a46d25a55cd90ad6b510a6` |
| `oz_installer_vi` | Binary Native Launcher (`Linux x86_64 / amd64`) | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi` | `1ff1f6dcc491cf8a61fbba385123308a279624661d12d9d2d6e17e5c05f9f1f6` |
| `oz_installer_vi-arm64` | Binary Native Launcher (`Linux ARM64 / aarch64`) | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi-arm64` | `f6d39e4a174530f1b7f2177af08d456e51ea9163bd78499e1c6b990d57bd2515` |
| `release.manifest.json` | Manifest kích thước, SHA-256 & `sequence` chống rollback | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/release.manifest.json` | — |
| `release.manifest.sig` | Chữ ký số **Ed25519 (64-byte)** của Publisher | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/release.manifest.sig` | — |
| `oz_installer_vi.sha256` | Checksum SHA-256 cho bản `x86_64` | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi.sha256` | — |
| `oz_installer_vi-arm64.sha256` | Checksum SHA-256 cho bản `ARM64` | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/oz_installer_vi-arm64.sha256` | — |
| `install.sh.sha256` | Checksum SHA-256 cho `install.sh` | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/install.sh.sha256` | — |
| `version.txt` | Phiên bản phát hành hiện hành (`9.1.4`) | `https://raw.githubusercontent.com/chuongminhofficial/ozPanel/main/version.txt` | — |

---

## Điểm nổi bật phiên bản v9.1.4

| Trụ cột | Tính năng nổi bật |
| :--- | :--- |
| **🖥️ Web Admin GUI `[27]` (Độc lập 100% CLI)** | Hoạt động độc lập hoàn toàn với giao diện OZM Studio cao cấp, bảng lệnh nhanh `Ctrl+K`, đầy đủ nút thao tác / biểu mẫu / input cho toàn bộ nghiệp vụ, ma trận sức khỏe dịch vụ thời gian thực, Terminal (`Quick Exec` & `Live PTY`), **AI DevOps Studio**, **API Live Tester**, **Load Balancer Studio**, **Backup Vault** và **1-Click SSO**. |
| **🤖 Kỹ sư AI DevOps `[32]` & 8-Tool MCP** | Thực thi tự động các yêu cầu phức tạp trong **1 prompt duy nhất**, đọc sâu file cấu hình & log để chẩn đoán/sửa lỗi hệ thống, tối ưu gom ngữ cảnh giảm tối đa request AI API, cảnh báo khẩn theo độ tải (không spam), và chuẩn hóa **8-Tool MCP Server** (`register_mcp_v914.sh`). |
| **🔌 Enterprise API Gateway `[31]`** | Viết bằng Go hiệu năng cao với **932 operations / 125 resources**, chuẩn **OpenAPI 3.1**, điều phối chuỗi `panel:batch` & `panel:dag`, tích hợp app & bên thứ ba (Cloudflare/SSL/DB/Trash/Systemd/IAM RBAC). |
| **🧩 Addon Store `[15]` & SDK 5.0.0** | Bộ công cụ công khai tại [`sdk-5.0.0/`](sdk-5.0.0/) kèm [tài liệu hướng dẫn SDK 5.0.0](sdk-5.0.0/GUIDE_9.1.4_SDK_5.0.0.html) và mẫu addon ký số Ed25519 (`addon_9002.ozaddon`). |
| **🛡️ Bảo mật OZV8-Fortress+ & Anti-RE** | Ký số **Ed25519** chống hạ cấp (`sequence: 1795816267586`), tách miền khóa độc lập `HMAC-SHA256`, mã hóa module không lưu khóa/S-Box rõ trên đĩa, xóa trắng FD bộ nhớ `<1.5ms`, chống hook/trace thời gian thực, giảm tải xác thực về License Server. |
| **⚡ Hiệu năng Native & SSO Mượt mà** | Mở `oz` & link SSO phản hồi tức thì, cơ chế *Stale-While-Revalidate* telemetry, streaming log `O(1)`, cắt giảm request đồng bộ nền về máy chủ trung tâm. |

---

## Xác thực tính toàn vẹn gói phát hành (Release Verification)

Mọi bản phát hành trên nhánh `main` và [GitHub Releases](https://github.com/chuongminhofficial/ozPanel/releases) đều đi kèm:
- `release.manifest.json` — Danh sách tệp, kích thước byte chính xác, mã băm SHA-256 và số thứ tự `sequence` chống hạ cấp (anti-rollback).
- `release.manifest.sig` — Chữ ký số **Ed25519 (64-byte)** do Publisher ký.
- `*.sha256` — Mã băm SHA-256 riêng cho từng binary (`oz_installer_vi`, `oz_installer_vi-arm64`, `install.sh`).

Xem chi tiết 46 nhóm tính năng tại [docs/FEATURES.md](docs/FEATURES.md) và chính sách bảo mật tại [SECURITY.md](SECURITY.md).

---
[![M8ven Score](https://m8ven.ai/badge/mcp/chuongminhofficial-ozpanel-wvnans?v=b1c90daffaa5afcec0d5ff00247e098f)](https://m8ven.ai/mcp/chuongminhofficial-ozpanel-wvnans?s=readme)
<div align="center">
Copyright © Chương Minh® Studio. All rights reserved.
</div>
