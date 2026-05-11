#!/usr/bin/env node
'use strict';

const {
  REINFORCEMENT,
  VALID_MODES,
  appendHistory,
  emitJson,
  flagPath,
  readFlag,
  removeFlag,
  safeWriteFlag,
  setTerminalTitle
} = require('./flint-config');

const fp = flagPath();

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', main);
process.stdin.resume();

function getPrompt() {
  try {
    const data = input.trim() ? JSON.parse(input) : {};
    return String(data.prompt || data.userPrompt || data.message || '').trim();
  } catch (e) {
    return '';
  }
}

function isDeactivate(raw) {
  return /\b(stop|disable|deactivate|turn off)\b.*\bflint\b/i.test(raw) ||
    /\bflint\b.*\b(stop|disable|deactivate|turn off)\b/i.test(raw) ||
    /\bnormal mode\b/i.test(raw);
}

function activationMode(raw) {
  const slash = /^\/flint(?:\s+(\S+))?/i.exec(raw);
  if (slash) {
    const arg = String(slash[1] || 'full').toLowerCase();
    if (['off', 'stop', 'disable'].includes(arg)) return 'off';
    return VALID_MODES.includes(arg) ? arg : 'full';
  }

  if (!/\bflint\b/i.test(raw)) return null;
  if (!/\b(activate|enable|turn on|start)\b/i.test(raw)) return null;

  const match = /\b(lite|full|ultra|wenyan)\b/i.exec(raw);
  return match ? match[1].toLowerCase() : 'full';
}

function main() {
  const rawPrompt = getPrompt();

  if (rawPrompt && isDeactivate(rawPrompt)) {
    removeFlag(fp);
    setTerminalTitle(null);
    emitJson({ continue: true, systemMessage: '[FLINT: off]' });
    return;
  }

  const requestedMode = rawPrompt ? activationMode(rawPrompt) : null;
  if (requestedMode) {
    if (requestedMode === 'off') {
      removeFlag(fp);
      setTerminalTitle(null);
      emitJson({ continue: true, systemMessage: '[FLINT: off]' });
      return;
    }

    safeWriteFlag(fp, requestedMode);
    setTerminalTitle(requestedMode);
    appendHistory(requestedMode, 'activate');
    emitJson({ continue: true, systemMessage: `[FLINT: ${requestedMode.toUpperCase()}] activated.` });
    return;
  }

  const mode = readFlag(fp);
  if (!mode) {
    setTerminalTitle(null);
    emitJson({ continue: true });
    return;
  }

  const reinforcement = REINFORCEMENT[mode] || `[FLINT: ${mode.toUpperCase()}] active.`;
  setTerminalTitle(mode);
  appendHistory(mode, 'turn');
  emitJson({
    continue: true,
    systemMessage: reinforcement,
    hookSpecificOutput: {
      hookEventName: 'UserPromptSubmit',
      additionalContext: reinforcement
    }
  });
}
