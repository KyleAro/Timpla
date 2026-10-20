import { Link } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { BrandMark } from '../components/BrandMark';
import { ThemePalette } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';

export default function SettingsScreen() {
  const { mode, palette, setThemeMode } = useTheme();
  const styles = makeStyles(palette);
  return (
    <SafeAreaView style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Link href="/profile" asChild><Pressable accessibilityRole="button" accessibilityLabel="Back to profile" style={styles.back}><AppIcon name="back" size={25} /></Pressable></Link>
          <BrandMark size={39} />
          <Text accessibilityRole="header" style={styles.title}>Settings</Text>
        </View>
        <View style={styles.appearance}>
          <Text style={styles.sectionTitle}>Appearance</Text>
          <View style={styles.segment}>
            {(['light', 'dark'] as const).map((value) => (
              <Pressable key={value} accessibilityRole="button" accessibilityLabel={`${value === 'light' ? 'Light' : 'Dark'} mode`} accessibilityState={{ selected: mode === value }} onPress={() => setThemeMode(value)} style={[styles.option, mode === value && styles.selectedOption]}>
                <AppIcon name={value === 'light' ? 'sun' : 'moon'} size={24} color={mode === value ? '#FFF8ED' : palette.text} />
                <Text style={[styles.optionText, mode === value && styles.selectedText]}>{value === 'light' ? 'Light' : 'Dark'}</Text>
              </Pressable>
            ))}
          </View>
          <Text style={styles.caption}>Applies across Timpla</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function makeStyles(p: ThemePalette) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: p.background },
    content: { padding: 22, width: '100%', maxWidth: 488, alignSelf: 'center' },
    header: { flexDirection: 'row', alignItems: 'center', gap: 11, marginBottom: 34 },
    back: { width: 40, minHeight: 46, alignItems: 'flex-start', justifyContent: 'center' },
    title: { color: p.text, fontSize: 27, fontWeight: '700', letterSpacing: -0.5 },
    appearance: { backgroundColor: p.surface, borderWidth: 1, borderColor: p.border, borderRadius: 19, padding: 18, marginBottom: 16 },
    sectionTitle: { color: p.text, fontSize: 22, fontWeight: '700', marginBottom: 18 },
    segment: { flexDirection: 'row', padding: 5, borderRadius: 16, borderWidth: 1, borderColor: p.border, backgroundColor: p.secondary },
    option: { flex: 1, minHeight: 54, borderRadius: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 },
    selectedOption: { backgroundColor: p.accent },
    optionText: { color: p.text, fontSize: 16, fontWeight: '600' },
    selectedText: { color: '#FFF8ED' },
    caption: { color: p.muted, fontSize: 13, textAlign: 'center', marginTop: 13 },
    row: { minHeight: 78, borderWidth: 1, borderColor: p.border, borderRadius: 18, backgroundColor: p.surface, flexDirection: 'row', alignItems: 'center', gap: 18, paddingHorizontal: 19, marginBottom: 12 },
    rowText: { color: p.text, fontSize: 16, fontWeight: '600', flex: 1 },
  });
}

