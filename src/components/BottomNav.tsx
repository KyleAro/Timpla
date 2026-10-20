import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';

export function useBottomNavPadding() {
  return 96 + useSafeAreaInsets().bottom + 24;
}

export function BottomNav({ active }: { active: 'home' | 'recipes' | 'profile' | 'recents' | 'scan' }) {
  const { palette } = useTheme();
  const { bottom } = useSafeAreaInsets();
  const items = [
    { key: 'home', title: 'Home', icon: 'home', onPress: () => router.replace('/home') },
    { key: 'recipes', title: 'Recipes', icon: 'book', onPress: () => router.replace('/recipes') },
    { key: 'scan', title: 'Scan', icon: 'camera', onPress: () => router.replace('/scan') },
    { key: 'recents', title: 'Recents', icon: 'history', onPress: () => router.replace('/recents') },
    { key: 'profile', title: 'Profile', icon: 'user', onPress: () => router.replace('/profile') },
  ] as const;
  return (
    <View pointerEvents="box-none" style={[styles.nav, { paddingBottom: bottom }]}>
      <View pointerEvents="none" style={[styles.bar, { backgroundColor: palette.surface, borderColor: palette.border }]} />
      <View pointerEvents="box-none" style={styles.items}>
      {items.map((item) => {
        const scan = item.key === 'scan';
        const selected = active === item.key;
        return (
          <Pressable key={item.key} accessibilityRole="button" accessibilityLabel={scan ? 'Scan ingredients' : item.title} accessibilityState={{ selected }} onPress={() => { if (!selected) item.onPress(); }} style={styles.item}>
            {scan ? <View style={[styles.scan, { backgroundColor: palette.accent, borderColor: palette.background }]}><AppIcon name="camera" size={22} color="#FFF8ED" /></View> : <AppIcon name={item.icon} size={20} color={selected ? palette.accent : palette.muted} />}
            <Text style={[styles.label, { color: selected ? palette.accent : palette.muted }, selected && styles.active]}>{item.title}</Text>
          </Pressable>
        );
      })}
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  nav: { position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 10, minHeight: 96 },
  bar: { position: 'absolute', top: 22, left: 0, right: 0, bottom: 0, borderTopWidth: StyleSheet.hairlineWidth },
  items: { flexDirection: 'row', width: '100%', maxWidth: 520, alignSelf: 'center', minHeight: 96 },
  item: { flex: 1, minWidth: 0, paddingTop: 42, paddingBottom: 10, alignItems: 'center', justifyContent: 'flex-end', gap: 9 },
  scan: { position: 'absolute', top: 0, width: 68, height: 68, borderRadius: 34, borderWidth: 6, alignItems: 'center', justifyContent: 'center' },
  label: { fontSize: 11, lineHeight: 16, includeFontPadding: false, textAlign: 'center' },
  active: { fontWeight: '700' },
});


