export const cookingStyles = ['Any style', 'Bicolano', 'Ilocano', 'Kapampangan', 'Ilonggo'] as const;
export type CookingStyle = typeof cookingStyles[number];
export const destinations = [
  { name: 'Bicol', style: 'Bicolano' },
  { name: 'Ilocos', style: 'Ilocano' },
  { name: 'Pampanga', style: 'Kapampangan' },
  { name: 'Iloilo', style: 'Ilonggo' },
] as const;
export function isCookingStyle(value: unknown): value is CookingStyle {
  return cookingStyles.some((style) => style === value);
}
