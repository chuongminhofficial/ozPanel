<div align="center">

# ⚡ OZPanel Cloud & OzonFS — v9.1.2

**Next-Generation Linux Control Panel · Standalone WHM Web Admin GUI · Autonomous AI DevOps Engineer · 830+ Enterprise REST API Endpoints**

[![Version](https://img.shields.io/badge/version-v9.1.2-2563eb?style=for-the-badge)](https://github.com/chuongminhofficial/ozPanel/releases/latest)
[![Platform](https://img.shields.io/badge/Linux-x86__64%20%7C%20ARM64-10b981?style=for-the-badge)](https://github.com/chuongminhofficial/ozPanel/releases/latest)
[![Security](https://img.shields.io/badge/Security-OZV7--Fortress%20Ed25519-f59e0b?style=for-the-badge)](SECURITY.md)
[![Modules](https://img.shields.io/badge/Modules-46%20Groups%20%C2%B7%20290%2B%20Actions-7c3aed?style=for-the-badge)](docs/FEATURES.md)
[![API](https://img.shields.io/badge/OpenAPI%203.1-830%20Endpoints-0ea5e9?style=for-the-badge)](docs/FEATURES.md)

*Phát triển bởi **Chương Minh® Studio** · Commercial Production Edition*

</div>

---

## Tổng quan (Overview)

**OZPanel v9.1.2** là nền tảng quản trị máy chủ Linux toàn diện (Ubuntu / Debian / AlmaLinux / Rocky / CentOS / RHEL — hỗ trợ **x86_64 & ARM64**), kết hợp **46 nhóm chức năng cốt lõi**, giao diện **Web Admin GUI `[27]` độc lập chuẩn WHM**, cổng **Enterprise API Gateway `[31]` chuẩn OpenAPI 3.1 (830 endpoints)**, trình quản lý tệp & IDE **OzonFS `[5]`**, và **Kỹ sư Trưởng AI DevOps 24/7 `[32]`** tích hợp **6-Tool MCP Server** cho Claude Code CLI & OpenAI Codex CLI.

---

## Cài đặt nhanh 1 dòng (Quick Install)

Yêu cầu: Máy chủ Linux (`root` / `sudo`), kiến trúc `x86_64` hoặc `ARM64`.

```bash
curl -fsSL https://github.com/chuongminhofficial/ozPanel/releases/latest/download/install.sh | sudo bash
```

Hoặc tải trực tiếp từ **GitHub Releases** kèm xác thực toàn vẹn SHA-256 & chữ ký số Ed25519:

```bash
curl -fsSLO https://github.com/chuongminhofficial/ozPanel/releases/latest/download/install.sh
curl -fsSLO https://github.com/chuongminhofficial/ozPanel/releases/latest/download/install.sh.sha256
sha256sum -c install.sh.sha256 && sudo bash install.sh
```

Sau khi cài đặt hoàn tất, mở Control Panel bằng lệnh:
```bash
oz
```

---

## Điểm nổi bật phiên bản v9.1.2

| Trụ cột | Tính năng nổi bật |
| :--- | :--- |
| **🖥️ Web Admin GUI `[27]` (WHM Độc lập)** | Thao tác 100% độc lập trên trình duyệt (46/46 live telemetry, 312/312 hành động backend thật, không phụ thuộc CLI), tích hợp sẵn **AI DevOps Console**, **API Gateway Studio**, **Live Resource Monitor**, **Load Balancer Studio**, **Backup Vault**, và **1-Click SSO**. |
| **🤖 Kỹ sư AI DevOps `[32]` & MCP** | Hiểu & thực thi đủ **46 nhóm × 290+ hàm con**; hỗ trợ **Đa tác vụ DAG** (*VD: thêm domain ➔ đẩy Cloudflare Proxy Xám/Cam ➔ xin SSL ➔ cân bằng tải ➔ quét virus*); tự động gia hạn SSL (<14 ngày), tự dọn đĩa (>=85%), tự hồi phục dịch vụ và gửi **Báo cáo Ca trực Hạ tầng** định kỳ qua Zalo / Telegram / Slack / WhatsApp / Discord. |
| **🔌 Enterprise API Gateway `[31]`** | Viết bằng Go hiệu năng cao với **830 operations / 118 resources**, chuẩn **OpenAPI 3.1**, Bearer Token phân quyền RBAC/Scope, IP ACL, Rate Limiting, Async Operations, và Interactive Swagger UI. |
| **🌐 Webserver & App Hosting** | Hỗ trợ **Nginx, OpenLiteSpeed, Apache2, Multi (Nginx ➔ OLS)**; PHP 7.4–8.5; **Node.js `[14]`**, **Go Auto-Build `[23]`**, **Python ASGI/WSGI `[24]`**, **Docker & Compose Studio `[10]`**, **Reverse Proxy `[22]`**, **L7 Load Balancer `[33]`**. |
| **📁 OzonFS `[5]` & Database `[4]`** | Trình quản lý tệp thương mại hỗ trợ RTL, Anti-Hotlink DMCA Shield, VS Code Web Runtime; quản trị **MariaDB/MySQL, PostgreSQL, MongoDB** kèm **AdminNeo 1-Click SSO**. |
| **🛡️ Bảo mật OZV7-Fortress** | Nhị phân ELF ký số **Ed25519** chống rollback đơn điệu, Firewall UFW/Fail2Ban `[13]`, ClamAV + Heuristic Webshell Scanner `[17]`, Immutable Folders `chattr +i` `[35]`, WAF ModSecurity `[36]`, Cloudflare Anti-DDoS `[38]`. |

---

## Xác thực tính toàn vẹn gói phát hành (Release Verification)

Mọi bản phát hành trong [GitHub Releases](https://github.com/chuongminhofficial/ozPanel/releases) đều đi kèm:
- `release.manifest.json` — Danh sách tệp, kích thước byte chính xác, mã băm SHA-256 và số thứ tự `sequence` chống hạ cấp (anti-rollback).
- `release.manifest.sig` — Chữ ký số **Ed25519 (64-byte)** do Publisher ký.
- `*.sha256` — Mã băm SHA-256 riêng cho từng binary (`oz_installer_vi`, `oz_installer_vi-arm64`, `install.sh`).

Xem chi tiết 46 nhóm tính năng tại [docs/FEATURES.md](docs/FEATURES.md) và chính sách bảo mật tại [SECURITY.md](SECURITY.md).

---

<div align="center">
Copyright © Chương Minh® Studio. All rights reserved.
</div>
