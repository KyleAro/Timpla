import { typography } from '../theme/tokens';
import { useRecommendations } from '../hooks/useRecommendations';
import { router } from 'expo-router';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';

import dataset from '../data/recipeDataset.json';

const catalogIds = new Set(dataset.map(recipe => recipe.id));
const label = (value: string) => value.replace(/_/g, ' ');

export default function RecommendationsScreen() {
  const { palette } = useTheme();
  const { ingredients, exclusions, allergies, diet, detecting, photo } = useCooking();
  const { current, loading, retry } = useRecommendations();
  function editIngredients() { router.push(photo ? '/ingredients' : '/scan'); }
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}>
      <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={() => router.canGoBack() ? router.back() : router.replace('/recipes')} style={styles.iconButton}><AppIcon name="back" /></Pressable>
      <Text accessibilityRole="header" style={[styles.headerTitle, { color: palette.text }]}>Recipe matches</Text><View style={styles.iconButton} />
    </View>
    <ScrollView contentContainerStyle={styles.content}>
      <View style={[styles.inventory, { backgroundColor: palette.secondary, borderColor: palette.border }]}>
        <View style={styles.row}><Text style={[styles.sectionTitle, { color: palette.text }]}>In your kitchen</Text><Pressable accessibilityRole="button" onPress={editIngredients} style={styles.edit}><AppIcon name="edit" size={16} color={palette.accent} /><Text style={{ color: palette.accent, fontWeight: '700' }}>Edit</Text></Pressable></View>
        <View style={styles.chips}>{ingredients.map(name => <View key={name} style={[styles.chip, { backgroundColor: palette.surface }]}><Text style={{ color: palette.text }}>{label(name)}</Text></View>)}</View>
      </View>
      <Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>A little cooking inspiration</Text>
      {(allergies.length > 0 || exclusions.length > 0 || diet !== 'No preference') && <View style={[styles.inventory, { backgroundColor: palette.secondary, borderColor: palette.border }]}><Pressable accessibilityRole="button" onPress={() => router.push('/allergies')} style={styles.edit}><AppIcon name="sliders" size={18} color={palette.accent} /><Text style={{ color: palette.text, flex: 1 }}>Your restrictions</Text><AppIcon name="chevron" size={18} color={palette.accent} /></Pressable><Text style={[styles.body, { color: palette.text }]}>{[diet !== 'No preference' ? diet : '', ...allergies.map(value => `${value} allergy`), ...exclusions.map(value => `Avoid ${value}`)].filter(Boolean).join(' · ')}</Text>{diet !== 'No preference' && <Text style={[styles.body, { color: palette.muted }]}>Only recipes with a verified {diet} label are shown.</Text>}{allergies.length > 0 && <Text style={[styles.body, { color: palette.muted }]}>Check recipe ingredients and product labels for allergens.</Text>}</View>}
      {detecting || loading ? <View accessibilityLiveRegion="polite" style={styles.state}><ActivityIndicator color={palette.accent} size="large" /><Text style={[styles.sectionTitle, { color: palette.text }]}>{detecting ? 'Waiting for your ingredients' : 'Finding your recipe matches'}</Text><Text style={[styles.body, styles.centered, { color: palette.muted }]}>Your suggestions will appear here.</Text></View>
        : !ingredients.length ? <View style={styles.state}><AppIcon name="leaf" size={36} color={palette.accent} /><Text style={[styles.sectionTitle, { color: palette.text }]}>Start with what you have</Text><Text style={[styles.body, styles.centered, { color: palette.muted }]}>Scan your ingredients, then review the list to find recipe matches.</Text><Pressable accessibilityRole="button" onPress={() => router.push('/scan')} style={[styles.button, { backgroundColor: palette.buttonBackground }]}><Text style={styles.buttonText}>Scan ingredients</Text></Pressable></View>
        : current?.error ? <View style={styles.state}><AppIcon name="help" size={32} color={palette.accent} /><Text accessibilityRole="alert" style={[styles.body, styles.centered, { color: palette.text }]}>{current.error}</Text><Pressable accessibilityRole="button" onPress={retry} style={[styles.button, { backgroundColor: palette.buttonBackground }]}><Text style={styles.buttonText}>Try again</Text></Pressable></View>
        : current && !current.items.length ? <View style={styles.state}><AppIcon name="book" size={34} color={palette.accent} /><Text style={[styles.sectionTitle, { color: palette.text }]}>No matches just yet</Text><Text style={[styles.body, styles.centered, { color: palette.muted }]}>{diet !== 'No preference' ? `No recipes with a verified ${diet} label match your ingredients yet.` : allergies.length > 0 || exclusions.length > 0 ? 'No recipes match your ingredients and saved restrictions. Review your list or try another set of ingredients.' : 'Check your ingredient list and add anything you missed, including pantry items.'}</Text><Pressable accessibilityRole="button" onPress={editIngredients} style={[styles.button, { backgroundColor: palette.buttonBackground }]}><Text style={styles.buttonText}>Review ingredients</Text></Pressable></View>
        : current?.items.map((item, index) => <View key={item.id} style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}>
          <View style={styles.row}><Text style={[styles.eyebrow, { color: palette.accent }]}>RECIPE MATCH</Text><Text style={[styles.body, { color: palette.muted }]}>0{index + 1}</Text></View>
          <Text accessibilityRole="header" style={[styles.recipeTitle, { color: palette.text }]}>{item.name}</Text>
          {item.ingredient_match && <Text style={{ color: palette.accent, fontWeight: '800' }}>{item.ingredient_match.percentage}% match · {item.ingredient_match.matched} of {item.ingredient_match.total} listed ingredients</Text>}
          {!!item.used_ingredients?.length && <><View style={styles.chips}>{item.used_ingredients.map(name => <View key={name} style={[styles.chip, { backgroundColor: palette.chip }]}><Text style={{ color: palette.text }}>{label(name)}</Text></View>)}</View></>}
          <View style={[styles.pantry, { backgroundColor: palette.secondary }]}><AppIcon name={item.missing_supporting.length ? 'help' : 'check'} size={18} color={palette.accent} /><View style={{ flex: 1, gap: 4 }}><Text style={[styles.smallTitle, { color: palette.text }]}>{item.missing_supporting.length ? 'Check your pantry' : 'Supporting ingredients matched'}</Text><Text style={[styles.body, { color: palette.muted }]}>{item.missing_supporting.length ? item.missing_supporting.map(label).join(' · ') : 'Review the full ingredient list and quantities.'}</Text></View></View>
          {catalogIds.has(item.id) ? <Pressable accessibilityRole="button" accessibilityLabel={`View recipe for ${item.name}`} onPress={() => router.push({ pathname: '/recipe', params: { id: item.id } })} style={[styles.recipeLink, { borderColor: palette.border }]}><Text style={{ color: palette.accent, fontWeight: '700' }}>View recipe</Text><AppIcon name="chevron" size={18} color={palette.accent} /></Pressable> : <Text style={[styles.body, { color: palette.muted }]}>Full recipe details aren’t available in this collection yet.</Text>}
        </View>)}
    </ScrollView>
  </SafeAreaView>;
}

const styles = StyleSheet.create({
  screen: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', width: '100%', maxWidth: 520, alignSelf: 'center', paddingHorizontal: 12, minHeight: 60 },
  iconButton: { width: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' }, headerTitle: { flex: 1, textAlign: 'center', fontSize: typography.title, fontWeight: '700' },
  content: { width: '100%', maxWidth: 520, alignSelf: 'center', padding: 20, paddingBottom: 40 },
  inventory: { padding: 16, borderWidth: 1, borderRadius: 20, marginBottom: 28, gap: 8 }, row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  edit: { minHeight: 48, paddingHorizontal: 8, flexDirection: 'row', alignItems: 'center', gap: 6 }, sectionTitle: { fontSize: typography.body, fontWeight: '700', flexShrink: 1 },
  title: { fontSize: typography.title, lineHeight: 34, fontWeight: '800', marginBottom: 10 }, body: { fontSize: typography.label, lineHeight: 21 }, centered: { textAlign: 'center' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 7 }, chip: { paddingHorizontal: 11, paddingVertical: 7, borderRadius: 16 },
  card: { borderWidth: 1, borderRadius: 16, padding: 16, marginBottom: 16, gap: 14 }, eyebrow: { fontSize: 10, fontWeight: '800', letterSpacing: 1.2 },
  recipeTitle: { fontSize: typography.section, lineHeight: 28, fontWeight: '700' }, smallTitle: { fontSize: typography.label, fontWeight: '700' }, pantry: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, borderRadius: 12, padding: 12 },
  recipeLink: { minHeight: 48, borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 10, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  state: { paddingVertical: 32, paddingHorizontal: 12, alignItems: 'center', gap: 16 }, button: { minHeight: 52, borderRadius: 12, paddingHorizontal: 24, justifyContent: 'center', alignItems: 'center', paddingVertical: 14 }, buttonText: { color: '#FFF8ED', fontWeight: '700', fontSize: typography.label },
});
