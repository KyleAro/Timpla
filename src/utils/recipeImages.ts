import type { ImageSourcePropType } from 'react-native';

// Illustrative food images, shared by source versions of the same dish.
// Unmatched dishes use a neutral kitchen still life, never a different meal.
const images: Record<string, ImageSourcePropType> = {
  'tortang talong': require('../../assets/recipes/tortang-talong.png'),
  'chicken adobo': require('../../assets/recipes/chicken-adobo.png'),
  'adobong manok': require('../../assets/recipes/chicken-adobo.png'),
  'ginisang sayote': require('../../assets/recipes/ginisang-sayote.png'),
  'adobo burrito': require('../../assets/recipes/adobo-burrito.png'),
};

export function recipeImage(family: string): ImageSourcePropType {
  return images[family.toLowerCase()] ?? require('../../assets/recipes/kitchen-fallback.png');
}
