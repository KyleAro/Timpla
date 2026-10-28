import options from '../data/ingredientOptions.json';
import { normalizeIngredient } from './normalizeIngredient';

export const ingredientCategories = ['All', 'Fruits', 'Vegetables', 'Meat', 'Seafood', 'Condiments', 'Others'] as const;
export type IngredientCategory = typeof ingredientCategories[number];

// Local vocabulary from the active detector labels, pantry items and common
// English/Filipino aliases. Suggestions work without a server request.
export function canonicalIngredientName(value: string): string {
  const key = normalizeIngredient(value);
  return options.find(option => [option.name, ...option.aliases].some(name => normalizeIngredient(name) === key))?.name
    ?? value.trim().replace(/\s+/g, ' ');
}

export function ingredientSuggestions(query: string, selected: string[], limit = 6, category: IngredientCategory = 'All') {
  const key = normalizeIngredient(query);
  const existing = new Set(selected.map(value => normalizeIngredient(canonicalIngredientName(value))));
  return options.filter(option => category === 'All' || option.category === category).map(option => {
    const name = normalizeIngredient(option.name);
    const aliases = option.aliases.map(normalizeIngredient);
    const rank = name.startsWith(key) ? 0
      : aliases.some(alias => alias.startsWith(key)) ? 1
      : name.split(' ').some(word => word.startsWith(key)) ? 2
      : key.length > 1 && [name, ...aliases].some(value => value.includes(key)) ? 3 : 4;
    return { ...option, rank };
  }).filter(option => option.rank < 4 && !existing.has(normalizeIngredient(option.name)))
    .sort((first, second) => first.rank - second.rank || first.name.localeCompare(second.name))
    .slice(0, limit);
}
