#!/usr/bin/env bash
# CODEX-FLINT hook gate for Codex lifecycle hooks.
#
# Usage:
#   flint-hook.sh session   — SessionStart: emit systemMessage with full rules (once per session)
#   flint-hook.sh prompt    — UserPromptSubmit: compact visible reinforcement
#
# Codex renders hook systemMessage as visible transcript text. SessionStart
# emits compact mode rules; UserPromptSubmit emits one-line reinforcement.

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

if [ "$EVENT" = "prompt" ]; then
    case "$mode" in
        lite)
            status_msg="[FLINT: $title_mode] Drop filler/hedging. Keep full sentences."
            ;;
        ultra)
            status_msg="[FLINT: $title_mode] Max density. Arrows/abbrev OK. Preserve facts/values."
            ;;
        wenyan)
            status_msg="[FLINT: $title_mode] Wenyan style. Preserve technical identifiers."
            ;;
        *)
            status_msg="[FLINT: $title_mode] Answer concisely. No preamble. Preserve nuance."
            ;;
    esac
    msg=$(printf '%s' "$status_msg" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null || printf '"%s"' "$status_msg")
    printf '{"continue":true,"systemMessage":%s}\n' "$msg"
    exit 0
fi

# SessionStart: emit full rules for active mode as systemMessage.
# User sees this once as session confirmation. Full ruleset anchors the model
# for the session; no per-turn re-injection needed.
rules_lite='[FLINT: LITE] COMPRESS LITE ACTIVE
Drop filler/hedging/pleasantries. Keep articles + full sentences. Professional-tight.
ACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'

rules_full='[FLINT: FULL] COMPRESS FULL ACTIVE
Answer concisely. No preamble.
Pattern: thing → cause → fix.
Fragments OK when clear. Preserve nuance/facts.
Example: "Auth bug: expiry check uses < not <=. Fix comparison."
ACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'

rules_ultra='[FLINT: ULTRA] COMPRESS ULTRA ACTIVE
Max density. No preamble.
Use → for causality. Abbrev prose: DB auth cfg req res fn impl ctx err.
Never abbrev code symbols, APIs, paths, URLs, numbers, errors.
Preserve established facts/values. No Chain-of-Draft.
Example: "Inline prop → new ref → re-render. useMemo."
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
