#!/usr/bin/env bash
# CODEX-FLINT hook status reporter for Codex lifecycle hooks.

set -euo pipefail

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
FLAG_FILE="$CODEX_DIR/.flint-active"

mode="off"
if [ -f "$FLAG_FILE" ] && [ ! -L "$FLAG_FILE" ]; then
    value=$(tr -d "[:space:]" < "$FLAG_FILE" 2>/dev/null | head -c 32 || true)
    case "$value" in
        lite|full|ultra|wenyan)
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
    wenyan)
        color="\\u001b[36m"
        ;;
    *)
        color=""
        ;;
esac
reset="\\u001b[0m"

case "$mode" in
    lite)
        rules="[FLINT: LITE] Drop filler/hedging. Keep articles + full sentences. Professional-tight."
        ;;
    full)
        rules="[FLINT: FULL] Drop articles. Fragments OK. No pleasantries. High-signal."
        ;;
    ultra)
        rules="[FLINT: ULTRA] Abbrev prose (DB/auth/cfg/req/res/fn/impl/ctx/err). X→Y causality. Strip conjunctions. One word when enough. | Before: 'component re-renders because new object reference created each render' After: 'inline obj prop → new ref → re-render. useMemo.' | Before: 'connection pooling reuses open DB connections instead of creating new ones per request' After: 'pool reuse DB conn. skip handshake → fast.' | Before: 'auth middleware checks if token expired before allowing access' After: 'auth: token expiry check. fail → 401.'"
        ;;
    wenyan)
        rules="[FLINT: WENYAN] Classical Chinese (文言). 之/其/者/也/矣 particles. VO syntax. 成語 idioms. Technical terms preserved."
        ;;
esac

printf '{"systemMessage":"%s⚡ %s%s","continue":true}\n' "$color" "$rules" "$reset"
