// runes-shrink — pure-Node prose compressor for MCP tool/resource descriptions.
// Zero external dependencies. Same boundaries as runes-compress:
// preserve code, URLs, paths, identifiers — compress everything else.
//
// API: compress(text) → { compressed, before, after }

'use strict';

const FILLERS = /\b(?:just|really|basically|actually|simply|quite|very|essentially|literally)\b/gi;
const PLEASANTRIES = /\b(?:please|kindly|thank you|thanks|sure|certainly|of course|happy to|i'?d be happy)\b[,.]?\s*/gi;
const HEDGES = /\b(?:perhaps|maybe|might|could potentially|would like to|i think|in my opinion|it seems|it appears)\b\s*/gi;
const LEADERS = /^(?:i'?ll|i will|i can|i'?d|you can|we will|we can|let me|let'?s)\s+/gim;
const ARTICLES = /\b(?:a|an|the)\s+(?=[a-z])/gi;

const PROTECTED = [
  /```[\s\S]*?```/g,
  /`[^`\n]+`/g,
  /\bhttps?:\/\/\S+/gi,
  /\b[\w.-]*[\/\\][\w.\/\\\-]+/g,
  /\b[A-Z][A-Za-z0-9]*(?:_[A-Z][A-Za-z0-9]*)+\b/g,
  /\b\w+\.\w+(?:\.\w+)*\(\)?/g,
  /[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)/g,
  /\b\d+\.\d+\.\d+\b/g,
];

// Sentinels use NUL-delimited tokens that cannot appear in real text.
// Plain-number sentinels (" 0 ", " 1 ") collide with numeric content and
// path fragments — restore regex incorrectly matches them and drops segments.
const SENTINEL_RE = /\x00RUNES(\d+)\x00/g;
function sentinel(i) { return `\x00RUNES${i}\x00`; }

// Single-pass combined regex: apply all PROTECTED patterns simultaneously.
// Sequential loop caused sentinel re-protection: later patterns matched inside
// already-placed \x00RUNESn\x00 tokens, producing nested sentinels that
// survive the single restore pass as raw \x00 bytes.
const ALL_PROTECTED_RE = new RegExp(PROTECTED.map(r => r.source).join('|'), 'gi');

function withProtected(text, fn) {
  const saved = [];
  const w = text.replace(ALL_PROTECTED_RE, m => {
    const i = saved.length;
    saved.push(m);
    return sentinel(i);
  });
  const out = fn(w);
  return out.replace(SENTINEL_RE, (_, i) => saved[+i] ?? '');
}

function compressProse(s) {
  s = s.replace(LEADERS, '');
  s = s.replace(PLEASANTRIES, '');
  s = s.replace(HEDGES, '');
  s = s.replace(FILLERS, '');
  s = s.replace(ARTICLES, '');
  s = s.replace(/[ \t]{2,}/g, ' ');
  s = s.replace(/\s+([,.;:!?])/g, '$1');
  s = s.replace(/\n{3,}/g, '\n\n');
  s = s.replace(/(^|[.!?]\s+)([a-z])/g, (_, pre, ch) => pre + ch.toUpperCase());
  return s.trim();
}

function compress(text) {
  if (typeof text !== 'string' || text.length === 0) return { compressed: text, before: 0, after: 0 };
  const before = text.length;
  const compressed = withProtected(text, compressProse);
  return { compressed, before, after: compressed.length };
}

function compressDescriptionsInPlace(obj, fields) {
  const fieldSet = new Set(fields || ['description']);
  if (!obj || typeof obj !== 'object') return;
  if (Array.isArray(obj)) { for (const item of obj) compressDescriptionsInPlace(item, [...fieldSet]); return; }
  for (const [key, val] of Object.entries(obj)) {
    if (fieldSet.has(key) && typeof val === 'string') obj[key] = compress(val).compressed;
    else if (val && typeof val === 'object') compressDescriptionsInPlace(val, [...fieldSet]);
  }
}

module.exports = { compress, compressDescriptionsInPlace };
