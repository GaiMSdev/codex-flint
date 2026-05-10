# CODEX-FLINT

High-signal compression for [Codex CLI](https://github.com/openai/codex).

Reduces output verbosity without sacrificing technical accuracy. Activate a mode once per session — the flag file at `~/.codex/.flint-active` persists it across turns.

Inspired by [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.

---

## Modes

| Mode | Description | Measured output reduction |
|------|-------------|-----------------|
| `lite` | Drop filler, hedging, pleasantries. Keep articles and full sentences. Professional-tight. | ~30% |
| `full` | Terse-first. No preamble. Short direct sentences. (default) | ~54% |
| `ultra` | Max density. Abbreviated prose. Causality arrows. Facts preserved. No Chain-of-Draft. | ~57-69% |
| `wenyan` | Classical Chinese literary compression. Technical identifiers preserved. | — |

Benchmarks measure savings vs unguided baseline. Generic terse instruction alone
reached ~82% output savings, so FLINT's value is persistence, consistency, and
mode control rather than beating `Answer concisely` on raw tokens.

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
| `flint-budget` | `flint budget`, `flint doctor`, "what is using tokens" | Diagnose input/context waste and risky tool-output patterns |
| `flint-benchmark` | `flint benchmark`, "compare with caveman", "does ultra lose data" | Compare FLINT against Caveman/RUNES-style ratios and test ultra retention fixtures |

---

## Input compression (flint-shrink)

`flint-shrink` is an MCP proxy that compresses tool and resource descriptions before
the model sees them — reducing tool description char-count ~3–5% on typical corpora; savings compound across many tools.

Wrap any MCP server in `.codex/config.toml`:

```toml
[[mcpServers]]
name = "filesystem"
command = "node"
args = [
  "/Users/robert/.codex/skills/codex-flint/mcp-shrink/index.js",
  "npx", "@modelcontextprotocol/server-filesystem", "/your/path"
]
```

Code, URLs, paths, and identifiers are never touched. Only prose descriptions are compressed.
Debug: `FLINT_SHRINK_DEBUG=1`. Extra fields: `FLINT_SHRINK_FIELDS=description,title`.

---

## Platform reality

Codex CLI (v0.130+) supports skills, plugins, flag file persistence, hooks, and session JSONL logs. Hook `systemMessage` output is rendered as transcript text, so CODEX-FLINT emits compact per-turn reinforcement plus terminal title (`Codex | FLINT ULTRA`, etc.). A true colored bottom status line requires a Codex TUI integration.

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
flint budget                # context budget diagnosis
flint benchmark             # compare against Caveman/RUNES-style compression
```

---

## Shell control

```bash
bash scripts/flint.sh on      # activate full
bash scripts/flint.sh lite    # activate lite
bash scripts/flint.sh ultra   # activate ultra
bash scripts/flint.sh wenyan  # activate wenyan
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
