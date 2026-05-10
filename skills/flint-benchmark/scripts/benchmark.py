#!/usr/bin/env python3
"""
CODEX-FLINT benchmark.

Local-only benchmark against Caveman/RUNES-style mode rules and deterministic
ultra retention fixtures. No model calls; this measures implementation surface,
estimated savings, and whether the ultra rules retain critical facts in sample
compressed outputs.
"""

from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HOME = Path.home()
CODEX_DIR = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))
SESSION_DIR = CODEX_DIR / "sessions"
FLINT_ROOT = Path(__file__).resolve().parents[3]
GEM_THAL_ROOTS = [
    HOME / ".gemini" / "extensions" / "gem-thal",
    HOME / "Xcode Prosjekter" / "GEM-THAL",
]
CAVEMAN_ROOTS = [
    HOME / ".agents" / "extensions" / "codex-caveman",
    HOME / ".claude" / "plugins" / "cache" / "caveman",
    HOME / ".claude" / "plugins" / "data" / "caveman-caveman",
]

FLINT_RATIOS = {"lite": 0.30, "full": 0.54, "ultra": 0.68}  # wenyan: no data
RUNES_RATIOS = {"lite": 0.35, "full": 0.54, "ultra": 0.69}  # wenyan: no data
CAVEMAN_RATIOS = {"full": 0.54, "ultra": 0.69}


@dataclass
class TokenTotals:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class RetentionCase:
    name: str
    source: str
    compressed: str
    required: tuple[str, ...]


@dataclass
class CorpusCase:
    name: str
    text: str
    required: tuple[str, ...]


RETENTION_CASES = [
    RetentionCase(
        name="auth regression",
        source=(
            "File src/auth/session.ts line 42 rejects expired JWTs before "
            "refreshToken(). Preserve error code AUTH_EXPIRED and timeout 5000ms."
        ),
        compressed="src/auth/session.ts:42 rejects expired JWT before refreshToken(). Keep AUTH_EXPIRED, timeout 5000ms.",
        required=("src/auth/session.ts", "42", "JWT", "refreshToken()", "AUTH_EXPIRED", "5000ms"),
    ),
    RetentionCase(
        name="database migration",
        source=(
            "Migration 20260510_add_user_index.sql adds CONCURRENTLY index "
            "idx_users_email on users(email); rollback is DROP INDEX CONCURRENTLY idx_users_email."
        ),
        compressed="20260510_add_user_index.sql → CREATE INDEX CONCURRENTLY idx_users_email ON users(email). Rollback: DROP INDEX CONCURRENTLY idx_users_email.",
        required=("20260510_add_user_index.sql", "CONCURRENTLY", "idx_users_email", "users(email)", "DROP INDEX"),
    ),
    RetentionCase(
        name="build command",
        source=(
            "Run xcodebuild build -project OnePlayer.xcodeproj -scheme OnePlayer "
            "-destination platform=macOS. Test action is not configured."
        ),
        compressed="xcodebuild build -project OnePlayer.xcodeproj -scheme OnePlayer -destination platform=macOS. test action absent.",
        required=("xcodebuild", "OnePlayer.xcodeproj", "-scheme OnePlayer", "platform=macOS", "test action"),
    ),
    RetentionCase(
        name="causal chain",
        source=(
            "Broad rg over ~/.codex/sessions captured JSONL tool output, which "
            "raised last-turn input to 118k tokens and made FLINT output savings irrelevant."
        ),
        compressed="Broad rg ~/.codex/sessions → JSONL tool output → 118k last-turn input → FLINT output savings marginal.",
        required=("rg", "~/.codex/sessions", "JSONL", "118k", "FLINT", "output"),
    ),
]

CORPUS_CASES = [
    CorpusCase(
        name="auth regression",
        text=RETENTION_CASES[0].source,
        required=RETENTION_CASES[0].required,
    ),
    CorpusCase(
        name="database migration",
        text=RETENTION_CASES[1].source,
        required=RETENTION_CASES[1].required,
    ),
    CorpusCase(
        name="build command",
        text=RETENTION_CASES[2].source,
        required=RETENTION_CASES[2].required,
    ),
    CorpusCase(
        name="context leak",
        text=RETENTION_CASES[3].source,
        required=RETENTION_CASES[3].required,
    ),
]


def fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def latest_session() -> Path | None:
    files = glob.glob(str(SESSION_DIR / "**" / "rollout-*.jsonl"), recursive=True)
    if not files:
        return None
    return Path(max(files, key=os.path.getmtime))


def latest_totals() -> TokenTotals:
    session = latest_session()
    if not session:
        return TokenTotals()
    latest = TokenTotals()
    try:
        with session.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = entry.get("payload") or {}
                if payload.get("type") != "token_count":
                    continue
                info = payload.get("info") or {}
                total = info.get("total_token_usage") or {}
                latest = TokenTotals(
                    input_tokens=int(total.get("input_tokens") or 0),
                    cached_input_tokens=int(total.get("cached_input_tokens") or 0),
                    output_tokens=int(total.get("output_tokens") or 0),
                    reasoning_output_tokens=int(total.get("reasoning_output_tokens") or 0),
                    total_tokens=int(total.get("total_tokens") or 0),
                )
    except OSError:
        pass
    return latest


def latest_session_path() -> Path | None:
    return latest_session()


def read_if_exists(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def flint_rule_text() -> dict[str, str]:
    skill = read_if_exists(FLINT_ROOT / "skills" / "flint" / "SKILL.md")
    rules: dict[str, str] = {}
    for mode in ("lite", "full", "ultra", "wenyan"):
        match = re.search(rf"\*\*{mode}:\*\*(.*?)(?:\n\n|\Z)", skill, re.IGNORECASE | re.DOTALL)
        if match:
            rules[mode] = " ".join(match.group(1).split())
    return rules


def runes_rule_text() -> dict[str, str]:
    for root in GEM_THAL_ROOTS:
        core = read_if_exists(root / "lib" / "runes-core.js")
        if core:
            return {
                mode: " ".join(match.group(1).split())
                for mode, match in (
                    (m, re.search(rf"mode === ['\"]{m}['\"]\) return [\"`](.*?)[\"`];", core))
                    for m in ("lite", "ultra", "wenyan")
                )
                if match
            } | {"full": "[RUNES: FULL] COMPRESS FULL: Drop articles. Fragments OK. No pleasantries. High-signal."}
    return {}


def caveman_surface() -> dict[str, int]:
    files: dict[str, int] = {}
    for root in CAVEMAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".js", ".ts"}:
                try:
                    files[str(path.relative_to(root))] = path.stat().st_size
                except OSError:
                    pass
        if files:
            break
    return files


def caveman_rule_text() -> dict[str, str]:
    for root in CAVEMAN_ROOTS:
        skill = read_if_exists(root / "skills" / "caveman" / "SKILL.md")
        hooks = read_if_exists(root / "hooks" / "hooks.json")
        if not skill and not hooks:
            continue
        rules: dict[str, str] = {}
        for mode in ("lite", "full", "ultra"):
            match = re.search(rf"\$caveman {mode}.*?—(.*?)(?:\n|$)", skill)
            if match:
                rules[mode] = " ".join(match.group(1).split())
        if hooks:
            rules["hook"] = " ".join(hooks.split())
        return rules
    return {}


def count_tool_outputs(session: Path | None) -> tuple[int, int, int]:
    if not session:
        return (0, 0, 0)
    count = 0
    chars = 0
    large = 0
    try:
        with session.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = entry.get("payload") or {}
                if entry.get("type") != "response_item" or payload.get("type") != "function_call_output":
                    continue
                output = payload.get("output") or ""
                if not isinstance(output, str):
                    continue
                count += 1
                chars += len(output)
                if len(output) >= 20_000:
                    large += 1
    except OSError:
        pass
    return count, chars, large


def retention_score() -> tuple[int, int, list[str]]:
    passed = 0
    total = 0
    failures: list[str] = []
    for case in RETENTION_CASES:
        missing = [needle for needle in case.required if needle not in case.compressed]
        total += len(case.required)
        passed += len(case.required) - len(missing)
        if missing:
            failures.append(f"{case.name}: missing {', '.join(missing)}")
    return passed, total, failures


def retention_negative_control() -> tuple[int, int, list[str]]:
    """Verify retention test catches intentionally lossy compression."""
    passed = 0
    total = 0
    failures: list[str] = []
    for case in RETENTION_CASES:
        lossy = re.sub(r"[A-Za-z0-9_./~-]+", "X", case.compressed)
        missing = [needle for needle in case.required if needle not in lossy]
        total += len(case.required)
        passed += len(missing)
        if not missing:
            failures.append(f"{case.name}: negative control failed to remove facts")
    return passed, total, failures


def corpus_stats() -> tuple[int, int, int]:
    chars = sum(len(case.text) for case in CORPUS_CASES)
    required = sum(len(case.required) for case in CORPUS_CASES)
    cases = len(CORPUS_CASES)
    return cases, chars, required


def benchmark_grade(has_session: bool, has_runes: bool, has_caveman: bool, negative_ok: bool) -> str:
    score = 0
    score += 1 if has_session else 0
    score += 1 if has_runes else 0
    score += 1 if has_caveman else 0
    score += 1 if negative_ok else 0
    if score >= 4:
        return "B: useful local benchmark; still no live model A/B"
    if score == 3:
        return "C: partial local benchmark; missing at least one comparator/control"
    return "D: smoke test only"


def estimated_saved(output_tokens: int, ratio: float) -> int:
    if output_tokens <= 0 or ratio <= 0 or ratio >= 1:
        return 0
    return round(output_tokens * (ratio / (1 - ratio)))


def total_budget_impact(output_tokens: int, total_tokens: int, ratio: float) -> float:
    if total_tokens <= 0:
        return 0.0
    return (output_tokens * ratio) / total_tokens


def imagined_vs_actual(totals: TokenTotals) -> list[str]:
    if not totals.total_tokens:
        return ["  No actual token totals available."]
    lines = []
    lines.append("  mode    imagined output cut   actual total-budget cut")
    for mode, ratio in FLINT_RATIOS.items():
        impact = total_budget_impact(totals.output_tokens, totals.total_tokens, ratio)
        lines.append(f"  {mode:6} {round(ratio * 100):>7}%              {impact * 100:>7.2f}%")
    return lines


def main() -> int:
    session = latest_session_path()
    totals = latest_totals()
    flint_rules = flint_rule_text()
    runes_rules = runes_rule_text()
    caveman_rules = caveman_rule_text()
    caveman_files = caveman_surface()
    retained, required, failures = retention_score()
    neg_retained, neg_required, neg_failures = retention_negative_control()
    cases, corpus_chars, corpus_required = corpus_stats()
    tool_count, tool_chars, large_tool_count = count_tool_outputs(session)
    has_runes = bool(runes_rules)
    has_caveman = bool(caveman_files)
    negative_ok = neg_retained == neg_required and not neg_failures

    print("CODEX-FLINT BENCHMARK")
    print("---------------------")

    print("Rule surface:")
    for mode in ("lite", "full", "ultra", "wenyan"):
        flint_len = len(flint_rules.get(mode, ""))
        runes_len = len(runes_rules.get(mode, ""))
        caveman_len = len(caveman_rules.get(mode, ""))
        print(f"  {mode:6} FLINT {flint_len:4} chars | RUNES {runes_len:4} chars | Caveman {caveman_len:4} chars")
    if caveman_rules.get("hook"):
        print(f"  Caveman hook context: {len(caveman_rules['hook'])} chars")
    if caveman_files:
        print(f"  Caveman local surface: {len(caveman_files)} files, {fmt_int(sum(caveman_files.values()))} bytes")
    else:
        print("  Caveman local surface: not found or empty")

    print("")
    print("Benchmark corpus:")
    print(f"  Cases:          {cases}")
    print(f"  Source chars:   {fmt_int(corpus_chars)}")
    print(f"  Required facts: {corpus_required}")
    print("  Model calls:    none (local methodology only)")

    print("")
    print("Current Codex session:")
    if totals.total_tokens:
        print(f"  Total:     {fmt_int(totals.total_tokens)}")
        print(f"  Input:     {fmt_int(totals.input_tokens)}")
        print(f"  Cached in: {fmt_int(totals.cached_input_tokens)}")
        print(f"  Output:    {fmt_int(totals.output_tokens)}")
        print(f"  Tool outs: {tool_count} outputs, {fmt_int(tool_chars)} chars, {large_tool_count} large")
        for mode, ratio in FLINT_RATIOS.items():
            saved = estimated_saved(totals.output_tokens, ratio)
            print(f"  FLINT {mode:6} est saved: {fmt_int(saved)} output tokens equivalent ({round(ratio * 100)}%)")
        for mode, ratio in RUNES_RATIOS.items():
            saved = estimated_saved(totals.output_tokens, ratio)
            print(f"  RUNES {mode:6} est saved: {fmt_int(saved)} output tokens equivalent ({round(ratio * 100)}%)")
    else:
        print("  No token totals found.")

    print("")
    print("Imagined vs actual value:")
    for line in imagined_vs_actual(totals):
        print(line)
    if totals.total_tokens and totals.output_tokens:
        output_share = totals.output_tokens / totals.total_tokens
        print(f"  Actual output share: {output_share * 100:.2f}% of session tokens")
        if output_share < 0.05:
            print("  Verdict: output compression alone cannot materially fix this session's usage limit burn.")

    print("")
    print("Ultra retention fixture:")
    pct = (retained / required * 100) if required else 0
    print(f"  Required facts retained: {retained}/{required} ({pct:.1f}%)")
    if failures:
        for failure in failures:
            print(f"  FAIL {failure}")
    else:
        print("  PASS no required facts missing in deterministic fixtures")
    neg_pct = (neg_retained / neg_required * 100) if neg_required else 0
    print(f"  Negative control caught: {neg_retained}/{neg_required} removed facts ({neg_pct:.1f}%)")
    if neg_failures:
        for failure in neg_failures:
            print(f"  WARN {failure}")

    print("")
    print("Benchmark grade:")
    print(f"  {benchmark_grade(bool(totals.total_tokens), has_runes, has_caveman, negative_ok)}")
    print("  Not measured: live model semantic equivalence, human readability, task success after compression.")

    print("")
    print("Interpretation:")
    print("  Live A/B showed generic terse prompting (~82%) beat structured FLINT prompts on raw output savings.")
    print("  FLINT value should be judged as persistence + mode control, not savings over terse.")
    print("  Current Codex budget is input-dominated; budget doctor matters more than extra output compression.")
    print("  Ultra retention fixture is a guardrail with negative control, not proof of arbitrary prose preservation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
