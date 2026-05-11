#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const VALID_MODES = ['lite', 'full', 'ultra', 'wenyan'];
const DEFAULT_MODES = ['off'].concat(VALID_MODES);
const MAX_FLAG_BYTES = 64;

const MODE_RULES = {
  lite: '[FLINT: LITE] Drop filler/hedging/pleasantries. Keep articles + full sentences. Professional-tight.\nACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".',
  full: '[FLINT: FULL] Answer concisely. No preamble. No pleasantries. Pattern: thing -> cause -> fix. Preserve nuance/facts. Code/names/errors exact. Tables only >=3x2, else prose.\nACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".',
  ultra: '[FLINT: ULTRA] Max density. Abbrev prose: DB auth cfg req res fn impl ctx err msg val. Arrows X->Y. Facts/values preserved. No Chain-of-Draft. Code/names/errors exact. Tables only >=3x2, else prose/arrows.\nACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".',
  wenyan: '[FLINT: WENYAN] Classical Chinese literary style. Pro-drop subjects. Technical identifiers preserved as-is.\nACTIVE EVERY RESPONSE. Off: "normal mode" / "stop flint".'
};

const REINFORCEMENT = {
  lite: '[FLINT: LITE] Drop filler. Keep full sentences.',
  full: '[FLINT: FULL] No preamble. Pattern: thing -> cause -> fix.',
  ultra: '[FLINT: ULTRA] Abbrev prose. X->Y causality. Facts preserved.',
  wenyan: '[FLINT: WENYAN] Classical Chinese style. Preserve identifiers.'
};

function codexDir() {
  return process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
}

function flagPath() {
  return path.join(codexDir(), '.flint-active');
}

function historyPath() {
  return path.join(codexDir(), '.flint-history.jsonl');
}

function readSmallFileNoFollow(filePath, maxBytes) {
  const stat = fs.lstatSync(filePath);
  if (stat.isSymbolicLink() || !stat.isFile() || stat.size > maxBytes) return null;

  const noFollow = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
  const fd = fs.openSync(filePath, fs.constants.O_RDONLY | noFollow);
  try {
    const buf = Buffer.alloc(maxBytes);
    const n = fs.readSync(fd, buf, 0, maxBytes, 0);
    return buf.slice(0, n).toString('utf8');
  } finally {
    fs.closeSync(fd);
  }
}

function readFlag(filePath = flagPath()) {
  try {
    const raw = readSmallFileNoFollow(filePath, MAX_FLAG_BYTES);
    if (raw === null) return null;
    const mode = raw.trim().toLowerCase();
    return VALID_MODES.includes(mode) ? mode : null;
  } catch (e) {
    return null;
  }
}

function safeWriteFlag(filePath, mode) {
  if (!VALID_MODES.includes(mode)) return false;

  try {
    const dir = path.dirname(filePath);
    fs.mkdirSync(dir, { recursive: true });

    let realDir = dir;
    const dirStat = fs.lstatSync(dir);
    if (dirStat.isSymbolicLink()) {
      realDir = fs.realpathSync(dir);
      const realStat = fs.statSync(realDir);
      if (!realStat.isDirectory()) return false;
      if (typeof process.getuid === 'function' && realStat.uid !== process.getuid()) return false;
    }

    const realFlagPath = path.join(realDir, path.basename(filePath));
    try {
      if (fs.lstatSync(realFlagPath).isSymbolicLink()) return false;
    } catch (e) {
      if (e.code !== 'ENOENT') return false;
    }

    const tempPath = path.join(realDir, `.flint-active.tmp.${process.pid}.${Date.now()}`);
    const noFollow = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
    const fd = fs.openSync(
      tempPath,
      fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | noFollow,
      0o600
    );
    try {
      fs.writeSync(fd, mode);
      try { fs.fchmodSync(fd, 0o600); } catch (e) {}
    } finally {
      fs.closeSync(fd);
    }
    fs.renameSync(tempPath, realFlagPath);
    return true;
  } catch (e) {
    return false;
  }
}

function removeFlag(filePath = flagPath()) {
  try {
    if (fs.lstatSync(filePath).isSymbolicLink()) return false;
    fs.unlinkSync(filePath);
    return true;
  } catch (e) {
    return e.code === 'ENOENT';
  }
}

function getDefaultMode() {
  const envMode = (process.env.CODEX_FLINT_DEFAULT_MODE || '').trim().toLowerCase();
  if (DEFAULT_MODES.includes(envMode)) return envMode;

  const configPath = path.join(os.homedir(), '.config', 'flint', 'config.json');
  try {
    const raw = JSON.parse(readSmallFileNoFollow(configPath, 512));
    const mode = String(raw.defaultMode || raw.default_mode || '').trim().toLowerCase();
    if (DEFAULT_MODES.includes(mode)) return mode;
  } catch (e) {}
  return 'off';
}

function setTerminalTitle(mode) {
  try {
    const title = mode ? `Codex | FLINT ${mode.toUpperCase()}` : 'Codex';
    fs.writeFileSync('/dev/tty', `\u001b]0;${title}\u0007`);
  } catch (e) {}
}

function emitJson(payload) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
}

function appendHistory(mode, event) {
  try {
    const hp = historyPath();
    fs.mkdirSync(path.dirname(hp), { recursive: true });
    const noFollow = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
    const fd = fs.openSync(hp, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_APPEND | noFollow, 0o600);
    try {
      try { fs.fchmodSync(fd, 0o600); } catch (e) {}
      fs.writeSync(fd, `${JSON.stringify({ ts: new Date().toISOString(), mode, event })}\n`);
    } finally {
      fs.closeSync(fd);
    }
  } catch (e) {}
}

module.exports = {
  MODE_RULES,
  REINFORCEMENT,
  VALID_MODES,
  appendHistory,
  emitJson,
  flagPath,
  getDefaultMode,
  readFlag,
  removeFlag,
  safeWriteFlag,
  setTerminalTitle
};
