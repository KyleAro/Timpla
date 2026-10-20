import { CookingStyle } from './cookingStyles';

export type Recipe = {
  cookingStyle?: Exclude<CookingStyle, 'Any style'>;
  id: string;
  name: string;
  minutes: number;
  servings: number;
  required: string[];
  image: number;
  quantities: string[];
  steps: string[];
};

// Small starter catalog. Required ingredients define the match denominator.
export const recipes: Recipe[] = [
  {
    id: 'ensaladang-talong', name: 'Ensaladang talong', minutes: 20, servings: 2,
    required: ['Eggplant', 'Tomato', 'Onion', 'Salt', 'Vinegar', 'Pepper'],
    image: require('../../assets/recipes/ensaladang-talong.png'),
    quantities: ['2 medium eggplants', '1 tomato, diced', '1 small onion, sliced', 'Salt, to taste', '2 tablespoons vinegar', 'Pepper, to taste'],
    steps: ['Grill the eggplants until tender and the skins are charred.', 'Cool, peel, and chop the eggplant flesh.', 'Combine with tomato, onion, and vinegar. Season with salt and pepper.'],
  },
  {
    id: 'tortang-talong', name: 'Tortang talong', minutes: 15, servings: 2,
    required: ['Eggplant', 'Salt', 'Egg', 'Oil'],
    image: require('../../assets/recipes/tortang-talong.png'),
    quantities: ['2 medium eggplants', 'Salt, to taste', '2 eggs', '2 tablespoons oil'],
    steps: ['Grill the eggplants until tender. Cool and peel, keeping the stems.', 'Beat the eggs with salt. Flatten each eggplant and coat it in egg.', 'Heat oil in a pan. Fry each coated eggplant until the egg is set and both sides are golden.'],
  },
];
