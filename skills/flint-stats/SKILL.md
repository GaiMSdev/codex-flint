---
name: flint-stats
description: Show CODEX-FLINT token usage stats for the current session. Parses ~/.codex/sessions/ JSONL files to report real input/output token counts, cached tokens, and estimated savings from active flint mode. Use when user says "flint stats", "show stats", "/flint-stats", or asks how many tokens have been used or saved.
---

# CODEX-FLINT Stats

Show real token usage and estimated savings for the current session.

## How to run

Execute the bundled stats script:

```bash
python3 scripts/parse_session.py
```

The script path is relative to this skill directory. Resolve it:
- Skill is at `~/.codex/skills/codex-flint/skills/flint-stats/` (after install)
- Script is at `~/.codex/skills/codex-flint/skills/flint-stats/scripts/parse_session.py`

Run it, capture stdout, and relay the output verbatim to the user.

## What the script does

1. Reads `~/.codex/.flint-active` to determine current mode
2. Finds the most recently modified `rollout-*.jsonl` in `~/.codex/sessions/`
3. Parses every `response_item` event to extract token usage from API response bodies
4. Calculates estimated savings based on the active mode's flint ratio

## Compression ratios used for estimates

| Mode | Ratio | Source | n |
|------|-------|--------|---|
| lite | 0.30 | estimated | 0 |
| full | 0.47 | BM001 single-run | 1 |
| ultra | 0.50 | BM001 single-run | 1 |
| wenyan | 0.75 | no benchmark data | 0 |

These are output-side estimates. Generic terse instruction alone measured about
82% output savings vs unguided baseline, so structured modes should be judged
against terse control as well as baseline. Codex total budget is often
input/context dominated.

## Savings claims — tentative until n≥5

**Do NOT report a savings percentage without naming its source.** Per M034 and
Hypotese K (bimodal latch), a single benchmark run is not enough evidence to
treat a ratio as measured. Status levels:

| Status | Requirement |
|--------|-------------|
| HYPOTHESIS | idea, no data |
| TESTED | one run, needs more validation |
| REVIEWED | ≥2 agent opinions + ≥1 benchmark |
| VALIDATED | ≥2 benchmarks + ≥2 reviews + real-world proxy |

Until a ratio reaches VALIDATED, the stats output must mark it as such (the
`source` column in `/flint-stats` does this).

When reporting `/flint-stats` output to the user: never collapse the source
column into a single "saved" number. Always include the source caveat or the
"TENTATIVE" header.

## If no token data is found

Codex CLI (v0.130+) stores sessions as JSONL but embeds token data inside nested response structures. If the script reports zero tokens, it means the session format has changed or the session is very new. Relay the note from the script output to the user — do not fabricate numbers.

## Fallback

If the script fails for any reason (missing Python, permissions), run this shell fallback:

```bash
echo "Mode: $(cat ~/.codex/.flint-active 2>/dev/null || echo 'off')"
echo "Sessions: $(find ~/.codex/sessions -name '*.jsonl' 2>/dev/null | wc -l | tr -d ' ') files"
echo "Latest: $(find ~/.codex/sessions -name '*.jsonl' 2>/dev/null | xargs ls -t 2>/dev/null | head -1)"
```

## History

When user writes `/flint-stats --history` or `flint history`:

```bash
python3 -c "
import os, json
fp = os.path.expanduser('~/.claude/.flint-history.jsonl')
O_NOFOLLOW = getattr(os, 'O_NOFOLLOW', 0)
try:
    fd = os.open(fp, os.O_RDONLY | O_NOFOLLOW)
    data = os.read(fd, 65536).decode()
    os.close(fd)
    lines = [l for l in data.split('\n') if l.strip()]
    for line in lines[-10:]:
        print(line)
except FileNotFoundError:
    pass  # handled below
except OSError:
    pass
"
```

Parse the output and render as a table. Count lines first. If ≥3 rows, render a pipe-delimited table. If <3 entries, render as prose.

```text
ts                  | mode  | event
────────────────────┼───────┼───────
2026-05-11T05:30:00 | full  | turn
2026-05-11T05:31:00 | full  | turn
2026-05-11T05:32:00 | ultra | turn
```

If the file doesn't exist or is empty, report: "No history yet. Flint must be activated first."
