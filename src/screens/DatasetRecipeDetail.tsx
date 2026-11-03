import { router } from 'expo-router';
import * as Linking from 'expo-linking';
import { useState } from 'react';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useTheme } from '../theme/ThemeContext';
import dataset from '../data/recipeDataset.json';
import { SaveRecipeButton } from '../components/SaveRecipeButton';
import { useCooking } from '../state/CookingContext';
import { recipeImage } from '../utils/recipeImages';

type DatasetRecipe = (typeof dataset)[number];

export function DatasetRecipeDetail({ recipe: initialRecipe }: { recipe: DatasetRecipe }) {
  const { palette } = useTheme();
  const [versionId, setVersionId] = useState(initialRecipe.id);
  const versions = dataset.filter(item => item.family === initialRecipe.family);
  const recipe = versions.find(item => item.id === versionId) ?? initialRecipe;
  const [sourceError, setSourceError] = useState('');
  const { recordCookedRecipe } = useCooking();
  const [cookedIds, setCookedIds] = useState<string[]>([]);
  const [savingCooked, setSavingCooked] = useState(false);
  const [cookError, setCookError] = useState('');
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.recipeFrame}>
      <View pointerEvents="none" style={styles.fixedPhoto}>
        <Image source={recipeImage(recipe.family)} accessibilityLabel={`${recipe.dishName} illustration`} style={styles.photo} />
      </View>
    <ScrollView style={styles.screen} showsVerticalScrollIndicator={false} contentContainerStyle={styles.content}>
      <View style={styles.photoSpacer} />
      <View style={[styles.sheet, { backgroundColor: palette.background }]}>
      <View style={[styles.collectionBadge, { backgroundColor: palette.olive }]}><AppIcon name="leaf" size={15} color={palette.oliveText} /><Text style={{ color: palette.oliveText, fontSize: 12 }}>From your recipe collection</Text></View>
      <Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>{recipe.dishName}</Text>
      {versions.length > 1 ? <View style={styles.versions}>
        <Text accessibilityRole="header" style={[styles.versionHeading, { color: palette.text }]}>Choose a recipe</Text>
        <ScrollView horizontal scrollEnabled={versions.length > 2} showsHorizontalScrollIndicator={false} contentContainerStyle={[styles.versionList, versions.length === 2 && styles.twoVersionList]}>
        {versions.map((version, index) => {
          const selected = version.id === recipe.id;
          return <Pressable key={version.id} accessibilityRole="button" accessibilityLabel={`Choose ${version.name}, version ${index + 1}`} accessibilityState={{ selected }} onPress={() => {
            if (selected) return;
            setVersionId(version.id); setSourceError('');
          }} style={({ pressed }) => [styles.versionCard, versions.length === 2 && styles.twoVersionCard, { borderColor: selected ? palette.accent : palette.border, backgroundColor: selected || pressed ? palette.chip : palette.surface }]}>
            <View style={styles.versionTop}><Image source={recipeImage(version.family)} accessibilityLabel="Recipe illustration" style={styles.optionPhoto} />{selected ? <View style={[styles.selected, { backgroundColor: palette.accent }]}><AppIcon name="check" size={15} color="#FFF8ED" /></View> : <AppIcon name="chevron" size={18} color={palette.muted} />}</View>
            <Text style={[styles.versionName, { color: palette.text }]}>Option {index + 1}</Text>
            <Text style={{ color: palette.muted }}>{version.sourceUrl ? `${version.sourceLabel} · ` : ''}{version.ingredients.length} ingredients</Text>
            <Text numberOfLines={2} style={[styles.versionPreview, { color: palette.muted }]}>{version.ingredients.filter(line => !versions.every(other => other.ingredients.includes(line))).slice(0, 3).join(' · ') || 'Same ingredient wording'}</Text>
          </Pressable>;
        })}
        </ScrollView>
        <Text style={{ color: palette.muted, fontSize: 13, lineHeight: 20 }}>{recipe.name}</Text>
      </View> : null}
      <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Ingredients</Text>
      {recipe.ingredients.map((line, index) => <View key={index} style={[styles.row, { borderColor: palette.border }]}>
        <Text style={[styles.body, { color: palette.text }]}>{line}</Text>
      </View>)}
      <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Cooking instructions</Text>
      {recipe.steps.length ? recipe.steps.map((step, index) => <View key={index} style={styles.step}><View style={[styles.stepNumber, { backgroundColor: palette.olive }]}><Text style={{ color: palette.oliveText, fontWeight: '700' }}>{index + 1}</Text></View><Text style={[styles.body, { color: palette.text }]}>{step}</Text></View>) : <Text style={{ color: palette.muted }}>Cooking instructions are not included in this dataset record.</Text>}
      {recipe.sourceUrl ? <Pressable accessibilityRole="link" onPress={() => { void Linking.openURL(recipe.sourceUrl).catch(() => setSourceError('Could not open the original recipe.')); }} style={styles.source}><Text style={{ color: palette.accent }}>View original recipe</Text></Pressable> : null}
      {sourceError ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{sourceError}</Text> : null}
      <View style={[styles.cookedCard, { borderColor: palette.olive, backgroundColor: palette.olive }]}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}><AppIcon name="leaf" size={30} color={palette.oliveText} /><View style={{ flex: 1 }}><Text style={[styles.versionName, { color: palette.oliveText }]}>Made this today?</Text><Text style={{ color: palette.oliveText, marginTop: 4, lineHeight: 20 }}>Add it to your cooking history.</Text></View></View>
        <Pressable accessibilityRole="button" disabled={savingCooked || cookedIds.includes(recipe.id)} onPress={() => {
          if (savingCooked || cookedIds.includes(recipe.id)) return;
          setSavingCooked(true); setCookError('');
          void recordCookedRecipe(recipe.id, recipe.dishName).then(() => setCookedIds(current => [...current, recipe.id])).catch(() => setCookError('Could not save to history. Please try again.')).finally(() => setSavingCooked(false));
        }} style={[styles.cookedButton, { backgroundColor: palette.accent }]}><Text style={{ color: '#FFF8ED', fontWeight: '700' }}>{cookedIds.includes(recipe.id) ? 'Added to cooking history' : savingCooked ? 'Saving…' : 'Yes, I cooked this'}</Text></Pressable>
        {cookError ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{cookError}</Text> : null}
      </View>
      </View>
    </ScrollView>
    <View pointerEvents="box-none" style={styles.headerOverlay}>
      <View pointerEvents="box-none" style={styles.header}>
        <Pressable accessibilityRole="button" accessibilityLabel="Back to recipes" onPress={() => router.canGoBack() ? router.back() : router.replace('/recipes')} style={[styles.back, { backgroundColor: palette.surface }]}><AppIcon name="back" size={25} /></Pressable>
        <SaveRecipeButton id={recipe.id} />
      </View>
    </View>
    </View>
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  recipeFrame: { flex: 1, width: '100%', maxWidth: 520, alignSelf: 'center', overflow: 'hidden' },
  fixedPhoto: { position: 'absolute', top: 0, left: 0, right: 0 },
  photoSpacer: { height: 300 },
  photo: { width: '100%', height: 300, resizeMode: 'cover' },
  sheet: { padding: 22, paddingTop: 20, marginTop: -24, borderTopLeftRadius: 28, borderTopRightRadius: 28, paddingBottom: 40 },
  collectionBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', borderRadius: 18, paddingHorizontal: 11, paddingVertical: 7, marginBottom: 12 },
  versionList: { gap: 10, paddingBottom: 4 }, optionPhoto: { width: 64, height: 58, borderRadius: 10, resizeMode: 'cover' },
  twoVersionList: { flexGrow: 1, width: '100%' }, twoVersionCard: { flex: 1, width: 0, minWidth: 0 },
  stepNumber: { width: 30, height: 30, borderRadius: 15, alignItems: 'center', justifyContent: 'center' },
  cookedCard: { marginTop: 28, padding: 18, borderWidth: 1, borderRadius: 18, gap: 14 }, cookedButton: { minHeight: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16 },
  versions: { marginTop: 24, gap: 12 }, versionHeading: { fontSize: 18, fontWeight: '700' },
  versionCard: { width: 200, borderWidth: 1.5, borderRadius: 16, padding: 12, gap: 8 },
  versionTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  selected: { width: 24, height: 24, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  versionName: { fontSize: 17, fontWeight: '700', lineHeight: 23 }, versionPreview: { fontSize: 13, lineHeight: 20 },
  screen: { flex: 1 }, headerOverlay: { position: 'absolute', top: 12, left: 0, right: 0, zIndex: 20 },
  header: { width: '100%', maxWidth: 520, alignSelf: 'center', paddingHorizontal: 16, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  back: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  content: { width: '100%', maxWidth: 520, alignSelf: 'center' }, title: { fontSize: 32, lineHeight: 38, fontWeight: '800', letterSpacing: -.7 },
  section: { fontSize: 21, fontWeight: '700', marginTop: 24, marginBottom: 14 }, row: { flexDirection: 'row', alignItems: 'center', gap: 12, minHeight: 56, paddingVertical: 12, borderBottomWidth: StyleSheet.hairlineWidth },
  body: { flex: 1, fontSize: 15, lineHeight: 24 }, step: { flexDirection: 'row', gap: 12, marginBottom: 18 }, source: { minHeight: 48, justifyContent: 'center', marginTop: 12 },
});
