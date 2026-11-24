#!/usr/bin/env bash
# ==============================================================================
# OZPanel 9.1.3 (OZV8-Fortress) — Signed Native Bootstrap & Atomic Updater
# ==============================================================================
# - Acquires /etc/ozon/native/release.lock BEFORE any state read or mutation.
# - Preserves /etc/ozon/native/revoked.lock, /etc/ozon/native/runtime.lease, and
#   pinned public keys (*.pub.pem) during --native-check or when update fails.
# - Stages trust pins in $STAGE, verifies manifest Ed25519 signature, enforces
#   monotonic anti-rollback (manifest.sequence >= accepted release.sequence),
#   and verifies artifact size + SHA-256 + --native-check BEFORE touching disk.
# - Commits binary, trust pins, and release.sequence atomically under the same
#   flock with automatic rollback if installation is interrupted or fails.
# ==============================================================================
set -Eeuo pipefail
umask 077

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo "[ERROR] Cần quyền root (sudo)." >&2
    exit 1
fi

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

BASE_URL="${OZ_RELEASE_BASE_URL:-https://usercontent.chgm.in/ozpanel}"
NATIVE_DIR="${OZ_NATIVE_DIR:-/etc/ozon/native}"
CORE_API_DIR="${OZ_CORE_API_DIR:-/etc/ozon/core-api}"
TARGET_BIN="${OZ_TARGET_BIN:-/usr/bin/oz}"

case "${BASE_URL}" in
    https://*) ;;
    http://127.0.0.1:*|http://localhost:*|file://*)
        if [ "${OZ_ALLOW_LOCAL_TEST_URL:-0}" != "1" ]; then
            echo "[ERROR] URL phát hành phải dùng HTTPS." >&2
            exit 1
        fi
        ;;
    *)
        echo "[ERROR] URL phát hành phải dùng HTTPS." >&2
        exit 1
        ;;
esac

for d in "$(dirname "$NATIVE_DIR")" "$NATIVE_DIR" "$CORE_API_DIR"; do
    if [ -L "$d" ]; then
        echo "[ERROR] Đường dẫn cấu hình là symlink không an toàn: $d" >&2
        exit 1
    fi
done
mkdir -p -m 700 "$NATIVE_DIR" "$CORE_API_DIR"
chmod 700 "$NATIVE_DIR" "$CORE_API_DIR"

# 1. Acquire exclusive update lock BEFORE touching any state file
exec 9>"$NATIVE_DIR/release.lock"
if ! flock -w 60 9; then
    echo "[ERROR] Một tiến trình cài đặt hoặc cập nhật OZPanel khác đang chạy." >&2
    exit 1
fi
export OZ_NATIVE_RELEASE_LOCK_FD=9

ARCH="$(uname -m)"
case "$ARCH" in
    x86_64|amd64)
        ASSET="oz_installer_vi"
        MKEY="x86_64"
        ;;
    aarch64|arm64)
        ASSET="oz_installer_vi-arm64"
        MKEY="aarch64"
        ;;
    *)
        echo "[ERROR] Kiến trúc CPU chưa được hỗ trợ: $ARCH" >&2
        exit 1
        ;;
esac

for tool in curl openssl python3 sha256sum; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        if command -v apt-get >/dev/null 2>&1; then
            apt-get update -y >/dev/null 2>&1 && apt-get install -y curl openssl python3 coreutils ca-certificates >/dev/null 2>&1
        elif command -v dnf >/dev/null 2>&1; then
            dnf install -y curl openssl python3 coreutils ca-certificates >/dev/null 2>&1
        elif command -v yum >/dev/null 2>&1; then
            if grep -rq 'mirrorlist\.centos\.org' /etc/yum.repos.d/ 2>/dev/null; then
                sed -i 's/mirrorlist=/#mirrorlist=/g; s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g; s|#baseurl=https://mirror.centos.org|baseurl=https://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo 2>/dev/null || true
            fi
            yum install -y curl openssl python3 coreutils ca-certificates >/dev/null 2>&1
        elif command -v zypper >/dev/null 2>&1; then
            zypper --non-interactive install curl openssl python3 coreutils ca-certificates >/dev/null 2>&1
        elif command -v pacman >/dev/null 2>&1; then
            pacman -Sy --noconfirm curl openssl python coreutils ca-certificates >/dev/null 2>&1
        elif command -v apk >/dev/null 2>&1; then
            apk add --no-cache curl openssl python3 coreutils ca-certificates bash >/dev/null 2>&1
        fi
        break
    fi
done

STAGE="$(mktemp -d "$NATIVE_DIR/.stage-XXXXXX")"
BACKUP_DIR="$STAGE/backup"
mkdir -p -m 700 "$BACKUP_DIR"

ROLLBACK_NEEDED=0
restore_on_failure() {
    local rc=$?
    if [ "$ROLLBACK_NEEDED" -eq 1 ]; then
        echo "[WARN] Cài đặt bị gián đoạn hoặc thất bại (mã $rc); đang khôi phục trạng thái trước đó..." >&2
        if [ -f "$BACKUP_DIR/oz.bin" ]; then
            cp -pf "$BACKUP_DIR/oz.bin" "$STAGE/.oz.restore" && chmod 755 "$STAGE/.oz.restore" && mv -f "$STAGE/.oz.restore" "$TARGET_BIN" 2>/dev/null || true
        fi
        for pin in server.pub.pem release.pub.pem; do
            if [ -f "$BACKUP_DIR/$pin" ]; then
                cp -pf "$BACKUP_DIR/$pin" "$NATIVE_DIR/.$pin.restore" && chmod 600 "$NATIVE_DIR/.$pin.restore" && mv -f "$NATIVE_DIR/.$pin.restore" "$NATIVE_DIR/$pin" 2>/dev/null || true
            elif [ -f "$BACKUP_DIR/missing_$pin" ]; then
                rm -f "$NATIVE_DIR/$pin" 2>/dev/null || true
            fi
        done
        if [ -f "$BACKUP_DIR/core_public.pem" ]; then
            cp -pf "$BACKUP_DIR/core_public.pem" "$CORE_API_DIR/.public.pem.restore" && chmod 644 "$CORE_API_DIR/.public.pem.restore" && mv -f "$CORE_API_DIR/.public.pem.restore" "$CORE_API_DIR/public.pem" 2>/dev/null || true
        elif [ -f "$BACKUP_DIR/missing_core_public.pem" ]; then
            rm -f "$CORE_API_DIR/public.pem" 2>/dev/null || true
        fi
        if [ -f "$BACKUP_DIR/release.sequence" ]; then
            cp -pf "$BACKUP_DIR/release.sequence" "$NATIVE_DIR/.release.sequence.restore" && chmod 600 "$NATIVE_DIR/.release.sequence.restore" && mv -f "$NATIVE_DIR/.release.sequence.restore" "$NATIVE_DIR/release.sequence" 2>/dev/null || true
        elif [ -f "$BACKUP_DIR/missing_release.sequence" ]; then
            rm -f "$NATIVE_DIR/release.sequence" 2>/dev/null || true
        fi
    fi
    rm -rf "$STAGE" 2>/dev/null || true
    return "$rc"
}
trap 'restore_on_failure' EXIT

# 2. Stage candidate trust pins in $STAGE ONLY (never overwrite /etc/ozon before signature verification)
python3 - "$STAGE" <<'PY_STAGE_PINS'
import os, sys
from pathlib import Path

stage = Path(sys.argv[1])
pins = {
    stage / 'server.pub.pem': '''-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAf1dc9k+hWiw11sS2c5w8jr/I38s2+G1gbHGea/+M7c0=
-----END PUBLIC KEY-----
''',
    stage / 'release.pub.pem': '''-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAWGTxWyjPwzELenbpESxdnFG8prvoYKgCsBNXdj1M+xI=
-----END PUBLIC KEY-----
''',
}
for path, content in pins.items():
    path.write_text(content, encoding='utf-8')
    os.chmod(path, 0o600)
PY_STAGE_PINS

# Select verification public key: prefer existing pinned local release.pub.pem if present and valid;
# fall back to staged release.pub.pem only on fresh installation.
VERIFY_PUB="$STAGE/release.pub.pem"
if [ -f "$NATIVE_DIR/release.pub.pem" ] && [ ! -L "$NATIVE_DIR/release.pub.pem" ] && [ -s "$NATIVE_DIR/release.pub.pem" ]; then
    VERIFY_PUB="$NATIVE_DIR/release.pub.pem"
fi

# 3. Download manifest & signature into $STAGE and verify Ed25519 signature BEFORE reading fields
oz_secure_fetch() {
    local url="$1" dst="$2" max_t="${3:-60}"
    if [ "${OZ_ALLOW_LOCAL_TEST_URL:-0}" = "1" ]; then
        curl -fsSL --connect-timeout 10 --max-time "$max_t" "$url" -o "$dst"
    else
        curl -fsSL --proto '=https' --tlsv1.2 --connect-timeout 10 --max-time "$max_t" "$url" -o "$dst"
    fi
}

oz_secure_fetch "$BASE_URL/release.manifest.json" "$STAGE/release.manifest.json" 60
oz_secure_fetch "$BASE_URL/release.manifest.sig" "$STAGE/release.manifest.sig.b64" 60

if [ "$(wc -c < "$STAGE/release.manifest.sig.b64" | tr -d '[:space:]')" = "64" ]; then
    cp -f "$STAGE/release.manifest.sig.b64" "$STAGE/release.manifest.sig"
else
    openssl base64 -d -A -in "$STAGE/release.manifest.sig.b64" -out "$STAGE/release.manifest.sig" 2>/dev/null || \
        openssl base64 -d -in "$STAGE/release.manifest.sig.b64" -out "$STAGE/release.manifest.sig" || \
        cp -f "$STAGE/release.manifest.sig.b64" "$STAGE/release.manifest.sig"
fi

if ! openssl pkeyutl -verify -pubin -inkey "$VERIFY_PUB" -rawin \
    -in "$STAGE/release.manifest.json" -sigfile "$STAGE/release.manifest.sig" >/dev/null 2>&1; then
    echo "[ERROR] Chữ ký Ed25519 của release.manifest.json không hợp lệ! Giữ nguyên toàn bộ trạng thái hiện tại." >&2
    exit 1
fi

# 4. Validate manifest schema AND enforce monotonic anti-rollback against /etc/ozon/native/release.sequence
read -r EXPECTED_SHA EXPECTED_SIZE NEW_SEQ < <(python3 - "$STAGE/release.manifest.json" "$MKEY" "$ASSET" "$NATIVE_DIR/release.sequence" "${OZ_ALLOW_SAME_SEQUENCE:-1}" <<'PY_VERIFY_MANIFEST'
import json, re, sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
arch_key = sys.argv[2]
expected_asset = sys.argv[3]
seq_path = Path(sys.argv[4])
allow_same = sys.argv[5] == '1'

r = json.loads(manifest_path.read_text(encoding='utf-8'))
if r.get('product') not in ('ozpanel', 'ozpanel.native.release/1'):
    raise SystemExit('[ERROR] Manifest product không khớp ozpanel.')

new_seq = r.get('sequence')
if type(new_seq) is not int or new_seq < 1:
    raise SystemExit('[ERROR] Manifest sequence không hợp lệ.')

current_seq = 0
if seq_path.exists():
    if seq_path.is_symlink():
        raise SystemExit('[ERROR] release.sequence là symlink không an toàn.')
    raw_seq = seq_path.read_text(encoding='utf-8').strip()
    if not raw_seq.isdigit() or int(raw_seq) < 1:
        raise SystemExit('[ERROR] release.sequence cục bộ bị hỏng; từ chối ghi đè tự động.')
    current_seq = int(raw_seq)

if current_seq > 0:
    if new_seq < current_seq:
        raise SystemExit(f'[ERROR] Anti-rollback: manifest sequence ({new_seq}) thấp hơn release.sequence hiện tại ({current_seq}).')
    if not allow_same and new_seq == current_seq:
        raise SystemExit(f'[ERROR] Manifest sequence ({new_seq}) không mới hơn bản hiện tại ({current_seq}).')

sha = ''
size = 0
if isinstance(r.get('artifacts'), list):
    entry = next((x for x in r['artifacts'] if isinstance(x, dict) and x.get('file') == expected_asset), {})
    sha = entry.get('sha256', '')
    size = entry.get('size', 0)
else:
    entry = (r.get('arch') or {}).get(arch_key) or {}
    if entry.get('asset') != expected_asset:
        raise SystemExit('[ERROR] Tên asset trong manifest không khớp kiến trúc hiện tại.')
    sha = entry.get('sha256', '')
    size = entry.get('size', 0)
if not re.fullmatch(r'[0-9a-f]{64}', sha) or type(size) is not int or size < 4096:
    raise SystemExit('[ERROR] Thông tin sha256/size trong manifest không hợp lệ.')

print(sha, size, new_seq)
PY_VERIFY_MANIFEST
)

# 5. Download binary artifact and verify byte size + SHA-256 + --native-check BEFORE any state change
if [ "${OZ_ALLOW_LOCAL_TEST_URL:-0}" = "1" ]; then
    curl -fL --connect-timeout 15 --max-time 600 "$BASE_URL/$ASSET" -o "$STAGE/$ASSET"
else
    curl -fL --proto '=https' --tlsv1.2 --connect-timeout 15 --max-time 600 "$BASE_URL/$ASSET" -o "$STAGE/$ASSET"
fi

ACTUAL_SIZE="$(wc -c < "$STAGE/$ASSET" | tr -d '[:space:]')"
if [ "$ACTUAL_SIZE" != "$EXPECTED_SIZE" ]; then
    echo "[ERROR] Kích thước artifact không khớp manifest (nhận $ACTUAL_SIZE, cần $EXPECTED_SIZE)." >&2
    exit 1
fi
printf '%s  %s\n' "$EXPECTED_SHA" "$STAGE/$ASSET" | sha256sum -c - >/dev/null
chmod 700 "$STAGE/$ASSET"

# Run self-check on staged binary before touching system state
"$STAGE/$ASSET" --native-check

# 6. If invoked in read-only check/inspection mode, do NOT mutate release.sequence, pins, lease, or /usr/bin/oz
case "${1:-}" in
    --native-check|--version|-v|--release-metadata|--help|-h|--native-help)
        if [ "${1:-}" != "--native-check" ]; then
            "$STAGE/$ASSET" "$@"
        fi
        exit 0
        ;;
esac

# 7. Backup current state for atomic rollback if installation fails or is interrupted
if [ -f "$TARGET_BIN" ] && [ ! -L "$TARGET_BIN" ]; then
    cp -pf "$TARGET_BIN" "$BACKUP_DIR/oz.bin"
fi
for pin in server.pub.pem release.pub.pem; do
    if [ -f "$NATIVE_DIR/$pin" ]; then
        cp -pf "$NATIVE_DIR/$pin" "$BACKUP_DIR/$pin"
    else
        touch "$BACKUP_DIR/missing_$pin"
    fi
done
if [ -f "$CORE_API_DIR/public.pem" ]; then
    cp -pf "$CORE_API_DIR/public.pem" "$BACKUP_DIR/core_public.pem"
else
    touch "$BACKUP_DIR/missing_core_public.pem"
fi
if [ -f "$NATIVE_DIR/release.sequence" ]; then
    cp -pf "$NATIVE_DIR/release.sequence" "$BACKUP_DIR/release.sequence"
else
    touch "$BACKUP_DIR/missing_release.sequence"
fi

ROLLBACK_NEEDED=1

# 8. Commit trust pins atomically under the held lock so --native-install-only has verified pins
python3 - "$STAGE" "$NATIVE_DIR" "$CORE_API_DIR" <<'PY_COMMIT_PINS'
import os, shutil, sys
from pathlib import Path

stage, native_dir, core_dir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for name in ('server.pub.pem', 'release.pub.pem'):
    tmp = native_dir / ('.' + name + '.tmp')
    shutil.copyfile(stage / name, tmp)
    os.chmod(tmp, 0o600)
    os.replace(tmp, native_dir / name)

core_tmp = core_dir / '.public.pem.tmp'
shutil.copyfile(stage / 'server.pub.pem', core_tmp)
os.chmod(core_tmp, 0o600)
os.replace(core_tmp, core_dir / 'public.pem')
lic_file = core_dir.parent / 'license.key'
if lic_file.is_file() and not lic_file.is_symlink():
    try:
        os.chmod(lic_file, 0o600)
    except OSError:
        pass
PY_COMMIT_PINS

# 9. Install the verified binary (preserving existing runtime.lease and revoked.lock)
"$STAGE/$ASSET" --native-install-only
for _oz_sync_bin in /usr/local/bin/oz /usr/bin/ozon /usr/local/bin/aiagent /usr/bin/aiagent; do
    if [ -L "$_oz_sync_bin" ] || [ -f "$_oz_sync_bin" ] || [ "$_oz_sync_bin" = "/usr/local/bin/oz" ]; then
        rm -f -- "$_oz_sync_bin.tmp.$$" 2>/dev/null || true
        if cp -pf "$TARGET_BIN" "$_oz_sync_bin.tmp.$$" 2>/dev/null && chmod 755 "$_oz_sync_bin.tmp.$$" 2>/dev/null; then
            [ -L "$_oz_sync_bin" ] && rm -f -- "$_oz_sync_bin" 2>/dev/null || true
            mv -f "$_oz_sync_bin.tmp.$$" "$_oz_sync_bin" 2>/dev/null || rm -f -- "$_oz_sync_bin.tmp.$$" 2>/dev/null
        fi
    fi
done
rm -f /etc/ozon/.auto_synced_version /etc/ozon/.version-cache.json /etc/ozon/.menu_telemetry_620 2>/dev/null || true

# 10. Commit new release.sequence atomically ONLY after --native-install-only succeeded
python3 - "$NATIVE_DIR/release.sequence" "$NEW_SEQ" <<'PY_COMMIT_SEQ'
import os, sys, tempfile
from pathlib import Path

seq_file = Path(sys.argv[1])
new_seq = int(sys.argv[2])
fd, tmp = tempfile.mkstemp(prefix='.seq-', dir=str(seq_file.parent))
try:
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(f'{new_seq}\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, seq_file)
finally:
    if os.path.exists(tmp):
        os.unlink(tmp)
PY_COMMIT_SEQ

# Transaction committed cleanly
ROLLBACK_NEEDED=0

if [ -d /etc/ozon/license-v2 ] || [ -d /etc/ozon/gui ]; then
    "$TARGET_BIN" --upgrade-ui >/dev/null 2>&1 || true
fi

if [ "${1:-}" = "--native-install-only" ]; then
    unset OZ_NATIVE_RELEASE_LOCK_FD
    flock -u 9 2>/dev/null || true
    exec 9>&- 2>/dev/null || true
    exit 0
fi

# Release update lock before exec'ing interactive / command runtime
unset OZ_NATIVE_RELEASE_LOCK_FD
flock -u 9
exec 9>&-
rm -rf "$STAGE" 2>/dev/null || true
trap - EXIT

if [ "$#" -eq 0 ] && [ ! -t 0 ] && [ -r /dev/tty ]; then
    exec "$TARGET_BIN" </dev/tty
fi
exec "$TARGET_BIN" "$@"
