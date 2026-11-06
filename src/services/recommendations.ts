import ingredientCounts from '../data/recipeIngredientCounts.json';

export type Recommendation = {
  id: string;
  name: string;
  ranking_score: number;
  used_ingredients?: string[];
  ingredient_match?: { matched: number; total: number; percentage: number };
  missing_essential?: string[];
  missing_supporting: string[];
  quantity_and_preparation_check_needed: boolean;
};

export async function getRecommendations(available: string[], excluded: string[], signal: AbortSignal, preferences: { allergies: string[]; diet: string } = { allergies: [], diet: 'No preference' }): Promise<Recommendation[]> {
  const configured = process.env.EXPO_PUBLIC_RECOMMENDATION_URL?.trim().replace(/\/$/, '');
  const base = configured || (typeof window !== 'undefined' && window.location?.hostname ? `${window.location.protocol}//${window.location.hostname}:8001` : '');
  if (!base) throw new Error('Set EXPO_PUBLIC_RECOMMENDATION_URL to the recommendation server address.');
  let response: Response;
  try {
    response = await fetch(`${base}/recommendations`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
      body: JSON.stringify({ available, excluded, ...preferences, limit: 20 }),
    });
  } catch (error) {
    if (signal.aborted) throw error;
    throw new Error('Could not reach the recipe server. Start quick_api.py on port 8001 and retry.');
  }
  let data: { recommendations?: unknown; error?: unknown; applied_preferences?: { allergies?: unknown; diet?: unknown; excluded?: unknown } };
  try { data = await response.json(); } catch { throw new Error('Recipe server returned an unreadable response.'); }
  if (!response.ok) throw new Error(typeof data?.error === 'string' ? data.error : 'Recipe request failed.');
  if (preferences.allergies.length || excluded.length || preferences.diet !== 'No preference') {
    const applied = data?.applied_preferences;
    if (!applied || applied.diet !== preferences.diet || JSON.stringify(applied.allergies) !== JSON.stringify(preferences.allergies) || JSON.stringify(applied.excluded) !== JSON.stringify(excluded)) throw new Error('Recipe server must be updated to apply your saved restrictions.');
  }
  if (!data || !Array.isArray(data.recommendations)) throw new Error('Recipe server returned an invalid list.');
  return data.recommendations.map(value => {
    if (!value || typeof value !== 'object') throw new Error('Invalid recipe response.');
    const item = value as Recommendation;
    if (item.ingredient_match !== undefined) {
      const match = item.ingredient_match;
      if (!match || !Number.isInteger(match.matched) || !Number.isInteger(match.total) || match.total <= 0 || match.matched < 0 || match.matched > match.total || match.percentage !== Math.round(100 * match.matched / match.total)) throw new Error('Invalid ingredient match percentage.');
    }
    if (typeof item.id !== 'string' || typeof item.name !== 'string' || !Array.isArray(item.missing_supporting) || item.missing_supporting.some(x => typeof x !== 'string') || typeof item.ranking_score !== 'number' || !Number.isFinite(item.ranking_score)) throw new Error('Invalid recipe response.');
    if (item.missing_essential !== undefined && (!Array.isArray(item.missing_essential) || item.missing_essential.some(x => typeof x !== 'string'))) throw new Error('Invalid missing ingredient response.');
    if (item.used_ingredients !== undefined && (!Array.isArray(item.used_ingredients) || item.used_ingredients.some(x => typeof x !== 'string'))) throw new Error('Invalid recipe ingredient-coverage response.');
    // Older running API instances omit coverage. Use the same serving catalog's
    // ingredient totals, never its ranking score, to calculate their percentage.
    if (!item.ingredient_match) {
      const total = (ingredientCounts as Record<string, number>)[item.id];
      if (!total || !item.used_ingredients) throw new Error('Recipe server must be updated to include ingredient match percentages.');
      const matched = new Set(item.used_ingredients.map(name => name.trim().toLowerCase().replace(/\s+/g, '_'))).size;
      if (matched > total) throw new Error('Invalid ingredient match count.');
      return { ...item, ingredient_match: { matched, total, percentage: Math.round(100 * matched / total) } };
    }
    return item;
  });
}
