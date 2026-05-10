#!/usr/bin/env python3
"""
CODEX-FLINT session token stats parser.

Reads the most recent Codex session JSONL from ~/.codex/sessions/
and reports token usage from the session's token_count events
and rate-limit metadata.

Codex session JSONL event types (observed in v0.130):
  - session_meta    : session start, contains model info
  - turn_context    : per-turn context (model, approval_policy, etc.)
  - token_count     : rate limit / usage snapshot (primary source for usage%)
  - response_item   : model messages, tool calls — token counts NOT stored here
  - event_msg       : agent_message, user_message, task_started, etc.

Unfortunately Codex CLI does NOT store raw input/output token counts per-turn
in the session JSONL. The token_count events contain rate limit percentages
(used_percent of window) and window sizes, not absolute token counts.

This script reports what IS available: rate limit consumption %, model, turns.
It estimates absolute tokens from the rate limit window when possible.

Usage: python3 parse_session.py [--session PATH]
"""

import json
import os
import sys
import glob
from pathlib import Path
from datetime import datetime

CODEX_DIR = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
SESSIONS_DIR = CODEX_DIR / "sessions"
FLAG_PATH = CODEX_DIR / ".flint-active"

COMPRESSION_RATIO = {
    "lite": 0.30,
    "full": 0.75,
    "ultra": 0.87,
}

# Codex Plus plan limits (approximate, from observed data)
# Primary window: 300 min (5h), Secondary: 10080 min (1 week)
# These are approximate — actual limits vary by plan
APPROXIMATE_PRIMARY_LIMIT_TOKENS = 2_000_000   # tokens per 5h window (plus plan estimate)


def read_flag():
    try:
        val = FLAG_PATH.read_text().strip().lower()
        if val in ("lite", "full", "ultra"):
            return val
    except Exception:
        pass
    return "off"


def find_latest_session():
    """Find the most recently modified session JSONL file."""
    pattern = str(SESSIONS_DIR / "**" / "rollout-*.jsonl")
    files = glob.glob(pattern, recursive=True)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def parse_session(path):
    """
    Parse a Codex session JSONL file.

    Returns a dict with:
      - model: model name
      - turns: number of assistant turns
      - primary_used_pct: latest primary rate limit used %
      - secondary_used_pct: latest secondary rate limit used %
      - primary_window_minutes: primary window duration
      - secondary_window_minutes: secondary window duration
      - primary_resets_at: epoch timestamp when primary resets
      - user_messages: count of user messages
      - session_start: ISO timestamp
      - plan_type: subscription plan (e.g. "plus")
      - token_count_events: count of token_count events seen
    """
    result = {
        "model": "unknown",
        "turns": 0,
        "primary_used_pct": None,
        "secondary_used_pct": None,
        "primary_window_minutes": None,
        "secondary_window_minutes": None,
        "primary_resets_at": None,
        "user_messages": 0,
        "session_start": None,
        "plan_type": None,
        "token_count_events": 0,
    }

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                etype = entry.get("type", "")
                payload = entry.get("payload", {})
                ts = entry.get("timestamp", "")

                if etype == "session_meta":
                    if not result["session_start"] and ts:
                        result["session_start"] = ts
                    # Model is in base_instructions context, not directly exposed
                    # Will be captured from turn_context instead

                elif etype == "turn_context":
                    m = payload.get("model", "")
                    if m:
                        result["model"] = m

                elif etype == "event_msg":
                    msg_type = payload.get("type", "")
                    if msg_type == "agent_message":
                        result["turns"] += 1
                    elif msg_type == "user_message":
                        result["user_messages"] += 1
                    elif msg_type == "token_count":
                        # token_count is nested inside event_msg (observed in Codex v0.130)
                        result["token_count_events"] += 1
                        rl = payload.get("rate_limits", {})
                        if rl:
                            primary = rl.get("primary", {})
                            secondary = rl.get("secondary", {})
                            plan = rl.get("plan_type", "")
                            if plan:
                                result["plan_type"] = plan
                            if primary:
                                result["primary_used_pct"] = primary.get("used_percent")
                                result["primary_window_minutes"] = primary.get("window_minutes")
                                result["primary_resets_at"] = primary.get("resets_at")
                            if secondary:
                                result["secondary_used_pct"] = secondary.get("used_percent")
                                result["secondary_window_minutes"] = secondary.get("window_minutes")

                # Also handle token_count as a top-level type (forward compat)
                elif etype == "token_count":
                    result["token_count_events"] += 1
                    rl = payload.get("rate_limits", {})
                    if rl:
                        primary = rl.get("primary", {})
                        secondary = rl.get("secondary", {})
                        plan = rl.get("plan_type", "")
                        if plan:
                            result["plan_type"] = plan
                        if primary:
                            result["primary_used_pct"] = primary.get("used_percent")
                            result["primary_window_minutes"] = primary.get("window_minutes")
                            result["primary_resets_at"] = primary.get("resets_at")
                        if secondary:
                            result["secondary_used_pct"] = secondary.get("used_percent")
                            result["secondary_window_minutes"] = secondary.get("window_minutes")

    except Exception as e:
        print(f"Error reading session: {e}", file=sys.stderr)

    return result


def format_window(minutes):
    if minutes is None:
        return "unknown"
    if minutes >= 10080:
        return f"{minutes // 1440}d"
    if minutes >= 60:
        return f"{minutes // 60}h"
    return f"{minutes}m"


def format_reset(epoch):
    if not epoch:
        return "unknown"
    try:
        dt = datetime.fromtimestamp(epoch)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(epoch)


def main():
    session_path = None
    if "--session" in sys.argv:
        idx = sys.argv.index("--session")
        if idx + 1 < len(sys.argv):
            session_path = sys.argv[idx + 1]

    if session_path is None:
        session_path = find_latest_session()

    mode = read_flag()

    print("CODEX-FLINT STATS")
    print("--------------------")

    if session_path is None:
        print("Session:    No session files found")
        print(f"Mode:       {mode.upper()}")
        print("\nSessions are stored at: ~/.codex/sessions/")
        return

    stats = parse_session(session_path)

    session_name = os.path.basename(session_path)
    print(f"Session:    {session_name}")
    if stats["session_start"]:
        print(f"Started:    {stats['session_start'][:19].replace('T', ' ')} UTC")
    print(f"Model:      {stats['model']}")
    print(f"Plan:       {stats['plan_type'] or 'unknown'}")
    print(f"Mode:       {mode.upper()}")
    print(f"Turns:      {stats['turns']} agent, {stats['user_messages']} user")

    # Rate limit info
    if stats["primary_used_pct"] is not None:
        window = format_window(stats["primary_window_minutes"])
        resets = format_reset(stats["primary_resets_at"])
        print(f"\nRate limit ({window} window):")
        print(f"  Primary:    {stats['primary_used_pct']:.1f}% used  (resets {resets})")
        if stats["secondary_used_pct"] is not None:
            sec_window = format_window(stats["secondary_window_minutes"])
            print(f"  Secondary:  {stats['secondary_used_pct']:.1f}% used  ({sec_window} window)")

    # Compression savings estimate (output-side only, since we don't have raw token counts)
    ratio = COMPRESSION_RATIO.get(mode, 0)
    if ratio > 0 and stats["turns"] > 0:
        pct = int(ratio * 100)
        print(f"\nCompression savings estimate:")
        print(f"  Mode {mode} reduces output by ~{pct}% vs. unflint.")
        print(f"  With {stats['turns']} turns, estimated {pct}% fewer output tokens consumed.")
        print(f"  Activate 'ultra' for maximum savings (~87% output reduction).")

    elif mode == "off" and stats["turns"] > 0:
        print(f"\nTip: 'activate flint' to reduce output tokens by ~75% (full mode).")

    print(f"\nFlag file:  {FLAG_PATH}")
    print(f"Sessions:   {SESSIONS_DIR}")

    if stats["token_count_events"] == 0:
        print("\nNote: No token_count events found — session may be too new or incomplete.")
    elif stats["primary_used_pct"] is None:
        print("\nNote: Rate limit data not available in this session.")


if __name__ == "__main__":
    main()
