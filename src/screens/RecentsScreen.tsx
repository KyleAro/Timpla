import { router } from 'expo-router';
import { Image, SectionList, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { RecentScan } from '../state/scanHistory';
import { recipeImage } from '../utils/recipeImages';
import recipeDataset from '../data/recipeDataset.json';

export function scanDate(timestamp: number) {
  return new Date(timestamp).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
}
function dayLabel(timestamp: number) {
  const date = new Date(timestamp);
  const today = new Date();
  const yesterday = new Date(); yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return 'Today';
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}
export default function RecentsScreen() {
  const bottomPadding = useBottomNavPadding();
  const { palette } = useTheme();
  const { recentScans, cookingHistory, historyError } = useCooking();
  const sections: { title: string; data: RecentScan[] }[] = [];
  for (const scan of [...recentScans].sort((a, b) => b.createdAt - a.createdAt)) {
    const title = dayLabel(scan.createdAt);
    const group = sections[sections.length - 1];
    if (group?.title === title) group.data.push(scan);
    else sections.push({ title, data: [scan] });
  }
  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <AppHeader />
    <SectionList sections={sections} keyExtractor={(item) => item.id} stickySectionHeadersEnabled={false} contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]}
      ListHeaderComponent={<View>
        <Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>History</Text>
        <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Cooked recipes</Text>
        {historyError ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{historyError}</Text> : null}
        {!cookingHistory.length && <Text style={{ color: palette.muted, marginBottom: 16 }}>Your cooked recipes will appear here.</Text>}
        {cookingHistory.map(item => <Pressable key={item.id} accessibilityRole="button" accessibilityLabel={`Open ${item.name}, cooked ${scanDate(item.cookedAt)}`} onPress={() => router.push({ pathname: '/recipe', params: { id: item.recipeId } })} style={[styles.row, { borderColor: palette.border, backgroundColor: palette.surface }]}>
          <Image source={recipeImage(recipeDataset.find(recipe => recipe.id === item.recipeId)?.family ?? '')} accessibilityLabel="Recipe illustration" style={{ width: 56, height: 56, borderRadius: 12 }} /><View style={styles.copy}><Text style={[styles.rowTitle, { color: palette.text }]}>{item.name}</Text><Text style={[styles.date, { color: palette.muted }]}>{scanDate(item.cookedAt)}</Text></View><AppIcon name="chevron" size={20} />
        </Pressable>)}
        <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Recent scans</Text>
      </View>}
      renderSectionHeader={({ section }) => <Text style={[styles.section, { color: palette.muted }]}>{section.title}</Text>}
      ListEmptyComponent={<View style={styles.empty}><AppIcon name="history" size={42} color={palette.accent} /><Text style={[styles.emptyTitle, { color: palette.text }]}>No scans yet</Text><Pressable accessibilityRole="button" onPress={() => router.replace('/scan')} style={[styles.button, { backgroundColor: palette.accent }]}><Text style={styles.buttonText}>Scan ingredients</Text></Pressable></View>}
      renderItem={({ item }) => <Pressable accessibilityRole="button" accessibilityLabel={`${item.selectedDish?.name ?? 'No dish selected'}, ${scanDate(item.createdAt)}`} onPress={() => router.push({ pathname: '/scan-details', params: { id: item.id } })} style={({ pressed }) => [styles.row, { borderColor: palette.border, backgroundColor: pressed ? palette.secondary : palette.surface }]}>
        <AppIcon name="history" size={27} />
        <View style={styles.copy}><Text style={[styles.rowTitle, { color: palette.text }]}>{item.selectedDish?.name ?? 'No dish selected'}</Text><Text style={[styles.date, { color: palette.muted }]}>{scanDate(item.createdAt)}</Text></View>
        <AppIcon name="chevron" size={20} />
      </Pressable>}
    />
    <BottomNav active="recents" />
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 }, content: { flexGrow: 1, width: '100%', maxWidth: 480, alignSelf: 'center', padding: 20, paddingBottom: 32 }, title: { fontSize: 30, fontWeight: '800', marginBottom: 12 }, section: { fontSize: 16, fontWeight: '600', marginTop: 18, marginBottom: 12 }, row: { minHeight: 80, flexDirection: 'row', alignItems: 'center', gap: 16, padding: 16, borderWidth: 1, borderRadius: 16, marginBottom: 10 }, copy: { flex: 1, minWidth: 0 }, rowTitle: { fontSize: 16, lineHeight: 23, fontWeight: '600' }, date: { fontSize: 13, marginTop: 5 }, empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 50, gap: 16 }, emptyTitle: { fontSize: 21, fontWeight: '700' }, button: { minHeight: 50, paddingHorizontal: 24, borderRadius: 25, justifyContent: 'center' }, buttonText: { color: '#FFF8ED', fontWeight: '700', fontSize: 15 },
});
