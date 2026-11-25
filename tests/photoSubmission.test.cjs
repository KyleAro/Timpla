const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');

function setup(detect) {
  const state = [];
  const navigations = [];
  let cleanup;
  const dependencies = {
    react: {
      useRef: current => ({ current }), useCallback: fn => fn, useEffect: fn => fn(),
      useState: initial => { const index = state.length; state.push(initial); return [initial, value => { state[index] = value; }]; },
    },
    'expo-router': { router: { push: route => navigations.push(route) }, useFocusEffect: fn => { cleanup = fn(); } },
    '../state/CookingContext': { useCooking: () => ({ setPhoto: detect }) },
  };
  const module = { exports: {} };
  const code = ts.transpileModule(fs.readFileSync('src/hooks/usePhotoSubmission.ts', 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, require: name => dependencies[name] });
  return { api: module.exports.usePhotoSubmission(), state, navigations, leave: () => cleanup() };
}

test('camera and upload submissions only open Results after ingredients are found', async () => {
  for (const outcome of ['found', 'empty', 'error', 'cancelled']) {
    const run = setup(async () => outcome);
    await run.api.submit('photo.jpg');
    assert.equal(run.navigations.join(','), outcome === 'found' ? '/ingredients' : '');
    assert.equal(run.state[0], false);
    assert.equal(run.state[1], ['empty', 'error'].includes(outcome) ? outcome : null);
  }
});

test('leaving scanner cancels a pending submission and prevents late navigation', async () => {
  let resolve;
  const calls = [];
  const run = setup(uri => { calls.push(uri); return uri === null ? Promise.resolve('cancelled') : new Promise(done => { resolve = done; }); });
  const submission = run.api.submit('photo.jpg');
  run.leave();
  resolve('found');
  await submission;
  assert.deepEqual(calls, ['photo.jpg', null]);
  assert.equal(run.navigations.length, 0);
});
