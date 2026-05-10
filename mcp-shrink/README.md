# flint-shrink

MCP proxy that compresses tool/resource descriptions before the model sees them.
Reduces input tokens 10-40% on tool-heavy sessions. Zero dependencies, pure Node.

## How it works

Sits between Codex and any MCP server. Intercepts `tools/list`, `prompts/list`,
`resources/list` responses and compresses `description` fields. Code, URLs,
paths, and identifiers preserved exactly. Tool call results NOT touched.

## Setup

In `.codex/config.toml`, wrap any MCP server:

```toml
[[mcpServers]]
name = "filesystem"
command = "node"
args = [
  "/Users/robert/.codex/skills/codex-flint/mcp-shrink/index.js",
  "npx", "@modelcontextprotocol/server-filesystem", "/your/path"
]
```

## Debug

```bash
FLINT_SHRINK_DEBUG=1 node index.js <upstream> [...args]
```

## Extra fields

```bash
FLINT_SHRINK_FIELDS=description,title node index.js <upstream>
```
