const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const Module = require('node:module');
const path = require('node:path');
const ts = require('typescript');

const filename = path.resolve(__dirname, '../src/services/offlineRecommendations.ts');
const source = fs.readFileSync(filename, 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const loaded = new Module(filename, module);
loaded.filename = filename;
loaded.paths = Module._nodeModulePaths(path.dirname(filename));
loaded._compile(compiled, filename);
const { getOfflineRecommendations } = loaded.exports;
const unrestricted = { allergies: [], diet: 'No preference' };

test('offline matches use local recipe requirements and report ingredient coverage', () => {
  const results = getOfflineRecommendations(['Egg', 'Beef ribs', 'Tilapia'], [], unrestricted);
  assert.ok(results.some(item => item.name.includes('Tilapia')));
  for (const item of results) {
    assert.equal(item.ingredient_match.percentage, Math.round(100 * item.ingredient_match.matched / item.ingredient_match.total));
  }
});

test('offline matches respect exclusions and conservatively handle allergies and diets', () => {
  assert.equal(getOfflineRecommendations(['Tilapia'], ['Tilapia'], unrestricted).length, 0);
  assert.equal(getOfflineRecommendations(['Tilapia'], [], { allergies: ['Fish'], diet: 'No preference' }).length, 0);
  assert.equal(getOfflineRecommendations(['Tilapia'], [], { allergies: ['Unreviewed allergy'], diet: 'No preference' }).length, 0);
  assert.equal(getOfflineRecommendations(['Tilapia'], [], { allergies: [], diet: 'Vegetarian' }).length, 0);
});
