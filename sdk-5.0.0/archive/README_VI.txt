OZPanel Addon Developer Kit — tài liệu hợp nhất

CẤU TRÚC
- OZPanel_Addon_Developer_Guide_Complete_7.2.0_SDK_1.0.0.html: tài liệu HTML độc lập, mở bằng trình duyệt; có tìm kiếm, sáng/tối, sao chép code, in/PDF và tải addon mẫu.
- examples/classic/addon_demo_9001.sh: addon Bash an toàn để học hợp đồng legacy của hàm [15].
- examples/sdk/manifest.example.json: template manifest theo tài liệu SDK 1.0.0; không phải manifest đã được pack/ký.
- examples/classic/catalog-row.example.txt: ví dụ 10 trường catalog.

LƯU Ý PHẠM VI
Tệp được người dùng gửi gồm hai tài liệu HTML và oz_v7.2.0.sh; chưa có mã nguồn SDK thực tế (ozsdk.py, lib/, tests/). Vì vậy ZIP này hợp nhất tài liệu và cung cấp ví dụ mẫu, không giả lập hay thay thế bằng một SDK khác. Các lệnh ozsdk.py chỉ dùng được khi bạn có bộ SDK chính thức đầy đủ.

BẮT ĐẦU
1. Mở tài liệu HTML.
2. Với addon classic: bash -n examples/classic/addon_demo_9001.sh
3. Xem hướng dẫn mục 04 và cài ở VPS thử nghiệm.
4. Đổi ID, publisher, license, quyền và thông tin metadata trước khi phát hành.
5. Không dùng ID 9001 cho sản phẩm thật.

CẢNH BÁO AN TOÀN
Addon thường chạy bằng quyền root. Chỉ cài nguồn tin cậy, kiểm SHA256/chữ ký qua kênh độc lập, test trên staging, backup cấu hình/dữ liệu và không ghi token/license/password vào log.
