#!/usr/bin/env python3
"""
CODEX-FLINT budget doctor.

Analyzes the latest Codex session JSONL and reports where token budget is going:
input/context, output, reasoning, tool output, hooks, and broad commands.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CODEX_DIR = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
SESSIONS_DIR = CODEX_DIR / "sessions"
FLAG_PATH = CODEX_DIR / ".flint-active"

LARGE_OUTPUT_CHARS = 20_000
HUGE_OUTPUT_CHARS = 100_000
HIGH_INPUT_TURN = 50_000

BROAD_PATTERNS = (
    "/Users/robert/.codex",
    "/Users/robert/.cache",
    "/Users/robert ",
    "node_modules",
    "DerivedData",
    "codex-tui.log",
    "rollout-",
    "find /Users/robert",
)


@dataclass
class TokenSnapshot:
    line: int
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0
    last_input_tokens: int = 0
    last_cached_input_tokens: int = 0
    last_output_tokens: int = 0
    last_reasoning_output_tokens: int = 0
    last_total_tokens: int = 0
    primary_used_percent: float | None = None
    secondary_used_percent: float | None = None


@dataclass
class ToolOutput:
    line: int
    chars: int
    command: str
    preview: str


def read_mode() -> str:
    try:
        mode = FLAG_PATH.read_text(encoding="utf-8").strip().lower()
        if mode in {"lite", "full", "ultra", "wenyan"}:
            return mode
    except OSError:
        pass
    return "off"


def latest_session() -> Path | None:
    files = glob.glob(str(SESSIONS_DIR / "**" / "rollout-*.jsonl"), recursive=True)
    if not files:
        return None
    return Path(max(files, key=os.path.getmtime))


def get_payload(entry: dict[str, Any]) -> dict[str, Any]:
    payload = entry.get("payload")
    return payload if isinstance(payload, dict) else {}


def read_text_parts(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    content = payload.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("output_text") or ""
                if isinstance(text, str):
                    chunks.append(text)
    return "\n".join(chunks)


def parse_command_from_output(output: str) -> str:
    match = re.search(r'ToolCall: exec_command (\{.*?"cmd".*?\})', output)
    if match:
        return match.group(1)[:240]
    match = re.search(r'"cmd":"([^"]+)"', output)
    if match:
        return match.group(1)[:240]
    match = re.search(r"Command line invocation:\n\s+(.+)", output)
    if match:
        return match.group(1)[:240]
    return "(unknown command)"


def token_snapshot(line_no: int, payload: dict[str, Any]) -> TokenSnapshot | None:
    if payload.get("type") != "token_count":
        return None

    info = payload.get("info") or {}
    total = info.get("total_token_usage") or {}
    last = info.get("last_token_usage") or {}
    limits = payload.get("rate_limits") or {}
    primary = limits.get("primary") or {}
    secondary = limits.get("secondary") or {}

    return TokenSnapshot(
        line=line_no,
        input_tokens=int(total.get("input_tokens") or 0),
        cached_input_tokens=int(total.get("cached_input_tokens") or 0),
        output_tokens=int(total.get("output_tokens") or 0),
        reasoning_output_tokens=int(total.get("reasoning_output_tokens") or 0),
        total_tokens=int(total.get("total_tokens") or 0),
        last_input_tokens=int(last.get("input_tokens") or 0),
        last_cached_input_tokens=int(last.get("cached_input_tokens") or 0),
        last_output_tokens=int(last.get("output_tokens") or 0),
        last_reasoning_output_tokens=int(last.get("reasoning_output_tokens") or 0),
        last_total_tokens=int(last.get("total_tokens") or 0),
        primary_used_percent=primary.get("used_percent"),
        secondary_used_percent=secondary.get("used_percent"),
    )


def analyze(path: Path) -> dict[str, Any]:
    snapshots: list[TokenSnapshot] = []
    tool_outputs: list[ToolOutput] = []
    commands: list[str] = []
    hook_messages = 0
    agent_turns = 0
    user_turns = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            payload = get_payload(entry)
            if entry.get("type") == "event_msg":
                kind = payload.get("type")
                if kind == "token_count":
                    snap = token_snapshot(line_no, payload)
                    if snap:
                        snapshots.append(snap)
                elif kind == "agent_message":
                    agent_turns += 1
                elif kind == "user_message":
                    user_turns += 1

            if entry.get("type") == "response_item":
                ptype = payload.get("type")
                if ptype == "function_call":
                    if payload.get("name") == "exec_command":
                        args = payload.get("arguments")
                        if isinstance(args, str):
                            try:
                                decoded = json.loads(args)
                                cmd = decoded.get("cmd")
                                if isinstance(cmd, str):
                                    commands.append(cmd)
                            except json.JSONDecodeError:
                                commands.append(args[:240])
                elif ptype == "function_call_output":
                    output = payload.get("output") or ""
                    if isinstance(output, str):
                        if "systemMessage" in output and "[FLINT:" in output:
                            hook_messages += 1
                        if len(output) >= LARGE_OUTPUT_CHARS:
                            tool_outputs.append(
                                ToolOutput(
                                    line=line_no,
                                    chars=len(output),
                                    command=parse_command_from_output(output),
                                    preview=output[:180].replace("\n", " "),
                                )
                            )

                elif ptype == "message":
                    text = read_text_parts(payload)
                    if "systemMessage" in text and "[FLINT:" in text:
                        hook_messages += 1

    broad_commands = [
        cmd for cmd in commands
        if any(pattern in cmd for pattern in BROAD_PATTERNS)
    ]

    return {
        "snapshots": snapshots,
        "tool_outputs": sorted(tool_outputs, key=lambda item: item.chars, reverse=True),
        "commands": commands,
        "broad_commands": broad_commands,
        "hook_messages": hook_messages,
        "agent_turns": agent_turns,
        "user_turns": user_turns,
    }


def fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def pct(part: int, whole: int) -> str:
    if whole <= 0:
        return "0.0%"
    return f"{part / whole * 100:.1f}%"


def main() -> int:
    session = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_session()
    mode = read_mode()

    print("CODEX-FLINT BUDGET DOCTOR")
    print("-------------------------")
    print(f"Mode:      {mode.upper()}")

    if not session:
        print("Session:   none found")
        return 0

    print(f"Session:   {session.name}")
    data = analyze(session)
    snapshots: list[TokenSnapshot] = data["snapshots"]

    print(f"Turns:     {data['agent_turns']} agent, {data['user_turns']} user")

    if snapshots:
        latest = snapshots[-1]
        print("")
        print("Token budget:")
        print(f"  Total:      {fmt_int(latest.total_tokens)}")
        print(f"  Input:      {fmt_int(latest.input_tokens)} ({pct(latest.input_tokens, latest.total_tokens)})")
        print(f"  Cached in:  {fmt_int(latest.cached_input_tokens)} ({pct(latest.cached_input_tokens, latest.input_tokens)})")
        print(f"  Output:     {fmt_int(latest.output_tokens)} ({pct(latest.output_tokens, latest.total_tokens)})")
        print(f"  Reasoning:  {fmt_int(latest.reasoning_output_tokens)} ({pct(latest.reasoning_output_tokens, latest.total_tokens)})")
        print(f"  Last turn:  {fmt_int(latest.last_total_tokens)} total, {fmt_int(latest.last_input_tokens)} input, {fmt_int(latest.last_output_tokens)} output")
        if latest.primary_used_percent is not None:
            print(f"  Primary:    {latest.primary_used_percent:.1f}% used")
        if latest.secondary_used_percent is not None:
            print(f"  Secondary:  {latest.secondary_used_percent:.1f}% used")

        high_turns = [snap for snap in snapshots if snap.last_input_tokens >= HIGH_INPUT_TURN]
        if high_turns:
            print(f"  High-input turns: {len(high_turns)} >= {fmt_int(HIGH_INPUT_TURN)} input tokens")

    large_outputs: list[ToolOutput] = data["tool_outputs"]
    print("")
    print("Large tool outputs:")
    if not large_outputs:
        print("  none >= 20k chars")
    else:
        for item in large_outputs[:5]:
            label = "huge" if item.chars >= HUGE_OUTPUT_CHARS else "large"
            print(f"  line {item.line}: {label}, {fmt_int(item.chars)} chars, {item.command}")

    broad_commands: list[str] = data["broad_commands"]
    print("")
    print("Broad command risk:")
    if not broad_commands:
        print("  none detected")
    else:
        for cmd in broad_commands[:8]:
            print(f"  {cmd[:180]}")

    print("")
    print("FLINT assessment:")
    if snapshots:
        latest = snapshots[-1]
        if latest.input_tokens > latest.output_tokens * 20:
            print("  Output compression helps, but input/context dominates this session.")
            print("  Best ROI: tool-output discipline + fresh sessions + tighter search scopes.")
        else:
            print("  Output is material. FLINT response compression likely has direct budget value.")
    if data["hook_messages"]:
        print(f"  Hook status messages detected: {data['hook_messages']} (low token cost, possible UI noise).")

    print("")
    print("Recommended actions:")
    print("  1. Start fresh session after heavy tool/log exploration.")
    print("  2. Default tool max_output_tokens <= 4k; raise only after targeted miss.")
    print("  3. Exclude node_modules, DerivedData, .cache, sessions, logs in broad searches.")
    print("  4. Prefer rg --files + narrow sed over broad rg content search.")
    print("  5. Disable FLINT warning hook unless status noise is worth it.")
    print("  6. Add flint-safe wrappers for rg/find/xcodebuild/log commands.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
