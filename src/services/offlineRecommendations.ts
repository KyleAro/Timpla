import catalog from '../data/offlineRecipeCatalog.json';
import type { Recommendation } from './recommendations';

type Requirement = { ingredient_id?: string; all_of?: Requirement[]; any_of?: Requirement[] };
type Recipe = { id: string; name: string; family: string; essential: Requirement; supporting: string[]; all_food: string[] };
const recipes = catalog as Recipe[];
const aliases: Record<string, string> = {
  eggs: 'egg', itlog: 'egg', talong: 'eggplant', kamatis: 'tomato', tomatoes: 'tomato',
  bawang: 'garlic', sibuyas: 'onion', oil: 'cooking_oil', mantika: 'cooking_oil',
  toyo: 'soy_sauce', suka: 'vinegar', asin: 'salt', repolyo: 'cabbage',
  sayote: 'chayote', upo: 'bottle_gourd', ampalaya: 'bitter_gourd',
  chicken_generic: 'chicken', pork_generic: 'pork',
};
const allergens: Record<string, RegExp> = {
  peanuts: /peanut|groundnut|arachis/,
  'tree nuts': /almond|cashew|walnut|pecan|pistachio|hazelnut|macadamia|brazil_nut|pine_nut/,
  shellfish: /shrimp|prawn|crab|lobster|crayfish|clam|mussel|oyster|scallop|squid|cuttlefish|octopus|bagoong|alamang|hipon|patis|fish_sauce|seafood|surimi/,
  fish: /fish|tilapia|bangus|tuna|salmon|sardine|anchov|patis|bagoong|seafood|surimi/,
  eggs: /(^|_)eggs?(_|$)|mayonnaise|meringue|custard|leche_flan/,
  dairy: /milk|cream|cheese|butter|yogurt|yoghurt|whey|casein|ghee|margarine|chocolate/,
  soy: /soy|soya|tofu|tokwa|taho|miso|edamame|tempeh|teriyaki|hoisin|oyster_sauce|margarine/,
  wheat: /wheat|flour|bread|pasta|spaghetti|macaroni|noodle|pancit|panko|cracker|biscuit|soy_sauce|teriyaki|hoisin|oyster_sauce|lumpia_wrapper|wonton|dumpling_wrapper|seitan/,
  sesame: /sesame|tahini/,
};

function normalize(value: string) {
  const key = value.trim().toLowerCase().replace(/\s+/g, '_');
  return aliases[key] ?? key;
}

function matches(requirement: Requirement, available: Set<string>): boolean {
  if (requirement.ingredient_id) return available.has(requirement.ingredient_id);
  if (requirement.any_of) return requirement.any_of.some(item => matches(item, available));
  return (requirement.all_of ?? []).every(item => matches(item, available));
}

export function getOfflineRecommendations(availableNames: string[], excludedNames: string[], preferences: { allergies: string[]; diet: string }): Recommendation[] {
  const available = new Set(availableNames.map(normalize));
  if (!available.size || preferences.diet !== 'No preference') return [];
  const excluded = excludedNames.map(normalize);
  const allergyPatterns: (RegExp | null)[] = preferences.allergies.map(name => allergens[name.toLowerCase()] ?? null);
  // Unknown allergies need reviewed declarations, which this draft catalog lacks.
  if (allergyPatterns.includes(null)) return [];
  const candidates: { item: Recommendation; family: string }[] = [];
  for (const recipe of recipes) {
    if (!matches(recipe.essential, available)) continue;
    if (recipe.all_food.some(food => excluded.some(value => food === value || food.startsWith(`${value}_`) || food.endsWith(`_${value}`)))) continue;
    if (recipe.all_food.some(food => allergyPatterns.some(pattern => pattern?.test(food)))) continue;
    const used = recipe.all_food.filter(food => available.has(food));
    const missing = recipe.supporting.filter(food => !available.has(food));
    const total = recipe.all_food.length;
    if (!total) continue;
    const rankingScore = used.length / available.size * 0.65 + (recipe.supporting.length ? (recipe.supporting.length - missing.length) / recipe.supporting.length : 0) * 0.35;
    candidates.push({ family: recipe.family, item: {
      id: recipe.id, name: recipe.name, ranking_score: rankingScore,
      ingredient_match: { matched: used.length, total, percentage: Math.round(100 * used.length / total) },
      used_ingredients: used.map(name => name.replace(/_/g, ' ')),
      missing_supporting: missing,
      quantity_and_preparation_check_needed: true,
    } });
  }
  candidates.sort((a, b) => b.item.ranking_score - a.item.ranking_score || a.item.missing_supporting.length - b.item.missing_supporting.length || a.item.id.localeCompare(b.item.id));
  const seen = new Set<string>();
  const result: Recommendation[] = [];
  for (const candidate of candidates) {
    if (seen.has(candidate.family)) continue;
    seen.add(candidate.family);
    result.push(candidate.item);
    if (result.length === 5) break;
  }
  return result;
}
