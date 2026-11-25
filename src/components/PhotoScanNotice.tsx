import { useRef } from 'react';
import { useDialogFocus } from '../hooks/useDialogFocus';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { typography } from '../theme/tokens';
import { ActivityIndicator, Modal, ScrollView, Pressable, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

export function PhotoScanNotice({ processing, notice, onDismiss }: { processing: boolean; notice: 'empty' | 'error' | null; onDismiss: () => void }) {
  const { palette } = useTheme();
  const reducedMotion = useReducedMotion();
  const dialogTitleRef = useRef<Text>(null);
  const showDialog = useDialogFocus(dialogTitleRef);
  return <Modal onShow={showDialog} visible={processing || notice !== null} transparent animationType={reducedMotion ? 'none' : 'fade'} onRequestClose={() => { if (!processing) onDismiss(); }}>
    <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.backdrop}><View accessibilityViewIsModal style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }]}>
      {processing && <ActivityIndicator color={palette.accent} size="large" />}
      <Text ref={dialogTitleRef} accessible accessibilityRole="header" style={[styles.title, { color: palette.text }]}>{processing ? 'Scanning ingredients…' : notice === 'empty' ? 'No ingredients found' : 'Couldn’t scan this photo'}</Text>
      <Text accessibilityLiveRegion="polite" style={[styles.body, { color: palette.muted }]}>{processing ? 'Please wait while we check your photo.' : notice === 'empty' ? 'Try a clear, well-lit photo of your food ingredients.' : 'Check your connection and try again.'}</Text>
      {!processing && <Pressable accessibilityRole="button" onPress={onDismiss} style={[styles.button, { backgroundColor: palette.buttonBackground }]}><Text style={styles.buttonText}>Try another photo</Text></Pressable>}
    </View></ScrollView>
  </Modal>;
}
const styles = StyleSheet.create({
  backdrop: { flexGrow: 1, alignItems: 'center', justifyContent: 'center', padding: 22, backgroundColor: 'rgba(0,0,0,0.65)' },
  card: { width: '100%', maxWidth: 420, borderWidth: 1, borderRadius: 16, padding: 24, gap: 18 }, title: { fontSize: typography.section, fontWeight: '700' }, body: { fontSize: typography.body, lineHeight: 22 },
  button: { minHeight: 52, borderRadius: 12, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16, paddingVertical: 14 }, buttonText: { color: '#FFF8ED', fontSize: typography.body, fontWeight: '700' },
});
