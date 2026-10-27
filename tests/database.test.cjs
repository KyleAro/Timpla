const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const ts = require('typescript');

function load(relative, dependencies = {}) {
  const filename = path.resolve(__dirname, '..', relative);
  const output = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(output, { module, exports: module.exports, Map, Promise, Error,
    require(name) { if (name in dependencies) return dependencies[name]; throw new Error(`Unexpected dependency ${name}`); },
  }, { filename });
  return module.exports;
}
const styles = load('src/data/cookingStyles.ts');
const accountData = load('src/data/account.ts');
const preferenceRow = { servings: 4, diet: 'Halal', allergies: ['Eggs'], excluded_ingredients: ['Pepper'], cuisine_styles: { name: 'Bicolano' } };

function service(results) {
  const calls = [];
  const client = {
    async rpc(name, input) { calls.push(['rpc', name, input]); return results.rpc ?? { error: null }; },
    from(table) {
      const builder = {};
      for (const method of ['select', 'update', 'eq', 'single', 'overrideTypes', 'order']) {
        builder[method] = (...args) => { calls.push([table, method, ...args]); return builder; };
      }
      builder.then = (resolve, reject) => Promise.resolve(results[table]).then(resolve, reject);
      return builder;
    },
  };
  return { calls, api: load('src/services/account.ts', {
    '../auth/supabase': { authClient: () => client }, '../data/account': accountData, '../data/cookingStyles': styles,
  }) };
}

test('profile loading reads the owner rows and preserves cloud preferences', async () => {
  const h = service({ profiles: { data: { full_name: 'Maria' } }, user_preferences: { data: preferenceRow } });
  const result = await h.api.loadAccount('account-a', 'Ilocano');
  assert.equal(result.fullName, 'Maria'); assert.equal(result.preferences.cookingStyle, 'Bicolano');
  assert.equal(result.preferences.people, 4);
  assert.ok(h.calls.some(call => call[0] === 'profiles' && call[1] === 'eq' && call[2] === 'id' && call[3] === 'account-a'));
  assert.ok(h.calls.some(call => call[0] === 'user_preferences' && call[1] === 'eq' && call[3] === 'account-a'));
});

test('a failed profile read never substitutes default preferences or writes them', async () => {
  const h = service({ profiles: { error: new Error('Profile unavailable') }, user_preferences: { data: preferenceRow } });
  await assert.rejects(h.api.loadAccount('account-a', null), /Profile unavailable/);
  assert.equal(h.calls.filter(call => call[1] === 'update').length, 0);
});

test('preference updates save only requested fields, normalize lists, and target the owner', async () => {
  const h = service({ user_preferences: { data: preferenceRow } });
  await h.api.saveAccountPreferences('account-a', { allergies: [' Eggs ', 'eggs', '  Shellfish  '] });
  const update = h.calls.find(call => call[1] === 'update')[2];
  assert.equal(Object.keys(update).join(','), 'allergies');
  assert.equal(update.allergies.length, 2); assert.equal(update.allergies[1], 'Shellfish');
  assert.ok(h.calls.some(call => call[1] === 'eq' && call[2] === 'user_id' && call[3] === 'account-a'));
});

test('Any style clears the style foreign key and failed updates are reported', async () => {
  const h = service({ user_preferences: { error: new Error('Permission denied') } });
  await assert.rejects(h.api.saveAccountPreferences('account-a', { cookingStyle: 'Any style' }), /Permission denied/);
  assert.equal(h.calls.find(call => call[1] === 'update')[2].cuisine_style_id, null);
  assert.equal(h.calls.some(call => call[0] === 'cuisine_styles'), false);
});

test('invalid servings and blank profile names are rejected before any write', async () => {
  const h = service({});
  await assert.rejects(h.api.saveAccountPreferences('account-a', { people: 0 }), /1–20/);
  await assert.rejects(h.api.saveAccountName('account-a', '   '), /1–40/);
  assert.equal(h.calls.length, 0);
});

const catalog = load('src/data/catalog.ts', {
  './cookingStyles': styles,
  '../../assets/recipes/ensaladang-talong.png': 1, '../../assets/recipes/tortang-talong.png': 2,
});
const recipeRow = {
  slug: 'tortang-talong', name: 'Tortang talong', minutes: 15, servings: 2,
  steps: ['Grill', 'Fry'], image_path: 'asset:tortang-talong', cuisine_styles: null,
  recipe_ingredients: [
    { position: 2, quantity_text: '2 eggs', is_required: true, ingredients: { name: 'Egg' } },
    { position: 0, quantity_text: '2 eggplants', is_required: true, ingredients: { name: 'Eggplant' } },
    { position: 1, quantity_text: 'Optional garnish', is_required: false, ingredients: { name: 'Onion' } },
  ],
};

test('database recipes retain stable route IDs and align quantities with required ingredients', () => {
  const mapped = catalog.mapRecipe(recipeRow);
  assert.equal(mapped.id, 'tortang-talong'); assert.equal(mapped.image, 2);
  assert.equal(mapped.required.join(','), 'Eggplant,Egg');
  assert.equal(mapped.quantities.join(','), '2 eggplants,2 eggs');
  assert.equal(mapped.cookingStyle, undefined);
});

test('incomplete catalog records fail visibly instead of creating fabricated matches', () => {
  assert.throws(() => catalog.mapRecipe({ ...recipeRow, recipe_ingredients: [] }), /incomplete/);
  assert.throws(() => catalog.mapRecipe({ ...recipeRow, steps: 'not an array' }), /incomplete/);
});

test('remote catalog images use HTTPS and unsupported image identifiers are rejected', () => {
  const mapped = catalog.mapRecipe({ ...recipeRow, image_path: 'https://example.com/recipe.jpg' });
  assert.equal(mapped.image.uri, 'https://example.com/recipe.jpg');
  assert.throws(() => catalog.mapRecipe({ ...recipeRow, image_path: 'file:///private/image.jpg' }), /unavailable/);
});
