import { typography } from '../theme/tokens';
import { useDeferredValue, useMemo, useRef, useState } from 'react';
import { router } from 'expo-router';
import { Pressable, ScrollView, SectionList, StyleSheet, Text, TextInput, View, type ViewToken } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { recipeGroups } from '../utils/recipeGroups';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { AppIcon } from '../components/AppIcon';

const filters = ['All', 'With chicken', 'With vegetables', 'Seafood'] as const;
type Filter = typeof filters[number];
type Dish = (typeof recipeGroups)[number];
type DishSection = { title: string; data: Dish[] };
const filterTerms: Record<Exclude<Filter, 'All'>, RegExp> = {
  'With chicken': /\b(chicken|manok)\b/i,
  'With vegetables': /\b(eggplant|talong|cabbage|repolyo|sayote|chayote|kangkong|okra|spinach|squash|kalabasa|carrot|pechay|sitaw)\b/i,
  Seafood: /\b(fish|shrimp|prawn|hipon|squid|pusit|crab|alimango|alimasag|tilapia|bangus|tuna|salmon|mussel|tahong)\b/i,
};

export default function RecipesScreen({ saved = false }: { saved?: boolean }) {
  const { palette } = useTheme();
  const reducedMotion = useReducedMotion();
  const bottomPadding = useBottomNavPadding();
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  const [filter, setFilter] = useState<Filter>('All');
  const deferredFilter = useDeferredValue(filter);
  const [filterOpen, setFilterOpen] = useState(false);
  const [showTop, setShowTop] = useState(false);
  const [activeLetter, setActiveLetter] = useState('');
  const listRef = useRef<SectionList<Dish, DishSection>>(null);
  const pendingSectionRef = useRef<number | null>(null);
  const viewabilityConfig = useMemo(() => ({ itemVisiblePercentThreshold: 10 }), []);
  const { savedRecipeIds } = useCooking();
  const listPending = query !== deferredQuery || filter !== deferredFilter;
  const dishes = useMemo(() => recipeGroups
    .filter(dish => (!saved || dish.versions.some(version => savedRecipeIds.includes(version.id)))
      && dish.versions.some(version => version.name.toLowerCase().includes(deferredQuery.trim().toLowerCase())
        && (deferredFilter === 'All' || filterTerms[deferredFilter].test(version.ingredients.join(' ')))))
    .map(dish => saved ? { ...dish, id: dish.versions.find(version => savedRecipeIds.includes(version.id))!.id } : dish)
    .sort((a, b) => a.name.localeCompare(b.name)), [deferredQuery, deferredFilter, saved, savedRecipeIds]);
  const sections = useMemo<DishSection[]>(() => {
    const groups = new Map<string, Dish[]>();
    for (const dish of dishes) {
      const initial = dish.name.trim().charAt(0).toUpperCase();
      const letter = /^[A-Z]$/.test(initial) ? initial : '#';
      groups.set(letter, [...(groups.get(letter) ?? []), dish]);
    }
    return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([title, data]) => ({ title, data }));
  }, [dishes]);
  const sectionIndexByLetter = useMemo(() => new Map(sections.map((section, index) => [section.title, index])), [sections]);
  const onViewableItemsChanged = useMemo(() => ({ viewableItems }: { viewableItems: ViewToken[] }) => {
    const firstVisibleDish = viewableItems.find(token => token.isViewable && token.section && typeof token.section.title === 'string');
    const visibleLetter = firstVisibleDish?.section?.title;
    if (visibleLetter && /^[A-Z]$/.test(visibleLetter)) {
      const requestedSection = pendingSectionRef.current;
      if (requestedSection !== null && sections[requestedSection]?.title !== visibleLetter) return;
      pendingSectionRef.current = null;
      setActiveLetter(current => current === visibleLetter ? current : visibleLetter);
    }
  }, [sections]);

  function jumpToLetter(letter: string) {
    const sectionIndex = sectionIndexByLetter.get(letter);
    if (sectionIndex === undefined) return;
    pendingSectionRef.current = sectionIndex;
    setActiveLetter(letter);
    listRef.current?.scrollToLocation({ sectionIndex, itemIndex: 0, viewPosition: 0, animated: !reducedMotion });
  }

  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <AppHeader />
    <View style={[styles.stickyPanel, { backgroundColor: palette.background, borderColor: palette.border }]}>
      {!saved && <Pressable accessibilityRole="button" onPress={() => router.push('/recommendations')} style={{ minHeight: 56, flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10, padding: 12, borderRadius: 14, backgroundColor: palette.olive }}><AppIcon name="leaf" size={22} color={palette.oliveText} /><View style={{ flex: 1 }}><Text style={{ color: palette.oliveText, fontWeight: '700', fontSize: typography.body }}>Cook with what you have</Text><Text style={{ color: palette.oliveText, fontSize: typography.label, marginTop: 3 }}>Find recipes for your ingredients</Text></View><AppIcon name="chevron" size={18} color={palette.oliveText} /></Pressable>}<View style={styles.searchRow}>
        <View style={[styles.searchBox, { backgroundColor: palette.secondary, borderColor: palette.border }]}>
          <AppIcon name="book" size={19} color={palette.muted} />
          <TextInput accessibilityLabel="Search Filipino recipes" placeholder="Search Filipino dishes" placeholderTextColor={palette.muted} value={query} onChangeText={setQuery} style={[styles.search, { color: palette.text }]} />
          {query.length > 0 && <Pressable accessibilityRole="button" accessibilityLabel="Clear recipe search" onPress={() => setQuery('')} style={{ minWidth: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' }}><AppIcon name="close" size={17} color={palette.muted} /></Pressable>}
        </View>
        <Pressable accessibilityRole="button" accessibilityLabel="Filter recipes" accessibilityState={{ expanded: filterOpen }} onPress={() => setFilterOpen(value => !value)} style={[styles.filterButton, { backgroundColor: palette.secondary, borderColor: palette.border }]}>
          <AppIcon name="sliders" size={19} color={filter !== 'All' ? palette.accent : palette.text} />
          {filter !== 'All' && <View style={[styles.filterDot, { backgroundColor: palette.buttonBackground }]} />}
        </Pressable>
      </View>
      {filterOpen && <View style={[styles.filterPopover, { top: saved ? 62 : 140, backgroundColor: palette.surface, borderColor: palette.border }]}>
        {filters.map(value => <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: filter === value }} onPress={() => { setFilter(value); setFilterOpen(false); }} style={[styles.filterOption, { borderColor: palette.border }]}><Text style={{ color: filter === value ? palette.accent : palette.text, fontWeight: filter === value ? '700' : '500' }}>{value === 'All' ? 'All dishes' : value.replace('With ', '')}</Text>{filter === value && <AppIcon name="check" size={16} color={palette.accent} />}</Pressable>)}
      </View>}
    {sections.length > 0 && <ScrollView horizontal showsHorizontalScrollIndicator={false} accessibilityLabel="Recipe alphabet" contentContainerStyle={styles.alphabetRail}>{'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map(letter => {
      const available = sectionIndexByLetter.has(letter);
      const active = activeLetter === letter;
      return <Pressable key={letter} accessibilityRole="button" accessibilityLabel={`Jump to recipes starting with ${letter}`} accessibilityState={{ disabled: !available, selected: active }} disabled={!available} onPress={() => jumpToLetter(letter)} style={[styles.letterButton, active && styles.letterActive]}><View style={[styles.letterMarker, { backgroundColor: active ? palette.accent : palette.muted, opacity: available ? 0.75 : 0.2, width: active ? 12 : 6 }]} /><Text style={[styles.indexLetter, { color: active ? palette.accent : palette.muted, opacity: available ? 1 : 0.3 }]}>{letter}</Text></Pressable>;
    })}</ScrollView>}
    </View>
    <SectionList automaticallyAdjustKeyboardInsets keyboardDismissMode="on-drag" keyboardShouldPersistTaps="handled" ref={listRef} sections={listPending ? [] : sections} keyExtractor={dish => dish.id} stickySectionHeadersEnabled showsVerticalScrollIndicator={false}
      contentContainerStyle={[styles.listContent, { paddingBottom: bottomPadding }]}
      viewabilityConfig={viewabilityConfig} onViewableItemsChanged={onViewableItemsChanged}
      onScroll={event => { const next = event.nativeEvent.contentOffset.y > 350; setShowTop(current => current === next ? current : next); }} scrollEventThrottle={100}
      onScrollToIndexFailed={({ index, averageItemLength }) => {
        const sectionIndex = pendingSectionRef.current;
        if (sectionIndex === null) return;
        listRef.current?.getScrollResponder()?.scrollTo({ y: averageItemLength * index, animated: !reducedMotion });
        setTimeout(() => {
          listRef.current?.scrollToLocation({ sectionIndex, itemIndex: 0, viewPosition: 0, animated: !reducedMotion });
        }, 450);
      }}
      onScrollBeginDrag={() => { pendingSectionRef.current = null; }}
      renderSectionHeader={({ section }) => <View style={[styles.letterHeader, { backgroundColor: palette.background }]}><Text style={[styles.sectionLetter, { color: palette.accent }]}>{section.title}</Text></View>}
      renderItem={({ item, index, section }) => {
        const isFinalDish = section.title === sections[sections.length - 1]?.title && index === section.data.length - 1;
        return <Pressable accessibilityRole="button" accessibilityLabel={`Open ${item.name}`} onPress={() => router.push({ pathname: '/recipe', params: { id: item.id } })} style={({ pressed }) => [styles.dishRow, { borderColor: palette.border, borderBottomWidth: isFinalDish ? 0 : StyleSheet.hairlineWidth }, pressed && { backgroundColor: palette.secondary }]}>
        <Text style={[styles.dishTitle, { color: palette.text }]}>{item.name}</Text>
      </Pressable>;
      }}
      ListEmptyComponent={listPending ? <View style={styles.skeletonGrid}>{[0, 1, 2, 3, 4, 5].map(row => <View key={row} style={[styles.skeletonRow, { borderColor: palette.border }]}><View style={[styles.skeletonLine, { backgroundColor: palette.secondary, width: `${58 + row % 3 * 11}%` }]} /></View>)}</View> : <Text style={{ color: palette.muted, padding: 18 }}>No recipes found. Try another search or filter.</Text>}
      ListFooterComponent={!listPending && dishes.length > 0 ? <View style={styles.countFooter}><View style={[styles.countLine, { backgroundColor: palette.border }]} /><Text style={[styles.countText, { color: palette.muted }]}> {dishes.length.toLocaleString()} {saved ? 'favorites found' : 'dishes found'} </Text><View style={[styles.countLine, { backgroundColor: palette.border }]} /></View> : null}
      />
    {showTop && <Pressable accessibilityRole="button" accessibilityLabel="Back to top" onPress={() => listRef.current?.scrollToLocation({ sectionIndex: 0, itemIndex: 0, viewPosition: 0, animated: !reducedMotion })} style={[styles.topButton, { backgroundColor: palette.buttonBackground }]}><View style={styles.upIcon}><AppIcon name="chevron" size={20} color="#FFF8ED" /></View></Pressable>}
    <BottomNav active={saved ? 'profile' : 'recipes'} />
  </SafeAreaView>;
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  stickyPanel: { position: 'relative', zIndex: 8, width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingTop: 12, paddingBottom: 9, borderBottomWidth: StyleSheet.hairlineWidth },
  searchRow: { flexDirection: 'row', alignItems: 'center', gap: 9 }, searchBox: { flex: 1, minWidth: 0, flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 52, paddingHorizontal: 14, borderRadius: 12, borderWidth: 1 }, search: { flex: 1, minWidth: 0, minHeight: 52, fontSize: typography.label },
  filterButton: { width: 48, minHeight: 48, borderRadius: 12, borderWidth: 1, alignItems: 'center', justifyContent: 'center' }, filterDot: { position: 'absolute', top: 8, right: 8, width: 6, height: 6, borderRadius: 3 },
  filterPopover: { zIndex: 20, position: 'absolute', top: 62, right: 20, width: 180, borderWidth: 1, borderRadius: 14, paddingHorizontal: 12, elevation: 9, shadowColor: '#000', shadowOpacity: 0.22, shadowRadius: 10, shadowOffset: { width: 0, height: 5 } }, filterOption: { minHeight: 42, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderBottomWidth: StyleSheet.hairlineWidth },
  listContent: { width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingRight: 20 },
  letterHeader: { paddingTop: 9, paddingBottom: 3 }, sectionLetter: { fontSize: typography.subtitle, lineHeight: 23, fontWeight: '800' },
  dishRow: { minHeight: 64, paddingVertical: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8, borderBottomWidth: StyleSheet.hairlineWidth }, dishTitle: { flex: 1, fontSize: typography.body, lineHeight: 21, fontWeight: '600' },
  skeletonGrid: { paddingTop: 8 }, skeletonRow: { minHeight: 52, borderBottomWidth: StyleSheet.hairlineWidth, justifyContent: 'center' }, skeletonLine: { height: 13, borderRadius: 7 },
  countFooter: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingTop: 24, paddingBottom: 12 }, countLine: { height: StyleSheet.hairlineWidth, flex: 1 }, countText: { fontSize: typography.label, fontWeight: '600' },
  indexLayer: { position: 'absolute', right: 3, top: '28%', bottom: '23%', width: 40, zIndex: 4 }, alphabetRail: { flexDirection: 'row', gap: 4, paddingVertical: 8 }, letterButton: { minWidth: 48, minHeight: 48, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 4, borderRadius: 12 }, letterMarker: { height: 1, borderRadius: 1 }, indexLetter: { width: 13, textAlign: 'right', fontSize: typography.caption, lineHeight: 13, fontWeight: '700' }, letterActive: { transform: [{ scale: 1.2 }], zIndex: 2 },
  topButton: { position: 'absolute', right: 16, bottom: 124, width: 50, height: 50, borderRadius: 25, alignItems: 'center', justifyContent: 'center', elevation: 4, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 6, shadowOffset: { width: 0, height: 3 } }, upIcon: { transform: [{ rotate: '-90deg' }] },
});
