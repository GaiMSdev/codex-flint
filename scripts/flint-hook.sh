#!/usr/bin/env bash
# CODEX-FLINT hook gate for Codex lifecycle hooks.
#
# Usage:
#   flint-hook.sh session   — SessionStart: emit systemMessage with full rules (once per session)
#   flint-hook.sh prompt    — UserPromptSubmit: set terminal title only, stay silent
#
# Codex renders hook systemMessage as a visible block. We accept this for
# SessionStart (user sees it once as confirmation) but suppress it for
# UserPromptSubmit (would appear on every turn as noise).

set -euo pipefail

EVENT="${1:-prompt}"
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

set_terminal_title() {
    local title="$1"
    if { true > /dev/tty; } 2>/dev/null; then
        { printf '\033]0;%s\007' "$title" > /dev/tty; } 2>/dev/null || true
    fi
}

if [ "$mode" = "off" ]; then
    set_terminal_title "Codex"
    printf '{"continue":true}\n'
    exit 0
fi

title_mode=$(printf '%s' "$mode" | tr '[:lower:]' '[:upper:]')
set_terminal_title "Codex | FLINT $title_mode"

# UserPromptSubmit: terminal title set above — stay silent, no systemMessage.
if [ "$EVENT" = "prompt" ]; then
    printf '{"continue":true}\n'
    exit 0
fi

# SessionStart: emit full rules for active mode as systemMessage.
# User sees this once as session confirmation. Full ruleset anchors the model
# for the session; no per-turn re-injection needed.
rules_lite='[FLINT: LITE] COMPRESS LITE ACTIVE
Drop filler/hedging/pleasantries. Keep articles + full sentences. Professional-tight.
ACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'

rules_full='[FLINT: FULL] COMPRESS FULL ACTIVE
Respond terse. Drop articles/filler/pleasantries/hedging. Fragments OK. Short synonyms.
Pattern: [thing] [action] [reason]. [next step].
Not: "Sure! I would be happy to help. The issue is likely caused by..."
Yes: "Bug in auth middleware. Token expiry check use < not <=. Fix:"
ACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'

rules_ultra='[FLINT: ULTRA] COMPRESS ULTRA ACTIVE
Abbreviate prose: DB auth cfg req res fn impl ctx err msg val bool pkg dep env init ref var arg param attr prop.
Never abbreviate: code symbols, function names, API names, error strings, file paths, URLs, numbers.
Use → for causality: X → Y → Z. Strip conjunctions where unambiguous. One word when one word enough.
Always include established facts/values in output — never omit.
Examples:
- Inline obj prop → new ref → re-render. useMemo.
- Pool reuse DB conn. Skip handshake → fast under load.
- Auth middleware: token expiry check. Fail → 401.
ACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'

rules_wenyan='[FLINT: WENYAN] COMPRESS WENYAN ACTIVE
Classical Chinese literary style (文言) compression.
Particles: 之 其 者 也 矣 乎 焉 哉 兮 耳. Pro-drop subjects. VO syntax. 成语 idioms.
Technical terms preserved as-is. Auto-revert to full prose for security/destructive ops.
ACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'

case "$mode" in
    lite)    rules="$rules_lite" ;;
    ultra)   rules="$rules_ultra" ;;
    wenyan)  rules="$rules_wenyan" ;;
    *)       rules="$rules_full" ;;
esac

# Emit systemMessage as JSON. Codex injects this into session context.
msg=$(printf '%s' "$rules" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null || printf '"%s"' "$rules")
printf '{"continue":true,"systemMessage":%s}\n' "$msg"
