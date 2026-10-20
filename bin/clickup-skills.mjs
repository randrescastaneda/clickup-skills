#!/usr/bin/env node
// No install lifecycle hook: setup runs only when the user explicitly invokes it.
import { spawnSync } from 'node:child_process';
import { existsSync, realpathSync } from 'node:fs';
import { dirname, delimiter, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

if (Number(process.versions.node.split('.')[0]) < 22) {
  console.error('ClickUp Skills needs Node.js 22 or later.');
  process.exit(1);
}
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const candidates = process.env.CLICKUP_SKILLS_PYTHON
  ? [[process.env.CLICKUP_SKILLS_PYTHON]]
  : [['python3'], ['python'], ['py', '-3']];
let python;
for (const command of candidates) {
  const result = spawnSync(command[0], [...command.slice(1), '-I', '-c',
    'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'], { stdio: 'ignore', shell: false });
  if (result.status === 0) { python = command; break; }
}
if (!python) {
  console.error('Install Python 3.11+ and rerun this command. No clone or manual virtual environment is needed.');
  process.exit(1);
}
const npmCandidates = [process.env.npm_execpath, join(dirname(process.execPath), 'node_modules/npm/bin/npm-cli.js')];
for (const part of (process.env.PATH || '').split(delimiter)) {
  const npm = join(part, process.platform === 'win32' ? 'npm.cmd' : 'npm');
  if (existsSync(npm)) {
    npmCandidates.push(realpathSync(npm), join(dirname(npm), 'node_modules/npm/bin/npm-cli.js'));
  }
}
const npm = npmCandidates.find(path => path && existsSync(path) && !path.endsWith('.cmd'));
const result = spawnSync(python[0], [...python.slice(1), '-I', join(root, 'scripts/setup.py'), ...args], {
  stdio: 'inherit', shell: false,
  env: { ...process.env, CLICKUP_SKILLS_NODE: process.execPath, ...(npm ? { CLICKUP_SKILLS_NPM_CLI: npm } : {}) }
});
if (result.error) console.error('Could not launch Python. Check your Python installation.');
process.exit(result.status ?? 1);
