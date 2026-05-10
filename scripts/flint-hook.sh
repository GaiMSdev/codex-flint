#!/usr/bin/env bash
# CODEX-FLINT hook status reporter for Codex lifecycle hooks.

set -euo pipefail

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
FLAG_FILE="$CODEX_DIR/.flint-active"

mode="off"
if [ -f "$FLAG_FILE" ] && [ ! -L "$FLAG_FILE" ]; then
    value=$(tr -d "[:space:]" < "$FLAG_FILE" 2>/dev/null | head -c 32 || true)
    case "$value" in
        lite|full|ultra)
            mode="$value"
            ;;
    esac
fi

if [ "$mode" = "off" ]; then
    printf '{"continue":true}\n'
    exit 0
fi

MODE=$(printf '%s' "$mode" | tr "[:lower:]" "[:upper:]")
case "$mode" in
    lite)
        color="\\u001b[32m"
        ;;
    full)
        color="\\u001b[33m"
        ;;
    ultra)
        color="\\u001b[35m"
        ;;
    *)
        color=""
        ;;
esac
reset="\\u001b[0m"

printf '{"systemMessage":"%s⚡ [FLINT: %s]%s","continue":true}\n' "$color" "$MODE" "$reset"
