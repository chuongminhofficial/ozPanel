#!/usr/bin/env bash
# OZPanel v9.1.4 · SDK 5.0.0 (OZV8-Fortress+ · OZV7-Fortress · OZV6-ZeroTrust · OZV5-Shield) Addon Runtime Helpers (Bash) — source this file; never auto-install packages on menu entry.
oz_require() { local name; for name in "$@"; do command -v "$name" >/dev/null || { printf 'Missing tool: %s\n' "$name" >&2; return 1; }; done; }
oz_confirm() { local reply; read -r -p "${1:-Continue?} [y/N]: " reply && [[ "$reply" =~ ^[Yy]$ ]]; }
oz_menu() { printf '%s\n' "$@"; }
oz_is_gui_form() { [[ "${OZ_GUI_FORM:-0}" == "1" || "${OZ_GUI_INTERNAL:-0}" == "1" ]]; }
oz_shimmer_banner() {
    local msg="${1:-OZPanel Addon}" len i pos ch
    len=${#msg}
    if [ -t 1 ] && [ "${OZ_NO_ANIM:-0}" != "1" ] && ! oz_is_gui_form && [ "$len" -gt 0 ]; then
        local c1='\033[1;38;2;255;252;225m' c2='\033[1;38;2;255;225;120m' c3='\033[1;38;2;212;175;55m' nc='\033[0m'
        for ((pos=0;pos<len;pos+=3)); do
            printf '\r\033[K  '
            for ((i=0;i<len;i++)); do
                ch="${msg:i:1}"
                if [ "$i" -ge "$((pos-1))" ] && [ "$i" -le "$((pos+1))" ]; then printf '%b%s%b' "$c1" "$ch" "$nc"
                elif [ "$i" -ge "$((pos-4))" ] && [ "$i" -le "$((pos+4))" ]; then printf '%b%s%b' "$c2" "$ch" "$nc"
                else printf '%b%s%b' "$c3" "$ch" "$nc"; fi
            done
            sleep 0.011
        done
        printf '\r\033[K  %b%s%b\n' "$c2" "$msg" "$nc"
    else
        printf '%s\n' "$msg"
    fi
}
oz_get() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" get "$1"; }
# One complete JSON value on stdin; do not place secrets in command arguments.
oz_set() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" set "$1"; }
oz_os() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" os; }
oz_shield_status() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" shield-status; }
oz_lease_status() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" lease-status; }
oz_health_json() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" health-json; }
oz_t() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" t "$@"; }
oz_api() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api "$@"; }
oz_api_call() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call "$@"; }
oz_local_ops() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" local-ops "$@"; }
oz_webserver() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call webserver "$@"; }
oz_database() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call database "$@"; }
oz_db_tables() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" db-tables "$@"; }
oz_docker() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call docker "$@"; }
oz_swap() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call swap "$@"; }
oz_waf() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call waf "$@"; }
oz_backup() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call backup "$@"; }
oz_ai() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call ai "$@"; }
oz_ai_cache_stats() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" ai-cache "$@"; }
oz_config_inspect() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" config-inspect "$1"; }
oz_chatops() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" chatops "$@"; }
oz_sso_link() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" sso-link "$@"; }
oz_ai_watchdog_status() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" ai-watchdog-status; }
oz_cf_delete_records() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call cloudflare delete_records --confirm; }
oz_analytics_3d() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call analytics report_3d --confirm; }
oz_edit() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" edit "$1"; }
oz_service() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" service "$@"; }
oz_license_path() { printf '%s/addons/license_%s.key\n' "${OZON_ROOT_DIR:-/etc/ozon}" "${OZ_ADDON_ID:?}"; }
oz_log() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" log "$*"; }
oz_install_packages() {
    oz_os >/dev/null || return 1
    local pkg; (( $# > 0 )) || return 1
    for pkg in "$@"; do [[ "$pkg" =~ ^[a-zA-Z0-9][a-zA-Z0-9_+.-]*$ ]] || return 1; done
    if command -v apt-get >/dev/null 2>&1; then
        apt-get install -y --no-install-recommends "$@"
    elif command -v dnf >/dev/null 2>&1; then
        dnf -y install "$@"
    else
        return 1
    fi
}
oz_apt_install() { oz_install_packages "$@"; }
oz_license_verify() { python3 "${OZ_SDK_CLI:?}" license-verify "$1" "$2" "$3" --product "$4"; }
oz_core_entitlement() { /usr/bin/oz --addon-entitlement "${OZ_ADDON_ID:?}"; }

# OZPanel v9.1.4 · SDK 5.0.0 Extended Helpers (46 Groups · 932 API Ops · AI DevOps Surgeon · Webhooks · App Pulse · Load Balancer · Fleet · MCP 8-Tool)
oz_ai_shift_report() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call ai shift_report "$@"; }
oz_loadbalancer() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call loadbalancer "$@"; }
oz_cloudflare() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call cloudflare "$@"; }
oz_fleet() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call fleet "$@"; }
oz_panel_groups() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" api-call panel groups "$@"; }
oz_app_pulse() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" app-pulse; }
oz_webhooks() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" webhooks "$@"; }
oz_gui_sso() { python3 "${OZ_SDK_RELEASE:?}/lib/ozaddon.py" sso-link gui "$@"; }
