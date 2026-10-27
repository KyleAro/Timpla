import { authClient } from '../auth/supabase';
import { cleanItems, Preferences } from '../data/account';
import { isCookingStyle } from '../data/cookingStyles';

const preferenceColumns = 'servings, diet, allergies, excluded_ingredients, cuisine_styles(name)';

export type PreferenceRow = {
  servings: number; diet: string; allergies: string[]; excluded_ingredients: string[];
  cuisine_styles: { name: string } | null;
};
export function readPreferences(row: PreferenceRow): Preferences {
  const style = row.cuisine_styles?.name ?? 'Any style';
  if (!isCookingStyle(style) || !['No preference', 'Vegetarian', 'Halal'].includes(row.diet)) throw new Error('Unsupported cooking preferences. Update the app.');
  return { people: row.servings, diet: row.diet as Preferences['diet'], cookingStyle: style, allergies: row.allergies, exclusions: row.excluded_ingredients };
}

export async function loadAccount(userId: string, legacyStyle: string | null) {
  const client = authClient();
  const imported = await client.rpc('timpla_import_legacy_style', { style_name: isCookingStyle(legacyStyle) ? legacyStyle : null });
  if (imported.error) throw imported.error;
  const [profile, preferences] = await Promise.all([
    client.from('profiles').select('full_name').eq('id', userId).single(),
    client.from('user_preferences').select(preferenceColumns).eq('user_id', userId).single().overrideTypes<PreferenceRow, { merge: false }>(),
  ]);
  if (profile.error) throw profile.error;
  if (preferences.error) throw preferences.error;
  return { fullName: profile.data.full_name as string, preferences: readPreferences(preferences.data) };
}

export async function saveAccountName(userId: string, fullName: string) {
  const name = fullName.trim();
  if (!name || name.length > 40) throw new Error('Enter a name of 1–40 characters.');
  const { data, error } = await authClient().from('profiles').update({ full_name: name }).eq('id', userId).select('full_name').single();
  if (error) throw error;
  return data.full_name as string;
}

export async function saveAccountPreferences(userId: string, patch: Partial<Preferences>) {
  const client = authClient();
  const values: Record<string, unknown> = {};
  if (patch.people !== undefined) {
    if (!Number.isInteger(patch.people) || patch.people < 1 || patch.people > 20) throw new Error('Choose 1–20 servings.');
    values.servings = patch.people;
  }
  if (patch.diet !== undefined) {
    if (!['No preference', 'Vegetarian', 'Halal'].includes(patch.diet)) throw new Error('Choose a supported diet.');
    values.diet = patch.diet;
  }
  if (patch.allergies !== undefined) values.allergies = cleanItems(patch.allergies);
  if (patch.exclusions !== undefined) values.excluded_ingredients = cleanItems(patch.exclusions);
  if (patch.cookingStyle !== undefined) {
    if (!isCookingStyle(patch.cookingStyle)) throw new Error('Choose a supported cooking style.');
    values.cuisine_style_id = null;
    if (patch.cookingStyle !== 'Any style') {
      const { data, error } = await client.from('cuisine_styles').select('id').eq('name', patch.cookingStyle).single();
      if (error) throw error;
      values.cuisine_style_id = data.id;
    }
  }
  const { data, error } = await client.from('user_preferences').update(values).eq('user_id', userId).select(preferenceColumns).single().overrideTypes<PreferenceRow, { merge: false }>();
  if (error) throw error;
  return readPreferences(data);
}
