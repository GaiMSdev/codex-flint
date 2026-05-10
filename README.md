# CODEX-FLINT

High-signal response flint for [Codex CLI](https://github.com/openai/codex). Reduces token waste without sacrificing technical accuracy.

Inspired by [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.

---

## What it does

CODEX-FLINT adds three flint modes to Codex CLI via its native skill system. Once activated, the model responds at reduced verbosity — dropping filler, articles, and hedging language proportional to the chosen mode. A flag file at `~/.codex/.flint-active` persists the mode across turns.

Security warnings and irreversible operations always use full prose regardless of mode.

---

## Modes

| Mode | Effect |
|------|--------|
| `lite` | Drop filler/hedging. Keep articles and full sentences. Professional-tight. ~30% shorter output. |
| `full` | Drop articles. Fragments OK. Short synonyms. No pleasantries. ~75% shorter output. (default) |
| `ultra` | MetaGlyph symbols (∈ → ∀ ∃ ∴). Abbreviate prose (DB/fn/req/res/impl/ctx/err/cfg/dep). Strip conjunctions. Arrows for causality. Chain-of-Draft: reason internally, output answer only. ~87% shorter output. |

---

## Platform reality check

Codex CLI (v0.130+) supports:

- **Skills** (`~/.codex/skills/<plugin>/skills/<name>/SKILL.md`) — first-class, auto-discovered
- **Plugins** (`~/.codex/skills/<plugin>/.codex-plugin/plugin.json`) — bundle skills together
- **Flag file persistence** — via shell commands inside skill workflows
- **Session JSONL logs** — at `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`

Codex CLI does **not** support:
- Native before-turn hooks (unlike Gemini CLI's `before-agent.js`)
- Session-start hooks that inject system messages automatically
- Per-turn reinforcement injection without explicit user invocation

This means flint mode must be **invoked by the user** per session. The flag file remembers the mode, but Codex does not auto-inject the rules on every turn the way GEM-THAL does for Gemini CLI. This is a real platform limitation, not an implementation gap.

---

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `flint` | `activate flint`, `flint lite/full/ultra`, `normal mode`, `stop flint` | Activate, switch, or deactivate mode |
| `flint-help` | `/flint-help`, "how does flint work" | Show full mode reference |
| `flint-stats` | `/flint-stats`, "flint stats", "show stats" | Parse session JSONL, report token usage and estimated savings |

---

## Install

```bash
cd /path/to/codex-flint
bash scripts/install.sh
```

This copies the plugin to `~/.codex/skills/codex-flint/`. Codex auto-discovers skills from `~/.codex/skills/`. Restart Codex after install.

### Uninstall

```bash
bash scripts/uninstall.sh
```

### Manual install (without the script)

```bash
cp -r /path/to/codex-flint ~/.codex/skills/codex-flint
```

---

## Usage

### In Codex

```
activate flint          # full mode (default)
activate flint lite     # lite mode
activate flint ultra    # ultra mode
switch to flint full    # switch while active
normal mode                # deactivate
stop flint              # deactivate
/flint-help             # show docs
/flint-stats            # token usage
```

### From the shell

```bash
# Control the flag file directly
bash scripts/flint.sh on      # activate full
bash scripts/flint.sh lite    # activate lite
bash scripts/flint.sh ultra   # activate ultra
bash scripts/flint.sh off     # deactivate
bash scripts/flint.sh status  # show current mode

# Check mode directly
cat ~/.codex/.flint-active 2>/dev/null || echo "off"

# Run stats directly
python3 ~/.codex/skills/codex-flint/skills/flint-stats/scripts/parse_session.py
```

---

## Auto-safety

Regardless of active mode, the model always uses full prose for:

- Security warnings or vulnerabilities
- Irreversible operations (destructive git commands, `rm`, force-push)
- Data loss scenarios
- Sequences where dropping conjunctions creates dangerous ambiguity
- Code blocks, commit messages, PR descriptions

---

## Examples

**full mode:**
> Input: "Why does my React component re-render?"
> Output: "New object ref each render. Inline prop = new ref = re-render. Wrap in `useMemo`."

**ultra mode:**
> Input: "Why does my React component re-render?"
> Output: "Inline prop → new ref → re-render. `useMemo`."

**lite mode:**
> Input: "Why does my React component re-render?"
> Output: "Your component re-renders because you create a new object reference on each render. Wrap the value in `useMemo`."

---

## Files

```
codex-flint/
├── .codex-plugin/
│   └── plugin.json              Plugin manifest
├── skills/
│   ├── flint/
│   │   ├── SKILL.md             Activation/deactivation logic
│   │   └── agents/openai.yaml   UI metadata
│   ├── flint-help/
│   │   ├── SKILL.md             Full mode reference
│   │   └── agents/openai.yaml
│   └── flint-stats/
│       ├── SKILL.md             Stats workflow
│       ├── agents/openai.yaml
│       └── scripts/
│           └── parse_session.py Real session JSONL parser
├── scripts/
│   ├── install.sh               Installer
│   ├── uninstall.sh             Uninstaller
│   └── flint.sh              Shell control script
├── LICENSE
└── README.md
```

Flag file: `~/.codex/.flint-active`

---

## Attribution

Inspired by [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.

---

## License

MIT. See [LICENSE](LICENSE).
