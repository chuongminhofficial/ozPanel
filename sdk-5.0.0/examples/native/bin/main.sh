#!/usr/bin/env bash
set -Eeuo pipefail
source "${OZ_SDK_RELEASE:?}/lib/ozaddon.sh"

_run_action() {
    local k="$1"
    case "$k" in
        1)
            oz_os
            ;;
        2)
            local note="${OZ_INPUT_NOTE:-}"
            if [[ -z "$note" ]] && ! oz_is_gui_form; then
                read -r -p 'Note (no secrets): ' note || return 0
            fi
            note="${note:-OZPanel v9.1.4 SDK 5.0.0 Check OK}"
            printf '%s' "$note" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))' | oz_set note
            oz_get note
            ;;
        3)
            python3 "${OZ_SDK_CLI:?}" --root "${OZON_ROOT_DIR:-/etc/ozon}" core-status
            ;;
        4)
            oz_lease_status
            ;;
        5)
            oz_health_json
            oz_ai_watchdog_status
            ;;
        6)
            oz_ai_cache_stats
            ;;
        *)
            printf 'Unknown action key: %s\n' "$k" >&2
            return 1
            ;;
    esac
}

if oz_is_gui_form; then
    oz_shimmer_banner "✦ $(oz_t title) · OZPanel v9.1.4 (OZV8-Fortress+ · 8-Tool MCP) · SDK v5.0.0 ✦"
    _run_action "${OZ_ACTION_KEY:-1}"
    exit $?
fi

while true; do
    oz_shimmer_banner "✦ $(oz_t title) · OZPanel v9.1.4 (OZV8-Fortress+ · AI Config Surgeon) · SDK v5.0.0 ✦"
    oz_menu \
        "[1] $(oz_t os)" \
        "[2] $(oz_t note)" \
        "[3] Kiểm tra trạng thái OZPanel Core v9.1.4 & OZV8-Fortress+" \
        "[4] Kiểm tra 72-Byte Cloud Lease (runtime.lease <Q / 6h)" \
        "[5] Kiểm tra Health JSON (<30ms) & AI Watchdog (log_cursors.json)" \
        "[6] Kiểm tra AI Cache / Token Telemetry (llm_cache.json)" \
        "[0] $(oz_t back)"
    read -r -p '> ' choice || exit 0
    case "$choice" in
        0) exit 0 ;;
        1|2|3|4|5|6) _run_action "$choice" ;;
        *) printf 'Lựa chọn không hợp lệ.\n' ;;
    esac
done
