#!/usr/bin/env bash
# CODEX-FLINT control script
# Manage the flag file directly from the shell.
# Usage: flint.sh [on|off|lite|full|ultra|status]

set -euo pipefail

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
FLAG_FILE="$CODEX_DIR/.flint-active"

VALID_MODES=("lite" "full" "ultra")

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

read_flag() {
    if [ -f "$FLAG_FILE" ] && [ ! -L "$FLAG_FILE" ]; then
        local val
        val=$(cat "$FLAG_FILE" 2>/dev/null | tr -d '[:space:]' | head -c 32)
        case "$val" in
            lite|full|ultra) echo "$val"; return ;;
        esac
    fi
    echo "off"
}

write_flag() {
    local mode="$1"
    # Safety: refuse to write if FLAG_FILE is a symlink
    if [ -L "$FLAG_FILE" ]; then
        echo "Error: $FLAG_FILE is a symlink. Refusing to write." >&2
        exit 1
    fi
    printf '%s' "$mode" > "$FLAG_FILE"
}

remove_flag() {
    rm -f "$FLAG_FILE"
}

show_status() {
    local mode
    mode=$(read_flag)
    if [ "$mode" = "off" ]; then
        printf "${YELLOW}CODEX-FLINT: off${NC}\n"
    else
        printf "${GREEN}CODEX-FLINT: %s${NC}\n" "$mode"
    fi
}

show_help() {
    printf "${CYAN}CODEX-FLINT control script${NC}\n\n"
    printf "Usage: %s [COMMAND]\n\n" "$(basename "$0")"
    printf "Commands:\n"
    printf "  on / full   Activate full mode (default)\n"
    printf "  lite        Activate lite mode\n"
    printf "  ultra       Activate ultra mode\n"
    printf "  off         Deactivate flint\n"
    printf "  status      Show current mode\n"
    printf "  help        Show this help\n\n"
    printf "Flag file: %s\n" "$FLAG_FILE"
}

CMD="${1:-status}"

case "$CMD" in
    on|full)
        write_flag "full"
        printf "${GREEN}CODEX-FLINT: full activated.${NC}\n"
        ;;
    lite)
        write_flag "lite"
        printf "${GREEN}CODEX-FLINT: lite activated.${NC}\n"
        ;;
    ultra)
        write_flag "ultra"
        printf "${GREEN}CODEX-FLINT: ultra activated.${NC}\n"
        ;;
    off|stop|deactivate)
        remove_flag
        printf "${YELLOW}CODEX-FLINT: off.${NC}\n"
        ;;
    status)
        show_status
        ;;
    help|-h|--help)
        show_help
        ;;
    *)
        printf "Unknown command: %s\n" "$CMD" >&2
        show_help
        exit 1
        ;;
esac
