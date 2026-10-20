// Offline fixture. Writes a minimal CLI where the installer expects npm's package.
const fs = require('node:fs');
const path = require('node:path');
if (process.env.TEST_NPM_FAIL) process.exit(23);
const args = process.argv.slice(2);
if (!args.includes('@krodak/clickup-cli@latest') || !args.includes('--ignore-scripts')) process.exit(24);
const root = path.join(args[args.indexOf('--prefix') + 1], 'node_modules/@krodak/clickup-cli');
fs.mkdirSync(path.join(root, 'dist'), {recursive: true});
fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({version:'9.0.0-test', bin:{cup:'./dist/index.cjs'}}));
fs.writeFileSync(path.join(root, 'dist/index.cjs'), 'console.log(process.argv.includes("--version") ? "9.0.0-test" : JSON.stringify(process.argv.slice(2)))');
