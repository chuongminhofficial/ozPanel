#!/usr/bin/env bash
# OZPanel v9.1.4 (OZV8-Fortress+ · OZV7-Fortress · OZV6-ZeroTrust · OZV5-Shield) Classic Addon Example — ID 9001 — v5.0.0
# Dùng để học và thử nghiệm; đổi ID trước khi phát hành thật.
set -Eeuo pipefail
umask 077

ADDON_ID=9001
ADDON_VERSION='5.0.0'
ROOT_DIR="${OZON_ROOT_DIR:-/etc/ozon}"
ADDON_DIR="${OZON_ADDON_DIR:-$ROOT_DIR/addons}"
STATE_DIR="$ROOT_DIR/addon-data/$ADDON_ID"

fail() { printf '[ERROR] %s\n' "$*" >&2; }
prepare() {
  if [[ "$(id -u)" -ne 0 ]] && [[ "$ROOT_DIR" == "/etc/ozon" ]]; then
    fail 'Ví dụ này cần quyền quản trị khi dùng đường dẫn mặc định trong /etc/ozon.'
    return 1
  fi
  install -d -m 700 -- "$STATE_DIR"
  chmod 700 -- "$STATE_DIR"
}
show_info() {
  printf '\nOZPanel Addon Demo v%s (Core v9.1.4 · OZV8-Fortress+ · OzonFS v9.1.4)\n' "$ADDON_VERSION"
  printf 'Addon ID     : %s\n' "$ADDON_ID"
  printf 'Dữ liệu      : %s\n' "$STATE_DIR"
  printf 'GUI form     : %s\n' "${OZ_GUI_FORM:-0}"
  printf 'Native Enroll: %s\n' "$( [[ -f "$ROOT_DIR/native/enrolled" ]] && echo "Đã đăng ký v3" || echo "Chưa đăng ký" )"
  printf 'Cloud Lease  : %s\n' "$( [[ -f "$ROOT_DIR/native/runtime.lease" ]] && echo "Đã niêm phong 72-byte (OZV8-Fortress+ 6h TTL)" || echo "Chưa có lease" )"
  if [[ -x /usr/bin/oz ]]; then
    /usr/bin/oz --health-json 2>/dev/null || true
    printf '\n'
  fi
  uname -a || true
  df -h / || return 1
}
check_mail_status() {
  if [[ -x /usr/bin/oz ]]; then
    /usr/bin/oz --local-ops mail-cli status 2>/dev/null || printf 'Chưa kích hoạt Máy chủ thư [9] trên máy chủ này.\n'
  else
    printf 'Không tìm thấy /usr/bin/oz (môi trường thử nghiệm độc lập).\n'
  fi
}
save_note() {
  local note="${OZ_INPUT_NOTE:-}" tmp
  if [[ -z "$note" ]] && [[ "${OZ_GUI_FORM:-0}" != "1" ]]; then
    read -r -p 'Nhập ghi chú (không nhập mật khẩu/secret): ' note || return 1
  fi
  note="${note:-OZPanel v9.1.4 Addon 9001 OK}"
  tmp="$(mktemp "$STATE_DIR/.note.XXXXXX")"
  if ! printf '%s\n' "$note" > "$tmp"; then
    rm -f -- "$tmp"
    return 1
  fi
  chmod 600 -- "$tmp"
  if ! mv -f -- "$tmp" "$STATE_DIR/note.txt"; then
    rm -f -- "$tmp"
    return 1
  fi
  printf 'Đã lưu ghi chú tại %s/note.txt\n' "$STATE_DIR"
}
show_note() {
  if [[ -f "$STATE_DIR/note.txt" ]]; then
    cat -- "$STATE_DIR/note.txt"
  else
    printf 'Chưa có ghi chú. Chọn mục 3 để tạo.\n'
  fi
}
main() {
  local choice
  prepare || return 1
  if [[ "${OZ_GUI_FORM:-0}" == "1" ]]; then
    case "${OZ_ACTION_KEY:-1}" in
      1) show_info || fail 'Không đọc được thông tin.' ;;
      2) check_mail_status ;;
      3) save_note || fail 'Không lưu được ghi chú.' ;;
      4) show_note ;;
      *) show_info ;;
    esac
    return 0
  fi
  while true; do
    printf '\n=== OZPanel v9.1.4 (OZV8-Fortress+) Sample Addon · ID #%s · v%s ===\n' "$ADDON_ID" "$ADDON_VERSION"
    printf '[1] Xem thông tin hệ thống, oz --health-json & trạng thái OZV8-Fortress+\n'
    printf '[2] Kiểm tra trạng thái Mail Server Chống Spam [9]\n'
    printf '[3] Lưu ghi chú thử nghiệm an toàn (0600)\n'
    printf '[4] Đọc ghi chú đã lưu\n'
    printf '[0] Quay lại OZPanel\n'
    read -r -p 'Lựa chọn: ' choice || return 0
    case "$choice" in
      1) show_info || fail 'Không đọc được thông tin.' ;;
      2) check_mail_status ;;
      3) save_note || fail 'Không lưu được ghi chú.' ;;
      4) show_note ;;
      0) return 0 ;;
      *) printf 'Lựa chọn không hợp lệ; hãy chọn 0, 1, 2, 3 hoặc 4.\n' ;;
    esac
  done
}
main "$@"
