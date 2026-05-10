---
name: flint-review
description: Review git diff or changed files. One finding per line, severity-tagged, no praise, no scope creep. Trigger: user says "/flint-review", "review this", "review the diff", "review my changes", "code review".
---

# FLINT-REVIEW

Review staged or recent changes. Signal-only. No praise. No scope creep.

## Steps

1. Run `git diff --staged`. If empty, run `git diff HEAD~1`. If no git, ask user to paste the diff.
2. Analyze for real problems only.
3. Output findings — one per line.

## Output format

```
path:line: SEVERITY: problem. fix.
```

**Severity levels:**
- `CRITICAL` — security hole, data loss, crash, broken logic
- `WARN` — likely bug, missing error handling, performance issue, bad assumption
- `NOTE` — non-obvious concern, minor risk, worth considering

## Rules

- Max 10 findings, sorted by severity (CRITICAL first)
- Only actionable findings — skip style, formatting, naming unless misleading
- No praise, no preamble, no closing summary
- Check: security (injection, auth bypass, secrets), logic errors, unhandled errors, race conditions, off-by-one

## Example output

```
src/auth.js:42: CRITICAL: token compared with == not ===. Use ===.
src/api.js:87: WARN: no timeout on fetch. Add {signal: AbortSignal.timeout(5000)}.
src/cache.js:12: NOTE: unbounded cache growth possible. Add max size or TTL.
```

## If no issues found

```
No findings. Diff looks clean.
```
