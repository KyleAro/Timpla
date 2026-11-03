import baseOptions from '../data/ingredientOptions.json';
import recipeOptions from '../data/recipeIngredientOptions.json';
import { normalizeIngredient } from './normalizeIngredient';
const options = [...baseOptions, ...recipeOptions];

export const ingredientCategories = ['All', 'Fruits', 'Vegetables', 'Meat', 'Seafood', 'Condiments', 'Others'] as const;
export type IngredientCategory = typeof ingredientCategories[number];

// Local vocabulary from the active detector labels, pantry items and common
// English/Filipino aliases. Suggestions work without a server request.
export function canonicalIngredientName(value: string): string {
  const key = normalizeIngredient(value);
  return options.find(option => [option.name, ...option.aliases].some(name => normalizeIngredient(name) === key))?.name
    ?? value.trim().replace(/\s+/g, ' ');
}

export function ingredientSuggestions(query: string, selected: string[], limit = Number.MAX_SAFE_INTEGER, category: IngredientCategory = 'All') {
  const key = normalizeIngredient(query);
  const terms = new Set([key]);
  // Search aliases as ingredient families without treating the variants as synonyms.
  for (const option of baseOptions) {
    if (option.aliases.some(alias => normalizeIngredient(alias) === key)) terms.add(normalizeIngredient(option.name));
  }
  const existing = new Set(selected.map(value => normalizeIngredient(canonicalIngredientName(value))));
  return options.filter(option => category === 'All' || option.category === category).map(option => {
    const name = normalizeIngredient(option.name);
    const aliases = option.aliases.map(normalizeIngredient);
    const rank = name === key ? 0 : name.startsWith(key) ? 1
      : aliases.some(alias => alias.startsWith(key)) ? 2
      : [...terms].some(term => term.split(' ').every(token => [name, ...aliases].some(value => value.split(' ').some(word => word.startsWith(token))))) ? 3 : 4;
    return { ...option, rank };
  }).filter(option => option.rank < 4 && !existing.has(normalizeIngredient(option.name)))
    .sort((first, second) => first.rank - second.rank || first.name.localeCompare(second.name))
    .slice(0, limit);
}
