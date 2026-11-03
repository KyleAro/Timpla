const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const Module = require('node:module');
const path = require('node:path');
const filename = path.resolve('src/services/recommendations.ts');
const mod = new Module(filename, module);
mod._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
}).outputText, filename);
const { getRecommendations } = mod.exports;

test('sends confirmed inventory and returns model suggestions', async () => {
  const original = global.fetch;
  const previous = process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
  process.env.EXPO_PUBLIC_RECOMMENDATION_URL = 'http://localhost:8001';
  try {
    global.fetch = async (url, request) => {
      assert.equal(url, 'http://localhost:8001/recommendations');
      assert.deepEqual(JSON.parse(request.body), { available: ['egg', 'eggplant'], limit: 5 });
      return { ok: true, json: async () => ({ recommendations: [{ id: 'r1', name: 'Tortang Talong', ranking_score: 0.3, missing_supporting: ['salt'] }] }) };
    };
    const result = await getRecommendations(['egg', 'eggplant'], new AbortController().signal);
    assert.deepEqual(result[0].missing_supporting, ['salt']);
  } finally {
    global.fetch = original;
    if (previous === undefined) delete process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
    else process.env.EXPO_PUBLIC_RECOMMENDATION_URL = previous;
  }
});

test('rejects non-JSON errors and malformed recipe responses', async () => {
  const original = global.fetch;
  const previous = process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
  process.env.EXPO_PUBLIC_RECOMMENDATION_URL = 'http://localhost:8001';
  try {
    global.fetch = async () => ({ ok: false, json: async () => { throw Error('HTML error'); } });
    await assert.rejects(getRecommendations(['egg'], new AbortController().signal), /unreadable/);
    global.fetch = async () => ({ ok: true, json: async () => ({ recommendations: [{ id: 'bad' }] }) });
    await assert.rejects(getRecommendations(['egg'], new AbortController().signal), /Invalid recipe/);
    global.fetch = async () => ({ ok: true, json: async () => ({ recommendations: [] }) });
    assert.deepEqual(await getRecommendations(['egg'], new AbortController().signal), []);
  } finally {
    global.fetch = original;
    if (previous === undefined) delete process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
    else process.env.EXPO_PUBLIC_RECOMMENDATION_URL = previous;
  }
});
