const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = JSON.parse(fs.readFileSync(path.join(root, 'ml/recipe_recommendation/data/processed/recipes.cleaned.json'), 'utf8'));
// Only remove presentation wording and known translations. Keep meat, method,
// regional names and other meaningful qualifiers in the family identity.
function dishName(name) {
  return name.replace(/\brecipe\b/gi, '').replace(/^basic\s+/i, '')
    .replace(/\s*\((?:filipino )?eggplant (?:omelet|omelette)\)\s*/gi, ' ')
    .replace(/\s+/g, ' ').trim();
}
const rows = source.map(x => {
  const title = dishName(x.name);
  const url = x.sources.find(s => /^https?:/.test(s.source_url))?.source_url || '';
  const collections = [...new Set(x.sources.map(s => s.collection))];
  return { id: x.id, name: x.name, dishName: title, family: title.toLowerCase(), ingredients: x.full_ingredients, steps: x.instructions, sourceUrl: url,
    sourceLabel: url ? new URL(url).hostname.replace(/^www\./, '') : collections.join(', ').replaceAll('_', ' ') };
}).sort((a, b) => a.name.localeCompare(b.name));
fs.writeFileSync(path.join(root, 'src/data/recipeDataset.json'), JSON.stringify(rows, null, 2) + '\n');
fs.writeFileSync(path.join(root, 'ml/recipe_recommendation/data/recipe_families.json'), JSON.stringify(Object.fromEntries(rows.map(r => [r.id, r.family])), null, 2) + '\n');
console.log(`${rows.length} records, ${new Set(rows.map(r => r.family)).size} dish groups`);
