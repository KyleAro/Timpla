export type Recommendation = {
  id: string;
  name: string;
  ranking_score: number;
  used_ingredients?: string[];
  missing_supporting: string[];
  quantity_and_preparation_check_needed: boolean;
};

export async function getRecommendations(available: string[], excluded: string[], signal: AbortSignal): Promise<Recommendation[]> {
  const configured = process.env.EXPO_PUBLIC_RECOMMENDATION_URL?.trim().replace(/\/$/, '');
  const base = configured || (typeof window !== 'undefined' && window.location?.hostname ? `${window.location.protocol}//${window.location.hostname}:8001` : '');
  if (!base) throw new Error('Set EXPO_PUBLIC_RECOMMENDATION_URL to the recommendation server address.');
  let response: Response;
  try {
    response = await fetch(`${base}/recommendations`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
      body: JSON.stringify({ available, excluded, limit: 5 }),
    });
  } catch (error) {
    if (signal.aborted) throw error;
    throw new Error('Could not reach the recipe server. Start quick_api.py on port 8001 and retry.');
  }
  let data: { recommendations?: unknown; error?: unknown };
  try { data = await response.json(); } catch { throw new Error('Recipe server returned an unreadable response.'); }
  if (!response.ok) throw new Error(typeof data?.error === 'string' ? data.error : 'Recipe request failed.');
  if (!data || !Array.isArray(data.recommendations)) throw new Error('Recipe server returned an invalid list.');
  return data.recommendations.map(value => {
    if (!value || typeof value !== 'object') throw new Error('Invalid recipe response.');
    const item = value as Recommendation;
    if (typeof item.id !== 'string' || typeof item.name !== 'string' || !Array.isArray(item.missing_supporting) || item.missing_supporting.some(x => typeof x !== 'string') || typeof item.ranking_score !== 'number' || !Number.isFinite(item.ranking_score)) throw new Error('Invalid recipe response.');
    if (item.used_ingredients !== undefined && (!Array.isArray(item.used_ingredients) || item.used_ingredients.some(x => typeof x !== 'string'))) throw new Error('Invalid recipe ingredient-coverage response.');
    return item;
  });
}
