# Benchmark Findings

Date: 2026-05-11

## Setup

- Runner: `compression_benchmark.py`
- Model: `claude-haiku-4-5-20251001`
- Scenarios: `long_conversation`, `context_retention`
- Metric: output-token savings vs unguided baseline, plus context-retention probes

## Key Results

| Mode | vs baseline | vs terse control | Note |
|------|-------------|------------------|------|
| `terse` | +81.8% | baseline control | Plain `Answer concisely` won raw savings |
| `caveman_ultra` | +68.8% | -71% | Best structured reference |
| `flint_full` | +54.1% | -152% | Too much structured overhead |
| `flint_ultra` / `ultra_plain` | +57.1% | -136% | Dense, but worse than terse |

`vs terse control` is negative when a mode produced more output than terse.

## Decisions

1. FLINT prompts become terse-first: short, direct, pattern-driven.
2. No Chain-of-Draft in ultra; it damaged multi-turn fact retention.
3. Claims stay honest: savings are vs unguided baseline; terse alone gives ~82%.

## What Stays

- Per-turn reinforcement stays. It is the persistence mechanism across long sessions.
- Modes stay. `lite`, `full`, `ultra`, and `wenyan` encode readability/density tradeoffs.
- `mcp-shrink` stays. Current measured effect is modest (~3-5%), but architecture is useful.

## Next

- Repeat benchmark with randomized mode order and `n_repeats=3`.
- Score full responses, not previews.
- Add task-success/readability scoring before changing prompts again.

