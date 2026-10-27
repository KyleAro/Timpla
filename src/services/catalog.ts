import { authClient } from '../auth/supabase';
import { CatalogRow, mapRecipe } from '../data/catalog';
import { isCookingStyle } from '../data/cookingStyles';

export async function loadCatalog() {
  const client = authClient();
  const [recipes, styles] = await Promise.all([
    client.from('recipes').select('slug, name, minutes, servings, steps, image_path, cuisine_styles(name), recipe_ingredients(position, quantity_text, is_required, ingredients(name))').eq('published', true).order('name').overrideTypes<CatalogRow[], { merge: false }>(),
    client.from('cuisine_styles').select('name, destination_name').order('position'),
  ]);
  if (recipes.error) throw recipes.error;
  if (styles.error) throw styles.error;
  return {
    recipes: recipes.data.map(mapRecipe),
    destinations: styles.data.map(item => {
      if (!isCookingStyle(item.name) || item.name === 'Any style') throw new Error('Unsupported cooking style. Update the app.');
      return { name: item.destination_name as string, style: item.name };
    }),
  };
}
