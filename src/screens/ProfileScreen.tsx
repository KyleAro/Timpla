import { router } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { useAuth } from '../auth/AuthContext';
import { useAuthAction } from '../auth/useAuthAction';

const sections = [
  { title: 'Saved recipes', subtitle: 'Your bookmarked dishes', icon: 'bookmark', route: '/saved-recipes' },
  { title: 'Profile details', subtitle: 'Name and profile', icon: 'user', route: '/profile-details' },
  { title: 'Cooking preferences', subtitle: 'Servings, diet and cooking style', icon: 'people', route: '/cooking-preferences' },
  { title: 'Allergies & exclusions', subtitle: 'Ingredients to avoid', icon: 'leaf', route: '/allergies' },
  { title: 'App settings', subtitle: 'Appearance and app options', icon: 'settings', route: '/settings' },
] as const;

export default function ProfileScreen() {
  const bottomPadding = useBottomNavPadding();
  const { displayName } = useCooking();
  const { palette } = useTheme();
  const { session, signOut, preview } = useAuth();
  const { busy, error, run } = useAuthAction();
  const names = displayName.trim().split(/\s+/).filter(Boolean);
  const initials = names.length > 1 ? `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase() : (names[0]?.[0] ?? 'U').toUpperCase();
  return <SafeAreaView edges={['top', 'left', 'right']} style={[styles.screen, { backgroundColor: palette.background }]}>
    <AppHeader />
    <ScrollView contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]}>
      <Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>Profile</Text>
      <View style={styles.identity}>
        <View style={[styles.avatar, { backgroundColor: palette.profile }]}><Text style={[styles.initials, { color: palette.profileText }]}>{initials}</Text></View>
        <View style={styles.copy}><Text style={[styles.name, { color: palette.text }]}>{displayName.trim() || 'Your profile'}</Text><Text style={[styles.subtitle, { color: palette.muted }]}>{preview ? 'Preview mode' : session?.user.email}</Text></View>
      </View>
      <View style={[styles.group, { backgroundColor: palette.surface, borderColor: palette.border }]}>
        {sections.map((item, index) => <Pressable key={item.route} accessibilityRole="button" accessibilityLabel={item.title} onPress={() => router.push(item.route)} style={({ pressed }) => [styles.row, { backgroundColor: pressed ? palette.secondary : palette.surface, borderColor: palette.border }, index < sections.length - 1 && styles.divider]}>
          <AppIcon name={item.icon} size={28} />
          <View style={styles.copy}><Text style={[styles.rowTitle, { color: palette.text }]}>{item.title}</Text><Text style={[styles.subtitle, { color: palette.muted }]}>{item.subtitle}</Text></View>
          <AppIcon name="chevron" size={20} />
        </Pressable>)}
      </View>
      {!preview ? <Pressable accessibilityRole="button" onPress={() => router.push('/forgot-password')} style={styles.accountAction}><Text style={{ color: palette.accent, fontSize: 15 }}>Change password</Text></Pressable> : null}
      {error ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{error}</Text> : null}
      <Pressable accessibilityRole="button" disabled={busy} onPress={() => { void run(async () => { await signOut(); router.replace('/'); }); }} style={[styles.accountAction, { opacity: busy ? 0.5 : 1 }]}><Text style={{ color: palette.error, fontSize: 15, fontWeight: '600' }}>{busy ? 'Logging out…' : preview ? 'Exit preview' : 'Log out'}</Text></Pressable>
    </ScrollView>
    <BottomNav active="profile" />
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { width: '100%', maxWidth: 480, alignSelf: 'center', padding: 22, paddingBottom: 32 },
  title: { fontSize: 30, fontWeight: '800', marginBottom: 26 },
  identity: { flexDirection: 'row', alignItems: 'center', gap: 18, marginBottom: 34 },
  avatar: { width: 76, height: 76, borderRadius: 38, alignItems: 'center', justifyContent: 'center' },
  initials: { fontSize: 26, fontWeight: '700' },
  name: { fontSize: 21, fontWeight: '700', lineHeight: 29 },
  accountAction: { minHeight: 50, justifyContent: 'center', alignItems: 'center', marginTop: 12 },
  group: { borderWidth: 1, borderRadius: 20, paddingHorizontal: 16, overflow: 'hidden' },
  row: { minHeight: 88, flexDirection: 'row', alignItems: 'center', gap: 16, paddingVertical: 18, paddingHorizontal: 3 },
  divider: { borderBottomWidth: StyleSheet.hairlineWidth },
  copy: { flex: 1, minWidth: 0 },
  rowTitle: { fontSize: 16, fontWeight: '600' },
  subtitle: { fontSize: 13, lineHeight: 19, marginTop: 4 },
});
