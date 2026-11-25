const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');
const ts = require('../node_modules/typescript');
const moduleUnderTest = { exports: {} };
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/utils/onboardingNavigation.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { module: moduleUnderTest, exports: moduleUnderTest.exports });
const { storyDirection } = moduleUnderTest.exports;

test('left and right taps move between onboarding pages', () => {
  assert.equal(storyDirection({ x: 50, y: 200 }, { x: 50, y: 200 }, 400, false), -1);
  assert.equal(storyDirection({ x: 350, y: 200 }, { x: 350, y: 200 }, 400, false), 1);
  assert.equal(storyDirection({ x: 190, y: 200 }, { x: 190, y: 200 }, 400, false), -1);
  assert.equal(storyDirection({ x: 210, y: 200 }, { x: 210, y: 200 }, 400, false), 1);
});

test('horizontal swipes navigate but vertical scrolling and form touches do not', () => {
  assert.equal(storyDirection({ x: 300, y: 200 }, { x: 100, y: 205 }, 400, false), 1);
  assert.equal(storyDirection({ x: 100, y: 200 }, { x: 300, y: 205 }, 400, false), -1);
  assert.equal(storyDirection({ x: 300, y: 200 }, { x: 100, y: 390 }, 400, false), 0);
  assert.equal(storyDirection({ x: 300, y: 200 }, { x: 100, y: 205 }, 400, true), 0);
});
