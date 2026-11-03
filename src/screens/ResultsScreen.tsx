import { Redirect, router } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Image, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { normalizeIngredient } from '../utils/normalizeIngredient';
import { canonicalIngredientName, ingredientCategories, IngredientCategory, ingredientSuggestions } from '../utils/ingredientSuggestions';
import { getRecommendations, type Recommendation } from '../services/recommendations';
import { recipeImage } from '../utils/recipeImages';
import recipeDataset from '../data/recipeDataset.json';

export default function ResultsScreen() {
  const bottomPadding = useBottomNavPadding();
  const { palette } = useTheme();
  const { ingredients, exclusions, allergies, diet, setIngredients, photo, detecting, detectionComplete, detectionError, retryDetection, scanIngredients } = useCooking();
  const [editing, setEditing] = useState(false);
  const [entry, setEntry] = useState('');
  const [ingredientCategory, setIngredientCategory] = useState<IngredientCategory>('All');
  const [error, setError] = useState('');
  const input = useRef<TextInput>(null);
  const [retry, setRetry] = useState(0);
  const requestKey = JSON.stringify([ingredients, exclusions, detecting, retry]);
  const [recipeState, setRecipeState] = useState<{ key: string; items: Recommendation[]; loading: boolean; error: string }>({ key: '', items: [], loading: false, error: '' });
  const recommendations = recipeState.key === requestKey ? recipeState.items : [];
  const recipeError = recipeState.key === requestKey ? recipeState.error : '';
  const recipeLoading = ingredients.length > 0 && !detecting && (recipeState.key !== requestKey || recipeState.loading);
  const coveredIngredientNames = new Set(recommendations.flatMap(recipe => recipe.used_ingredients ?? []).map(normalizeIngredient));
  const coveredIngredients = ingredients.filter(name => coveredIngredientNames.has(normalizeIngredient(name)));
  const uncoveredIngredients = ingredients.filter(name => !coveredIngredientNames.has(normalizeIngredient(name)));
  const coverageAvailable = recommendations.length > 0 && recommendations.every(recipe => Array.isArray(recipe.used_ingredients));
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    if (!photo || !ingredients.length || detecting) return () => controller.abort();
    const timeout = setTimeout(() => controller.abort(), 30000);
    const debounce = setTimeout(() => {
      setRecipeState({ key: requestKey, items: [], loading: true, error: '' });
      void getRecommendations(ingredients, exclusions, controller.signal).then(items => {
        if (active) setRecipeState({ key: requestKey, items, loading: false, error: '' });
      }).catch(reason => {
        if (active) setRecipeState({ key: requestKey, items: [], loading: false, error: controller.signal.aborted ? 'Recipe request timed out. Retry.' : reason instanceof Error ? reason.message : 'Could not load recipes.' });
      }).finally(() => { clearTimeout(timeout); });
    }, 350);
    return () => { active = false; clearTimeout(debounce); clearTimeout(timeout); controller.abort(); };
  }, [ingredients, exclusions, detecting, retry, requestKey, photo]);
  const suggestions = ingredientSuggestions(entry, ingredients, entry.trim() ? Number.MAX_SAFE_INTEGER : 50, ingredientCategory);
  function addIngredient(value = entry) {
    const name = canonicalIngredientName(value);
    if (!name) return;
    if (ingredients.some((item) => normalizeIngredient(canonicalIngredientName(item)) === normalizeIngredient(name))) { setError('Already added.'); return; }
    setIngredients([...ingredients, name]); setEntry(''); setError('');
    input.current?.focus();
  }
  function openEditor() { setEditing(true); }
  if (!photo) return <Redirect href="/scan" />;
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
            <View style={styles.chips}>
              {ingredients.map((name) => {
                const confidence = scanIngredients.find(item => item.name === name)?.confidence;
                return <Pressable key={name} accessibilityRole="button" accessibilityLabel={`Remove ${name}`} onPress={() => setIngredients(ingredients.filter((item) => item !== name))} style={[styles.chip, { backgroundColor: palette.chip }]}>
                  <Text style={[styles.chipText, { color: palette.text }]}>{confidence != null ? `${name} : ${Math.round(confidence * 100)}%` : name}</Text>
                  <AppIcon name="close" size={16} color={palette.text} />
                </Pressable>;
              })}
              <Pressable accessibilityRole="button" accessibilityLabel="Add ingredient" onPress={openEditor} style={[styles.plus, { backgroundColor: palette.accent }]}><AppIcon name="plus" size={23} color="#FFF8ED" /></Pressable>
            </View>
          </View>
        </View>
        {detecting && <View style={[styles.scanStatus, { borderColor: palette.border, borderWidth: 1, borderRadius: 14, padding: 14 }]} accessibilityLiveRegion="polite"><ActivityIndicator color={palette.accent} /><View style={{ flex: 1, gap: 3 }}><Text style={{ color: palette.text, fontWeight: '700' }}>Scanning your photo</Text><Text style={{ color: palette.muted }}>The scanner is analyzing the image. This may take a little while while Render wakes up.</Text></View></View>}
        {detectionError ? <View style={styles.scanStatus}><Text accessibilityRole="alert" style={{ color: palette.error, flex: 1 }}>{detectionError}</Text><Pressable accessibilityRole="button" onPress={retryDetection} style={styles.iconButton}><Text style={{ color: palette.accent }}>Retry</Text></Pressable></View> : null}
        {detectionComplete && !detectionError && <View style={[styles.scanStatus, { borderColor: palette.oliveText, borderWidth: 1, borderRadius: 14, padding: 14 }]} accessibilityLiveRegion="polite"><View style={[styles.resultDot, { backgroundColor: palette.oliveText }]} /><View style={{ flex: 1, gap: 3 }}><Text style={{ color: palette.text, fontWeight: '700' }}>Scan results ready</Text><Text style={{ color: palette.muted }}>{scanIngredients.length ? `${scanIngredients.length} ingredient${scanIngredients.length === 1 ? '' : 's'} detected. Review them below.` : 'No ingredients detected. Add ingredients manually or try another photo.'}</Text></View></View>}
        {photo && <Pressable accessibilityRole="button" accessibilityLabel="Rescan: take or upload another photo" onPress={() => router.replace('/scan')} style={[styles.rescanButton, { borderColor: palette.border }]}><Text style={{ color: palette.accent }}>Rescan</Text></Pressable>}
        {editing && <View style={styles.ingredientEditor}>
          <View accessibilityLabel="Ingredient category filters" style={styles.filterRow}>
            {ingredientCategories.map(category => <Pressable key={category} accessibilityRole="button" accessibilityLabel={`Filter ingredients: ${category}`} accessibilityState={{ selected: ingredientCategory === category }} onPress={() => { setIngredientCategory(category); setError(''); }} style={[styles.filterChip, { backgroundColor: ingredientCategory === category ? palette.accent : palette.surface, borderColor: palette.border }]}>
              <Text style={{ color: ingredientCategory === category ? '#FFF8ED' : palette.text, fontSize: 13 }}>{category}</Text>
            </Pressable>)}
          </View>
          <View style={[styles.entryRow, { backgroundColor: palette.surface, borderColor: palette.border }]}><TextInput ref={input} autoFocus accessibilityLabel="Ingredient name" accessibilityHint="Type to see ingredient suggestions, then tap one to add it." placeholder="Ingredient name" placeholderTextColor={palette.muted} value={entry} onChangeText={(value) => { setEntry(value); setError(''); }} onSubmitEditing={() => addIngredient()} returnKeyType="done" autoCorrect={false} maxLength={60} style={[styles.input, { color: palette.text }]} /><Pressable accessibilityRole="button" accessibilityLabel="Save ingredient" disabled={!entry.trim()} onPress={() => addIngredient()} style={styles.iconButton}><AppIcon name="check" color={palette.accent} /></Pressable></View>
          {suggestions.length > 0 && <View accessibilityLabel="Ingredient suggestions" style={[styles.suggestions, { backgroundColor: palette.surface, borderColor: palette.border }]}>
            <ScrollView nestedScrollEnabled keyboardShouldPersistTaps="handled" style={styles.suggestionList}>
            {suggestions.map(option => <Pressable key={option.name} accessibilityRole="button" accessibilityLabel={`Add ${option.name}`} onPress={() => addIngredient(option.name)} style={styles.suggestionRow}>
              <Text style={[styles.suggestionName, { color: palette.text }]}>{option.name}</Text><AppIcon name="plus" size={18} color={palette.accent} />
            </Pressable>)}
            </ScrollView>
          </View>}
          {(Boolean(entry.trim()) || ingredientCategory !== 'All') && !suggestions.length && <Text style={{ color: palette.muted, marginTop: 8 }}>No suggestions in this category. Try All, or add a custom ingredient using the check button.</Text>}
        </View>}
        {error ? <Text accessibilityLiveRegion="polite" style={{ color: palette.error, marginBottom: 12 }}>{error}</Text> : null}
        <Text accessibilityRole="header" style={[styles.sectionTitle, { color: palette.text, marginTop: 12, marginBottom: 12 }]}>Recipes</Text>
        {(allergies.length > 0 || diet !== 'No preference') && <Text accessibilityRole="alert" style={{ color: palette.error, marginBottom: 12 }}>Saved allergy and diet preferences are not verified for these scan suggestions yet. Review every recipe ingredient before cooking.</Text>}
        {recipeLoading && <View style={styles.scanStatus}><ActivityIndicator color={palette.accent} /><Text style={{ color: palette.muted }}>Finding recipes...</Text></View>}
        {recipeError ? <View style={styles.scanStatus}><Text accessibilityRole="alert" style={{ color: palette.error, flex: 1 }}>{recipeError}</Text><Pressable accessibilityRole="button" onPress={() => setRetry(value => value + 1)} style={styles.iconButton}><Text style={{ color: palette.accent }}>Retry</Text></Pressable></View> : null}
        {!detecting && !recipeLoading && !recipeError && !recommendations.length && <Text style={{ color: palette.muted }}>{!ingredients.length ? 'Add ingredients with +.' : 'No matching recipes yet.'}</Text>}
        {recommendations.length > 0 && <View style={[styles.coverageCard, { backgroundColor: palette.surface, borderColor: palette.border }]}>
          <Text style={{ color: palette.text, fontWeight: '700', marginBottom: 5 }}>Scanned ingredient coverage</Text>
          {coverageAvailable ? <>
            <Text style={{ color: palette.muted }}>{coveredIngredients.length} of {ingredients.length} scanned ingredients appear across these recipe suggestions.</Text>
            {uncoveredIngredients.length > 0 && <Text style={{ color: palette.muted, marginTop: 5 }}>Not represented yet: {uncoveredIngredients.join(', ')}</Text>}
          </> : <Text style={{ color: palette.muted }}>Restart the recipe recommendation service to see which scanned ingredients appear in these suggestions.</Text>}
        </View>}
        {recommendations.map(recipe => <View key={recipe.id} style={{ backgroundColor: palette.surface, borderColor: palette.border, borderWidth: 1, borderRadius: 14, padding: 16, marginBottom: 12 }}>
          <Image source={recipeImage(recipeDataset.find(item => item.id === recipe.id)?.family ?? '')} accessibilityLabel="Recipe illustration" style={{ width: '100%', height: 170, borderRadius: 10, marginBottom: 12, resizeMode: 'cover' }} />
          <Text style={{ color: palette.text, fontSize: 17, fontWeight: '700', marginBottom: 8 }}>{recipe.name}</Text>
          <Text style={{ color: palette.muted }}>{recipe.missing_supporting.length ? `Confirm supporting items: ${recipe.missing_supporting.map(x => x.replace(/_/g, ' ')).join(', ')}` : 'No missing supporting ingredients reported.'}</Text>
        </View>)}
      </ScrollView>
    </KeyboardAvoidingView>
    <BottomNav active="scan" />
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  resultDot: { width: 10, height: 10, borderRadius: 5 },
  filterRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 10 },
  filterChip: { minHeight: 44, paddingHorizontal: 12, justifyContent: 'center', borderRadius: 22, borderWidth: 1 },
  suggestionList: { maxHeight: 240 },
  ingredientEditor: { marginBottom: 14 },
  suggestions: { borderWidth: 1, borderRadius: 12, overflow: 'hidden', marginTop: 6 },
  suggestionRow: { minHeight: 48, paddingHorizontal: 14, paddingVertical: 10, flexDirection: 'row', alignItems: 'center', gap: 12 },
  suggestionName: { fontSize: 15, flex: 1 },
  rescanButton: { alignSelf: 'flex-end', minHeight: 44, justifyContent: 'center', paddingHorizontal: 16, borderWidth: 1, borderRadius: 12, marginBottom: 14 },
  scanStatus: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 14 },
  coverageCard: { borderWidth: 1, borderRadius: 14, padding: 14, marginBottom: 14 },
  screen: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 12, minHeight: 62 },
  iconButton: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' }, pageTitle: { fontSize: 22, fontWeight: '700' },
  content: { width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingBottom: 20 }, ingredientSummary: { flexDirection: 'row', gap: 14, marginBottom: 18, marginTop: 8 },
  thumbnail: { width: 72, height: 78, borderRadius: 10, resizeMode: 'cover' }, summaryCopy: { flex: 1, minWidth: 0 }, sectionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }, sectionTitle: { fontSize: 18, fontWeight: '700' }, edit: { minHeight: 44, paddingLeft: 12, justifyContent: 'center' }, editText: { fontSize: 14, fontWeight: '600' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 7 }, chip: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 44, paddingHorizontal: 11, borderRadius: 22 }, chipText: { fontSize: 13, flexShrink: 1 }, plus: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  entryRow: { flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderRadius: 14, paddingLeft: 14 }, input: { flex: 1, minWidth: 0, minHeight: 48, fontSize: 16 },
});
