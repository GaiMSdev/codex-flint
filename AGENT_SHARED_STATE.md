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

## Claude Plugin Reality Check

- Installed Claude plugin path: `/Users/robert/.claude/plugins/claude-flint`.
- `hooks/flint-tracker.js` already emits correct `hookSpecificOutput.additionalContext` JSON for `UserPromptSubmit`.
- `hooks/flint-config.js` already uses `O_NOFOLLOW`, temp+rename, `0600`, symlink refusal, and size-capped reads.
- `hooks/package.json` was added in installed plugin with `{ "type": "commonjs" }`.
- `node --check` passes for installed `flint-tracker.js`, `flint-config.js`, and `flint-activate.js`.
- `FLINT_DEFAULT_MODE` / config-file default mode support is still missing in installed Claude plugin.

## Caveman Follow-Up Priority

1. Implement real `flint-compress` script for Markdown memory/context files with backup, protected code blocks, and measured before/after size.
2. Add `hooks/package.json` with `"type": "commonjs"` to source Claude plugin hooks, not just installed copy.
3. Keep JS config writer standards: `O_NOFOLLOW`, `0600`, temp+rename, and symlink refusal.
4. Add default mode resolution: `FLINT_DEFAULT_MODE` env -> `~/.config/flint/config.json` -> `full`.

## Blockers

- Codex cannot directly read/edit Maestri note `flint-benchmark-handoff`; terminal is not connected to that note.
- Orchestrator owns Maestri-note updates and mirrors shared data into this repo file when needed.
- `compression_benchmark.py` with live `MODES` is in the OnePlayer workspace, not this repo.
- Current deep-dive references files absent from `codex-flint`; need target repo/path before fixing `flint-tracker.js` or `flint-config.js` specifically.

## flint-compress — DONE (2026-05-11)

- `skills/flint-compress/SKILL.md` — inline LLM compression skill (Claude Code + Codex)
- `skills/flint-compress/scripts/flint_compress.py` — zero-dep Python script
- Installed: `~/.claude/plugins/claude-flint/skills/flint-compress/`, `~/.codex/skills/codex-flint/skills/flint-compress/`
- Test result: 15.2% savings on prose-heavy markdown, code blocks unchanged
- Commit: 9261b22

Caveman-compress average: ~46% (prose-heavy files). flint-compress Python script: ~15% on mixed content (code ratio lowers savings). LLM-based compression via SKILL.md expected to reach ~40-50%.

