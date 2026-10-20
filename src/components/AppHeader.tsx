import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';
import { BrandMark } from './BrandMark';
import { BrandWordmark } from './BrandWordmark';

export function AppHeader() {
  const { palette } = useTheme();
  return (
    <View style={[styles.background, { backgroundColor: palette.background }]}>
      <View style={[styles.header, { borderColor: palette.border }]}>
        <View style={styles.brand}><View style={styles.logoFrame}><BrandMark size={48} /></View><View style={styles.wordmarkFrame}><BrandWordmark /></View></View>
          <Pressable accessibilityRole="button" accessibilityLabel="Open help" onPress={() => router.push('/help')} style={[styles.help, { backgroundColor: palette.surface, borderColor: palette.border }]}>
            <AppIcon name="help" size={20} /><Text style={[styles.helpText, { color: palette.text }]}>Help</Text>
          </Pressable>
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  background: { width: '100%' },
  header: { width: '100%', maxWidth: 480, alignSelf: 'center', height: 76, paddingHorizontal: 20, paddingVertical: 12, gap: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderBottomWidth: StyleSheet.hairlineWidth },
  brand: { height: 48, flexDirection: 'row', alignItems: 'center', gap: 7, flexShrink: 1 },
  logoFrame: { width: 48, height: 48, alignItems: 'center', justifyContent: 'center' },
  // Anchor the wordmark to the logo frame's base instead of centering it vertically.
  wordmarkFrame: { height: 48, justifyContent: 'flex-end' },
  help: { height: 44, minWidth: 82, flexShrink: 0, paddingHorizontal: 12, borderRadius: 23, borderWidth: 1, flexDirection: 'row', gap: 6, alignItems: 'center', justifyContent: 'center' },
  helpText: { fontSize: 14, lineHeight: 20, includeFontPadding: false, textAlignVertical: 'center', fontWeight: '600' },
});




