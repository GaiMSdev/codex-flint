---
name: flint-delegate
description: >
  Delegate investigate/build/review tasks to compressed cavecrew subagents
  (caveman:cavecrew-investigator, caveman:cavecrew-builder,
  caveman:cavecrew-reviewer). Use when the task is focused enough for a
  single-shot subagent and would benefit from caveman-compressed output.
  Triggers: "delegate investigate", "delegate build", "delegate review",
  "cavecrew that", "spawn investigator", "/flint-delegate".
---

# Flint Delegate — Cavecrew Subagent Dispatch

Dispatch a focused task to a compressed cavecrew subagent. Each subagent type
has a restricted tool set and a fixed output contract. Always append the
compression instruction to the prompt.

## Global compression instruction

Append this to EVERY subagent prompt:

```
Return caveman-compressed output. Drop articles, use fragments.
```

---

## Investigate — `caveman:cavecrew-investigator`

**Tools:** Read, Grep, Glob, Bash (read-only)
**Use when:** You need to explore code, find patterns, check if something exists.
**Output contract:** One line per finding — `path:line: — symbol/finding` table.
No explanation, no summary, no narrative.

```
Agent(
  subagent_type="caveman:cavecrew-investigator",
  prompt=f"""Investigate: <what to look for and where>

Output format:
path/to/file.py:42: — UserAuthenticator
path/to/file.py:89: — token_expiry_check

Return caveman-compressed output. Drop articles, use fragments."""
)
```

### When to use

- "Find all places where we read the flag file"
- "Check if there are any hardcoded credentials in src/"
- "Map all database queries in this module"

---

## Build — `caveman:cavecrew-builder`

**Tools:** Read, Edit, Write (surgical — 1-2 files max)
**Use when:** A focused, well-defined code change. Not for exploratory work.
**Output contract:** Diff receipt — max 3 lines of `path:line: changed X to Y`.
No explanation of why — diff speaks for itself.

```
Agent(
  subagent_type="caveman:cavecrew-builder",
  prompt=f"""Build: <exact change to make, in what file>

Output format:
path/to/file.py:14: changed MAX_FLAG_BYTES = 32 to MAX_FLAG_BYTES = 64
path/to/file.py:22: changed fs.openSync(fp, O_RDONLY) to fs.openSync(fp, O_RDONLY | O_NOFOLLOW)

Return caveman-compressed output. Drop articles, use fragments."""
)
```

### When to use

- "Add O_NOFOLLOW to flag file read in src/flag.ts"
- "Rename function validateToken to verifyToken in auth.py"
- "Bump version from 1.2.3 to 1.3.0 in package.json"

### Rules

- Never build without an investigate first (unless the change is trivial and the
  path is unambiguous).
- The prompt must specify the exact file path and exact change. Ambiguity →
  broken output.

---

## Review — `caveman:cavecrew-reviewer`

**Tools:** Read, Grep, Bash (read-only, analysis only)
**Use when:** Code needs a second set of eyes — security, logic, correctness.
**Output contract:** One line per finding:
`path:line: <severity>: <problem>. <fix>.`
No praise, no scope creep, max 10 findings sorted by severity.

```
Agent(
  subagent_type="caveman:cavecrew-reviewer",
  prompt=f"""Review: <what to review and what to check for>

Output format:
path/to/file.py:14: CRITICAL: hardcoded secret. use env var.
path/to/file.py:22: WARN: O_NOFOLLOW missing. add flag.
path/to/file.py:89: NOTE: unused import. remove.

Return caveman-compressed output. Drop articles, use fragments."""
)
```

### When to use

- Before committing any security-critical change
- After a build task — verify the change is correct
- When the user asks "does this look right?"

---

## Flow: investigate → build → review (the standard pipeline)

```
1. INVESTIGATE — map the territory
   caveman:cavecrew-investigator → path:line: — symbol table

2. BUILD — make the change
   caveman:cavecrew-builder → diff receipt (≤3 lines)

3. REVIEW — verify correctness
   caveman:cavecrew-reviewer → severity-tagged findings

Each step uses the previous step's output as context for the next prompt.
```

## Anti-patterns

- DO NOT delegate "investigate everything wrong with this project" — too broad.
  Be specific: "investigate O_NOFOLLOW usage in flag.ts".
- DO NOT delegate build without specifying exact file path and exact change.
- DO NOT skip review for security-critical changes.
- DO NOT use caveman:cavecrew-builder for multi-file refactors — it's limited
  to 1-2 files.
