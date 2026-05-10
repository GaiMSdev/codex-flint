#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m py_compile \
  skills/flint-stats/scripts/parse_session.py \
  skills/flint-budget/scripts/analyze_budget.py \
  skills/flint-benchmark/scripts/benchmark.py

tmp_home="$(mktemp -d)"
trap 'rm -rf "$tmp_home"' EXIT

CODEX_HOME="$tmp_home/.codex" bash scripts/flint.sh lite >/dev/null
test "$(cat "$tmp_home/.codex/.flint-active")" = "lite"

CODEX_HOME="$tmp_home/.codex" bash scripts/flint.sh full >/dev/null
test "$(cat "$tmp_home/.codex/.flint-active")" = "full"

CODEX_HOME="$tmp_home/.codex" bash scripts/flint.sh ultra >/dev/null
test "$(cat "$tmp_home/.codex/.flint-active")" = "ultra"

CODEX_HOME="$tmp_home/.codex" bash scripts/flint.sh wenyan >/dev/null
test "$(cat "$tmp_home/.codex/.flint-active")" = "wenyan"

hook_out="$(CODEX_HOME="$tmp_home/.codex" bash scripts/flint-hook.sh)"
printf '%s' "$hook_out" | grep -q '"continue":true'
if printf '%s' "$hook_out" | grep -q 'systemMessage'; then
  echo "flint-hook should not emit warning-style systemMessage output" >&2
  exit 1
fi

CODEX_HOME="$tmp_home/.codex" bash scripts/flint.sh off >/dev/null
test ! -e "$tmp_home/.codex/.flint-active"

python3 skills/flint-benchmark/scripts/benchmark.py >/tmp/codex-flint-benchmark.out
grep -q "Benchmark grade:" /tmp/codex-flint-benchmark.out
grep -q "Negative control caught:" /tmp/codex-flint-benchmark.out

echo "CODEX-FLINT tests passed"
