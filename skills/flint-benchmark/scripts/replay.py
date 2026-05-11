#!/usr/bin/env python3
"""
flint-replay — Replay real session transcripts to measure compression savings.

Scans ~/.claude/projects/ for transcript JSONL files, extracts user prompts,
and estimates FLINT compression savings using benchmark-derived ratios.

Two modes:
  --estimate  Use known compression ratios (fast, no API cost)
  --replay    Actually call API for true token counts (needs ANTHROPIC_API_KEY)

Usage:
    python3 replay.py [--dir DIR] [--estimate] [--replay] [--min-turns 5] [--json]

Output:
    Per-session + aggregated savings with 95% confidence interval
"""

import argparse
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Compression ratios (from benchmark_results.json — output-side savings vs baseline)
# ---------------------------------------------------------------------------
COMPRESSION_RATIOS = {
    "lite": 0.30,
    "full": 0.54,
    "ultra": 0.63,
    "wenyan": 0.71,
    "flint_compact": 0.57,
}

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

try:
    import anthropic
except ImportError:
    anthropic = None


def redact_pii(text: str) -> str:
    """Redact common PII patterns from transcript text."""
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', text)
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[CARD]', text)
    text = re.sub(r'\b[A-Z]{2}-\d{6,}\b', '[PASSPORT]', text)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    text = re.sub(r'(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*\S+', r'\1: [REDACTED]', text)
    return text


def extract_turns(transcript_path: Path) -> list[dict]:
    """Extract user / assistant turn pairs from a transcript JSONL.

    Returns list of {user_text, assistant_text, tool_calls, tokens_in, tokens_out}.
    """
    lines = []
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if raw:
                try:
                    lines.append(json.loads(raw))
                except json.JSONDecodeError:
                    continue

    turns: list[dict] = []
    current_user: str | None = None
    current_tool_calls: int = 0
    current_tokens_in: int = 0
    current_tokens_out: int = 0
    assistant_parts: list[str] = []

    for entry in lines:
        t = entry.get("type", "")
        msg = entry.get("message", {})

        if t == "user":
            if current_user is not None:
                turns.append({
                    "user_text": current_user,
                    "assistant_text": " ".join(assistant_parts),
                    "tool_calls": current_tool_calls,
                    "tokens_in": current_tokens_in,
                    "tokens_out": current_tokens_out,
                })
            current_user = msg.get("content", "") if isinstance(msg, dict) else ""
            current_tool_calls = 0
            current_tokens_in = 0
            current_tokens_out = 0
            assistant_parts = []

            # Extract token usage if present
            usage = entry.get("usage") or msg.get("usage") or {}
            current_tokens_in = usage.get("input_tokens", 0) or 0

        elif t == "assistant":
            content = msg.get("content", []) if isinstance(msg, dict) else []
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        assistant_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        current_tool_calls += 1
                        if block.get("input") and isinstance(block["input"], dict):
                            assistant_parts.append(json.dumps(block["input"], ensure_ascii=False))

            usage = msg.get("usage", {})
            current_tokens_out = usage.get("output_tokens", 0) or 0

    if current_user is not None:
        turns.append({
            "user_text": current_user,
            "assistant_text": " ".join(assistant_parts),
            "tool_calls": current_tool_calls,
            "tokens_in": current_tokens_in,
            "tokens_out": current_tokens_out,
        })

    return turns


def estimate_token_count(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 chars for English text."""
    return len(text) // 4


def analyze_estimate(turns: list[dict], mode: str) -> dict:
    """Estimate savings using known compression ratios (no API call)."""
    ratio = COMPRESSION_RATIOS.get(mode, 0.50)
    total_in = sum(t.get("tokens_in", 0) or estimate_token_count(t["user_text"]) for t in turns)
    total_out = sum(t.get("tokens_out", 0) or estimate_token_count(t["assistant_text"]) for t in turns)
    flint_out = int(total_out * (1 - ratio))
    saved_out = total_out - flint_out

    return {
        "mode": mode,
        "total_turns": len(turns),
        "baseline_input_tokens": total_in,
        "baseline_output_tokens": total_out,
        "baseline_total_tokens": total_in + total_out,
        "flint_output_tokens": flint_out,
        "flint_total_tokens": total_in + flint_out,
        "output_savings_pct": round(saved_out / total_out * 100, 1) if total_out else 0.0,
        "total_savings_pct": round(saved_out / (total_in + total_out) * 100, 1) if (total_in + total_out) else 0.0,
        "method": "estimate",
    }


def analyze_replay(turns: list[dict], mode: str) -> dict:
    """Replay prompts against API with mode instructions to measure actual savings.

    Requires ANTHROPIC_API_KEY and anthropic SDK.
    """
    if not anthropic:
        return {"error": "anthropic SDK not installed. pip3 install anthropic", "method": "replay"}

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    mode_instruction = {
        "full": "Reply concisely. Omit articles (a/an/the), filler, pleasantries. Use fragments. Be brief.",
        "ultra": "Abbreviate prose. Use arrows for causality. Maximal density.",
        "lite": "Drop filler words. Keep standard grammar and articles.",
    }.get(mode, "Reply concisely.")

    total_baseline_out = 0
    total_flint_out = 0
    total_in = 0

    for turn in turns:
        user_text = turn["user_text"]
        if not user_text.strip():
            continue

        try:
            # Baseline: no system prompt
            r0 = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": user_text}],
            )
            baseline_out = r0.usage.output_tokens
            total_in += r0.usage.input_tokens

            # FLINT: with mode instruction
            r1 = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=mode_instruction,
                messages=[{"role": "user", "content": user_text}],
            )
            flint_out = r1.usage.output_tokens

            total_baseline_out += baseline_out
            total_flint_out += flint_out

            time.sleep(0.2)  # rate limit

        except Exception as e:
            print(f"    API error: {e}", file=sys.stderr)
            continue

    saved = total_baseline_out - total_flint_out
    return {
        "mode": mode,
        "total_turns": len(turns),
        "baseline_input_tokens": total_in,
        "baseline_output_tokens": total_baseline_out,
        "baseline_total_tokens": total_in + total_baseline_out,
        "flint_output_tokens": total_flint_out,
        "flint_total_tokens": total_in + total_flint_out,
        "output_savings_pct": round(saved / total_baseline_out * 100, 1) if total_baseline_out else 0.0,
        "total_savings_pct": round(saved / (total_in + total_baseline_out) * 100, 1) if (total_in + total_baseline_out) else 0.0,
        "method": "replay",
    }


def mean_ci(values: list[float]) -> tuple[float, float, float]:
    """Return (mean, half_width, n) for 95% CI using Student's t."""
    n = len(values)
    if n < 2:
        return (values[0] if values else 0.0, 0.0, n)
    avg = sum(values) / n
    variance = sum((v - avg) ** 2 for v in values) / (n - 1)
    std = math.sqrt(variance)
    # t-value for 95% CI: approx 1.96 for large n, use proper table for small n
    t_table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
    t = min(t_table.get(n, 1.96), 12.706)
    half = t * std / math.sqrt(n)
    return (round(avg, 1), round(half, 1), n)


def print_session_table(results: list[dict]) -> None:
    """Render results as pipe table if >= 3 rows."""
    if len(results) < 3:
        for r in results:
            fn = Path(r.get("file", "?")).name
            print(f"  {fn}: {r['baseline_total_tokens']:,} → {r.get('flint_total_tokens', 0):,} ({r['output_savings_pct']:+.1f}%)")
        return

    header = f"{'Session':<12} | {'Mode':<8} | {'Baseline':>8} | {'FLINT':>8} | {'Savings':>7} | Method"
    sep = f"{'-' * 12}-+-{'-' * 8}-+-{'-' * 8}-+-{'-' * 8}-+-{'-' * 7}-+--------"
    print(header)
    print(sep)
    for r in results:
        fn = Path(r.get("file", "?")).name[:10]
        print(f"{fn:<12} | {r['mode']:<8} | {r['baseline_total_tokens']:>8,} | {r.get('flint_total_tokens', 0):>8,} | {r['output_savings_pct']:>+6.1f}% | {r.get('method', 'est')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="FLINT replay — measure compression savings from real transcripts.")
    parser.add_argument("--dir", type=Path, default=Path.home() / ".claude" / "projects",
                        help="Directory containing transcript JSONL files (default: ~/.claude/projects)")
    parser.add_argument("--min-turns", type=int, default=5, help="Minimum turns per session (default: 5)")
    parser.add_argument("--max-sessions", type=int, default=50, help="Max sessions to analyze (default: 50)")
    parser.add_argument("--mode", default="full", choices=list(COMPRESSION_RATIOS.keys()) + ["all"],
                        help="FLINT mode to test (default: full)")
    parser.add_argument("--estimate", action="store_true", help="Use benchmark ratios for estimation (fast)")
    parser.add_argument("--replay", action="store_true",
                        help="Actual API replay (needs ANTHROPIC_API_KEY, costs money)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--redact", action="store_true", help="Redact PII from extracted prompts (for sharing)")
    args = parser.parse_args()

    if not args.estimate and not args.replay:
        args.estimate = True

    if args.replay and not ANTHROPIC_API_KEY:
        print("ERROR: --replay requires ANTHROPIC_API_KEY", file=sys.stderr)
        sys.exit(1)

    # ── Collect sessions ────────────────────────────────────────────────────
    project_root = args.dir.resolve()
    session_files: list[Path] = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d != "subagents"]
        for f in files:
            if f.endswith(".jsonl"):
                session_files.append(Path(root) / f)

    session_files.sort(key=lambda p: p.stat().st_size, reverse=True)
    session_files = [f for f in session_files if f.stat().st_size > 4096]

    if len(session_files) > args.max_sessions:
        session_files = session_files[:args.max_sessions]

    # ── Analyze ─────────────────────────────────────────────────────────────
    results: list[dict] = []
    modes = list(COMPRESSION_RATIOS.keys()) if args.mode == "all" else [args.mode]
    skipped = 0

    for sf in session_files:
        turns = extract_turns(sf)
        if len(turns) < args.min_turns:
            skipped += 1
            continue

        if args.redact:
            for t in turns:
                t["user_text"] = redact_pii(t["user_text"])
                t["assistant_text"] = redact_pii(t["assistant_text"])

        for mode in modes:
            if args.estimate:
                r = analyze_estimate(turns, mode)
            elif args.replay:
                r = analyze_replay(turns, mode)
            else:
                continue
            r["file"] = str(sf)
            r["turns"] = len(turns)
            results.append(r)

        if len(results) >= args.max_sessions * len(modes):
            break

    # ── Aggregate ───────────────────────────────────────────────────────────
    if not results:
        print("No sessions found matching criteria.")
        sys.exit(0)

    # Group by mode for aggregation
    by_mode: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_mode[r["mode"]].append(r)

    aggregates = {}
    for mode, mode_results in by_mode.items():
        savings = [r["output_savings_pct"] for r in mode_results]
        total_tokens = [r["baseline_total_tokens"] for r in mode_results]
        avg, ci_half, n = mean_ci(savings)
        total_baseline = sum(r["baseline_total_tokens"] for r in mode_results)
        total_flint = sum(r.get("flint_total_tokens", 0) for r in mode_results)
        total_saved_pct = round((total_baseline - total_flint) / total_baseline * 100, 1) if total_baseline else 0.0
        aggregates[mode] = {
            "n_sessions": n,
            "mean_output_savings_pct": avg,
            "ci_95_half_width": ci_half,
            "ci_95_lower": round(avg - ci_half, 1),
            "ci_95_upper": round(avg + ci_half, 1),
            "total_baseline_tokens": total_baseline,
            "total_flint_tokens": total_flint,
            "total_savings_pct": total_saved_pct,
            "min_turns_filter": args.min_turns,
            "method": "estimate" if args.estimate else "replay",
        }

    # ── Output ──────────────────────────────────────────────────────────────
    if args.json:
        output = {
            "sessions": results,
            "aggregates": aggregates,
            "config": {
                "mode": args.mode,
                "min_turns": args.min_turns,
                "n_files_scanned": len(session_files),
                "skipped": skipped,
                "method": "estimate" if args.estimate else "replay",
            },
        }
        print(json.dumps(output, indent=2, default=str))
        return

    print(f"\nFLINT-REPLAY — {args.dir}")
    print(f"  Scanned {len(session_files)} files ({skipped} skipped, <{args.min_turns} turns)")
    print(f"  Method: {'estimate' if args.estimate else 'replay'}")
    print(f"  Mode(s): {', '.join(modes)}")
    print()

    print_session_table(results)

    print(f"\n{'=' * 60}")
    print("AGGREGATE RESULTS")
    print(f"{'=' * 60}")
    for mode, agg in sorted(aggregates.items()):
        print(f"\n  [{mode}] {agg['n_sessions']} sessions")
        print(f"    Mean output savings:  {agg['mean_output_savings_pct']:+.1f}%  "
              f"(95% CI: {agg['ci_95_lower']:+.1f}% to {agg['ci_95_upper']:+.1f}%)")
        print(f"    Total tokens:         {agg['total_baseline_tokens']:,} → {agg['total_flint_tokens']:,} "
              f"({agg['total_savings_pct']:+.1f}%)")


if __name__ == "__main__":
    main()
