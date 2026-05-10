---
name: flint-compress
description: >
  Compress natural language memory files (AGENTS.md, todos, preferences, notes) to save
  input tokens. Preserves all technical substance, code, URLs, and structure.
  Compressed version overwrites the original. Backup saved as FILE.original.md.
  Trigger: /flint:compress FILEPATH or "compress this file"
---

# Flint Compress

## Purpose

Compress natural language files into terse prose to reduce input tokens on every future turn. Compressed version overwrites original. Backup saved as `<filename>.original.md`.

Input token savings compound across the entire session — every turn that reads the file pays less.

## Trigger

`/flint:compress <filepath>` or when user asks to compress a memory/context file.

## Process

1. Read the target file.
2. Compress it according to the rules below.
3. Write the compressed version back to the original path.
4. Save the original as `<filepath>.original.md`.
5. Report: original size, compressed size, % reduction.

## Compression Rules

### Remove
- Articles: a, an, the
- Filler: just, really, basically, actually, simply, essentially, generally
- Pleasantries: sure, certainly, of course, happy to
- Hedging: it might be worth, you could consider, it would be good to
- Redundant phrasing: "in order to" → "to", "make sure to" → "ensure"
- Connective fluff: however, furthermore, additionally, in addition

### Preserve EXACTLY
- Code blocks (``` fenced and indented)
- Inline code (`backtick content`)
- URLs and links
- File paths
- Commands (shell, git, npm — never shorten)
- Technical terms (library names, API names, protocols)
- Proper nouns (project names, companies)
- Dates, version numbers, numeric values
- Environment variables

### Compress
- Short synonyms: "big" not "extensive", "fix" not "implement a solution for"
- Fragments OK: "Run tests before commit" not "You should always run tests before committing"
- Drop "you should", "make sure to", "remember to" — state the action directly
- Merge redundant bullets that repeat the same point

### Never Touch
- `.py .js .ts .json .yaml .yml .toml .env .sh` — never compress code files
- Files with `.original.md` suffix — skip them
- Code blocks — read-only, copy exactly

## Example

**Before (47 tokens):**
> You should always make sure to run the test suite before pushing any changes. This is important because it helps catch bugs early.

**After (16 tokens):**
> Run tests before push. Catch bugs early.

## Output Format

```
Compressed: path/to/file.md
  Before: 1,240 tokens (~4,800 chars)
  After:    510 tokens (~1,980 chars)
  Saved:    730 tokens (59%)
  Backup: path/to/file.md.original.md
```
