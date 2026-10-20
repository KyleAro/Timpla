const aliases: Record<string, string> = {
  aubergine: 'eggplant', talong: 'eggplant', tomatoes: 'tomato', kamatis: 'tomato', onions: 'onion', sibuyas: 'onion', eggs: 'egg', itlog: 'egg', asin: 'salt', suka: 'vinegar', paminta: 'pepper', 'black pepper': 'pepper', 'cooking oil': 'oil', mantika: 'oil',
};
export function normalizeIngredient(value: string): string {
  const cleaned = value.trim().toLowerCase().replace(/\s+/g, ' ');
  return aliases[cleaned] ?? cleaned;
}
export function ingredientMatch(required: readonly string[], available: readonly string[]) {
  const uniqueRequired = [...new Map(required.map((name) => [normalizeIngredient(name), name])).values()];
  const pantry = new Set(available.map(normalizeIngredient));
  const missing = uniqueRequired.filter((name) => !pantry.has(normalizeIngredient(name)));
  const matched = uniqueRequired.length - missing.length;
  return { matched, total: uniqueRequired.length, missing, percent: uniqueRequired.length ? Math.round(matched / uniqueRequired.length * 100) : 0 };
}
