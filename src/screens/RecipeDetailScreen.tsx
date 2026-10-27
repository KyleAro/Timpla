import { router, useLocalSearchParams } from 'expo-router';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { PeopleSelector } from '../components/PeopleSelector';
import { SaveRecipeButton } from '../components/SaveRecipeButton';
import { CatalogStatus } from '../components/CatalogStatus';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { ingredientMatch, normalizeIngredient } from '../utils/ingredientMatch';
import { recipeQuantity } from '../utils/recipeQuantity';

export default function RecipeDetailScreen() {
  const { id, mode } = useLocalSearchParams<{ id: string; mode?: string }>();
  const { ingredients, people, huntIngredients, toggleHuntIngredient, recipes, catalogLoading, catalogError } = useCooking();
  const recipe = recipes.find((item) => item.id === id);
  const { palette } = useTheme();
  const hunt = mode === 'hunt';
  const back = () => router.canGoBack() ? router.back() : router.replace(hunt ? '/reverse-cooking' : '/recipes');
  if (!recipe) return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}><CatalogStatus />{!catalogLoading && !catalogError && <Text style={[styles.title, { color: palette.text }]}>Recipe unavailable</Text>}<Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={back} style={styles.back}><AppIcon name="back" /></Pressable></SafeAreaView>;
  const available = hunt ? huntIngredients[recipe.id] ?? [] : ingredients;
  const match = ingredientMatch(recipe.required, available);
  const availableNames = new Set(available.map(normalizeIngredient));
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}><Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={back} style={styles.back}><AppIcon name="back" size={25} /></Pressable><Text style={[styles.headerTitle, { color: palette.text }]}>{hunt ? 'Reverse cooking' : 'Recipe'}</Text><SaveRecipeButton id={recipe.id} /></View>
    <ScrollView contentContainerStyle={styles.content}>
      <Image source={recipe.image} accessibilityLabel={recipe.name} style={styles.photo} />
      <Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>{recipe.name}</Text>
      <Text style={[styles.summary, { color: palette.muted }]}>{recipe.minutes} min{recipe.cookingStyle ? ` · ${recipe.cookingStyle}` : ''}</Text>
      <View style={styles.servings}><Text style={[styles.servingLabel, { color: palette.text }]}>Servings</Text><PeopleSelector /></View>
      <View style={[styles.match, { backgroundColor: palette.olive }]} accessibilityLiveRegion="polite"><Text style={[styles.matchTitle, { color: palette.oliveText }]}>{hunt ? `${match.matched} of ${match.total} ingredients ready` : `${match.percent}% ingredient match`}</Text><Text style={[styles.matchSub, { color: palette.oliveText }]}>{match.missing.length ? `${match.missing.length} missing` : 'Ready to cook'}</Text></View>
      <View style={styles.sectionRow}><Text accessibilityRole="header" style={[styles.section, styles.inlineSection, { color: palette.text }]}>{hunt ? 'Ingredient hunt' : 'Ingredients'}</Text>{!hunt && <Pressable accessibilityRole="button" onPress={() => router.push({ pathname: '/recipe', params: { id: recipe.id, mode: 'hunt' } })} style={styles.huntButton}><Text style={{ color: palette.accent, fontWeight: '600', fontSize: 13 }}>Start hunt</Text></Pressable>}</View>
      {recipe.required.map((name, index) => {
        const ready = availableNames.has(normalizeIngredient(name));
        const row = <><View style={[styles.check, { borderColor: ready ? palette.accent : palette.border, backgroundColor: ready ? palette.chip : palette.surface }]}>{ready && <AppIcon name="check" size={17} color={palette.accent} />}</View><Text style={[styles.quantity, { color: palette.text }]}>{recipeQuantity(recipe.quantities[index], people, recipe.servings)}</Text><Text style={[styles.status, { color: ready ? palette.accent : palette.muted }]}>{ready ? 'Have' : 'Missing'}</Text></>;
        return hunt ? <Pressable key={name} accessibilityRole="checkbox" accessibilityLabel={name} accessibilityState={{ checked: ready }} onPress={() => toggleHuntIngredient(recipe.id, name)} style={[styles.ingredientRow, { borderColor: palette.border }]}>{row}</Pressable> : <View key={name} style={[styles.ingredientRow, { borderColor: palette.border }]}>{row}</View>;
      })}
      <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Steps</Text>
      {recipe.steps.map((step, index) => <View key={step} style={styles.step}><Text style={[styles.number, { color: palette.accent }]}>{index + 1}</Text><Text style={[styles.stepText, { color: palette.text }]}>{step}</Text></View>)}
    </ScrollView>
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 12, minHeight: 64, gap: 8 }, back: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' }, headerTitle: { flex: 1, fontSize: 21, fontWeight: '700' }, content: { padding: 20, paddingTop: 8, paddingBottom: 40, width: '100%', maxWidth: 480, alignSelf: 'center' }, photo: { width: '100%', height: 210, borderRadius: 18, resizeMode: 'cover', marginBottom: 18 }, title: { fontSize: 26, fontWeight: '700', marginBottom: 10 }, summary: { fontSize: 14, marginBottom: 18 }, servings: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 20 }, servingLabel: { fontSize: 16, fontWeight: '600' }, match: { padding: 17, borderRadius: 16, gap: 6 }, matchTitle: { fontSize: 16, fontWeight: '700' }, matchSub: { fontSize: 13 }, sectionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginTop: 24, marginBottom: 8 }, section: { fontSize: 21, fontWeight: '700', marginTop: 24, marginBottom: 14 }, inlineSection: { marginTop: 0, marginBottom: 0 }, huntButton: { minHeight: 44, justifyContent: 'center' }, ingredientRow: { flexDirection: 'row', alignItems: 'center', gap: 11, minHeight: 62, paddingVertical: 13, borderBottomWidth: StyleSheet.hairlineWidth }, check: { width: 24, height: 24, borderRadius: 7, borderWidth: 1, alignItems: 'center', justifyContent: 'center' }, quantity: { flex: 1, fontSize: 15, lineHeight: 22 }, status: { fontSize: 12 }, step: { flexDirection: 'row', gap: 14, marginBottom: 18 }, number: { width: 22, fontSize: 19, fontWeight: '700' }, stepText: { flex: 1, fontSize: 15, lineHeight: 24 },
});
