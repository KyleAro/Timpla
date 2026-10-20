import { router, useLocalSearchParams } from 'expo-router';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { SaveRecipeButton } from '../components/SaveRecipeButton';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { destinations } from '../data/cookingStyles';
import { recipes } from '../data/recipes';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { normalizeIngredient } from '../utils/ingredientMatch';

export default function ExploreScreen() {
  const bottomPadding = useBottomNavPadding();
  const { place, ingredient } = useLocalSearchParams<{ place?: string; ingredient?: string }>();
  const { palette } = useTheme();
  const { allergies, exclusions } = useCooking();
  const destination = destinations.find((item) => item.name === place);
  const ingredientBrowse = ingredient === 'Eggplant';
  const title = destination?.name ?? (ingredientBrowse ? 'Cook with talong' : 'Explore the Philippines');
  const blocked = new Set([...allergies, ...exclusions].map(normalizeIngredient));
  const items = recipes.filter((recipe) => !recipe.required.some((name) => blocked.has(normalizeIngredient(name))) && (destination ? recipe.cookingStyle === destination.style : ingredientBrowse && recipe.required.some((name) => normalizeIngredient(name) === normalizeIngredient('Eggplant'))));
  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <AppHeader />
    <ScrollView contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]}>
      <View style={styles.heading}><Pressable accessibilityRole="button" accessibilityLabel="Back to Home" onPress={() => router.canGoBack() ? router.back() : router.replace('/home')} style={styles.back}><AppIcon name="back" /></Pressable><Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>{title}</Text></View>
      {!destination && !ingredientBrowse && destinations.map((item) => <Pressable key={item.name} accessibilityRole="button" accessibilityLabel={`Explore ${item.name} recipes`} onPress={() => router.push({ pathname: '/explore', params: { place: item.name } })} style={[styles.card, styles.destination, { backgroundColor: palette.surface, borderColor: palette.border }]}><AppIcon name="book" color={palette.accent} /><Text style={[styles.name, { color: palette.text, flex: 1 }]}>{item.name}</Text><AppIcon name="chevron" /></Pressable>)}
      {items.map((recipe) => <View key={recipe.id} style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}><Pressable accessibilityRole="button" onPress={() => router.push({ pathname: '/recipe', params: { id: recipe.id } })}><Image source={recipe.image} style={styles.photo} accessibilityLabel={recipe.name} /><View style={styles.copy}><View style={{ flex: 1 }}><Text style={[styles.name, { color: palette.text }]}>{recipe.name}</Text><Text style={[styles.meta, { color: palette.muted }]}>{recipe.minutes} min</Text></View><AppIcon name="chevron" /></View></Pressable><SaveRecipeButton id={recipe.id} floating /></View>)}
      {!items.length && (destination || ingredientBrowse) && <View style={styles.empty}><AppIcon name="book" size={40} color={palette.accent} /><Text style={[styles.emptyText, { color: palette.muted }]}>{destination ? 'Recipes coming soon' : 'No recipes available'}</Text></View>}
    </ScrollView>
    <BottomNav active="home" />
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 }, content: { width: '100%', maxWidth: 480, alignSelf: 'center', padding: 20, paddingBottom: 32 },
  heading: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 22 }, back: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' }, title: { flex: 1, fontSize: 25, fontWeight: '700' },
  card: { borderWidth: 1, borderRadius: 18, overflow: 'hidden', marginBottom: 16 }, photo: { width: '100%', height: 165, resizeMode: 'cover' }, copy: { padding: 16, flexDirection: 'row', gap: 10, alignItems: 'center' }, name: { fontSize: 18, fontWeight: '700' }, meta: { fontSize: 14, marginTop: 7 },
  empty: { paddingVertical: 70, alignItems: 'center', gap: 18 }, emptyText: { fontSize: 16 },
  destination: { padding: 20, minHeight: 78, flexDirection: 'row', alignItems: 'center', gap: 14 },
});
