---
name: flint-compress
description: >
  Compress AGENTS.md and memory markdown files to save input tokens on every session start.
  Preserves all technical substance, code, URLs, and structure. Compressed version overwrites
  the original. Human-readable backup saved as FILE.original.md.
  Trigger: /flint-compress <filepath>, "compress AGENTS.md", "compress this file".
---

# FLINT-COMPRESS

## Purpose

Compress natural language files (AGENTS.md, todos, preferences, notes) into terse prose to reduce input tokens. Compressed version overwrites original. Human-readable backup saved as `<filename>.original.md`.

Input token savings compound across every session — every turn that reads the file pays less forever.

## Triggers

- `/flint-compress <filepath>`
- `/flint:compress <filepath>`
- "compress AGENTS.md", "compress this file", "compress [filename]"

## Process

1. Read the target file.
2. Check: if `FILE.original.md` already exists, warn the user and ask before proceeding.
3. Check: reject code/config extensions (`.py .js .ts .json .yaml .yml .toml .env .sh` etc.).
4. Check: reject `*.original.md` files (backup files must not be compressed).
5. Run validation on the original (count headings, code blocks, URLs, inline code — record counts).
6. Compress: apply rules below to prose only. Never touch code blocks, inline code, URLs, paths.
7. Pre-write validation:
   - All headings still present (same count and text)
   - All code blocks still present and unchanged (compare count + content)
   - All URLs still present
   - No inline code lost
   - File is not empty
   - If any check fails: report error, do NOT write, offer to try again.
8. If compressed version is LONGER than original: abort, report.
9. Write backup: `FILE.original.md` (original content, verbatim).
10. Write compressed content back to FILE.
11. Report: original char count, compressed char count, savings %.

## Compression Rules

### Drop
- Articles: a, an, the
- Filler words: just, really, basically, actually, simply, essentially, generally, quite, very
- Pleasantries: "sure", "certainly", "of course", "happy to", "I'd recommend", "please note"
- Hedging phrases: "it might be worth", "you could consider", "it would be good to", "perhaps", "might want to"
- Instruction padding: "you should", "make sure to", "remember to", "be sure to", "don't forget to"
- Connective fluff: however, furthermore, additionally, in addition, moreover
- Redundant phrasing: "in order to" → "to", "the reason is because" → "because"
- Subject openers: drop leading "I" or "We" when it adds no meaning

### Short synonyms
- "big" not "extensive"
- "fix" not "implement a solution for"
- "use" not "utilize"
- "check" not "verify that"
- "run" not "execute"

### Compress prose to fragments
- "You should always run the test suite before pushing" → "Run tests before push"
- Merge redundant bullets that say the same thing differently
- Keep one example where multiple examples show the same pattern

### Preserve Structure (never remove)
- All markdown headings (keep exact heading text, only compress body under them)
- Bullet point hierarchy and nesting levels
- Numbered lists (keep numbering)
- Tables (keep structure, compress cell prose only)
- Frontmatter/YAML headers

## Preserve EXACTLY — Never Touch

### Code blocks
- Everything inside ``` ... ``` must be copied byte-for-byte
- Do NOT: remove comments, reorder lines, shorten commands, simplify anything
- Do NOT merge sections around code blocks
- Treat code blocks as read-only regions

### Inline code
- Everything inside `backticks` preserved exactly
- Never modify anything inside backticks

### Other preserved content
- URLs (`https://`, `http://`) — full URL, exact characters
- File paths (`/usr/...`, `~/...`, `./relative`, `../..`) — exact
- Shell commands, git commands, npm/yarn commands — never shorten
- Technical identifiers: function names, library names, API names, protocols
- Environment variables (`$HOME`, `NODE_ENV`, `ANTHROPIC_API_KEY`)
- Proper nouns: project names, company names, people's names
- Dates, version numbers, numeric values

## Safety Rules

- If file has more code blocks than prose lines: warn "File is mostly code — savings will be minimal". Ask before proceeding.
- If compressed version is LONGER than original: abort, do not write.
- If any validation check fails: do not write, report what failed, offer to try again.
- Never compress `.original.md` files.
- Never compress code/config files (`.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.toml`, `.env`, `.sh`, `.lock`, `.css`, `.html`, `.xml`, `.sql`).

## Script Alternative

A standalone Python script is available at:
`<plugin-dir>/skills/flint-compress/scripts/flint_compress.py`

Run it for deterministic regex-based pre-compression (zero LLM tokens):
```bash
python3 flint_compress.py [--dry-run] [--no-backup] <filepath>
```

## Output Format

```
flint-compress: path/to/file.md
  Before:   4,823 chars
  After:    1,980 chars
  Saved:    2,843 chars (59%)
  Backup:   path/to/file.original.md
```

## Example

**Before (47 tokens):**
> You should always make sure to run the test suite before pushing any changes to the main branch. This is important because it helps catch bugs early and prevents broken builds from being deployed to production.

**After (16 tokens):**
> Run tests before push to main. Catch bugs early, prevent broken prod deploys.
