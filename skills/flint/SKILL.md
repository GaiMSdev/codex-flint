---
name: flint
description: Activate, switch, or deactivate CODEX-FLINT response flint mode (lite/full/ultra/wenyan). Use when user says "activate flint", "flint lite/full/ultra/wenyan", "flint on", "normal mode", "stop flint", "deactivate flint", or similar flint control phrases.
---

# CODEX-FLINT

High-signal response flint for Codex CLI. Reduces output verbosity without sacrificing technical accuracy.

## Flag file

`~/.codex/.flint-active` contains: `lite`, `full`, `ultra`, or `wenyan`. Missing or `off` = inactive.

## Activation commands

- `activate flint` — enable at `full` (default)
- `activate flint lite` — enable lite mode
- `activate flint full` — enable full mode
- `activate flint ultra` — enable ultra mode
- `activate flint wenyan` — enable wenyan mode

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

**Activate wenyan:**
```bash
printf 'wenyan' > ~/.codex/.flint-active
```
Confirm: "CODEX-FLINT: wenyan."

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

**full:** Terse-first. Answer concisely. No pleasantries or preamble. Short direct sentences. Fragments OK when clear. Preserve nuance/facts. Tables only if ≥3 rows × 2 cols. Code+comment preferred over prose for examples.

**ultra:** Max density. Abbrev prose: DB auth cfg req res fn impl ctx err msg val. Arrows X→Y→Z. PRESERVE ALWAYS: technical values (numbers, IDs, versions, constants) — quote exact, never paraphrase. Never abbrev: code symbols, function names, API names, error strings, paths, URLs. No Chain-of-Draft. One concrete example per answer. Format rules: tables only if ≥3 rows × 2 cols (else prose). Examples: prefer code+1-line comment over prose (15% fewer tokens). Language: technical answers in English (Norwegian tokenizes 30–50% more).

**wenyan:** Classical Chinese compression. Use 之/其/者/也/矣 particles and compact classical syntax where understandable. Preserve technical identifiers, file paths, commands, APIs, and error text as-is.

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
