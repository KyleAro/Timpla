const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const ts = require('typescript');
function load(file, imports = {}) {
  const filename = path.resolve(file);
  const mod = new Module(filename, module);
  mod.filename = filename;
  const original = mod.require.bind(mod);
  mod.require = name => imports[name] || original(name);
  mod._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true },
  }).outputText, filename);
  return mod.exports;
}
const helpers = load('src/utils/normalizeIngredient.ts');
const { ingredientSuggestions, canonicalIngredientName } = load('src/utils/ingredientSuggestions.ts', { './normalizeIngredient': helpers });
test('rice search includes different forms without collapsing identities', () => {
  const names = ingredientSuggestions('rice', []).map(x => x.name.toLowerCase());
  assert.ok(names.includes('cooked white rice'));
  assert.ok(names.some(x => x.includes('rice') && x.includes('flour')));
  assert.ok(names.some(x => x.includes('fried rice')));
  assert.ok(names.length > 6);
  assert.notEqual(canonicalIngredientName('Rice flour'), canonicalIngredientName('Cooked white rice'));
});
test('aliases find families, selection and category filters still apply', () => {
  assert.ok(ingredientSuggestions('manok', []).some(x => /chicken breast/i.test(x.name)));
  assert.ok(ingredientSuggestions('pork', []).some(x => /ground pork/i.test(x.name)));
  assert.ok(ingredientSuggestions('rice', ['Cooked white rice']).every(x => x.name !== 'Cooked white rice'));
  assert.ok(ingredientSuggestions('chicken', [], 100, 'Meat').every(x => x.category === 'Meat'));
});
