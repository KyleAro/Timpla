import { ActivityIndicator, Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

export function PhotoScanNotice({ processing, notice, onDismiss }: { processing: boolean; notice: 'empty' | 'error' | null; onDismiss: () => void }) {
  const { palette } = useTheme();
  return <Modal visible={processing || notice !== null} transparent animationType="fade" onRequestClose={() => { if (!processing) onDismiss(); }}>
    <View style={styles.backdrop}><View accessibilityViewIsModal style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}>
      {processing && <ActivityIndicator color={palette.accent} size="large" />}
      <Text accessibilityRole="header" style={[styles.title, { color: palette.text }]}>{processing ? 'Scanning ingredients…' : notice === 'empty' ? 'No ingredients found' : 'Couldn’t scan this photo'}</Text>
      <Text accessibilityLiveRegion="polite" style={[styles.body, { color: palette.muted }]}>{processing ? 'Please wait while we check your photo.' : notice === 'empty' ? 'Try a clear, well-lit photo of your food ingredients.' : 'Check your connection and try again.'}</Text>
      {!processing && <Pressable accessibilityRole="button" onPress={onDismiss} style={[styles.button, { backgroundColor: palette.accent }]}><Text style={styles.buttonText}>Try another photo</Text></Pressable>}
    </View></View>
  </Modal>;
}
const styles = StyleSheet.create({
  backdrop: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 22, backgroundColor: 'rgba(0,0,0,0.65)' },
  card: { width: '100%', maxWidth: 420, borderWidth: 1, borderRadius: 20, padding: 24, gap: 18 }, title: { fontSize: 21, fontWeight: '700' }, body: { fontSize: 15, lineHeight: 22 },
  button: { minHeight: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16 }, buttonText: { color: '#FFF8ED', fontSize: 15, fontWeight: '700' },
});
