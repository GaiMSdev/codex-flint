#!/usr/bin/env python3
"""
flint-pipeline — run detect → compress → validate in a single pass.

Scans a directory tree for compression candidates, optionally compresses
the top-N with validation, and reports results.

Usage:
    python3 run_pipeline.py [--root DIR] [--apply] [--top N]

Options:
    --root DIR   Root directory to scan (default: cwd)
    --apply      Actually run compression + validation
    --top N      Limit to top N candidates (default: 10)

Exit codes:
    0 = all OK (or dry-run with candidates found)
    1 = errors during pipeline execution
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DETECT_PY = SCRIPT_DIR / "detect.py"
COMPRESS_PY = SCRIPT_DIR / "flint_compress.py"
VALIDATE_PY = SCRIPT_DIR / "validate.py"


def run_detect(root: Path, min_bytes: int = 512) -> list[dict]:
    """Run detect.py --json and parse output."""
    result = subprocess.run(
        [sys.executable, str(DETECT_PY), "--root", str(root),
         "--min-bytes", str(min_bytes), "--json"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"ERROR: detect.py failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    try:
        candidates = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"ERROR: detect.py output not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    return candidates


def run_compress(filepath: Path) -> dict:
    """Run flint_compress.py on a file. Returns {ok, original_chars, compressed_chars, savings_pct}."""
    result = subprocess.run(
        [sys.executable, str(COMPRESS_PY), str(filepath)],
        capture_output=True, text=True, timeout=120,
    )
    ok = result.returncode == 0
    # Parse output for stats
    original_chars = compressed_chars = 0
    savings_pct = 0.0
    for line in result.stdout.split("\n"):
        if "Before:" in line:
            try:
                original_chars = int(line.split()[1].replace(",", ""))
            except (ValueError, IndexError):
                pass
        elif "After:" in line:
            try:
                compressed_chars = int(line.split()[1].replace(",", ""))
            except (ValueError, IndexError):
                pass
        elif "Saved:" in line:
            try:
                pct_str = line.split("(")[-1].rstrip(")").replace("%", "")
                savings_pct = float(pct_str)
            except (ValueError, IndexError):
                pass
    return {
        "ok": ok,
        "original_chars": original_chars,
        "compressed_chars": compressed_chars,
        "savings_pct": savings_pct,
        "stderr": result.stderr.strip(),
    }


def run_validate(filepath: Path) -> dict:
    """Run validate.py --json on a file. Returns {ok, checks, ...}."""
    result = subprocess.run(
        [sys.executable, str(VALIDATE_PY), str(filepath), "--json"],
        capture_output=True, text=True, timeout=30,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"ok": False, "checks": [], "error": result.stderr.strip()}
    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="flint-pipeline: detect → compress → validate in one pass.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory (default: cwd)")
    parser.add_argument("--apply", action="store_true", help="Actually run compression + validation")
    parser.add_argument("--top", type=int, default=10, help="Limit to top N candidates (default: 10)")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: Not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"FLINT-PIPELINE: {root}")
    print(f"{'=' * 60}")
    print(f"Running detect.py...")

    detect_start = time.time()
    candidates = run_detect(root)
    detect_elapsed = time.time() - detect_start

    if not candidates:
        print("No compression candidates found.")
        sys.exit(0)

    total_est_savings = sum(c["est_savings_pct"] for c in candidates)
    avg_est = total_est_savings / len(candidates)
    total_bytes = sum(c["bytes"] for c in candidates)

    top_n = candidates[:args.top]
    print(f"\nDetected {len(candidates)} candidates ({detect_elapsed:.1f}s)")
    print(f"Total bytes: {total_bytes:,}")
    print(f"Average estimated savings: {avg_est:.1f}%")
    print(f"Top {args.top} estimated total: {sum(c['est_savings_pct'] for c in top_n):.1f}% cumulative")

    if not args.apply:
        print(f"\n{'=' * 60}")
        print(f"DRY-RUN — use --apply to actually compress")
        print(f"{'=' * 60}")
        print(f"{'Path':<60} {'Bytes':>8} {'Est.%':>6}")
        print(f"{'-' * 60}-+-{'-' * 8}-+-{'-' * 6}")
        for c in top_n:
            path_display = c["path"] if len(c["path"]) <= 58 else "..." + c["path"][-55:]
            print(f"{path_display:<60} {c['bytes']:>8,} {c['est_savings_pct']:>5.1f}%")
        print(f"\nTo compress: run with --apply")
        return

    # ── APPLY mode ──────────────────────────────────────────────────────────
    results: list[dict] = []
    errors = 0

    print(f"\n{'=' * 60}")
    print(f"APPLY — compressing top {len(top_n)} candidates")
    print(f"{'=' * 60}")

    for i, c in enumerate(top_n):
        fp = Path(c["path"])
        print(f"\n  [{i + 1}/{len(top_n)}] {fp.name}")

        # Security: skip if file changed since detect pass
        try:
            current_mtime = fp.stat().st_mtime
        except OSError:
            print(f"    SKIP: cannot stat file")
            results.append({**c, "compress_ok": False, "validate_ok": False, "skip_reason": "cannot stat"})
            continue

        # Compress
        comp = run_compress(fp)
        if not comp["ok"]:
            print(f"    COMPRESS FAILED")
            print(f"      {comp['stderr'][:200] if comp['stderr'] else '(no stderr)'}")
            results.append({**c, **comp, "validate_ok": False})
            errors += 1
            continue

        orig = comp["original_chars"]
        comp_chars = comp["compressed_chars"]
        saved = comp["savings_pct"]
        print(f"    compressed: {orig:,} → {comp_chars:,} chars ({saved:+.1f}%)")

        # Validate
        val = run_validate(fp)
        val_ok = val.get("ok", False)
        if not val_ok:
            failed = [ch["name"] for ch in val.get("checks", []) if not ch["passed"]]
            print(f"    VALIDATE FAILED: {', '.join(failed)}")
            print(f"      Backup preserved at {fp}.original.md — manual restore: cp {fp}.original.md {fp}")
            results.append({**c, **comp, "validate_ok": False, "validate_fails": failed})
            errors += 1
        else:
            print(f"    validate PASSED")
            results.append({**c, **comp, "validate_ok": True})

    # ── Final report ────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"PIPELINE RESULTS")
    print(f"{'=' * 60}")

    total_orig = sum(r.get("original_chars", 0) for r in results if r.get("compress_ok", False))
    total_comp = sum(r.get("compressed_chars", 0) for r in results if r.get("compress_ok", False))
    compress_count = sum(1 for r in results if r.get("compress_ok", False))

    if compress_count >= 3:
        header = f"{'File':<50} | {'Before':>7} | {'After':>7} | {'Savings':>7} | Validate"
        sep = f"{'-' * 50}-+-{'-' * 7}-+-{'-' * 7}-+-{'-' * 7}-+---------"
        print(header)
        print(sep)
        for r in results:
            name = Path(r["path"]).name
            name_display = name if len(name) <= 48 else name[:45] + "..."
            before = r.get("original_chars", 0)
            after = r.get("compressed_chars", 0)
            svg = f"{r.get('savings_pct', 0):+.1f}%" if r.get("compress_ok", False) else "FAIL"
            val = "PASS" if r.get("validate_ok", False) else ("FAIL" if r.get("compress_ok") else "-")
            print(f"{name_display:<50} | {before:>7,} | {after:>7,} | {svg:>7} | {val}")
    else:
        for r in results:
            name = Path(r["path"]).name
            svg = f"{r.get('savings_pct', 0):+.1f}%" if r.get("compress_ok", False) else "FAIL"
            val = "PASS" if r.get("validate_ok", False) else ("FAIL" if r.get("compress_ok") else "-")
            print(f"{name}: {r.get('original_chars', 0):,} → {r.get('compressed_chars', 0):,} ({svg}, {val})")

    if total_orig > 0:
        total_saved = total_orig - total_comp
        total_pct = total_saved / total_orig * 100
        success_count = sum(1 for r in results if r.get("validate_ok", False))
        print(f"\n  Total: {total_orig:,} → {total_comp:,} chars ({total_pct:+.1f}%)")
        print(f"  Files: {compress_count} compressed, {success_count} validated OK, {errors} errors")
    else:
        print(f"  No files were successfully compressed.")
        print(f"  Errors: {errors}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
