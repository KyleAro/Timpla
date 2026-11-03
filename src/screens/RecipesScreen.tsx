import { useDeferredValue, useMemo, useRef, useState } from 'react';
import { router } from 'expo-router';
import { Pressable, SectionList, StyleSheet, Text, TextInput, View, type ViewToken } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { recipeGroups } from '../utils/recipeGroups';
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
  const sectionLayouts = useMemo(() => {
    const layouts: { length: number; offset: number; index: number }[] = [];
    let offset = 0;
    sections.forEach(section => {
      layouts.push({ length: 35, offset, index: layouts.length });
      offset += 35;
      section.data.forEach(() => {
        layouts.push({ length: 52, offset, index: layouts.length });
        offset += 52;
      });
      layouts.push({ length: 0, offset, index: layouts.length });
    });
    return layouts;
  }, [sections]);
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
    listRef.current?.scrollToLocation({ sectionIndex, itemIndex: 0, viewPosition: 0, animated: true });
  }

  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <AppHeader />
    <View style={[styles.stickyPanel, { backgroundColor: palette.background, borderColor: palette.border }]}>
      <View style={styles.searchRow}>
        <View style={[styles.searchBox, { backgroundColor: palette.secondary, borderColor: palette.border }]}>
          <AppIcon name="book" size={19} color={palette.muted} />
          <TextInput accessibilityLabel="Search Filipino recipes" placeholder="Search Filipino dishes" placeholderTextColor={palette.muted} value={query} onChangeText={setQuery} style={[styles.search, { color: palette.text }]} />
          {query.length > 0 && <Pressable accessibilityRole="button" accessibilityLabel="Clear recipe search" onPress={() => setQuery('')} hitSlop={8}><AppIcon name="close" size={17} color={palette.muted} /></Pressable>}
        </View>
        <Pressable accessibilityRole="button" accessibilityLabel="Filter recipes" accessibilityState={{ expanded: filterOpen }} onPress={() => setFilterOpen(value => !value)} style={[styles.filterButton, { backgroundColor: palette.secondary, borderColor: palette.border }]}>
          <AppIcon name="sliders" size={19} color={filter !== 'All' ? palette.accent : palette.text} />
          {filter !== 'All' && <View style={[styles.filterDot, { backgroundColor: palette.accent }]} />}
        </Pressable>
      </View>
      {filterOpen && <View style={[styles.filterPopover, { backgroundColor: palette.surface, borderColor: palette.border }]}>
        {filters.map(value => <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: filter === value }} onPress={() => { setFilter(value); setFilterOpen(false); }} style={[styles.filterOption, { borderColor: palette.border }]}><Text style={{ color: filter === value ? palette.accent : palette.text, fontWeight: filter === value ? '700' : '500' }}>{value === 'All' ? 'All dishes' : value.replace('With ', '')}</Text>{filter === value && <AppIcon name="check" size={16} color={palette.accent} />}</Pressable>)}
      </View>}
    </View>
    <SectionList ref={listRef} sections={listPending ? [] : sections} keyExtractor={dish => dish.id} stickySectionHeadersEnabled showsVerticalScrollIndicator={false}
      contentContainerStyle={[styles.listContent, { paddingBottom: bottomPadding }]}
      getItemLayout={(_, index) => sectionLayouts[index] ?? { length: 0, offset: 0, index }}
      viewabilityConfig={viewabilityConfig} onViewableItemsChanged={onViewableItemsChanged}
      onScroll={event => { const next = event.nativeEvent.contentOffset.y > 350; setShowTop(current => current === next ? current : next); }} scrollEventThrottle={100}
      onScrollToIndexFailed={({ index, averageItemLength }) => {
        const sectionIndex = pendingSectionRef.current;
        if (sectionIndex === null) return;
        listRef.current?.getScrollResponder()?.scrollTo({ y: averageItemLength * index, animated: true });
        setTimeout(() => {
          listRef.current?.scrollToLocation({ sectionIndex, itemIndex: 0, viewPosition: 0, animated: true });
        }, 450);
      }}
      onScrollBeginDrag={() => { pendingSectionRef.current = null; }}
      renderSectionHeader={({ section }) => <View style={[styles.letterHeader, { backgroundColor: palette.background }]}><Text style={[styles.sectionLetter, { color: palette.accent }]}>{section.title}</Text></View>}
      renderItem={({ item, index, section }) => {
        const isFinalDish = section.title === sections[sections.length - 1]?.title && index === section.data.length - 1;
        return <Pressable accessibilityRole="button" accessibilityLabel={`Open ${item.name}`} onPress={() => router.push({ pathname: '/recipe', params: { id: item.id } })} style={({ pressed }) => [styles.dishRow, { borderColor: palette.border, borderBottomWidth: isFinalDish ? 0 : StyleSheet.hairlineWidth }, pressed && { backgroundColor: palette.secondary }]}>
        <Text numberOfLines={1} ellipsizeMode="tail" style={[styles.dishTitle, { color: palette.text }]}>{item.name}</Text>
      </Pressable>;
      }}
      ListEmptyComponent={listPending ? <View style={styles.skeletonGrid}>{[0, 1, 2, 3, 4, 5].map(row => <View key={row} style={[styles.skeletonRow, { borderColor: palette.border }]}><View style={[styles.skeletonLine, { backgroundColor: palette.secondary, width: `${58 + row % 3 * 11}%` }]} /></View>)}</View> : <Text style={{ color: palette.muted, padding: 18 }}>No recipes found. Try another search or filter.</Text>}
      ListFooterComponent={!listPending && dishes.length > 0 ? <View style={styles.countFooter}><View style={[styles.countLine, { backgroundColor: palette.border }]} /><Text style={[styles.countText, { color: palette.muted }]}> {dishes.length.toLocaleString()} {saved ? 'favorites found' : 'dishes found'} </Text><View style={[styles.countLine, { backgroundColor: palette.border }]} /></View> : null}
      />
    {sections.length > 0 && <View pointerEvents="box-none" style={styles.indexLayer}><View style={styles.alphabetRail}>{'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map(letter => {
      const available = sectionIndexByLetter.has(letter);
      const active = activeLetter === letter;
      return <Pressable key={letter} accessibilityRole="button" accessibilityLabel={`Jump to recipes starting with ${letter}`} accessibilityState={{ disabled: !available, selected: active }} disabled={!available} onPress={() => jumpToLetter(letter)} style={[styles.letterButton, active && styles.letterActive]}><View style={[styles.letterMarker, { backgroundColor: active ? palette.accent : palette.muted, opacity: available ? 0.75 : 0.2, width: active ? 12 : 6 }]} /><Text style={[styles.indexLetter, { color: active ? palette.accent : palette.muted, opacity: available ? 1 : 0.3 }]}>{letter}</Text></Pressable>;
    })}</View></View>}
    {showTop && <Pressable accessibilityRole="button" accessibilityLabel="Back to top" onPress={() => listRef.current?.scrollToLocation({ sectionIndex: 0, itemIndex: 0, viewPosition: 0, animated: true })} style={[styles.topButton, { backgroundColor: palette.accent }]}><View style={styles.upIcon}><AppIcon name="chevron" size={20} color="#FFF8ED" /></View></Pressable>}
    <BottomNav active={saved ? 'profile' : 'recipes'} />
  </SafeAreaView>;
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  stickyPanel: { position: 'relative', zIndex: 8, width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingTop: 12, paddingBottom: 9, borderBottomWidth: StyleSheet.hairlineWidth },
  searchRow: { flexDirection: 'row', alignItems: 'center', gap: 9 }, searchBox: { flex: 1, minWidth: 0, flexDirection: 'row', alignItems: 'center', gap: 10, height: 44, paddingHorizontal: 14, borderRadius: 13, borderWidth: 1 }, search: { flex: 1, minWidth: 0, height: 44, fontSize: 14 },
  filterButton: { width: 44, height: 44, borderRadius: 13, borderWidth: 1, alignItems: 'center', justifyContent: 'center' }, filterDot: { position: 'absolute', top: 8, right: 8, width: 6, height: 6, borderRadius: 3 },
  filterPopover: { position: 'absolute', top: 62, right: 20, width: 180, borderWidth: 1, borderRadius: 14, paddingHorizontal: 12, elevation: 9, shadowColor: '#000', shadowOpacity: 0.22, shadowRadius: 10, shadowOffset: { width: 0, height: 5 } }, filterOption: { minHeight: 42, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderBottomWidth: StyleSheet.hairlineWidth },
  listContent: { width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 20, paddingRight: 56 },
  letterHeader: { paddingTop: 9, paddingBottom: 3 }, sectionLetter: { fontSize: 18, lineHeight: 23, fontWeight: '800' },
  dishRow: { height: 52, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8, borderBottomWidth: StyleSheet.hairlineWidth }, dishTitle: { flex: 1, fontSize: 15, lineHeight: 21, fontWeight: '600' },
  skeletonGrid: { paddingTop: 8 }, skeletonRow: { minHeight: 52, borderBottomWidth: StyleSheet.hairlineWidth, justifyContent: 'center' }, skeletonLine: { height: 13, borderRadius: 7 },
  countFooter: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingTop: 24, paddingBottom: 12 }, countLine: { height: StyleSheet.hairlineWidth, flex: 1 }, countText: { fontSize: 12, fontWeight: '600' },
  indexLayer: { position: 'absolute', right: 3, top: '28%', bottom: '23%', width: 40, zIndex: 4 }, alphabetRail: { flex: 1, alignItems: 'flex-end', justifyContent: 'space-between', paddingVertical: 1 }, letterButton: { minWidth: 37, minHeight: 13, flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', gap: 4, borderRadius: 10 }, letterMarker: { height: 1, borderRadius: 1 }, indexLetter: { width: 13, textAlign: 'right', fontSize: 11, lineHeight: 13, fontWeight: '700' }, letterActive: { transform: [{ scale: 1.2 }], zIndex: 2 },
  topButton: { position: 'absolute', right: 16, bottom: 124, width: 50, height: 50, borderRadius: 25, alignItems: 'center', justifyContent: 'center', elevation: 4, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 6, shadowOffset: { width: 0, height: 3 } }, upIcon: { transform: [{ rotate: '-90deg' }] },
});
