import { router } from 'expo-router';
import { useRef, useState } from 'react';
import { ActivityIndicator, Image, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { SaveRecipeButton } from '../components/SaveRecipeButton';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { CatalogStatus } from '../components/CatalogStatus';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { ingredientMatch, normalizeIngredient } from '../utils/ingredientMatch';

export default function ResultsScreen() {
  const bottomPadding = useBottomNavPadding();
  const { palette } = useTheme();
  const { ingredients, setIngredients, photo, allergies, exclusions, selectDish, cookingStyle, detecting, detectionError, retryDetection, recipes, catalogLoading, catalogError } = useCooking();
  const [editing, setEditing] = useState(false);
  const [entry, setEntry] = useState('');
  const [error, setError] = useState('');
  const input = useRef<TextInput>(null);
  const blocked = new Set([...allergies, ...exclusions].map(normalizeIngredient));
  const matches = recipes
    .filter((recipe) => !recipe.required.some((name) => blocked.has(normalizeIngredient(name))))
    .map((recipe) => ({ recipe, ...ingredientMatch(recipe.required, ingredients) }))
    .filter((item) => item.matched > 0)
    .sort((a, b) => b.percent - a.percent || Number(b.recipe.cookingStyle === cookingStyle) - Number(a.recipe.cookingStyle === cookingStyle) || b.matched - a.matched || a.recipe.name.localeCompare(b.recipe.name));
  function addIngredient() {
    const name = entry.trim().replace(/\s+/g, ' ');
    if (!name) return;
    if (ingredients.some((item) => normalizeIngredient(item) === normalizeIngredient(name))) { setError('Already added.'); return; }
    setIngredients([...ingredients, name]); setEntry(''); setError('');
  }
  function openEditor() { setEditing(true); }
  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}>
      <Pressable accessibilityRole="button" accessibilityLabel="Back to Home" onPress={() => router.replace('/home')} style={styles.iconButton}><AppIcon name="back" size={25} /></Pressable>
      <Text accessibilityRole="header" style={[styles.pageTitle, { color: palette.text }]}>Results</Text><View style={styles.iconButton} />
    </View>
    <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]} keyboardShouldPersistTaps="handled">
        <View style={styles.ingredientSummary}>
          {photo ? <Pressable accessibilityRole="button" accessibilityLabel="View captured photo" onPress={() => router.push('/photo')}><Image source={{ uri: photo }} accessibilityLabel="Ingredient photo" style={styles.thumbnail} /></Pressable> : null}
          <View style={styles.summaryCopy}>
            <View style={styles.sectionRow}><Text accessibilityRole="header" style={[styles.sectionTitle, { color: palette.text }]}>Ingredients</Text><Pressable accessibilityRole="button" onPress={() => setEditing(!editing)} style={styles.edit}><Text style={[styles.editText, { color: palette.accent }]}>{editing ? 'Done' : 'Edit'}</Text></Pressable></View>
            <View style={styles.chips}>{ingredients.map((name) => <Pressable key={name} accessibilityRole="button" accessibilityLabel={`Remove ${name}`} onPress={() => setIngredients(ingredients.filter((item) => item !== name))} style={[styles.chip, { backgroundColor: palette.chip }]}><Text style={[styles.chipText, { color: palette.text }]}>{name}</Text><Text style={[styles.cross, { color: palette.text }]}>×</Text></Pressable>)}<Pressable accessibilityRole="button" accessibilityLabel="Add ingredient" onPress={openEditor} style={[styles.plus, { backgroundColor: palette.accent }]}><AppIcon name="plus" size={23} color="#FFF8ED" /></Pressable></View>
          </View>
        </View>
        {detecting && <View style={styles.scanStatus} accessibilityLiveRegion="polite"><ActivityIndicator color={palette.accent} /><Text style={{ color: palette.muted }}>Scanning…</Text></View>}
        {detectionError ? <View style={styles.scanStatus}><Text accessibilityLiveRegion="polite" style={{ color: palette.error, flex: 1 }}>{detectionError}</Text><Pressable accessibilityRole="button" onPress={retryDetection} style={styles.iconButton}><Text style={{ color: palette.accent }}>Retry</Text></Pressable></View> : null}
        {editing && <View style={[styles.entryRow, { backgroundColor: palette.surface, borderColor: palette.border }]}><TextInput ref={input} autoFocus accessibilityLabel="Ingredient name" placeholder="Ingredient name" placeholderTextColor={palette.muted} value={entry} onChangeText={(value) => { setEntry(value); setError(''); }} onSubmitEditing={addIngredient} returnKeyType="done" maxLength={60} style={[styles.input, { color: palette.text }]} /><Pressable accessibilityRole="button" accessibilityLabel="Save ingredient" disabled={!entry.trim()} onPress={addIngredient} style={styles.iconButton}><AppIcon name="check" color={palette.accent} /></Pressable></View>}
        {error ? <Text accessibilityLiveRegion="polite" style={{ color: palette.error, marginBottom: 12 }}>{error}</Text> : null}
        <Text accessibilityRole="header" style={[styles.recipeHeading, { color: palette.text }]}>Recipes</Text>
        <CatalogStatus />
        {catalogLoading || catalogError ? null : !ingredients.length ? <View style={styles.empty}><AppIcon name="book" size={40} color={palette.accent} /><Text style={[styles.emptyText, { color: palette.muted }]}>Add ingredients to see recipes.</Text></View> : !matches.length ? <View style={styles.empty}><AppIcon name="book" size={40} color={palette.accent} /><Text style={[styles.emptyText, { color: palette.muted }]}>No matching recipes yet.</Text></View> : matches.map(({ recipe, matched, total, missing, percent }) => <View key={recipe.id} style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}><Pressable accessibilityRole="button" accessibilityLabel={`${recipe.name}, ${percent}% match, ${matched} of ${total} ingredients`} onPress={() => { selectDish({ id: recipe.id, name: recipe.name, required: recipe.required }); router.push({ pathname: '/recipe', params: { id: recipe.id } }); }}>
          <Image source={recipe.image} accessibilityLabel={recipe.name} style={styles.recipePhoto} />
          <View style={styles.cardBody}>
            <View style={styles.cardTop}><Text style={[styles.dishName, { color: palette.text }]}>{recipe.name}</Text><View style={[styles.matchBadge, { backgroundColor: percent >= 60 ? palette.olive : palette.secondary }]}><Text style={[styles.matchText, { color: percent >= 60 ? palette.oliveText : palette.muted }]}>{percent}% match</Text></View></View>
            <Text style={[styles.cardText, { color: palette.muted }]}>{matched} of {total} ingredients</Text>
            <View style={styles.cardTop}><Text style={[styles.missing, { color: missing.length ? palette.muted : palette.accent }]}>{missing.length ? `Missing: ${missing.join(', ').toLowerCase()}` : 'You can cook this'}</Text><AppIcon name="chevron" size={19} /></View>
            <Text style={[styles.time, { color: palette.text }]}>{recipe.minutes} min</Text>
          </View>
        </Pressable><SaveRecipeButton id={recipe.id} floating /></View>)}
      </ScrollView>
    </KeyboardAvoidingView>
    <BottomNav active="recipes" />
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  scanStatus: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 14 },
  screen: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 12, minHeight: 62 },
  iconButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' }, pageTitle: { fontSize: 22, fontWeight: '700' },
  content: { width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingBottom: 20 }, ingredientSummary: { flexDirection: 'row', gap: 14, marginBottom: 18, marginTop: 8 },
  thumbnail: { width: 72, height: 78, borderRadius: 10, resizeMode: 'cover' }, summaryCopy: { flex: 1, minWidth: 0 }, sectionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }, sectionTitle: { fontSize: 18, fontWeight: '700' }, edit: { minHeight: 44, paddingLeft: 12, justifyContent: 'center' }, editText: { fontSize: 14, fontWeight: '600' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 7 }, chip: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 44, paddingHorizontal: 11, borderRadius: 22 }, chipText: { fontSize: 13, flexShrink: 1 }, cross: { fontSize: 18 }, plus: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  entryRow: { flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderRadius: 14, paddingLeft: 14, marginBottom: 14 }, input: { flex: 1, minWidth: 0, minHeight: 48, fontSize: 16 },
  recipeHeading: { fontSize: 24, fontWeight: '700', marginTop: 4, marginBottom: 12 }, card: { borderRadius: 18, borderWidth: 1, overflow: 'hidden', marginBottom: 16 }, recipePhoto: { width: '100%', height: 155, resizeMode: 'cover' }, cardBody: { padding: 14, gap: 5 }, cardTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 }, dishName: { fontSize: 19, fontWeight: '700', flex: 1 }, matchBadge: { paddingHorizontal: 10, paddingVertical: 7, borderRadius: 18 }, matchText: { fontSize: 12, fontWeight: '700' }, cardText: { fontSize: 14 }, missing: { fontSize: 14, lineHeight: 20, flex: 1 }, time: { fontSize: 14, marginTop: 3 }, empty: { alignItems: 'center', gap: 15, paddingVertical: 60 }, emptyText: { fontSize: 15 },
});
