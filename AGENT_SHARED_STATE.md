# Agent Shared State

Purpose: shared coordination file for Codex and Claude Orchestrator.

## Current Focus

- Apply benchmark and Caveman deep-dive findings to `codex-flint`.
- Keep local commits in this repo; do not push.
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
- [x] Commit prompt/benchmark-doc changes once: `75cec8d`.
- [x] Do not push.

## Caveman Deep-Dive Triage

- `flint-tracker.js`: not present in this repo. No existing plain-text Claude Code hook to fix here.
- `flint-config.js`: not present in this repo. Existing `scripts/flint.sh` already checks symlinks and uses temp+rename, but does not use `O_NOFOLLOW` because it is shell-based.
- `hooks/package.json`: no `hooks/` directory exists in this repo, so CJS enforcement applies only if/when a Claude Code hook package is added.
- Memory compression: `skills/flint-compress/SKILL.md` exists as workflow docs, but there is no executable compressor implementation yet. This is highest-ROI missing feature for input savings.
- Default config support: no `FLINT_DEFAULT_MODE` or `~/.config/flint/config.json` support yet.

## Caveman Follow-Up Priority

1. Implement real `flint-compress` script for Markdown memory/context files with backup, protected code blocks, and measured before/after size.
2. If adding Claude Code hooks, create `hooks/package.json` with `"type": "commonjs"` and emit `hookSpecificOutput.additionalContext`.
3. If adding JS config writer, use `O_NOFOLLOW`, `0600`, temp+rename, and symlink refusal.
4. Add default mode resolution: `FLINT_DEFAULT_MODE` env -> `~/.config/flint/config.json` -> `full`.

## Blockers

- Codex cannot directly read/edit Maestri note `flint-benchmark-handoff`; terminal is not connected to that note.
- Orchestrator owns Maestri-note updates and mirrors shared data into this repo file when needed.
- `compression_benchmark.py` with live `MODES` is in the OnePlayer workspace, not this repo.
- Current deep-dive references files absent from `codex-flint`; need target repo/path before fixing `flint-tracker.js` or `flint-config.js` specifically.
