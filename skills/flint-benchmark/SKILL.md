---
name: flint-benchmark
description: Benchmark CODEX-FLINT against Caveman/RUNES-style compression and estimate ultra-mode data retention. Use when user asks to benchmark FLINT, compare against Caveman, measure value, or check if ultra loses data.
---

# CODEX-FLINT Benchmark

Run the bundled benchmark:

```bash
python3 ~/.codex/skills/codex-flint/skills/flint-benchmark/scripts/benchmark.py
```

The script compares:

- FLINT mode rule sizes vs local Caveman/RUNES prompt rules when available
- Estimated output-token savings by mode
- Actual current Codex session token shape when available
- Ultra retention on deterministic technical fixtures

Relay the output to the user. Treat the retention suite as a guardrail test: it checks whether ultra-style compression preserves required IDs, numbers, paths, commands, and causal facts. It does not prove semantic equivalence for arbitrary prose.

