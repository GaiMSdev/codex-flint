#!/usr/bin/env python3
"""
flint-validate — post-pass that verifies integrity of compressed output.

Ensures all technical content survived compression intact:
headings, code blocks, inline code, URLs, file paths, numbers.

Usage:
    python3 validate.py <compressed_file> [--original FILE]
    python3 validate.py <compressed_file> --json

Options:
    --original FILE  Path to original file (default: <file>.original.md)
    --json           Output as JSON object

Exit codes:
    0 = all PASS
    1 = one or more FAIL
    2 = invalid arguments / file missing
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from flint_compress import (
    extract_headings,
    extract_code_blocks,
    extract_urls,
    extract_inline_codes,
)


PATH_RE = re.compile(r"(?:\.{0,2}/|~/|/|[A-Za-z]:\\)[^\s,;)\]>\"]*[^\s.,;:)\]>\"'\\]")
NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def validate_file(compressed_path: Path, original_path: Path | None = None) -> dict:
    if original_path is None:
        original_path = compressed_path.with_name(
            compressed_path.stem + ".original.md"
        )

    checks: list[dict] = []
    all_pass = True
    warn_only = False

    # 1. Both files exist and are readable
    if not compressed_path.is_file():
        return {
            "ok": False,
            "checks": [{"name": "files_exist", "passed": False, "detail": f"Compressed file not found: {compressed_path}"}],
            "original_chars": 0,
            "compressed_chars": 0,
            "savings_pct": 0.0,
        }
    if not original_path.is_file():
        return {
            "ok": False,
            "checks": [{"name": "files_exist", "passed": False, "detail": f"Original file not found: {original_path}"}],
            "original_chars": 0,
            "compressed_chars": 0,
            "savings_pct": 0.0,
        }

    try:
        original_text = original_path.read_text(encoding="utf-8", errors="replace")
        compressed_text = compressed_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {
            "ok": False,
            "checks": [{"name": "readable", "passed": False, "detail": str(e)}],
            "original_chars": 0,
            "compressed_chars": 0,
            "savings_pct": 0.0,
        }

    orig_chars = len(original_text)
    comp_chars = len(compressed_text)
    savings_pct = round((orig_chars - comp_chars) / orig_chars * 100, 1) if orig_chars else 0.0

    # 9. Compressed is not empty
    if not compressed_text.strip():
        checks.append({"name": "not_empty", "passed": False, "detail": "Compressed output is empty"})
        all_pass = False
    else:
        checks.append({"name": "not_empty", "passed": True, "detail": ""})

    # 2. Compressed is shorter than original
    if comp_chars >= orig_chars:
        checks.append({
            "name": "length_decreased",
            "passed": False,
            "detail": f"Compressed ({comp_chars} chars) not shorter than original ({orig_chars} chars)"
        })
        warn_only = True
    else:
        checks.append({"name": "length_decreased", "passed": True, "detail": f"{orig_chars} → {comp_chars} chars ({savings_pct:+.1f}%)"})

    # 3. Heading preservation
    h_orig = set(extract_headings(original_text))
    h_comp = set(extract_headings(compressed_text))
    lost_headings = h_orig - h_comp
    if lost_headings:
        checks.append({"name": "headings", "passed": False, "detail": f"Lost headings: {', '.join(sorted(lost_headings)[:5])}"})
        all_pass = False
    else:
        checks.append({"name": "headings", "passed": True, "detail": f"{len(h_orig)} headings preserved"})

    # 4. Code block preservation
    cb_orig = extract_code_blocks(original_text)
    cb_comp = extract_code_blocks(compressed_text)
    if len(cb_orig) != len(cb_comp):
        checks.append({"name": "code_blocks", "passed": False, "detail": f"Count: {len(cb_orig)} → {len(cb_comp)}"})
        all_pass = False
    elif cb_orig != cb_comp:
        checks.append({"name": "code_blocks", "passed": False, "detail": "Code block content changed (must be byte-for-byte identical)"})
        all_pass = False
    else:
        checks.append({"name": "code_blocks", "passed": True, "detail": f"{len(cb_orig)} blocks identical"})

    # 5. Inline code preservation
    ic_orig = sorted(extract_inline_codes(original_text))
    ic_comp = sorted(extract_inline_codes(compressed_text))
    if ic_orig != ic_comp:
        from collections import Counter
        c1, c2 = Counter(ic_orig), Counter(ic_comp)
        lost = set(c1) - set(c2)
        if lost:
            checks.append({"name": "inline_code", "passed": False, "detail": f"Lost inline code: {', '.join(f'`{x}`' for x in sorted(lost)[:10])}"})
            all_pass = False
        else:
            checks.append({"name": "inline_code", "passed": True, "detail": f"{len(ic_orig)} inline codes preserved"})
    else:
        checks.append({"name": "inline_code", "passed": True, "detail": f"{len(ic_orig)} inline codes preserved"})

    # 6. URL preservation
    u_orig = extract_urls(original_text)
    u_comp = extract_urls(compressed_text)
    lost_urls = u_orig - u_comp
    if lost_urls:
        checks.append({"name": "urls", "passed": False, "detail": f"Lost URLs: {', '.join(sorted(lost_urls)[:5])}"})
        all_pass = False
    else:
        checks.append({"name": "urls", "passed": True, "detail": f"{len(u_orig)} URLs preserved"})

    # 7. File path preservation (heuristic)
    p_orig = set(PATH_RE.findall(original_text))
    p_comp = set(PATH_RE.findall(compressed_text))
    lost_paths = p_orig - p_comp
    if lost_paths:
        checks.append({"name": "file_paths", "passed": False, "detail": f"Lost paths: {', '.join(sorted(lost_paths)[:5])}"})
        all_pass = False
    else:
        checks.append({"name": "file_paths", "passed": True, "detail": f"{len(p_orig)} paths preserved"})

    # 8. Number preservation
    n_orig = set(NUM_RE.findall(original_text))
    n_comp = set(NUM_RE.findall(compressed_text))
    lost_nums = n_orig - n_comp
    if lost_nums:
        checks.append({"name": "numbers", "passed": False, "detail": f"Lost numbers: {', '.join(sorted(lost_nums, key=lambda x: float(x))[:10])}"})
        all_pass = False
    else:
        checks.append({"name": "numbers", "passed": True, "detail": f"{len(n_orig)} numbers preserved"})

    if warn_only and all_pass:
        all_pass = False

    return {
        "ok": all_pass,
        "warn_only": warn_only,
        "checks": checks,
        "original_chars": orig_chars,
        "compressed_chars": comp_chars,
        "savings_pct": savings_pct,
    }


def print_results(result: dict) -> None:
    print(f"FLINT-VALIDATE: {result['original_chars']} → {result['compressed_chars']} chars ({result['savings_pct']:+.1f}%)")
    print(f"{'=' * 60}")
    for c in result["checks"]:
        status = "PASS" if c["passed"] else "FAIL"
        detail = f" — {c['detail']}" if c["detail"] else ""
        print(f"  [{status}] {c['name']}{detail}")
    if result.get("warn_only"):
        print(f"\n  ⚠  WARN: length increased — but this is informational, not a data loss")
    verdict = "ALL CHECKS PASSED" if result["ok"] else "SOME CHECKS FAILED"
    print(f"\n{'=' * 60}")
    print(f"  VERDICT: {verdict}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="flint-validate: verify compressed file integrity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("compressed", type=Path, help="Compressed file to validate")
    parser.add_argument("--original", type=Path, default=None, help="Original file (default: <file>.original.md)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = validate_file(args.compressed.resolve(), args.original.resolve() if args.original else None)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_results(result)

    if result["ok"]:
        sys.exit(0)
    elif result.get("warn_only") and all(
        c["passed"] or c["name"] == "length_decreased" for c in result["checks"]
    ):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
