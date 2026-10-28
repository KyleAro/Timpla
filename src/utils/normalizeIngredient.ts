// Text normalization for manual input and preference filters; does not rank recipes.
export function normalizeIngredient(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, ' ');
}
