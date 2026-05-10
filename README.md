# CODEX-FLINT

High-signal compression for [Codex CLI](https://github.com/openai/codex).

Reduces token waste without sacrificing technical accuracy. Activate a mode once per session — the flag file at `~/.codex/.flint-active` persists it across turns.

Inspired by [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.

---

## Modes

| Mode | Description | Output reduction |
|------|-------------|-----------------|
| `lite` | Drop filler, hedging, pleasantries. Keep articles and full sentences. Professional-tight. | ~30% |
| `full` | Drop articles. Fragments OK. Short synonyms. No preamble. (default) | ~75% |
| `ultra` | MetaGlyph symbols. Abbreviated prose. Strip conjunctions. Arrows for causality. Chain-of-Draft. | ~87% |
| `wenyan` | Classical Chinese literary compression. Technical identifiers preserved. | — |

---

## MetaGlyph symbols (ultra only)

| Symbol | Meaning |
|--------|---------|
| `∈` | is a member of / belongs to |
| `→` | causes / leads to / results in |
| `∀` | for all / in every case |
| `∃` | there exists / some |
| `∴` | therefore |
| `!` | important / watch out |

Prose abbreviations: `DB fn req res impl ctx err cfg dep`

Technical identifiers (variable names, file paths, APIs) are never abbreviated.

---

## Auto-safety

Regardless of active mode, the model always uses full prose for:

- Security warnings and vulnerabilities
- Irreversible operations (`rm`, destructive git commands, force-push, overwrites)
- Data loss scenarios
- Sequences where dropping conjunctions creates dangerous ambiguity
- Code blocks, commit messages, PR descriptions

---

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `flint` | `activate flint [lite\|full\|ultra\|wenyan]`, `normal mode`, `stop flint` | Activate, switch, or deactivate compression mode |
| `flint-commit` | `/flint-commit`, "commit this", "write commit" | Generate a high-signal Conventional Commits message from staged diff |
| `flint-review` | `/flint-review`, "review the diff", "code review" | Signal-only review: one finding per line, severity-tagged, no praise |
| `flint-stats` | `/flint-stats`, "flint stats", "show stats" | Parse session JSONL, report token usage and estimated savings |

---

## Platform reality

Codex CLI (v0.130+) supports skills, plugins, flag file persistence, and session JSONL logs. It does **not** support native before-turn hooks or automatic per-turn system-message injection. This means flint mode must be invoked by the user at the start of each session. The flag file remembers the chosen mode, but Codex does not re-inject the rules automatically on every turn.

---

## Installation

```bash
git clone https://github.com/raakanin/codex-flint ~/.codex/skills/codex-flint
cd ~/.codex/skills/codex-flint
bash scripts/install.sh
```

Restart Codex after install. Skills are auto-discovered from `~/.codex/skills/`.

### Uninstall

```bash
bash scripts/uninstall.sh
```

---

## Commands

```
activate flint              # full mode (default)
activate flint lite         # lite mode
activate flint ultra        # ultra mode
activate flint wenyan       # wenyan mode
normal mode                 # deactivate
stop flint                  # deactivate
/flint-commit               # generate commit message
/flint-review               # review staged diff
/flint-stats                # token usage report
```

---

## Shell control

```bash
bash scripts/flint.sh on      # activate full
bash scripts/flint.sh lite    # activate lite
bash scripts/flint.sh ultra   # activate ultra
bash scripts/flint.sh off     # deactivate
bash scripts/flint.sh status  # show current mode

cat ~/.codex/.flint-active 2>/dev/null || echo "off"
```

---

## Examples

**lite:**
> "Your component re-renders because you create a new object reference on each render. Wrap the value in `useMemo`."

**full:**
> "New object ref each render. Inline prop = new ref = re-render. Wrap in `useMemo`."

**ultra:**
> "Inline prop → new ref → re-render. `useMemo`."

---

## License

MIT. See [LICENSE](LICENSE).
