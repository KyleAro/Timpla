import test from 'node:test';
import assert from 'node:assert/strict';
import { previewIngredientImport, seafoodSubgroup, starterIngredients } from '../dist/ingredients.js';
test('grouped ingredient JSON creates fruit and vegetable folders', () => {
  const result = previewIngredientImport('{"fruits":["Mango","Banana"],"vegetables":["Tomato","Carrot"]}');
  assert.equal(result.added.length, 4);
  assert.deepEqual(result.added[2], { name: 'Tomato', category: 'Vegetables', exportName: 'tomato' });
});
test('duplicates preserve existing labels and collapse spaces and case', () => {
  const existing = [{ id: 'keep', name: 'Sweet Mango', exportName: 'sweet_mango', category: 'Fruits' }];
  const before = JSON.stringify(existing);
  const result = previewIngredientImport('{"fruits":["  sweet   MANGO ","Banana","banana","Sweet-Mango"]}', existing);
  assert.equal(result.added.length, 1); assert.equal(result.skipped.length, 3); assert.equal(JSON.stringify(existing), before);
});
test('invalid and empty input is rejected before any changes are applied', () => {
  for (const input of ['{"fruits":["Mango",]}', '[]', '{"fruits":"Mango"}', '{"fruits":[null]}', '{"fruits":[""]}', '{"fruits":[]}']) assert.throws(() => previewIngredientImport(input));
  assert.equal(previewIngredientImport('{"fruits":["Mango"]}', [{ name: 'Mango', exportName: 'mango' }]).added.length, 0);
});
test('nested seafood imports preserve subgroups and normalize category aliases', () => {
  const result = previewIngredientImport('{"seafoods":{"Shrimp & Prawns":["White shrimp","Tiger prawn"],"Fish":["Tilapia"]},"chicken":["Chicken thigh"]}');
  assert.equal(result.added.length, 4);
  assert.equal(result.added[0].category, 'Seafood');
  assert.equal(result.added[0].subgroup, 'Shrimp & Prawns');
  assert.equal(result.added[2].subgroup, 'Fish');
  assert.equal(result.added[3].category, 'Chicken');
  assert.equal(seafoodSubgroup('White shrimp'), 'Shrimp & Prawns');
  assert.ok(starterIngredients.Pork.includes('Pork belly'));
  assert.ok(starterIngredients.Beef.includes('Beef ribs'));
  assert.throws(() => previewIngredientImport('{"seafood":{"Fish":{"nested":["Tilapia"]}}}'));
});
