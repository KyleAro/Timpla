import { router } from 'expo-router';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { useRecommendations } from '../hooks/useRecommendations';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';
import dataset from '../data/recipeDataset.json';

const catalogIds = new Set(dataset.map(recipe => recipe.id));

export function RecipeMatchesPreview({ expanded = false }: { expanded?: boolean }) {
  const { palette } = useTheme();
  const { ingredients, detecting, diet } = useCooking();
  const { current, loading, retry } = useRecommendations();
  return <View style={styles.section}>
    <View style={styles.heading}><Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>Recipe matches</Text>{!expanded && <Pressable accessibilityRole="button" accessibilityLabel="See all recipe matches" onPress={() => router.push('/recommendations')} style={styles.seeAll}><Text style={{ color: palette.accent, fontWeight: '700' }}>See all</Text><AppIcon name="chevron" size={16} color={palette.accent} /></Pressable>}</View>
    {detecting || loading ? <View accessibilityLiveRegion="polite" style={styles.state}><ActivityIndicator color={palette.accent} /><Text style={{ color: palette.muted }}>{detecting ? 'Waiting for ingredients…' : 'Finding recipe matches…'}</Text></View>
      : !ingredients.length ? <Text style={[styles.message, { color: palette.muted }]}>Add ingredients to see recipe matches.</Text>
        : current?.error ? <View style={styles.state}><Text accessibilityRole="alert" style={[styles.message, { color: palette.muted, flex: 1 }]}>{current.error}</Text><Pressable accessibilityRole="button" onPress={retry} style={styles.seeAll}><Text style={{ color: palette.accent, fontWeight: '700' }}>Retry</Text></Pressable></View>
          : !current?.items.length ? <Text style={[styles.message, { color: palette.muted }]}>{diet !== 'No preference' ? `No recipes with a verified ${diet} label match yet.` : 'No matches yet. Check your ingredients and saved restrictions.'}</Text>
            : current.items.slice(0, expanded ? 20 : 3).map(item => <Pressable key={item.id} accessibilityRole="button" accessibilityLabel={`Open ${item.name}${item.ingredient_match ? `, ${item.ingredient_match.percentage}% ingredient match` : ''}`} onPress={() => router.push(catalogIds.has(item.id) ? { pathname: '/recipe', params: { id: item.id } } : '/recommendations')} style={({ pressed }) => [styles.card, { backgroundColor: pressed ? palette.secondary : palette.surface, borderColor: palette.border }]}>
              <View style={styles.cardTop}><View style={[styles.recipeIcon, { backgroundColor: palette.olive }]}><AppIcon name="book" size={22} color={palette.oliveText} /></View><Text style={[styles.name, { color: palette.text }]}>{item.name}</Text><AppIcon name="chevron" size={18} color={palette.accent} /></View>
              {item.ingredient_match && <View style={styles.coverage}><View style={[styles.matchBadge, { backgroundColor: palette.olive }]}><Text style={[styles.match, { color: palette.oliveText }]}>{item.ingredient_match.percentage}% match</Text></View><Text style={{ color: palette.muted, fontSize: 12 }}>{item.ingredient_match.matched} of {item.ingredient_match.total} listed ingredients</Text></View>}
              {!!item.missing_essential?.length && <Text style={[styles.message, { color: palette.muted }]}>Still needed: {item.missing_essential.map(name => name.replace(/_/g, ' ')).join(', ')}</Text>}
              {!!item.missing_supporting.length && <Text style={[styles.message, { color: palette.muted }]}>Check pantry: {item.missing_supporting.map(name => name.replace(/_/g, ' ')).join(', ')}</Text>}
            </Pressable>)}
  </View>;
}

const styles = StyleSheet.create({
  section: { marginTop: 12, gap: 12, marginBottom: 20 }, heading: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 10 }, title: { fontSize: 21, fontWeight: '700', flexShrink: 1 },
  seeAll: { minHeight: 44, paddingHorizontal: 4, flexDirection: 'row', alignItems: 'center', gap: 3 }, state: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 14 }, message: { fontSize: 13, lineHeight: 19 },
  card: { borderWidth: 1, borderRadius: 18, padding: 16, gap: 12 }, cardTop: { flexDirection: 'row', alignItems: 'center', gap: 12 }, recipeIcon: { width: 42, height: 42, borderRadius: 13, alignItems: 'center', justifyContent: 'center' }, name: { flex: 1, fontSize: 16, lineHeight: 22, fontWeight: '700' },
  matchBadge: { borderRadius: 16, paddingHorizontal: 12, paddingVertical: 7 },
  coverage: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: 8 }, match: { fontSize: 15, fontWeight: '800' },
});
