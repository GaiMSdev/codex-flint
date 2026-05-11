#!/usr/bin/env node
'use strict';

const {
  MODE_RULES,
  appendHistory,
  emitJson,
  flagPath,
  getDefaultMode,
  readFlag,
  safeWriteFlag,
  setTerminalTitle
} = require('./flint-config');

const fp = flagPath();
let mode = readFlag(fp);

if (!mode) {
  const defaultMode = getDefaultMode();
  if (defaultMode !== 'off') {
    safeWriteFlag(fp, defaultMode);
    mode = defaultMode;
  }
}

if (!mode) {
  setTerminalTitle(null);
  emitJson({ continue: true });
  process.exit(0);
}

setTerminalTitle(mode);
appendHistory(mode, 'session');
emitJson({
  continue: true,
  systemMessage: MODE_RULES[mode]
});
