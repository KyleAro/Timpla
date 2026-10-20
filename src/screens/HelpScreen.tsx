import { router } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useTheme } from '../theme/ThemeContext';

const tips = [
  ['Add ingredients', 'Tap the center Scan button to take or upload a photo. You can also choose Add manually on Home.'],
  ['Check your list', 'Review your photo, add ingredient names, and edit or uncheck items before continuing. Automatic detection is still being built.'],
  ['Recent photos', 'Open Recents to revisit photos from this session. History currently resets when the app restarts.'],
  ['Profile and appearance', 'Open Profile to change your name, servings, and preferences. Settings & appearance contains the light and dark themes.'],
];
export default function HelpScreen() {
  const { palette } = useTheme();
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}><Pressable accessibilityRole="button" accessibilityLabel="Close help" onPress={() => router.canGoBack() ? router.back() : router.replace('/home')} style={styles.back}><AppIcon name="back" /></Pressable><Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>Help</Text></View>
    <ScrollView contentContainerStyle={styles.content}>{tips.map(([title, text]) => <View key={title} style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}><Text style={[styles.heading, { color: palette.text }]}>{title}</Text><Text style={[styles.body, { color: palette.muted }]}>{text}</Text></View>)}</ScrollView>
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 16, minHeight: 72, gap: 8 },
  back: { width: 48, height: 48, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 27, fontWeight: '700' },
  content: { width: '100%', maxWidth: 480, alignSelf: 'center', padding: 20, gap: 14 },
  card: { padding: 20, borderWidth: 1, borderRadius: 18 },
  heading: { fontSize: 17, fontWeight: '700', marginBottom: 8 },
  body: { fontSize: 15, lineHeight: 23 },
});
