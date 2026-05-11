# Privacy

FLINT respects user privacy. **No runtime telemetry. No phone-home. No update-checks.**

## What FLINT does at runtime

| Component | Network access | Data sent | Logged where |
|-----------|----------------|-----------|--------------|
| SessionStart hook (`flint-activate.js`) | none | — | local stdout only |
| UserPromptSubmit hook (`flint-tracker.js`) | none | — | `~/.codex/.flint-history.jsonl` (local) |
| PostToolUse hook (`flint-memory-compress.js`) | none | — | local file rewrites only |
| Codex hook scripts (`codex-flint/scripts/*.js`, `flint-hook.sh`) | none | — | local stdout/stderr only |
| `mcp-shrink` proxy | none beyond upstream MCP server you choose | — | local stderr if `FLINT_SHRINK_DEBUG=1` |
| Skills (`flint`, `flint-commit`, etc.) | none | — | none |

Hooks make zero network calls during normal operation.

## Local-only storage

| Path | Purpose | Format |
|------|---------|--------|
| `~/.codex/.flint-active` (Codex) / `~/.claude/.flint-active` (Claude) | Active mode flag | plain text (`lite`/`full`/`ultra`/`wenyan`) |
| `~/.codex/.flint-history.jsonl` | Turn-count history for `/flint-stats` | one JSON object per line, local only |
| `~/.config/flint/config.json` | Optional default-mode config | JSON |

Files are written with `0600` permissions and refused if they are symlinks. See F086 fail-open and F067 single-source-of-truth for implementation.

## What FLINT does NOT do

- No analytics, no metrics service, no crash reporting
- No automatic update checks. The plugin never contacts a remote endpoint to look for new versions
- No anonymous identifiers, no install IDs, no fingerprinting
- No data shared with the FLINT authors or any third party
- No reading or writing outside the paths listed above

## Network paths (install-time only)

Code is fetched from a Git repository when you clone or `git pull`. After install, FLINT does not initiate any network connection. Any network traffic you observe from your AI CLI is initiated by that CLI (Codex / Claude Code) for its own model inference and is unrelated to FLINT.

## `mcp-shrink` and upstream servers

`mcp-shrink` wraps an upstream MCP server. It proxies stdin/stdout between the model and that upstream server and compresses prose in `description` fields of `tools/list`, `prompts/list`, and `resources/list` responses. Whether the upstream MCP server makes network calls is determined by that server, not by `mcp-shrink`. Examples:

- `@modelcontextprotocol/server-filesystem` → local-only
- Cloud MCP servers (Shopify, Drive, Gmail) → those services define their own privacy policies

`mcp-shrink` adds nothing beyond compression.

## Auditing

All hook scripts are short and human-readable. Run a require audit at any time:

```bash
# Codex scripts + skills (no hooks — hooks are in claude-flint):
cd codex-flint
grep -rE "require\(" scripts/ mcp-shrink/
grep -rE "^(import|from) " skills/

# Claude Code hooks (in user plugins dir):
grep -rE "require\(" ~/.claude/plugins/claude-flint/hooks/
```

Stdlib only — no `https`, no `http`, no `net`, no `dns`, no telemetry SDK.

## Reporting

If you find any unexpected network call or data exfiltration, open an issue. The plugin should be entirely local.
