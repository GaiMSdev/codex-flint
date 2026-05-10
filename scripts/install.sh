#!/usr/bin/env bash
# CODEX-FLINT installer
# Installs the plugin into ~/.codex/skills/codex-flint/
# and registers it in ~/.codex/config.toml

set -euo pipefail

PLUGIN_NAME="codex-flint"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
INSTALL_DIR="$CODEX_DIR/skills/$PLUGIN_NAME"
FLAG_FILE="$CODEX_DIR/.flint-active"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { printf "${GREEN}[codex-flint]${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}[codex-flint]${NC} %s\n" "$1"; }
error()   { printf "${RED}[codex-flint]${NC} %s\n" "$1" >&2; }

# ─── Pre-flight ────────────────────────────────────────────────────────────────

if ! command -v codex >/dev/null 2>&1; then
    error "codex not found in PATH. Install Codex CLI first: npm install -g @openai/codex"
    exit 1
fi

CODEX_VERSION=$(codex --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
info "Codex CLI version: $CODEX_VERSION"

if [ ! -d "$CODEX_DIR" ]; then
    error "~/.codex/ does not exist. Run 'codex' once to initialize it."
    exit 1
fi

# ─── Install ───────────────────────────────────────────────────────────────────

if [ -d "$INSTALL_DIR" ]; then
    warn "Plugin already exists at $INSTALL_DIR"
    read -r -p "  Overwrite? [y/N] " REPLY
    if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
        info "Aborted."
        exit 0
    fi
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$CODEX_DIR/skills"
cp -r "$PLUGIN_DIR" "$INSTALL_DIR"
info "Plugin copied to $INSTALL_DIR"

# Make the stats script executable
chmod +x "$INSTALL_DIR/skills/flint-stats/scripts/parse_session.py" 2>/dev/null || true

# Ensure ~/.codex/skills/ directory exists (Codex auto-discovers skills from here)
info "Skills auto-discovered from ~/.codex/skills/ — no config.toml edits needed."

# ─── Status ────────────────────────────────────────────────────────────────────

info ""
info "CODEX-FLINT installed."
info ""
info "  Skills installed:"
info "    flint       — activate/deactivate flint"
info "    flint-help  — show mode reference"
info "    flint-stats — show token usage stats"
info ""
info "  Flag file: $FLAG_FILE (created on first activation)"
info ""
info "  Usage:"
info "    In Codex: 'activate flint'       — full mode"
info "    In Codex: 'activate flint lite'  — lite mode"
info "    In Codex: 'activate flint ultra' — ultra mode"
info "    In Codex: 'normal mode'             — deactivate"
info "    In Codex: '/flint-help'          — show full docs"
info "    In Codex: '/flint-stats'         — token usage"
info ""
warn "  Restart Codex to pick up new skills."
