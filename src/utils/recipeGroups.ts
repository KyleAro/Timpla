import dataset from '../data/recipeDataset.json';

const groups = new Map<string, typeof dataset>();
for (const recipe of dataset) {
  const versions = groups.get(recipe.family) ?? [];
  versions.push(recipe);
  groups.set(recipe.family, versions);
}
export const recipeGroups = [...groups.values()].map(versions => ({
  id: versions[0].id,
  name: versions[0].dishName,
  versions,
}));
