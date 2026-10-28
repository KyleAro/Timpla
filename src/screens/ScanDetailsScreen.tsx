import { router, useLocalSearchParams } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { scanDate } from './RecentsScreen';

export default function ScanDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { recentScans, openRecentScan } = useCooking();
  const { palette } = useTheme();
  const scan = recentScans.find((item) => item.id === id);
  const back = () => router.canGoBack() ? router.back() : router.replace('/recents');
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}><Pressable accessibilityRole="button" accessibilityLabel="Back to recents" onPress={back} style={styles.back}><AppIcon name="back" size={25} /></Pressable><Text accessibilityRole="header" style={[styles.headerTitle, { color: palette.text }]}>Scan details</Text><View style={styles.back} /></View>
    <ScrollView contentContainerStyle={styles.content}>
      {!scan ? <Text style={[styles.body, { color: palette.muted }]}>Scan unavailable</Text> : <>
        <Text style={[styles.date, { color: palette.muted }]}>{scanDate(scan.createdAt)}</Text>
        <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Ingredients</Text>
        {scan.ingredients.length ? <>
          <View style={[styles.ingredientRow, { borderColor: palette.border }]}><Text style={[styles.body, { color: palette.muted }]}>Ingredient</Text><Text style={[styles.body, { color: palette.muted }]}>Confidence</Text></View>
          {scan.ingredients.map((item) => <View key={item.name} style={[styles.ingredientRow, { borderColor: palette.border }]}><Text style={[styles.ingredient, { color: palette.text }]}>{item.name}</Text><Text style={[styles.confidence, { color: item.confidence === null ? palette.muted : palette.text }]}>{item.confidence === null ? 'Added manually' : `${Math.round(item.confidence * 100)}%`}</Text></View>)}
        </> : <Text style={[styles.body, { color: palette.muted }]}>No ingredients added</Text>}
        <Text style={[styles.dishLabel, { color: palette.muted }]}>Selected dish</Text>
        <Text style={[styles.dish, { color: palette.text }]}>{scan.selectedDish?.name ?? 'Not selected'}</Text>
        <Pressable accessibilityRole="button" onPress={() => { openRecentScan(scan.id); router.push('/ingredients'); }} style={[styles.resultsButton, { borderColor: palette.text }]}><Text style={[styles.resultsText, { color: palette.text }]}>View results</Text></Pressable>
      </>}
    </ScrollView>
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 }, header: { minHeight: 64, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 12 }, back: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' }, headerTitle: { fontSize: 22, fontWeight: '700' }, content: { width: '100%', maxWidth: 480, alignSelf: 'center', padding: 22, paddingBottom: 40 }, date: { fontSize: 14, marginBottom: 28 }, section: { fontSize: 23, fontWeight: '700', marginBottom: 15 }, ingredientRow: { minHeight: 54, paddingVertical: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 18, borderBottomWidth: StyleSheet.hairlineWidth }, ingredient: { fontSize: 17, flex: 1 }, confidence: { fontSize: 14, textAlign: 'right', flexShrink: 1 }, body: { fontSize: 15, lineHeight: 23 }, dishLabel: { fontSize: 15, marginTop: 32, marginBottom: 10 }, dish: { fontSize: 25, fontWeight: '700', marginBottom: 20 }, match: { padding: 20, borderRadius: 16, gap: 6 }, matchTitle: { fontSize: 21, fontWeight: '700' }, resultsButton: { marginTop: 28, minHeight: 54, borderWidth: 1, borderRadius: 16, alignItems: 'center', justifyContent: 'center' }, resultsText: { fontSize: 16, fontWeight: '600' },
});
