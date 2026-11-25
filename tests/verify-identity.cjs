// Run against a disposable checkout at the pinned upstream commit.
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = process.argv[2];
assert(root, 'Usage: node tests/verify-identity.cjs DISPOSABLE_CHECKOUT');
const file = path.resolve(root, 'apps/desktop/product-identity.cjs');
const code = 'process.stdout.write(JSON.stringify(require(process.argv[1])))';
function run(variant, legacy, channel) {
  return spawnSync(process.execPath, [...(legacy ? ['--no-experimental-require-module'] : []), '-e', code, file], {
    env: { HERMES_DESKTOP_VARIANT: variant, ...(channel === undefined ? {} : { _HERMES_CHANNEL_REQUEST_JSON: channel }) }, encoding: 'utf8'
  });
}
for (const [variant, name] of [['', 'Hermes'], ['light', 'Hermes Light'], ['bundled', 'Hermes Agent']]) {
  const result = run(variant, true);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).displayName, name);
  assert.deepEqual(JSON.parse(result.stdout), JSON.parse(run(variant, false).stdout));
}
const invalid = run('bundled', false, '{invalid');
assert.notEqual(invalid.status, 0, 'invalid channel request must not fall back silently');
assert.match(invalid.stderr, /SyntaxError/);
console.log('PASS: three non-channel identities on the legacy loader; invalid channel input rejected on the modern loader');
