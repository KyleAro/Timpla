import { Pressable, StyleSheet } from 'react-native';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';

export function SaveRecipeButton({ id, floating = false }: { id: string; floating?: boolean }) {
  const { savedRecipeIds, toggleSavedRecipe } = useCooking();
  const { palette } = useTheme();
  const saved = savedRecipeIds.includes(id);
  return <Pressable accessibilityRole="button" accessibilityLabel={saved ? 'Unsave recipe' : 'Save recipe'} accessibilityState={{ selected: saved }} onPress={(event) => { event.stopPropagation(); toggleSavedRecipe(id); }} style={[styles.button, { backgroundColor: saved ? palette.chip : palette.surface, borderColor: saved ? palette.accent : palette.border }, floating && styles.floating]}><AppIcon name={saved ? 'check' : 'bookmark'} size={22} color={saved ? palette.accent : palette.text} /></Pressable>;
}
const styles = StyleSheet.create({ button: { width: 44, height: 44, borderRadius: 22, borderWidth: 1, alignItems: 'center', justifyContent: 'center' }, floating: { position: 'absolute', top: 12, right: 12, zIndex: 1 } });
