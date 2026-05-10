#!/usr/bin/env node
// flint-shrink — MCP proxy that compresses prose fields in upstream server responses.
// Wraps any MCP server and reduces token cost of tool/resource descriptions.
//
// Usage (in .codex/config.toml or Codex MCP config):
//   [[mcpServers]]
//   name = "fs-shrunk"
//   command = "node"
//   args = ["/path/to/codex-flint/mcp-shrink/index.js", "npx", "@modelcontextprotocol/server-filesystem", "/some/path"]
//
// Env vars:
//   FLINT_SHRINK_FIELDS   comma-separated extra fields to compress (default: description)
//   FLINT_SHRINK_DEBUG=1  log compression deltas to stderr

'use strict';

const { spawn } = require('child_process');
const { compressDescriptionsInPlace, compress } = require('./compress');

const args = process.argv.slice(2);
if (args.length === 0) {
  process.stderr.write('flint-shrink: missing upstream command.\n');
  process.stderr.write('Usage: flint-shrink <upstream-command> [...args]\n');
  process.exit(2);
}

const debug = process.env.FLINT_SHRINK_DEBUG === '1';
const fields = (process.env.FLINT_SHRINK_FIELDS || 'description')
  .split(',').map(s => s.trim()).filter(Boolean);

const upstream = spawn(args[0], args.slice(1), { stdio: ['pipe', 'pipe', 'inherit'] });

upstream.on('error', err => {
  process.stderr.write(`flint-shrink: failed to spawn upstream: ${err.message}\n`);
  process.exit(1);
});

upstream.on('exit', (code, signal) => {
  if (signal) process.exit(128 + (signal === 'SIGTERM' ? 15 : 9));
  process.exit(code || 0);
});

function makeLineBuffer(onLine) {
  let buf = '';
  return chunk => {
    buf += chunk.toString('utf8');
    let nl;
    while ((nl = buf.indexOf('\n')) !== -1) {
      const line = buf.slice(0, nl);
      buf = buf.slice(nl + 1);
      if (line.trim()) onLine(line);
    }
  };
}

function transformResponse(msg) {
  if (!msg || !msg.result || typeof msg.result !== 'object') return msg;
  const r = msg.result;
  let changed = false;

  for (const arrayName of ['tools', 'prompts', 'resources', 'resourceTemplates']) {
    if (Array.isArray(r[arrayName])) {
      for (const item of r[arrayName]) {
        for (const field of fields) {
          if (typeof item[field] === 'string') {
            const { compressed, before, after } = compress(item[field]);
            if (compressed !== item[field]) {
              item[field] = compressed;
              changed = true;
              if (debug) process.stderr.write(
                `[flint-shrink] ${arrayName}.${item.name || '?'}.${field}: ${before}→${after} chars\n`
              );
            }
          }
        }
      }
    }
  }

  if (!changed) compressDescriptionsInPlace(r, fields);
  return msg;
}

upstream.stdout.on('data', makeLineBuffer(line => {
  let msg;
  try { msg = JSON.parse(line); } catch {
    process.stdout.write(line + '\n');
    return;
  }
  process.stdout.write(JSON.stringify(transformResponse(msg)) + '\n');
}));

process.stdin.on('data', chunk => upstream.stdin.write(chunk));
process.stdin.on('end', () => upstream.stdin.end());
