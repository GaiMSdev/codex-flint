#!/usr/bin/env python3
"""
flint-compress — compress prose in markdown files to save input tokens.

Applies deterministic regex-based compression to natural language text,
skipping code blocks, inline code, URLs, file paths, and technical content.

Usage:
    python3 flint_compress.py [--dry-run] [--no-backup] <filepath>

Options:
    --dry-run     Print compressed output without writing any files
    --no-backup   Skip creating FILE.original.md backup (dangerous)

Requires: Python 3.8+, zero external dependencies.
"""

import re
import sys
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# File type detection
# ---------------------------------------------------------------------------

COMPRESSIBLE_EXTENSIONS = {".md", ".txt", ".markdown", ".rst", ".typ", ".typst", ".tex"}

SKIP_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
    ".toml", ".env", ".lock", ".css", ".scss", ".html", ".xml",
    ".sql", ".sh", ".bash", ".zsh", ".go", ".rs", ".java", ".c",
    ".cpp", ".h", ".hpp", ".rb", ".php", ".swift", ".kt", ".lua",
    ".csv", ".ini", ".cfg",
}


def should_compress(filepath: Path) -> tuple[bool, str]:
    """Return (ok, reason). ok=False means skip."""
    if not filepath.is_file():
        return False, "not a file"
    if filepath.name.endswith(".original.md"):
        return False, "backup file — skip"
    ext = filepath.suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return False, f"code/config file ({ext}) — never compress"
    if ext in COMPRESSIBLE_EXTENSIONS:
        return True, "natural language"
    if not ext:
        # Extensionless: heuristic content check
        try:
            text = filepath.read_text(errors="ignore")
        except OSError:
            return False, "unreadable"
        code_lines = sum(
            1 for l in text.splitlines()[:50]
            if re.match(r"^\s*(import |from .+ import |def |class |const |let |var |\{|\})", l)
        )
        non_empty = sum(1 for l in text.splitlines()[:50] if l.strip())
        if non_empty and code_lines / non_empty > 0.4:
            return False, "looks like code (extensionless)"
        return True, "extensionless natural language"
    return False, f"unknown extension ({ext})"


# ---------------------------------------------------------------------------
# Code block tracking
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r"^(\s{0,3})(`{3,}|~{3,})(.*)")


def split_into_regions(text: str) -> list[tuple[str, str]]:
    """Split text into (type, content) regions: 'prose' or 'code'.

    Code regions include the opening fence line, all body lines, and the
    closing fence line. Prose regions are everything else.
    """
    regions: list[tuple[str, str]] = []
    lines = text.split("\n")
    i = 0
    n = len(lines)
    prose_buf: list[str] = []

    while i < n:
        m = FENCE_RE.match(lines[i])
        if m:
            # Flush prose buffer
            if prose_buf:
                regions.append(("prose", "\n".join(prose_buf)))
                prose_buf = []

            fence_char = m.group(2)[0]
            fence_len = len(m.group(2))
            code_buf: list[str] = [lines[i]]
            i += 1
            closed = False

            while i < n:
                close_m = FENCE_RE.match(lines[i])
                if (
                    close_m
                    and close_m.group(2)[0] == fence_char
                    and len(close_m.group(2)) >= fence_len
                    and close_m.group(3).strip() == ""
                ):
                    code_buf.append(lines[i])
                    i += 1
                    closed = True
                    break
                code_buf.append(lines[i])
                i += 1

            regions.append(("code", "\n".join(code_buf)))
            if not closed:
                # Unclosed fence — treat remainder as code to be safe
                pass
        else:
            prose_buf.append(lines[i])
            i += 1

    if prose_buf:
        regions.append(("prose", "\n".join(prose_buf)))

    return regions


# ---------------------------------------------------------------------------
# Inline code protection
# ---------------------------------------------------------------------------

_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def protect_inline_code(text: str) -> tuple[str, dict[str, str]]:
    """Replace inline code spans with stable placeholders. Return (patched, map)."""
    placeholders: dict[str, str] = {}
    counter = [0]

    def replace(m: re.Match) -> str:
        key = f"\x00INLINECODE{counter[0]}\x00"
        counter[0] += 1
        placeholders[key] = m.group(0)
        return key

    patched = _INLINE_CODE_RE.sub(replace, text)
    return patched, placeholders


def restore_inline_code(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


# ---------------------------------------------------------------------------
# URL and path protection
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://[^\s)\]>\"]+")
_PATH_RE = re.compile(r"(?:\.{1,2}/|~/|/)[^\s,;)\]>\"]*[^\s.,;:)\]>\"']")


def protect_technical(text: str) -> tuple[str, dict[str, str]]:
    """Protect URLs and file paths from compression."""
    placeholders: dict[str, str] = {}
    counter = [0]

    def replace(m: re.Match) -> str:
        key = f"\x00TECH{counter[0]}\x00"
        counter[0] += 1
        placeholders[key] = m.group(0)
        return key

    # URLs first, then paths (avoid double-replacing)
    text = _URL_RE.sub(replace, text)
    text = _PATH_RE.sub(replace, text)
    return text, placeholders


def restore_technical(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


# ---------------------------------------------------------------------------
# Compression patterns
# The order matters: apply longer/more-specific patterns first.
# ---------------------------------------------------------------------------

# Each entry: (compiled_pattern, replacement)
COMPRESS_PATTERNS: list[tuple[re.Pattern, str]] = []


def _p(pattern: str, replacement: str, flags: int = re.IGNORECASE) -> None:
    COMPRESS_PATTERNS.append((re.compile(pattern, flags), replacement))


# Redundant multi-word phrases → compact forms
_p(r"\bin order to\b", "to")
_p(r"\bthe reason (?:is |was )?because\b", "because")
_p(r"\bmake sure to\b\s*", "")
_p(r"\bremember to\b\s*", "")
_p(r"\bbe sure to\b\s*", "")
_p(r"\bdon'?t forget to\b\s*", "")
_p(r"\byou should\b\s*", "")
_p(r"\byou must\b\s*", "")
_p(r"\byou can\b\s*", "")
_p(r"\byou need to\b\s*", "")
_p(r"\bplease note that\b\s*", "")
_p(r"\bplease\b\s*", "")
_p(r"\bit(?:'s| is) important to\b\s*", "")
_p(r"\bit(?:'s| is) worth noting that\b\s*", "")
_p(r"\bit might be worth\b\s*", "")
_p(r"\byou could consider\b", "consider")
_p(r"\bit would be good to\b\s*", "")
_p(r"\bwhat you need to do is\b\s*", "")
_p(r"\bthe way to do this is\b\s*", "")
_p(r"\bthis is because\b", "because")

# Connective fluff (standalone words — only when at word boundary)
_p(r"\bhowever[,]?\s*", "")
_p(r"\bfurthermore[,]?\s*", "")
_p(r"\badditionally[,]?\s*", "")
_p(r"\bin addition[,]?\s*", "")
_p(r"\bmoreover[,]?\s*", "")
_p(r"\bnevertheless[,]?\s*", "")
_p(r"\bnonetheless[,]?\s*", "")

# Filler words (only when surrounded by spaces/punctuation — avoid corrupting identifiers)
_p(r"(?<=\s)just(?=\s)", "")
_p(r"(?<=\s)really(?=\s)", "")
_p(r"(?<=\s)basically(?=\s)", "")
_p(r"(?<=\s)actually(?=\s)", "")
_p(r"(?<=\s)simply(?=\s)", "")
_p(r"(?<=\s)essentially(?=\s)", "")
_p(r"(?<=\s)generally(?=\s)", "")
_p(r"(?<=\s)quite(?=\s)", "")

# Articles — only at the START of a bullet/list item, not mid-sentence
# (removing mid-sentence articles is too aggressive and corrupts technical prose)
_p(r"^([-*+>]\s*)(?:The|A|An)\s+", r"\1", re.MULTILINE | re.IGNORECASE)

# Verbose synonyms
_p(r"\butilize\b", "use")
_p(r"\bimplement a solution for\b", "fix")
_p(r"\bextensive\b", "large")
_p(r"\bexecute\b", "run")
_p(r"\bverify that\b", "check")
_p(r"\bensure that\b", "ensure")

# Pleasantries at sentence start
_p(r"^(?:Sure[,.]?\s*|Certainly[,.]?\s*|Of course[,.]?\s*)", "", re.MULTILINE)

# Clean up multiple spaces created by removals
MULTI_SPACE_RE = re.compile(r"  +")
LEADING_SPACE_RE = re.compile(r"^ +", re.MULTILINE)


def compress_prose_line(line: str) -> str:
    """Apply all compression patterns to a single prose line."""
    # Protect inline code and technical content
    line, inline_map = protect_inline_code(line)
    line, tech_map = protect_technical(line)

    # Apply patterns
    for pattern, replacement in COMPRESS_PATTERNS:
        line = pattern.sub(replacement, line)

    # Clean up artifacts from removals
    line = MULTI_SPACE_RE.sub(" ", line)
    line = LEADING_SPACE_RE.sub("", line)
    # Strip trailing spaces
    line = line.rstrip()

    # Restore protected content
    line = restore_technical(line, tech_map)
    line = restore_inline_code(line, inline_map)

    return line


def compress_prose(text: str) -> str:
    """Compress a prose region line by line."""
    lines = text.split("\n")
    compressed = [compress_prose_line(line) for line in lines]
    return "\n".join(compressed)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^#{1,6}\s+.+", re.MULTILINE)
URL_RE = re.compile(r"https?://[^\s)\]>\"]+")
FENCE_OPEN_RE = re.compile(r"^(\s{0,3})(`{3,}|~{3,})(.*)")


def extract_headings(text: str) -> list[str]:
    return HEADING_RE.findall(text)


def extract_code_blocks(text: str) -> list[str]:
    """Extract all fenced code blocks as strings."""
    blocks = []
    lines = text.split("\n")
    i, n = 0, len(lines)
    while i < n:
        m = FENCE_OPEN_RE.match(lines[i])
        if m:
            fence_char = m.group(2)[0]
            fence_len = len(m.group(2))
            buf = [lines[i]]
            i += 1
            while i < n:
                cm = FENCE_OPEN_RE.match(lines[i])
                if cm and cm.group(2)[0] == fence_char and len(cm.group(2)) >= fence_len and cm.group(3).strip() == "":
                    buf.append(lines[i])
                    i += 1
                    break
                buf.append(lines[i])
                i += 1
            blocks.append("\n".join(buf))
        else:
            i += 1
    return blocks


def extract_urls(text: str) -> set[str]:
    return set(URL_RE.findall(text))


def extract_inline_codes(text: str) -> list[str]:
    # Remove fenced blocks first
    no_fences = re.sub(r"```[\s\S]*?```", "", text)
    no_fences = re.sub(r"~~~[\s\S]*?~~~", "", no_fences)
    return re.findall(r"`([^`\n]+)`", no_fences)


class ValidationError(Exception):
    pass


def validate(original: str, compressed: str) -> list[str]:
    """Compare original vs compressed. Return list of error strings (empty = ok)."""
    errors: list[str] = []

    # Headings
    h_orig = extract_headings(original)
    h_comp = extract_headings(compressed)
    if len(h_orig) != len(h_comp):
        errors.append(f"Heading count: {len(h_orig)} → {len(h_comp)} (lost {len(h_orig) - len(h_comp)})")
    elif h_orig != h_comp:
        errors.append("Heading text changed")

    # Code blocks
    cb_orig = extract_code_blocks(original)
    cb_comp = extract_code_blocks(compressed)
    if len(cb_orig) != len(cb_comp):
        errors.append(f"Code block count: {len(cb_orig)} → {len(cb_comp)}")
    elif cb_orig != cb_comp:
        errors.append("Code block content changed (must be byte-for-byte identical)")

    # URLs
    u_orig = extract_urls(original)
    u_comp = extract_urls(compressed)
    lost_urls = u_orig - u_comp
    if lost_urls:
        errors.append(f"URLs lost: {', '.join(sorted(lost_urls))}")

    # Inline code
    ic_orig = sorted(extract_inline_codes(original))
    ic_comp = sorted(extract_inline_codes(compressed))
    if ic_orig != ic_comp:
        from collections import Counter
        c1, c2 = Counter(ic_orig), Counter(ic_comp)
        lost = set(c1) - set(c2)
        if lost:
            errors.append(f"Inline code lost: {', '.join(f'`{x}`' for x in sorted(lost))}")

    # Not empty
    if not compressed.strip():
        errors.append("Compressed output is empty")

    # Not longer
    if len(compressed) > len(original):
        errors.append(
            f"Compressed ({len(compressed)} chars) is longer than original ({len(original)} chars)"
        )

    return errors


# ---------------------------------------------------------------------------
# Code-heavy file detection
# ---------------------------------------------------------------------------

def code_ratio(text: str) -> float:
    """Fraction of non-empty lines that are inside code blocks."""
    regions = split_into_regions(text)
    code_lines = sum(
        len([l for l in r[1].split("\n") if l.strip()])
        for r in regions if r[0] == "code"
    )
    prose_lines = sum(
        len([l for l in r[1].split("\n") if l.strip()])
        for r in regions if r[0] == "prose"
    )
    total = code_lines + prose_lines
    return code_lines / total if total else 0.0


# ---------------------------------------------------------------------------
# Main compression entry point
# ---------------------------------------------------------------------------

def compress_text(text: str) -> str:
    """Compress a full markdown document."""
    regions = split_into_regions(text)
    parts: list[str] = []
    for region_type, content in regions:
        if region_type == "code":
            parts.append(content)  # copy exactly
        else:
            parts.append(compress_prose(content))
    return "\n".join(parts)


def compress_file(filepath: Path, dry_run: bool = False, no_backup: bool = False) -> None:
    """Compress a markdown file in place."""
    filepath = filepath.resolve()

    # Existence
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    if not filepath.is_file():
        print(f"ERROR: Not a file: {filepath}")
        sys.exit(1)

    # Type check
    ok, reason = should_compress(filepath)
    if not ok:
        print(f"SKIP: {filepath.name} — {reason}")
        sys.exit(0)

    # Read
    original = filepath.read_text(encoding="utf-8", errors="replace")

    if not original.strip():
        print("ERROR: File is empty or whitespace-only. Nothing to compress.")
        sys.exit(1)

    # Code-heavy warning
    ratio = code_ratio(original)
    if ratio > 0.6:
        print(f"WARNING: {ratio:.0%} of non-empty lines are inside code blocks.")
        print("Savings will be minimal — most content is already code.")
        if not dry_run:
            answer = input("Proceed anyway? [y/N] ").strip().lower()
            if answer != "y":
                print("Aborted.")
                sys.exit(0)

    # Backup check
    backup_path = filepath.with_name(filepath.stem + ".original.md")
    if backup_path.exists() and not dry_run:
        print(f"WARNING: Backup already exists: {backup_path}")
        print("Overwriting backup will destroy the previous original.")
        answer = input("Overwrite backup and re-compress? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            sys.exit(0)

    # Compress
    compressed = compress_text(original)

    # Validate
    errors = validate(original, compressed)
    if errors:
        print("VALIDATION FAILED — not writing output.")
        for e in errors:
            print(f"  - {e}")
        sys.exit(2)

    # Stats
    orig_chars = len(original)
    comp_chars = len(compressed)
    saved = orig_chars - comp_chars
    pct = saved / orig_chars * 100 if orig_chars else 0

    if dry_run:
        print("--- DRY RUN (no files written) ---")
        print(compressed)
        print()
        print(f"Before:  {orig_chars:,} chars")
        print(f"After:   {comp_chars:,} chars")
        print(f"Saved:   {saved:,} chars ({pct:.1f}%)")
        return

    # Write backup
    if not no_backup:
        backup_path.write_text(original, encoding="utf-8")
        # Verify backup
        if backup_path.read_text(encoding="utf-8", errors="replace") != original:
            print("ERROR: Backup verification failed. Aborting before touching original.")
            backup_path.unlink(missing_ok=True)
            sys.exit(1)

    # Write compressed
    filepath.write_text(compressed, encoding="utf-8")

    print(f"flint-compress: {filepath}")
    print(f"  Before:  {orig_chars:,} chars")
    print(f"  After:   {comp_chars:,} chars")
    print(f"  Saved:   {saved:,} chars ({pct:.1f}%)")
    if not no_backup:
        print(f"  Backup:  {backup_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="flint-compress: compress prose in markdown files to save input tokens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 flint_compress.py CLAUDE.md
  python3 flint_compress.py --dry-run docs/preferences.md
  python3 flint_compress.py --no-backup /tmp/test.md
""",
    )
    parser.add_argument("filepath", type=Path, help="Markdown file to compress")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print compressed output without writing files",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating FILE.original.md backup (dangerous)",
    )
    args = parser.parse_args()

    compress_file(args.filepath, dry_run=args.dry_run, no_backup=args.no_backup)


if __name__ == "__main__":
    main()
