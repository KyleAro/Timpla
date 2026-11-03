const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const ts = require('typescript');

function mount(account, storage) {
  const states = [];
  const react = { useRef: value => ({ current: value }), useState: value => {
    const index = states.push(value) - 1;
    return [value, next => { states[index] = next; }];
  }, useEffect: callback => callback() };
  const filename = path.resolve('src/hooks/useCookingHistory.ts');
  const mod = new Module(filename, module);
  mod.require = name => name === 'react' ? react : storage;
  mod._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true },
  }).outputText, filename);
  return { hook: mod.exports.useCookingHistory(account), states };
}
test('cooked recipes persist, reload and stay isolated by account', async () => {
  const db = new Map();
  const storage = { getItem: async key => db.get(key), setItem: async (key, value) => db.set(key, value) };
  const first = mount('kyle', storage);
  await Promise.resolve();
  await first.hook.recordCookedRecipe('version-a', 'Adobo');
  assert.equal(first.states[0][0].recipeId, 'version-a');
  assert.ok(first.states[0][0].cookedAt > 0);
  const reload = mount('kyle', storage);
  const other = mount('another-user', storage);
  await Promise.resolve();
  assert.equal(reload.states[0][0].name, 'Adobo');
  assert.deepEqual(other.states[0], []);
});
test('failed persistence does not falsely add a cooked entry', async () => {
  const mounted = mount('kyle', { getItem: async () => null, setItem: async () => { throw Error('disk'); } });
  await Promise.resolve();
  await assert.rejects(mounted.hook.recordCookedRecipe('a', 'Adobo'));
  assert.deepEqual(mounted.states[0], []);
});
