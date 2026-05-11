# Contributing

Keep changes small, measured, and easy to audit.

## Prompt Changes

For `SKILL.md`, hook prompt, or mode-rule changes, include:

- Before/after examples for at least two realistic prompts.
- Expected effect: shorter output, better retention, safer behavior, or clearer UX.
- Benchmark status: HYPOTHESIS, TESTED, REVIEWED, or VALIDATED.
- Whether the result is measured vs unguided baseline, terse control, or both.

Do not report a savings number without its source, model, scenario, and repeat
count. Single-run results are TESTED, not VALIDATED.

## Hook Checklist

Any hook/config change must satisfy this checklist:

- Hooks fail open: local filesystem or malformed input errors must not block agent startup.
- Predictable user-owned writes go through the shared safe-write helper.
- Flag/state reads reject symlinks, oversized files, invalid modes, and untrusted bytes.
- Per-turn reinforcement stays short; do not inject full prompts every turn.
- Unknown mode args leave existing state untouched.
- Stop/deactivate commands take precedence over activation in the same prompt.
- Config-dir env vars are respected.
- Shell-to-Node path passing uses env vars or argv, not interpolated shell strings.
- Hook hot paths stay bounded and avoid stats, benchmark, or session-log parsing work.

## Generated Copies

Edit source files only. If a future sync workflow generates plugin, marketplace,
or agent-surface copies, do not hand-edit generated outputs. Update the source
map and verification instead.

## Compression Tools

Compression tools cross a data boundary when they send file contents to a model
API or CLI. Before enabling automatic compression:

- Refuse secret-looking paths before reading or sending content.
- Preserve code, URLs, paths, identifiers, headings, and structured data.
- Keep a verified backup before overwriting.
- Restore the original if validation fails.
- Document exactly what can leave the machine.

## Review Standard

Reviews prioritize correctness, safety, fact retention, reproducibility, and user
control. No benchmark or compression method becomes VALIDATED without the
multi-method validation policy in `COMPRESSION_RESEARCH_DB.md`.
