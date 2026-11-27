# OZPanel Addon Developer Kit — v9.1.4 (SDK 5.0.0)

Official SDK, packaging toolchain, runtime libraries, and documentation for building and distributing addons for **OZPanel v9.1.4** (`OZV8-Fortress+` · `OZV8-SES/2`, 125 REST API resources / 932 operations, Standalone Web GUI `[27]`, Autonomous AI Config Surgeon `[32]`, and 8-Tool MCP Server).

## What's New in SDK 5.0.0 (OZPanel v9.1.4 Sync)
- **OZPanel v9.1.4 Baseline**: Synced `PANEL='9.1.4'`, `OZONFS_VERSION='9.1.4'`, `SHIELD_ENGINE='OZV8-Fortress+'`, `LEASE_TTL_SECONDS=21600` (6h lease window), and `MCP_TOOLS_V914` (`8` MCP tools including `panel_config_surgeon`).
- **Native Little-Endian Lease Inspection**: Fixed `runtime.lease` offset unpacking to natively read `<Q` (little-endian) written by `launcher.rs` / `ozbackend` while preserving fallback compatibility.
- **Full `API_V914_CATALOG` (125 Resources / 932 Operations)**: Includes `app/{bootstrap,pulse}`, `webhooks/*`, `billing/*`, `ozonfs/*`, `sso/*`, `panel/{groups,execute,batch,dag}`, `ai/{config_inspect,config_repair,cache_stats,shift_report,multitask}`, `database/{tables_list,query_readonly}`, and all 46 CLI feature bridges.
- **CLI Flag Parity**: `ozsdk.py` supports `--category` on `init`, `--out` on `keygen`, `--sign-key` on `pack`, `--pub-key` on `verify`, and `--publisher`/`--pub-key` on `trust` out of the box, plus `amd64`/`arm64` architecture aliases.
- **v9.1.4 Runtime Helpers (`lib/ozaddon.sh` & `lib/ozaddon.py`)**: Added `oz_health_json` (`oz --health-json` <30ms telemetry), `oz_ai_cache_stats`, `oz_config_inspect`, `oz_app_pulse`, `oz_webhooks`, and `oz_db_tables`, plus fixed GET query-string routing in `Context.api_call()`.
- **Core Panel Auto-Integration**: Both SSH `[15] → [6]` and Web GUI `[27] → [15]` (`addon.sdk_list`, `addon.sdk_run`, `addon.sdk_import_url`, `addon.sdk_health`) natively inspect, verify, install, and run `.ozaddon` packages; `build.sh` auto-deploys SDK runtime to `/usr/local/lib/ozpanel/sdk/`.

## 5-Minute Quickstart

```bash
python3 ozsdk.py --version
python3 ozsdk.py init ./my-addon --id 9010 --publisher my-studio --name "My Addon" --category automation
python3 ozsdk.py validate ./my-addon
python3 ozsdk.py audit ./my-addon
python3 ozsdk.py keygen --out ./keys
python3 ozsdk.py pack ./my-addon --out ./dist/addon_9010.ozaddon --sign-key ./keys/publisher-private.pem
python3 ozsdk.py verify ./dist/addon_9010.ozaddon --pub-key ./keys/publisher-public.pem
```

## Distribution via GitHub Raw URL
Commit `addon_<ID>.ozaddon`, `addon_<ID>.ozaddon.sha256`, and `publisher-public.pem` to your public repository's `main` branch and share the direct `https://raw.githubusercontent.com/<owner>/<repo>/main/addon_<ID>.ozaddon` URL for 1-click installation in OZPanel `[15] → [6]` or Web GUI `[27] → [15]`.

© 2026 Chương Minh Studio · https://github.com/chuongminhofficial/ozPanel
