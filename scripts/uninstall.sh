#!/usr/bin/env bash
# CODEX-FLINT uninstaller

set -euo pipefail

PLUGIN_NAME="codex-flint"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
INSTALL_DIR="$CODEX_DIR/skills/$PLUGIN_NAME"
FLAG_FILE="$CODEX_DIR/.flint-active"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { printf "${GREEN}[codex-flint]${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}[codex-flint]${NC} %s\n" "$1"; }

if [ ! -d "$INSTALL_DIR" ]; then
    warn "Plugin not installed at $INSTALL_DIR"
    exit 0
fi

read -r -p "Remove CODEX-FLINT from $INSTALL_DIR? [y/N] " REPLY
if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    info "Aborted."
    exit 0
fi

rm -rf "$INSTALL_DIR"
info "Plugin removed."

if [ -f "$FLAG_FILE" ]; then
    rm -f "$FLAG_FILE"
    info "Flag file removed."
fi

warn "Restart Codex to complete uninstall."
