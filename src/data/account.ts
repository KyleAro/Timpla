import { CookingStyle } from './cookingStyles';

export type Diet = 'No preference' | 'Vegetarian' | 'Halal';
export type Preferences = {
  people: number;
  diet: Diet;
  cookingStyle: CookingStyle;
  allergies: string[];
  exclusions: string[];
};
export const defaultPreferences: Preferences = {
  people: 2, diet: 'No preference', cookingStyle: 'Any style', allergies: [], exclusions: [],
};

export function cleanItems(items: string[]) {
  return [...new Map(items.map(value => value.trim().replace(/\s+/g, ' ')).filter(Boolean).map(value => [value.toLowerCase(), value])).values()];
}
