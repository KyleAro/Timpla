import { router } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useCooking } from '../state/CookingContext';
import { ThemePalette } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';
import { CatalogStatus } from '../components/CatalogStatus';

export default function HomeScreen() {
  const bottomPadding = useBottomNavPadding();
  const { displayName, people, setPhoto, recentScans, destinations } = useCooking();
  const { palette } = useTheme();
  const styles = makeStyles(palette);
  const firstName = displayName.trim().split(/\s+/)[0] || 'there';
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={styles.screen}>
      <AppHeader />
      <ScrollView style={styles.scroller} contentContainerStyle={[styles.scroll, { paddingBottom: bottomPadding }]}>
        <View style={styles.content}>
          <Text accessibilityRole="header" style={styles.greeting}>What are we cooking, <Text style={styles.name}>{firstName}?</Text></Text>
          <View style={styles.servingCard}>
            <AppIcon name="people" size={32} color={palette.oliveText} />
            <View style={styles.copy}>
              <Text style={styles.servingTitle}>Cooking for {people}</Text>
            </View>
            <Pressable onPress={() => router.push('/cooking-preferences')} accessibilityRole="button" accessibilityLabel="Edit serving size" style={styles.edit}><Text style={styles.editText}>Edit</Text><View style={styles.editIcon}><AppIcon name="chevron" size={16} /></View></Pressable>
          </View>
          <View style={styles.actions}>
            <Pressable accessibilityRole="button" accessibilityLabel="Reverse cooking" onPress={() => router.push('/reverse-cooking')} style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}>
              <AppIcon name="reverse" size={20} color={palette.accent} />
              <Text style={styles.actionTitle}>Reverse cooking</Text>
              <Text style={styles.actionNote}>Choose a dish</Text>
            </Pressable>
            <Pressable accessibilityRole="button" accessibilityLabel="Add ingredients manually" onPress={() => { setPhoto(null); router.push('/ingredients'); }} style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}>
              <AppIcon name="edit" size={20} color={palette.accent} />
              <Text style={styles.actionTitle}>Add manually</Text>
              <Text style={styles.actionNote}>＋ Ingredients</Text>
            </Pressable>
          </View>
          <Text accessibilityRole="header" style={styles.sectionTitle}>Ingredient highlight</Text>
          <Pressable accessibilityRole="button" accessibilityLabel="Explore recipes with talong" onPress={() => router.push({ pathname: '/explore', params: { ingredient: 'Eggplant' } })} style={styles.highlight}>
            <View style={styles.copy}><Text style={styles.highlightLabel}>Cook with</Text><Text style={styles.highlightName}>Talong</Text><View style={styles.highlightLink}><Text style={styles.highlightLinkText}>Explore recipes</Text><AppIcon name="chevron" size={16} color={palette.accent} /></View></View>
            <AppIcon name="leaf" size={58} color={palette.accent} />
          </Pressable>
          <View style={styles.sectionRow}><Text accessibilityRole="header" style={[styles.sectionTitle, { flex: 1 }]}>Explore the Philippines</Text><Pressable accessibilityRole="button" accessibilityLabel="View all Philippine destinations" onPress={() => router.push('/explore')} style={styles.viewAll}><Text style={styles.highlightLinkText}>View all</Text></Pressable></View>
          <CatalogStatus />
          <View style={styles.places}>{destinations.map((place) => <Pressable key={place.name} accessibilityRole="button" accessibilityLabel={`Explore ${place.name} recipes`} onPress={() => router.push({ pathname: '/explore', params: { place: place.name } })} style={({ pressed }) => [styles.place, pressed && styles.pressed]}><AppIcon name="book" size={24} color={palette.accent} /><Text style={styles.placeName}>{place.name}</Text><AppIcon name="chevron" size={16} /></Pressable>)}</View>
          <View style={styles.sectionRow}><Text accessibilityRole="header" style={styles.sectionTitle}>Recent scans</Text><Pressable accessibilityRole="button" onPress={() => router.replace('/recents')} style={styles.viewAll}><Text style={styles.highlightLinkText}>View all</Text></Pressable></View>
          <View style={styles.recentGroup}>{[...recentScans].sort((a, b) => b.createdAt - a.createdAt).slice(0, 2).map((scan) => <Pressable key={scan.id} accessibilityRole="button" onPress={() => router.push({ pathname: '/scan-details', params: { id: scan.id } })} style={styles.recentRow}><View style={styles.copy}><Text numberOfLines={1} style={styles.placeName}>{scan.ingredients.map((item) => item.name).join(', ') || scan.selectedDish?.name || 'Ingredient scan'}</Text><Text style={styles.note}>{new Date(scan.createdAt).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}</Text></View><AppIcon name="chevron" size={18} /></Pressable>)}{!recentScans.length && <Text style={styles.emptyRecent}>No scans yet</Text>}</View>
        </View>
      </ScrollView>
      <BottomNav active="home" />
    </SafeAreaView>
  );
}
function makeStyles(p: ThemePalette) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: p.background },
    scroller: { flex: 1 },
    scroll: { flexGrow: 1, paddingHorizontal: 20, paddingTop: 24, paddingBottom: 40 },
    content: { width: '100%', maxWidth: 440, alignSelf: 'center', gap: 14 },
    greeting: { color: p.text, fontSize: 32, lineHeight: 39, fontWeight: '600', letterSpacing: -1, marginBottom: 10 },
    name: { fontWeight: '800' },
    servingCard: { backgroundColor: p.olive, borderRadius: 19, minHeight: 88, flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16 },
    copy: { flex: 1, minWidth: 0 },
    servingTitle: { color: p.oliveText, fontSize: 16, fontWeight: '700' },
    note: { color: p.muted, fontSize: 12, marginTop: 4 },
    edit: { minHeight: 44, minWidth: 76, flexShrink: 0, alignSelf: 'center', paddingHorizontal: 14, paddingVertical: 11, borderRadius: 23, backgroundColor: p.surface, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, borderWidth: 1, borderColor: p.border },
    editText: { color: p.text, fontSize: 14, lineHeight: 20, includeFontPadding: false, textAlignVertical: 'center', fontWeight: '600' },
    editIcon: { width: 16, height: 20, alignItems: 'center', justifyContent: 'center' },
    actions: { flexDirection: 'row', gap: 10, alignItems: 'stretch' },
    actionCard: { flex: 1, minWidth: 0, minHeight: 106, gap: 9, padding: 13, borderWidth: 1, borderColor: p.border, borderRadius: 17, backgroundColor: p.surface },
    actionTitle: { color: p.text, fontWeight: '700', fontSize: 14 },
    actionNote: { color: p.muted, fontSize: 12 },
    pressed: { backgroundColor: p.secondary },
    sectionTitle: { color: p.text, fontSize: 20, fontWeight: '700', marginTop: 14 },
    sectionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    highlight: { backgroundColor: p.chip, borderRadius: 20, padding: 22, flexDirection: 'row', alignItems: 'center', gap: 16 },
    highlightLabel: { color: p.muted, fontSize: 13 },
    highlightName: { color: p.text, fontSize: 30, fontWeight: '800', marginTop: 5, marginBottom: 15 },
    highlightLink: { alignSelf: 'flex-start', flexDirection: 'row', gap: 7, alignItems: 'center', backgroundColor: p.surface, borderRadius: 22, paddingVertical: 10, paddingHorizontal: 13 },
    highlightLinkText: { color: p.accent, fontSize: 13, fontWeight: '600' },
    places: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
    place: { flexGrow: 1, flexBasis: '46%', minHeight: 80, flexDirection: 'row', alignItems: 'center', gap: 10, padding: 13, borderRadius: 17, borderWidth: 1, borderColor: p.border, backgroundColor: p.surface },
    placeName: { color: p.text, fontSize: 15, fontWeight: '600', flexShrink: 1, flexGrow: 1 },
    viewAll: { minHeight: 44, justifyContent: 'center', paddingLeft: 12, marginTop: 14 },
    recentGroup: { borderTopWidth: StyleSheet.hairlineWidth, borderColor: p.border },
    recentRow: { minHeight: 78, flexDirection: 'row', gap: 12, alignItems: 'center', borderBottomWidth: StyleSheet.hairlineWidth, borderColor: p.border, paddingVertical: 14 },
    emptyRecent: { color: p.muted, paddingVertical: 22, fontSize: 14 },
  });
}
