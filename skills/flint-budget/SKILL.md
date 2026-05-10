---
name: flint-budget
description: Analyze Codex session token budget and context hygiene. Use when user asks what is using tokens, why Codex quota disappears quickly, whether FLINT can help input/context usage, or asks for flint doctor/budget.
---

# CODEX-FLINT Budget Doctor

Diagnose token waste from Codex session JSONL. Focus on input/context bloat, large tool outputs, command patterns, and whether FLINT is helping the right side of the budget.

## How to run

Execute the bundled script:

```bash
python3 scripts/analyze_budget.py
```

The script path is relative to this skill directory. Resolve it after install:

```bash
python3 ~/.codex/skills/codex-flint/skills/flint-budget/scripts/analyze_budget.py
```

Relay the output to the user. If the user asks to reduce waste, use the "Recommended actions" section as the implementation checklist.

## What it checks

- Current FLINT mode from `~/.codex/.flint-active`
- Latest Codex session under `~/.codex/sessions/`
- Real token usage from `token_count` events when available
- Input vs output ratio
- Per-turn token growth
- Large tool outputs stored in transcript
- Broad command patterns likely to explode context
- Hook status overhead and warning-style status noise

## Interpretation

- If input tokens dominate output tokens, FLINT response style alone will not solve the budget problem.
- If large tool outputs appear, tighten command defaults before adding more compression modes.
- If per-turn input is high even for short user prompts, recommend new session or compaction.
- If hook status appears as `warning:`, treat it as UX noise, not material token waste.

