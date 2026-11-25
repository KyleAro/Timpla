const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');
const ts = require('../node_modules/typescript');
const moduleUnderTest = { exports: {} };
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/auth/onboarding.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { module: moduleUnderTest, exports: moduleUnderTest.exports });
const { hasCompletedOnboarding } = moduleUnderTest.exports;

test('new installation and unfinished or corrupted setup require onboarding', () => {
  for (const raw of [null, '', 'broken', 'null', '[]', '{}', 'true',
    JSON.stringify({ name: 'Juan' }),
    JSON.stringify({ completed: false, name: 'Juan', preferences: {} }),
  ]) assert.equal(hasCompletedOnboarding(raw), false);
});

test('completion is recognized with either a name or the skipped name', () => {
  for (const name of ['Juan', '']) {
    assert.equal(hasCompletedOnboarding(JSON.stringify({
      completed: true, name, preferences: { people: 2, allergies: [] },
    })), true);
  }
});

test('existing completed setup from the previous app version is preserved', () => {
  assert.equal(hasCompletedOnboarding(JSON.stringify({
    name: 'Juan', preferences: { people: 2, allergies: ['Peanuts'] },
  })), true);
});
