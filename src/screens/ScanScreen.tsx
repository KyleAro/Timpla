import { router } from 'expo-router';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useCallback, useEffect, useRef, useState } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useIngredientPhoto } from '../hooks/useIngredientPhoto';
import { ThemePalette } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';
import { checkDetectorStatus } from '../services/detection';

export default function ScanScreen() {
  const { palette } = useTheme();
  const bottomPadding = useBottomNavPadding();
  const styles = makeStyles(palette);
  const { pick, busy, error } = useIngredientPhoto();
  const [scannerStatus, setScannerStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [scannerMessage, setScannerMessage] = useState('Waking the scanner on Render…');
  const healthRequest = useRef<AbortController | null>(null);
  const scannerOnline = scannerStatus === 'online';
  const scannerLight = scannerStatus === 'online' ? '#31B765' : scannerStatus === 'checking' ? '#E9B949' : '#D94A43';

  const checkScanner = useCallback(async () => {
    healthRequest.current?.abort();
    const controller = new AbortController();
    healthRequest.current = controller;
    setScannerStatus('checking');
    setScannerMessage('Waking the scanner on Render… this can take up to a minute.');
    const timeout = setTimeout(() => controller.abort(), 90_000);
    try {
      await checkDetectorStatus(controller.signal);
      setScannerStatus('online');
      setScannerMessage('Scanner is online and ready. Try taking or uploading a photo.');
    } catch (reason) {
      if (controller.signal.aborted && healthRequest.current !== controller) return;
      setScannerStatus('offline');
      setScannerMessage(reason instanceof Error && reason.name !== 'AbortError'
        ? `Scanner is not ready: ${reason.message}`
        : 'No response from the scanner yet. Retry the connection, then check Render logs.');
    } finally {
      clearTimeout(timeout);
      if (healthRequest.current === controller) healthRequest.current = null;
    }
  }, []);

  useEffect(() => {
    const startupCheck = setTimeout(() => { void checkScanner(); }, 0);
    return () => {
      clearTimeout(startupCheck);
      const activeRequest = healthRequest.current;
      healthRequest.current = null;
      activeRequest?.abort();
    };
  }, [checkScanner]);

  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={styles.screen}>
      <AppHeader />
      <ScrollView contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]}>
        <View style={styles.intro}>
          <Text accessibilityRole="header" style={styles.title}>Scan your ingredients</Text>
          <Text style={styles.description}>Check that the scanner is online, then scan your ingredients or upload a photo.</Text>
        </View>

        <View style={styles.actions}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Scan ingredients with the camera"
            accessibilityHint={scannerOnline ? 'Opens the camera to scan your ingredients.' : 'Available after the scanner is online.'}
            disabled={busy || !scannerOnline}
            onPress={() => router.push('/live-scan')}
            style={({ pressed }) => [styles.actionCard, pressed && styles.pressed, (busy || !scannerOnline) && styles.disabled]}
          >
            <View style={[styles.iconBubble, { backgroundColor: palette.accent }]}><AppIcon name="camera" size={29} color="#FFF8ED" /></View>
            <View style={styles.actionCopy}>
              <Text style={styles.actionTitle}>Scan ingredients</Text>
              <Text style={styles.actionDescription}>Open the camera and scan what you have.</Text>
            </View>
            <AppIcon name="chevron" size={20} color={palette.muted} />
          </Pressable>

          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Upload a photo of your ingredients"
            accessibilityHint={scannerOnline ? 'Choose an existing photo to scan.' : 'Available after the scanner is online.'}
            disabled={busy || !scannerOnline}
            onPress={() => { void pick('library'); }}
            style={({ pressed }) => [styles.actionCard, pressed && styles.pressed, (busy || !scannerOnline) && styles.disabled]}
          >
            <View style={[styles.iconBubble, { backgroundColor: palette.secondary }]}><AppIcon name="upload" size={27} color={palette.accent} /></View>
            <View style={styles.actionCopy}>
              <Text style={styles.actionTitle}>Upload a photo</Text>
              <Text style={styles.actionDescription}>Choose an existing photo from your gallery.</Text>
            </View>
            {busy ? <ActivityIndicator color={palette.accent} /> : <AppIcon name="chevron" size={20} color={palette.muted} />}
          </Pressable>
        </View>

        <View style={[styles.scannerStatus, { borderColor: scannerLight, backgroundColor: palette.surface }]}>
          <View style={styles.statusCopy}>
            <View style={styles.statusHeading}>
              {scannerStatus === 'checking' ? <ActivityIndicator size="small" color={scannerLight} /> : <View style={[styles.statusDot, { backgroundColor: scannerLight }]} />}
              <Text style={[styles.statusTitle, { color: palette.text }]}>{scannerStatus === 'checking' ? 'Waking scanner' : scannerStatus === 'online' ? 'Scanner available' : 'Scanner unavailable'}</Text>
            </View>
            <Text accessibilityLiveRegion="polite" style={[styles.statusMessage, { color: palette.muted }]}>{scannerMessage}</Text>
          </View>
          {scannerStatus === 'offline' && <Pressable accessibilityRole="button" onPress={() => void checkScanner()} style={({ pressed }) => [styles.statusButton, { borderColor: palette.border }, pressed && styles.pressed]}><Text style={[styles.statusButtonText, { color: palette.accent }]}>Wake / retry</Text></Pressable>}
        </View>

        {error ? <Text accessibilityRole="alert" style={styles.error}>{error}</Text> : null}
        <View style={styles.tip}>
          <AppIcon name="leaf" size={19} color={palette.oliveText} />
          <Text style={styles.tipText}>Use a clear, well-lit photo. You can review and edit detected ingredients before viewing recipes.</Text>
        </View>
      </ScrollView>
      <BottomNav active="scan" />
    </SafeAreaView>
  );
}

function makeStyles(palette: ThemePalette) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: palette.background },
    content: { width: '100%', maxWidth: 480, alignSelf: 'center', flexGrow: 1, paddingHorizontal: 20, paddingTop: 30, gap: 22 },
    intro: { gap: 10 },
    title: { color: palette.text, fontSize: 28, lineHeight: 34, fontWeight: '800', letterSpacing: -0.5 },
    description: { color: palette.muted, fontSize: 15, lineHeight: 22 },
    actions: { gap: 12 },
    scannerStatus: { minHeight: 78, flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, borderWidth: 1, borderRadius: 16 },
    statusCopy: { flex: 1, minWidth: 0, gap: 5 },
    statusHeading: { flexDirection: 'row', alignItems: 'center', gap: 8 },
    statusDot: { width: 9, height: 9, borderRadius: 5 },
    statusTitle: { fontSize: 15, fontWeight: '700' },
    statusMessage: { fontSize: 12, lineHeight: 17 },
    statusButton: { minWidth: 64, minHeight: 40, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 12, borderWidth: 1, borderRadius: 12 },
    statusButtonText: { fontSize: 14, fontWeight: '700' },
    actionCard: { minHeight: 104, flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 15, paddingVertical: 15, borderWidth: 1, borderColor: palette.border, borderRadius: 18, backgroundColor: palette.surface },
    iconBubble: { width: 54, height: 54, borderRadius: 27, alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
    actionCopy: { flex: 1, minWidth: 0, gap: 5 },
    actionTitle: { color: palette.text, fontSize: 17, lineHeight: 22, fontWeight: '700' },
    actionDescription: { color: palette.muted, fontSize: 13, lineHeight: 18 },
    pressed: { backgroundColor: palette.secondary, opacity: 0.88 },
    disabled: { opacity: 0.55 },
    error: { color: palette.error, fontSize: 14, lineHeight: 20 },
    tip: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, padding: 14, borderRadius: 15, backgroundColor: palette.olive },
    tipText: { color: palette.oliveText, flex: 1, fontSize: 13, lineHeight: 19 },
  });
}
