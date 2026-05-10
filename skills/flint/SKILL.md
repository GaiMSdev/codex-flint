---
name: flint
description: Activate, switch, or deactivate CODEX-FLINT response flint mode (lite/full/ultra). Use when user says "activate flint", "flint lite/full/ultra", "flint on", "normal mode", "stop flint", "deactivate flint", or similar flint control phrases.
---

# CODEX-FLINT

High-signal response flint for Codex CLI. Reduces token waste without sacrificing technical accuracy.

## Flag file

`~/.codex/.flint-active` contains: `lite`, `full`, or `ultra`. Missing or `off` = inactive.

## Activation commands

- `activate flint` — enable at `full` (default)
- `activate flint lite` — enable lite mode
- `activate flint full` — enable full mode
- `activate flint ultra` — enable ultra mode

## Deactivation commands

- `normal mode` — deactivate
- `stop flint` — deactivate
- `deactivate flint` — deactivate

## Logic

Run the appropriate shell command, then confirm with a short status line:

**Activate full (default):**
```bash
printf 'full' > ~/.codex/.flint-active
```
Confirm: "CODEX-FLINT: full. Respond flint."

**Activate lite:**
```bash
printf 'lite' > ~/.codex/.flint-active
```
Confirm: "CODEX-FLINT: lite."

**Activate ultra:**
```bash
printf 'ultra' > ~/.codex/.flint-active
```
Confirm: "CODEX-FLINT: ultra."

**Deactivate:**
```bash
rm -f ~/.codex/.flint-active
```
Confirm: "CODEX-FLINT: off. Normal mode restored."

**Check status:**
```bash
cat ~/.codex/.flint-active 2>/dev/null || echo "off"
```

## After activation — apply the active mode

After activating or when already active, apply the mode rules for your response:

**lite:** Drop filler, hedging, and pleasantries. Keep articles and full sentences. Professional-tight.

**full:** Drop articles. Fragments OK. Short synonyms preferred. No pleasantries or preamble. High-signal only.

**ultra:** MetaGlyph symbols allowed (∈ → ∀ ∃ ∴). Abbreviate prose (DB/fn/req/res/impl/ctx/err/cfg/dep). Strip conjunctions. Arrows for causality (X → Y). Chain-of-Draft: reason internally, output answer only. One word when one word is enough. Technical identifiers never abbreviated.

## Auto-safety — NEVER flint these

Regardless of active mode, always use full prose for:
- Security warnings or vulnerabilities
- Irreversible operations (destructive git commands, `rm`, overwrites, force-push)
- Data loss scenarios
- Sequences where dropping conjunctions creates dangerous ambiguity
- Code blocks, commit messages, PR descriptions

## Persistence note

The flag file persists across turns. To confirm current mode at any time: `cat ~/.codex/.flint-active 2>/dev/null || echo "off"`

For full documentation: use the `flint-help` skill.
