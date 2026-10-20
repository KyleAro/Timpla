// Starter recipes use numeric leading quantities; seasonings remain "to taste".
export function recipeQuantity(quantity: string, servings: number, baseServings: number) {
  return quantity.replace(/^\d+(?:\.\d+)?/, (amount) => String(Math.round(Number(amount) * servings / baseServings * 100) / 100));
}
