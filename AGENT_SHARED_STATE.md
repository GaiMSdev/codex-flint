# Agent Shared State

Purpose: shared coordination file for Codex and Claude Orchestrator.

## Current Focus

- Apply benchmark findings to `codex-flint`.
- Keep one commit in this repo; do not push.
- Avoid parallel edits to the same file without updating this state.

## Benchmark Inputs

- Model: Claude Haiku 4.5 via Anthropic API.
- Key finding: `terse` (`Answer concisely`) reached 81.8% output savings vs unguided baseline.
- `caveman_ultra`: about 68.8% output savings vs baseline.
- `flint_full`: about 54.1% output savings vs baseline.
- `flint_ultra` / `ultra_plain`: about 57.1% output savings vs baseline.
- CoD/Chain-of-Draft damaged context retention in multi-turn tests.
- `mcp-shrink` measured about 3-5% description compression on local corpora.

## Decisions

- FLINT full/ultra should be terse-first and short.
- Keep per-turn reinforcement; it is the persistence mechanism.
- Remove CoD from ultra guidance and benchmark variants used as FLINT defaults.
- Keep modes (`lite`, `full`, `ultra`, `wenyan`) because they encode density/readability choices.
- Claims must be honest: savings are vs unguided baseline; terse control is stronger for raw output.

## File Ownership

- Codex edited:
  - `scripts/flint-hook.sh`
  - `README.md`
  - `skills/flint/SKILL.md`
  - `skills/flint-help/SKILL.md`
  - `skills/flint-stats/SKILL.md`
  - `skills/flint-stats/scripts/parse_session.py`
  - `skills/flint-benchmark/scripts/benchmark.py`
  - `FINDINGS.md`
- Orchestrator should avoid direct edits to those files until Codex commit is complete.

## Open Tasks

- [x] Finish doc/stat prompt updates.
- [x] Add `FINDINGS.md` max 60 lines.
- [x] Run tests.
- [ ] Commit all repo changes once.
- [x] Do not push.

## Blockers

- Codex cannot directly read/edit Maestri note `flint-benchmark-handoff`; terminal is not connected to that note.
- Orchestrator owns Maestri-note updates and mirrors shared data into this repo file when needed.
- `compression_benchmark.py` with live `MODES` is in the OnePlayer workspace, not this repo.
