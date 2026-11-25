import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import recipeNeeds from '../dist/recipe-needs.js';
import { previewIngredientImport } from '../dist/ingredients.js';
const bytes = readFileSync(new URL('../../../ml/recipe_recommendation/models/quick_v1/catalog.json', import.meta.url));
const catalog = JSON.parse(bytes);
test('recipe priorities reconcile exactly to the serving catalog', () => {
  assert.equal(recipeNeeds.sourceSha256, createHash('sha256').update(bytes).digest('hex'));
  assert.equal(recipeNeeds.recipeCount, catalog.length);
  const counts = new Map();
  for (const recipe of catalog) for (const id of new Set(recipe.all_food)) counts.set(id, (counts.get(id) || 0) + 1);
  assert.equal(recipeNeeds.ingredients.length, counts.size);
  for (const need of recipeNeeds.ingredients) { assert.equal(need.recipeCount, counts.get(need.id)); assert.ok(need.essentialRecipeCount <= need.recipeCount); assert.ok(need.examples.length > 0); }
});
test('photo folder suggestions keep sauces separate from meat and seafood', () => {
  const byId = new Map(recipeNeeds.ingredients.map(need => [need.id, need]));
  assert.equal(byId.get('shrimp').subgroup, 'Shrimp & Prawns');
  assert.equal(byId.get('shrimp_paste').category, 'Pantry & seasonings');
  assert.equal(byId.get('beef_broth').category, 'Pantry & seasonings');
  assert.equal(byId.get('pork_belly').category, 'Pork');
  assert.equal(byId.get('tomato').category, 'Vegetables');
  assert.ok(recipeNeeds.suggestedFolderIds.includes('garlic'));
  assert.ok(!recipeNeeds.suggestedFolderIds.includes('aa_powder'));
});
test('complete recipe ingredient JSON can be imported without manual rewriting', () => {
  const text = readFileSync(new URL('../dist/recipe-ingredients.json', import.meta.url), 'utf8');
  const preview = previewIngredientImport(text);
  assert.equal(preview.added.length + preview.skipped.length, recipeNeeds.ingredientCount);
});
