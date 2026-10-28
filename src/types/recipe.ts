import { CookingStyle } from '../data/cookingStyles';
import type { ImageSourcePropType } from 'react-native';

export type Recipe = {
  cookingStyle?: Exclude<CookingStyle, 'Any style'>;
  id: string;
  name: string;
  minutes: number | null;
  servings: number;
  required: string[];
  image?: ImageSourcePropType;
  quantities: string[];
  steps: string[];
  sourceUrl?: string;
  supporting?: string[];
  optional?: string[];
};
