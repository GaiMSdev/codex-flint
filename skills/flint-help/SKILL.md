---
name: flint-help
description: Show help for CODEX-FLINT — modes, commands, examples, and attribution. Use when user invokes /flint-help or asks how flint mode works.
---

When the user invokes `/flint-help` or asks for flint help, display the following exactly:

---

## CODEX-FLINT — Help

High-signal response flint for Codex CLI. Removes filler without sacrificing technical accuracy.

### Modes

| Mode | Effect |
|------|--------|
| `lite` | Drop filler and hedging. Keep articles and full sentences. Professional-tight. |
| `full` | Drop articles. Fragments OK. Short synonyms. No pleasantries. (default) |
| `ultra` | MetaGlyph (∈ → ∀ ∃ ∴). Abbreviate prose (DB/fn/req/res/impl/ctx/err/cfg/dep). Strip conjunctions. Arrows for causality. Chain-of-Draft. One word when one word is enough. |

### Commands

**Activate:**
- `activate flint` — enable at `full` (default)
- `activate flint lite` — enable lite mode
- `activate flint full` — enable full mode
- `activate flint ultra` — enable ultra mode

**Switch while active:**
- `switch to flint lite`
- `switch to flint ultra`
- `activate flint full`

**Deactivate:**
- `normal mode`
- `stop flint`
- `deactivate flint`

**Check status:**
```bash
cat ~/.codex/.flint-active 2>/dev/null || echo "off"
```

**Direct flag write (advanced):**
```bash
printf 'full' > ~/.codex/.flint-active   # activate full
rm -f ~/.codex/.flint-active              # deactivate
```

### What is NEVER flint

- Security or data-loss warnings
- Irreversible operations (destructive git commands, `rm`, force-push)
- Sequences where dropping conjunctions creates ambiguity
- Code blocks, commit messages, PR descriptions

### Examples

**lite:**
> Input: "Why does my React component re-render?"
> Output: "Your component re-renders because you create a new object reference on each render. Wrap the value in `useMemo`."

**full:**
> Input: "Why does my React component re-render?"
> Output: "New object ref each render. Inline prop = new ref = re-render. Wrap in `useMemo`."

**ultra:**
> Input: "Why does my React component re-render?"
> Output: "Inline prop → new ref → re-render. `useMemo`."

### Files

| File | Purpose |
|------|---------|
| `~/.codex/.flint-active` | Flag file — contains `lite`, `full`, or `ultra` |
| `~/.codex/skills/codex-flint/` | Plugin root (after install) |

### Stats

Use `$flint-stats` to see token usage estimates for the current session.

### Attribution

Inspired by [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.

---
