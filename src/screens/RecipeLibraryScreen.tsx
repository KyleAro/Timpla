import { router } from 'expo-router';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { SaveRecipeButton } from '../components/SaveRecipeButton';
import { recipes } from '../data/recipes';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { normalizeIngredient } from '../utils/ingredientMatch';

export default function RecipeLibraryScreen({ saved = false }: { saved?: boolean }) {
  const { palette } = useTheme();
  const { savedRecipeIds, allergies, exclusions } = useCooking();
  const bottomPadding = useBottomNavPadding();
  const blocked = new Set([...allergies, ...exclusions].map(normalizeIngredient));
  const items = recipes.filter((recipe) => saved ? savedRecipeIds.includes(recipe.id) : !recipe.required.some((name) => blocked.has(normalizeIngredient(name))));
  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <AppHeader />
    <ScrollView contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]}>
      <View style={styles.heading}><Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={() => router.canGoBack() ? router.back() : router.replace(saved ? '/profile' : '/home')} style={styles.back}><AppIcon name="back" /></Pressable><Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>{saved ? 'Saved recipes' : 'Reverse cooking'}</Text></View>
      {items.map((recipe) => <View key={recipe.id} style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}><Pressable accessibilityRole="button" accessibilityLabel={`Open ${recipe.name}`} onPress={() => router.push({ pathname: '/recipe', params: { id: recipe.id, ...(saved ? {} : { mode: 'hunt' }) } })}><Image source={recipe.image} accessibilityLabel={recipe.name} style={styles.image} /><View style={styles.copy}><View style={{ flex: 1 }}><Text style={[styles.name, { color: palette.text }]}>{recipe.name}</Text><Text style={[styles.meta, { color: palette.muted }]}>{recipe.minutes} min · {recipe.required.length} ingredients</Text></View><AppIcon name="chevron" /></View></Pressable><SaveRecipeButton id={recipe.id} floating /></View>)}
    </ScrollView>
    <BottomNav active={saved ? 'profile' : 'home'} />
  </SafeAreaView>;
}
const styles = StyleSheet.create({ screen: { flex: 1 }, content: { width: '100%', maxWidth: 480, alignSelf: 'center', padding: 20 }, heading: { flexDirection: 'row', gap: 8, alignItems: 'center', marginBottom: 22 }, back: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center' }, title: { flex: 1, fontSize: 26, fontWeight: '700' }, card: { borderWidth: 1, borderRadius: 18, overflow: 'hidden', marginBottom: 16 }, image: { width: '100%', height: 165, resizeMode: 'cover' }, copy: { padding: 16, flexDirection: 'row', alignItems: 'center', gap: 10 }, name: { fontSize: 19, fontWeight: '700' }, meta: { marginTop: 7, fontSize: 13 } });
