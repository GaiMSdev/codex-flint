---
name: flint-commit
description: >
  Generate a compressed, high-signal git commit message following Conventional Commits format.
  Trigger: /flint-commit, "commit message", "write commit", "generate commit".
---

# FLINT-COMMIT

Generate a high-signal git commit message. No noise. No "what" descriptions — code shows that. Only "why" when non-obvious.

## Steps

1. Run `git diff --staged` to see staged changes. If empty, run `git diff HEAD` instead.
2. Analyze the diff: what type of change, what scope, what is the intent.
3. Generate commit message following Conventional Commits.

## Format

```
type(scope): subject
```

Subject ≤50 chars. Imperative mood. No period at end.

**Types:** feat, fix, refactor, perf, test, docs, ci, chore, style, build

**Body** (optional — only if "why" is not obvious from subject):
- One blank line after subject
- Explain motivation / constraint / trade-off
- Not what changed — why

**Never:**
- Emojis (unless user explicitly asks)
- Passive voice
- Multi-paragraph body for simple changes

## Examples

Good:
```
fix(auth): reject expired tokens before handler
```

Good with body:
```
perf(cache): switch LRU to FIFO for write-heavy workloads

LRU caused lock contention under concurrent writes. FIFO eliminates
per-access locking at the cost of slightly lower hit rate.
```

## Output

Print only the commit message. No explanation. No preamble. Just the message, ready to copy-paste.
