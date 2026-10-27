import type { ImageSourcePropType } from 'react-native';
import { isCookingStyle } from './cookingStyles';
import type { Recipe } from './recipes';

const images: Record<string, ImageSourcePropType> = {
  'asset:ensaladang-talong': require('../../assets/recipes/ensaladang-talong.png'),
  'asset:tortang-talong': require('../../assets/recipes/tortang-talong.png'),
};
export type CatalogRow = {
  slug: string; name: string; minutes: number; servings: number; steps: unknown; image_path: string;
  cuisine_styles: { name: string } | null;
  recipe_ingredients: { position: number; quantity_text: string; is_required: boolean; ingredients: { name: string } | null }[];
};
export function mapRecipe(row: CatalogRow): Recipe {
  const required = row.recipe_ingredients.filter(item => item.is_required).sort((a, b) => a.position - b.position);
  if (!required.length || required.some(item => !item.ingredients)) throw new Error('Recipe ingredients are incomplete.');
  if (!Array.isArray(row.steps) || !row.steps.length || !row.steps.every(step => typeof step === 'string')) throw new Error('Recipe instructions are incomplete.');
  const image = images[row.image_path] ?? (/^https:\/\//.test(row.image_path) ? { uri: row.image_path } : undefined);
  if (!image) throw new Error('Recipe image is unavailable.');
  const style = row.cuisine_styles?.name;
  if (style && (!isCookingStyle(style) || style === 'Any style')) throw new Error('Unsupported recipe style. Update the app.');
  return {
    id: row.slug, name: row.name, minutes: row.minutes, servings: row.servings,
    required: required.map(item => item.ingredients!.name), quantities: required.map(item => item.quantity_text),
    steps: row.steps, image, ...(style ? { cookingStyle: style as Recipe['cookingStyle'] } : {}),
  };
}
