import { useDialogFocus } from '../hooks/useDialogFocus';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { typography } from '../theme/tokens';
import { Redirect, router, useFocusEffect } from 'expo-router';
import { useCallback, useRef, useState } from 'react';
import { ActivityIndicator, BackHandler, Image, KeyboardAvoidingView, Modal, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { RecipeMatchesPreview } from '../components/RecipeMatchesPreview';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useSwipeBack } from '../hooks/useSwipeBack';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { normalizeIngredient } from '../utils/normalizeIngredient';
import { canonicalIngredientName, ingredientCategories, IngredientCategory, ingredientSuggestions } from '../utils/ingredientSuggestions';

export default function ResultsScreen() {
  const bottomPadding = useBottomNavPadding();
  const { palette } = useTheme();
  const reducedMotion = useReducedMotion();
  const discardTitleRef = useRef<Text>(null);
  const showDiscardDialog = useDialogFocus(discardTitleRef);
  const leaveTitleRef = useRef<Text>(null);
  const showLeaveDialog = useDialogFocus(leaveTitleRef);
  const { ingredients, setIngredients, photo, detecting, detectionError, retryDetection, saveScanResult, discardScanResult } = useCooking();
  const [leaveOpen, setLeaveOpen] = useState(false);
  const [discardOpen, setDiscardOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const pendingNavigation = useRef<() => void>(() => router.replace('/home'));
  const requestLeave = useCallback((navigate: () => void) => {
    pendingNavigation.current = navigate;
    setSaveError('');
    setLeaveOpen(true);
  }, []);
  const requestSwipeBack = useCallback(() => {
    requestLeave(() => {
      if (router.canGoBack()) router.back();
      else router.replace('/home');
    });
  }, [requestLeave]);
  const swipeBack = useSwipeBack(!leaveOpen && !discardOpen && !saving, requestSwipeBack);
  useFocusEffect(useCallback(() => {
    const subscription = BackHandler.addEventListener('hardwareBackPress', () => {
      requestLeave(() => router.replace('/home'));
      return true;
    });
    return () => subscription.remove();
  }, [requestLeave]));
  async function finishResult(save: boolean, navigate = pendingNavigation.current) {
    if (saving) return;
    setSaving(true);
    setSaveError('');
    try {
      if (save) await saveScanResult(); else await discardScanResult();
      setLeaveOpen(false);
      setDiscardOpen(false);
      navigate();
    } catch { setSaveError('Couldn’t update your saved results. Please try again.'); }
    finally { setSaving(false); }
  }
  const [editing, setEditing] = useState(false);
  const [entry, setEntry] = useState('');
  const [ingredientCategory, setIngredientCategory] = useState<IngredientCategory>('All');
  const [error, setError] = useState('');
  const input = useRef<TextInput>(null);
  const suggestions = ingredientSuggestions(entry, ingredients, Number.MAX_SAFE_INTEGER, ingredientCategory);
  function addIngredient(value = entry) {
    const name = canonicalIngredientName(value);
    if (!name) return;
    if (ingredients.some((item) => normalizeIngredient(canonicalIngredientName(item)) === normalizeIngredient(name))) { setError('Already added.'); return; }
    setIngredients([...ingredients, name]); setEntry(''); setError('');
    input.current?.focus();
  }
  function openEditor() { setEditing(true); }
  function closeEditor() {
    setEditing(false);
    setEntry('');
    setError('');
    input.current?.blur();
  }
  if (!photo) return <Redirect href="/scan" />;
  return <SafeAreaView {...swipeBack} edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}>
      <Pressable accessibilityRole="button" accessibilityLabel="Back to Home" onPress={() => requestLeave(() => router.replace('/home'))} style={styles.iconButton}><AppIcon name="back" size={25} /></Pressable>
      <Text accessibilityRole="header" style={[styles.pageTitle, { color: palette.text }]}>Results</Text><View style={styles.iconButton} />
    </View>
    <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView keyboardDismissMode="on-drag" contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]} keyboardShouldPersistTaps="handled">
        <View style={styles.ingredientSummary}>
          {photo ? <Pressable accessibilityRole="button" accessibilityLabel="View captured photo" onPress={() => router.push('/photo')}><Image source={{ uri: photo }} accessibilityLabel="Ingredient photo" style={styles.thumbnail} /></Pressable> : null}
          <View style={styles.summaryCopy}>
            <View style={styles.sectionRow}><Text accessibilityRole="header" style={[styles.sectionTitle, { color: palette.text }]}>Ingredients detected</Text><Pressable accessibilityRole="button" accessibilityState={{ expanded: editing }} onPress={() => editing ? closeEditor() : openEditor()} style={styles.edit}><Text style={[styles.editText, { color: palette.accent }]}>{editing ? 'Done' : 'Edit'}</Text></Pressable></View>
            <View style={styles.chips}>
              {ingredients.map((name) => {
                return <Pressable key={name} disabled={!editing} accessibilityRole={editing ? 'button' : undefined} accessibilityLabel={editing ? `Remove ${name}` : name} onPress={() => setIngredients(ingredients.filter((item) => item !== name))} style={[styles.chip, { backgroundColor: palette.chip }]}>
                  <Text style={[styles.chipText, { color: palette.text }]}>{name}</Text>
                  {editing && <AppIcon name="close" size={16} color={palette.text} />}
                </Pressable>;
              })}
              {editing && <Pressable accessibilityRole="button" accessibilityLabel="Add ingredient" onPress={() => input.current?.focus()} style={[styles.plus, { backgroundColor: palette.buttonBackground }]}><AppIcon name="plus" size={23} color="#FFF8ED" /></Pressable>}
            </View>
          </View>
        </View>
        {detecting && <View style={[styles.scanStatus, { borderColor: palette.border, borderWidth: 1, borderRadius: 14, padding: 14 }]} accessibilityLiveRegion="polite"><ActivityIndicator color={palette.accent} /><Text style={{ color: palette.muted }}>Looking for ingredients…</Text></View>}
        {detectionError ? <View style={[styles.scanStatus, { alignItems: 'flex-start' }]}><View style={{ flex: 1, gap: 5 }}><Text accessibilityRole="alert" style={{ color: palette.error }}>Couldn’t find ingredients in this photo. Try again or add them manually.</Text></View><Pressable accessibilityRole="button" onPress={retryDetection} style={styles.iconButton}><Text style={{ color: palette.accent }}>Retry</Text></Pressable></View> : null}
        {photo && <Pressable accessibilityRole="button" accessibilityLabel="Rescan: take or upload another photo" onPress={() => requestLeave(() => router.replace('/scan'))} style={[styles.rescanButton, { borderColor: palette.border }]}><Text style={{ color: palette.accent }}>Rescan</Text></Pressable>}
        {editing && <View style={styles.ingredientEditor}>
          <View style={styles.sectionRow}>
            <Text style={[styles.sectionTitle, { color: palette.text }]}>Add ingredients</Text>
            <Pressable accessibilityRole="button" accessibilityLabel="Close ingredient picker" onPress={closeEditor} style={styles.editorClose}>
              <AppIcon name="close" size={20} color={palette.accent} />
              <Text style={[styles.editText, { color: palette.accent }]}>Close</Text>
            </Pressable>
          </View>
          <View accessibilityLabel="Ingredient category filters" style={styles.filterRow}>
            {ingredientCategories.map(category => <Pressable key={category} accessibilityRole="button" accessibilityLabel={`Filter ingredients: ${category}`} accessibilityState={{ selected: ingredientCategory === category }} onPress={() => { setIngredientCategory(category); setError(''); }} style={[styles.filterChip, { backgroundColor: ingredientCategory === category ? palette.buttonBackground : palette.surface, borderColor: palette.border }]}>
              <Text style={{ color: ingredientCategory === category ? '#FFF8ED' : palette.text, fontSize: typography.label }}>{category}</Text>
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
        <RecipeMatchesPreview />
        {saveError && !leaveOpen && !discardOpen ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{saveError}</Text> : null}
        <View style={styles.resultActions}>
          <Pressable accessibilityRole="button" disabled={saving || detecting} onPress={() => { void finishResult(true, () => router.replace('/recents')); }} style={[styles.noticePrimary, { backgroundColor: palette.buttonBackground, opacity: saving || detecting ? 0.5 : 1 }]}><Text style={styles.noticePrimaryText}>{saving ? 'Saving…' : 'Save result'}</Text></Pressable>
          <Pressable accessibilityRole="button" disabled={saving} onPress={() => { setSaveError(''); setDiscardOpen(true); }} style={[styles.noticeSecondary, { borderColor: palette.border }]}><Text style={[styles.noticeSecondaryText, { color: palette.text }]}>Discard</Text></Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
    <BottomNav active="scan" onNavigate={requestLeave} />
    <Modal onShow={showDiscardDialog} visible={discardOpen} transparent animationType={reducedMotion ? 'none' : 'fade'} onRequestClose={() => { if (!saving) setDiscardOpen(false); }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.noticeBackdrop}><View accessibilityViewIsModal style={[styles.noticeCard, { backgroundColor: palette.surface, borderColor: palette.border }]}>
        <Text ref={discardTitleRef} accessible accessibilityRole="header" style={[styles.noticeTitle, { color: palette.text }]}>Are you sure you want to discard this result?</Text>
        {saveError ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{saveError}</Text> : null}
        <Pressable accessibilityRole="button" disabled={saving} onPress={() => { void finishResult(false, () => router.replace('/home')); }} style={[styles.noticePrimary, { backgroundColor: palette.buttonBackground, opacity: saving ? 0.5 : 1 }]}><Text style={styles.noticePrimaryText}>{saving ? 'Discarding…' : 'Yes'}</Text></Pressable>
        <Pressable accessibilityRole="button" disabled={saving} onPress={() => setDiscardOpen(false)} style={[styles.noticeSecondary, { borderColor: palette.border }]}><Text style={[styles.noticeSecondaryText, { color: palette.text }]}>No</Text></Pressable>
      </View></ScrollView>
    </Modal>
    <Modal onShow={showLeaveDialog} visible={leaveOpen} transparent animationType={reducedMotion ? 'none' : 'fade'} onRequestClose={() => { if (!saving) setLeaveOpen(false); }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.noticeBackdrop}><View accessibilityViewIsModal style={[styles.noticeCard, { backgroundColor: palette.surface, borderColor: palette.border }]}>
        <Text ref={leaveTitleRef} accessible accessibilityRole="header" style={[styles.noticeTitle, { color: palette.text }]}>Save this result?</Text>
        <Text style={[styles.noticeBody, { color: palette.muted }]}>Keep this scan in Recents, or discard it before leaving.</Text>
        {saveError ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{saveError}</Text> : null}
        <Pressable accessibilityRole="button" disabled={saving || detecting} onPress={() => { void finishResult(true); }} style={[styles.noticePrimary, { backgroundColor: palette.buttonBackground, opacity: saving || detecting ? 0.5 : 1 }]}><Text style={styles.noticePrimaryText}>{detecting ? 'Finishing scan…' : saving ? 'Saving…' : 'Save result'}</Text></Pressable>
        <Pressable accessibilityRole="button" disabled={saving} onPress={() => { void finishResult(false); }} style={[styles.noticeSecondary, { borderColor: palette.border }]}><Text style={[styles.noticeSecondaryText, { color: palette.text }]}>Discard</Text></Pressable>
        <Pressable accessibilityRole="button" disabled={saving} onPress={() => setLeaveOpen(false)} style={styles.noticeSecondary}><Text style={[styles.noticeSecondaryText, { color: palette.muted }]}>Keep editing</Text></Pressable>
      </View></ScrollView>
    </Modal>
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  resultActions: { gap: 10, marginTop: 12, marginBottom: 20 },
  filterRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 10 },
  filterChip: { minHeight: 48, paddingHorizontal: 12, justifyContent: 'center', borderRadius: 22, borderWidth: 1 },
  suggestionList: { maxHeight: 240 },
  ingredientEditor: { marginBottom: 14 },
  editorClose: { minHeight: 48, paddingHorizontal: 8, flexDirection: 'row', alignItems: 'center', gap: 5 },
  suggestions: { borderWidth: 1, borderRadius: 12, overflow: 'hidden', marginTop: 6 },
  suggestionRow: { minHeight: 48, paddingHorizontal: 14, paddingVertical: 10, flexDirection: 'row', alignItems: 'center', gap: 12 },
  suggestionName: { fontSize: typography.body, flex: 1 },
  rescanButton: { alignSelf: 'flex-end', minHeight: 52, justifyContent: 'center', paddingHorizontal: 16, borderWidth: 1, borderRadius: 12, marginBottom: 14, paddingVertical: 14 },
  scanStatus: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 14 },
  screen: { flex: 1 }, header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 12, minHeight: 62 },
  iconButton: { width: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' }, pageTitle: { fontSize: typography.title, fontWeight: '700' },
  content: { width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingBottom: 20 }, ingredientSummary: { gap: 14, marginBottom: 18, marginTop: 8 },
  thumbnail: { width: '100%', aspectRatio: 4 / 3, borderRadius: 16, resizeMode: 'cover' }, summaryCopy: { minWidth: 0 }, sectionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }, sectionTitle: { fontSize: typography.subtitle, fontWeight: '700' }, edit: { minHeight: 48, paddingLeft: 12, justifyContent: 'center' }, editText: { fontSize: typography.label, fontWeight: '600' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 7 }, chip: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 48, paddingHorizontal: 11, borderRadius: 22 }, chipText: { fontSize: typography.label, flexShrink: 1 }, plus: { width: 48, minHeight: 48, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  entryRow: { flexDirection: 'row', alignItems: 'center', borderWidth: 1, borderRadius: 14, paddingLeft: 14 }, input: { flex: 1, minWidth: 0, minHeight: 48, fontSize: typography.body },
  noticeBackdrop: { flexGrow: 1, justifyContent: 'center', alignItems: 'center', padding: 22, backgroundColor: 'rgba(0, 0, 0, 0.62)' },
  noticeCard: { width: '100%', maxWidth: 420, borderWidth: 1, borderRadius: 16, padding: 22, gap: 14 },
  noticeHeading: { minHeight: 42, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  noticeTitle: { fontSize: typography.section, lineHeight: 28, fontWeight: '700', flexShrink: 0 },
  noticeClose: { width: 40, height: 40, alignItems: 'center', justifyContent: 'center' },
  noticeBody: { fontSize: typography.body, lineHeight: 22 },
  noticePrimary: { minHeight: 52, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16, borderRadius: 12, paddingVertical: 14 },
  noticePrimaryText: { color: '#FFF8ED', fontSize: typography.body, fontWeight: '700' },
  noticeSecondary: { minHeight: 52, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16, borderWidth: 1, borderRadius: 12, paddingVertical: 14 },
  noticeSecondaryText: { fontSize: typography.body, fontWeight: '600' },
});
