const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const Module = require('node:module');
const path = require('node:path');
const filename = path.resolve('src/services/recommendations.ts');
const mod = new Module(filename, module);
mod.filename = filename;
mod.require = Module.createRequire(filename);
mod._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
}).outputText, filename);
const { getRecommendations } = mod.exports;
const ingredientCounts = require('../src/data/recipeIngredientCounts.json');
const catalogId = Object.keys(ingredientCounts).find(id => ingredientCounts[id] > 0);

test('requires server acknowledgement of saved restrictions', async () => {
  const original = global.fetch;
  const previous = process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
  process.env.EXPO_PUBLIC_RECOMMENDATION_URL = 'http://localhost:8001';
  const preferences = { allergies: ['Peanuts'], diet: 'Vegetarian' };
  try {
    global.fetch = async (_, request) => {
      assert.deepEqual(JSON.parse(request.body), { available: ['eggplant'], excluded: ['garlic'], ...preferences, limit: 20 });
      return { ok: true, json: async () => ({ recommendations: [] }) };
    };
    await assert.rejects(getRecommendations(['eggplant'], ['garlic'], new AbortController().signal, preferences), /saved restrictions/);
    global.fetch = async () => ({ ok: true, json: async () => ({ recommendations: [], applied_preferences: { ...preferences, excluded: ['garlic'] } }) });
    assert.deepEqual(await getRecommendations(['eggplant'], ['garlic'], new AbortController().signal, preferences), []);
  } finally {
    global.fetch = original;
    if (previous === undefined) delete process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
    else process.env.EXPO_PUBLIC_RECOMMENDATION_URL = previous;
  }
});

test('sends confirmed inventory and returns model suggestions', async () => {
  const original = global.fetch;
  const previous = process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
  process.env.EXPO_PUBLIC_RECOMMENDATION_URL = 'http://localhost:8001';
  try {
    global.fetch = async (url, request) => {
      assert.equal(url, 'http://localhost:8001/recommendations');
      assert.deepEqual(JSON.parse(request.body), { available: ['egg', 'eggplant'], excluded: [], allergies: [], diet: 'No preference', limit: 20 });
      return { ok: true, json: async () => ({ recommendations: [{ id: catalogId, name: 'Tortang Talong', ranking_score: 0.3, used_ingredients: ['egg'], missing_supporting: ['salt'] }] }) };
    };
    const result = await getRecommendations(['egg', 'eggplant'], [], new AbortController().signal);
    assert.deepEqual(result[0].missing_supporting, ['salt']);
    assert.equal(result[0].ingredient_match.percentage, Math.round(100 / ingredientCounts[catalogId]));
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
    await assert.rejects(getRecommendations(['egg'], [], new AbortController().signal), /unreadable/);
    global.fetch = async () => ({ ok: true, json: async () => ({ recommendations: [{ id: 'bad' }] }) });
    await assert.rejects(getRecommendations(['egg'], [], new AbortController().signal), /Invalid recipe/);
    const recipe = { id: 'coverage', name: 'Coverage fixture', ranking_score: 0.3, missing_supporting: [], ingredient_match: { matched: 3, total: 5, percentage: 60 } };
    global.fetch = async () => ({ ok: true, json: async () => ({ recommendations: [recipe] }) });
    assert.equal((await getRecommendations(['egg'], [], new AbortController().signal))[0].ingredient_match.percentage, 60);
    recipe.ingredient_match.percentage = 90;
    await assert.rejects(getRecommendations(['egg'], [], new AbortController().signal), /Invalid ingredient match/);
    global.fetch = async () => ({ ok: true, json: async () => ({ recommendations: [] }) });
    assert.deepEqual(await getRecommendations(['egg'], [], new AbortController().signal), []);
  } finally {
    global.fetch = original;
    if (previous === undefined) delete process.env.EXPO_PUBLIC_RECOMMENDATION_URL;
    else process.env.EXPO_PUBLIC_RECOMMENDATION_URL = previous;
  }
});
