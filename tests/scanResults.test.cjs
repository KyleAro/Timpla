const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function load(relative, dependencies, globals = {}) {
  const filename = path.resolve(process.cwd(), relative);
  const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(code, { module, exports: module.exports, Map, Set, Error,
    require(name) { if (name in dependencies) return dependencies[name]; throw Error(`Unexpected import ${name}`); },
    ...globals,
  }, { filename });
  return module.exports;
}
const normalization = load('src/utils/normalizeIngredient.ts', {});
const { scanReducer, initialScanState } = load('src/state/scanHistory.ts', { '../utils/normalizeIngredient': normalization });
const capture = (state, id) => scanReducer(state, { type: 'capture', scan: { id, photo: `${id}.jpg`, createdAt: 1, ingredients: [], selectedDish: null } });
const predicted = [{ name: 'Egg', label: 'egg', confidence: 0.9 }, { name: 'Tomato', label: 'tomato', confidence: 0.8 }];

test('saved results retain edited ingredients and discarding leaves other history intact', () => {
  let state = capture(initialScanState, 'saved');
  state = scanReducer(state, { type: 'ingredients', names: ['Egg', 'Salt'] });
  state = scanReducer(state, { type: 'save' });
  assert.equal(state.recentScans[0].saved, true);
  assert.equal(state.recentScans[0].ingredients.map(item => item.name).join(','), 'Egg,Salt');
  state = capture(state, 'draft');
  state = scanReducer(state, { type: 'discard' });
  assert.equal(state.photo, null);
  assert.equal(state.activeId, null);
  assert.equal(state.ingredients.length, 0);
  assert.equal(state.recentScans.length, 1);
  assert.equal(state.recentScans[0].id, 'saved');
  assert.equal(scanReducer(state, { type: 'detected', id: 'draft', ingredients: predicted }), state);
});

test('restoring saved history preserves an active draft without duplicates', () => {
  const state = capture(initialScanState, 'draft');
  const saved = { id: 'saved', photo: 'saved.jpg', createdAt: 1, ingredients: [], selectedDish: null, saved: true };
  const restored = scanReducer(state, { type: 'restore', scans: [saved, state.recentScans[0]] });
  assert.equal(restored.activeId, 'draft');
  assert.equal(restored.photo, 'draft.jpg');
  assert.equal(restored.recentScans.length, 2);
});

test('deleting a history entry preserves other entries and clears only the deleted active scan', () => {
  let state = capture(capture(initialScanState, 'older'), 'current');
  state = scanReducer(state, { type: 'delete', id: 'older' });
  assert.equal(state.activeId, 'current');
  assert.equal(state.recentScans.length, 1);
  state = scanReducer(state, { type: 'delete', id: 'current' });
  assert.equal(state.activeId, null);
  assert.equal(state.photo, null);
  assert.equal(state.recentScans.length, 0);
});
