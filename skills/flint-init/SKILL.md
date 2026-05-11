---
name: flint-init
description: >
  Initialize FLINT ultra rule files in the current repo — drops compressed
  response instructions into Cursor, Windsurf, Copilot, and CLAUDE.md.
  Trigger: "init flint", "flint init", "setup flint in this repo",
  "/flint-init".
---

# FLINT Init — Drop IDE Rule Files

Drop FLINT compression rules into the current repo for every supported IDE
agent. Idempotent — safe to re-run.

## Rule body (ultra-level)

This is the content written to each rule file:

```
CODEX-FLINT ACTIVE. Max density response.

Abbrev prose: DB auth cfg req res fn impl ctx err msg val.
Arrows: X→Y→Z.
PRESERVE ALWAYS: technical values (numbers, IDs, versions, constants) — quote exact, never paraphrase.
Never abbrev: code symbols, function names, API names, error strings, paths, URLs.
Auto-safety — always full prose: security warnings, irreversible ops, data loss, dangerous ambiguity.

Format rules: tables only if ≥3 rows × 2 cols. Examples: code+1-line comment over prose. Technical answers in English. No emoji. No pretty-printed JSON. Plain labels over headers. Bullets over numbered lists unless order matters.

Stop: "normal mode" or "stop flint"
```

## Steps

1. Verify git repo: `git rev-parse --git-dir 2>/dev/null || exit 1`
2. For each target file below:
   - If file already contains `CODEX-FLINT ACTIVE` or `FLINT ACTIVE`: skip
   - If file exists and mode is `replace`: skip (unless `--force`)
   - If file exists and mode is `append`: append rule body with separator
   - If file does not exist: create with rule body
3. Confirm: one line per file with status, then total count

## Targets

| Agent | File | Mode |
|-------|------|------|
| Cursor | `.cursorrules` | replace |
| Windsurf | `.windsurf/rules/flint.md` | replace |
| Copilot | `.github/copilot-instructions.md` | append |
| CLAUDE.md | `CLAUDE.md` | append |

### Cursor — `.cursorrules`

```bash
mkdir -p "$(git rev-parse --show-toplevel)"
cat > "$(git rev-parse --show-toplevel)/.cursorrules" << 'RULES'
<rule-body>
RULES
```

### Windsurf — `.windsurf/rules/flint.md`

```bash
mkdir -p "$(git rev-parse --show-toplevel)/.windsurf/rules"
cat > "$(git rev-parse --show-toplevel)/.windsurf/rules/flint.md" << 'RULES'
---
description: "FLINT compression — max density response mode, ~75% fewer tokens"
globs: []
alwaysApply: true
---
<rule-body>
RULES
```

### GitHub Copilot — `.github/copilot-instructions.md`

```bash
FILE="$(git rev-parse --show-toplevel)/.github/copilot-instructions.md"
mkdir -p "$(dirname "$FILE")"
touch "$FILE"
if ! grep -q "CODEX-FLINT ACTIVE" "$FILE" 2>/dev/null; then
  echo -e "\n## FLINT compression\n" >> "$FILE"
  cat << 'RULES' >> "$FILE"
<rule-body>
RULES
fi
```

### CLAUDE.md — append FLINT section

```bash
FILE="$(git rev-parse --show-toplevel)/CLAUDE.md"
touch "$FILE"
if ! grep -q "CODEX-FLINT ACTIVE" "$FILE" 2>/dev/null; then
  echo -e "\n## FLINT\n\nFLINT ACTIVE. IDE rule files reference.\n" >> "$FILE"
fi
```

## Confirmation

After writing all files, confirm with:

```
FLINT: initialized <N> rule files
  + .cursorrules
  ~ .windsurf/rules/flint.md
  ~ .github/copilot-instructions.md
  ~ CLAUDE.md
```

Where `+` = created, `~` = appended, `=` = skipped (unchanged), `!` = overwritten.

## Flags (optional)

- `--dry-run` — show what would change, do not write
- `--force` — overwrite existing rule files (default: skip if exists)
- `--only cursor|windsurf|copilot|claude` — only install for one agent

If the user does not pass `--force`, use `--dry-run` first to preview changes.
