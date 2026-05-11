#!/usr/bin/env python3
"""
flint-detect — pre-pass scanner that finds compression candidates in a directory tree.

Scans for markdown/prose files that would benefit from flint-compress,
estimates potential savings, and presents ranked candidates.

Usage:
    python3 detect.py [--root DIR] [--min-bytes N] [--json]

Options:
    --root DIR       Root directory to scan (default: cwd)
    --min-bytes N    Skip files smaller than N bytes (default: 1024)
    --json           Output as JSON array instead of table

Exit codes:
    0 = success (may have 0 candidates)
    1 = error
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from flint_compress import should_compress

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build", ".ruff_cache", ".mypy_cache", ".pytest_cache"}
MAX_FILE_BYTES = 1_048_576

FILLER_PATTERNS = re.compile(
    r"\b(?:just|really|basically|actually|simply|essentially|generally|quite|"
    r"however|furthermore|additionally|moreover|nevertheless|nonetheless|"
    r"in order to|make sure to|remember to|be sure to|please|"
    r"it (?:is|'s) (?:important|worth) (?:to|noting)|"
    r"you should|you must|you can|you need to|"
    r"the reason (?:is|was) because)\b",
    re.IGNORECASE,
)

ARTICLE_PATTERNS = re.compile(r"\b(?:a|an|the)\s+", re.IGNORECASE)


def estimate_savings(text: str) -> tuple[int, int, float]:
    """Return (total_words, filler_words, estimated_savings_pct)."""
    words = text.split()
    total = len(words)
    if total == 0:
        return 0, 0, 0.0
    filler = len(FILLER_PATTERNS.findall(text))
    articles = len(ARTICLE_PATTERNS.findall(text))
    removable = filler + articles
    pct = (removable / total) * 100
    return total, removable, round(pct, 1)


def scan(root: Path, min_bytes: int) -> list[dict]:
    """Walk directory tree, return list of candidate dicts."""
    candidates: list[dict] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            fp = Path(dirpath) / name
            if fp.suffix == ".original.md":
                continue
            ok, _reason = should_compress(fp)
            if not ok:
                continue
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            if size < min_bytes:
                continue
            if size > MAX_FILE_BYTES:
                continue
            backup = fp.with_name(fp.stem + ".original.md")
            if backup.exists():
                continue
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            total, removable, pct = estimate_savings(text)
            candidates.append({
                "path": str(fp.resolve()),
                "bytes": size,
                "est_savings_pct": pct,
                "word_count": total,
            })
    candidates.sort(key=lambda c: c["est_savings_pct"], reverse=True)
    return candidates


def print_table(candidates: list[dict]) -> None:
    """Render as pipe-delimited table if ≥3 rows, else prose."""
    if not candidates:
        print("No compression candidates found.")
        return
    if len(candidates) < 3:
        for c in candidates:
            print(f"{c['path']}  [{c['bytes']:,}B, est. ~{c['est_savings_pct']}% savings, {c['word_count']} words]")
        return
    max_path = max(len(c["path"]) for c in candidates)
    max_path = min(max_path, 60)
    header = f"{'Path':<{max_path}} | {'Bytes':>8} | {'Est.%':>6} | Words"
    sep = f"{'-' * max_path}-+-{'-' * 8}-+-{'-' * 6}-+-------"
    print(header)
    print(sep)
    for c in candidates:
        path_display = c["path"] if len(c["path"]) <= max_path else "..." + c["path"][-(max_path - 3):]
        print(f"{path_display:<{max_path}} | {c['bytes']:>8,} | {c['est_savings_pct']:>5.1f}% | {c['word_count']:>7,}")
    print(f"\n{len(candidates)} candidates found.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="flint-detect: find compression candidates in a directory tree.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory to scan (default: cwd)")
    parser.add_argument("--min-bytes", type=int, default=1024, help="Skip files smaller than N bytes (default: 1024)")
    parser.add_argument("--json", action="store_true", help="Output as JSON array")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: Not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    candidates = scan(root, args.min_bytes)

    if args.json:
        print(json.dumps(candidates, indent=2))
    else:
        print_table(candidates)


if __name__ == "__main__":
    main()
