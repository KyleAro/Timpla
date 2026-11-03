import { router } from 'expo-router';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { BottomNav, useBottomNavPadding } from '../components/BottomNav';
import { useIngredientPhoto } from '../hooks/useIngredientPhoto';
import { ThemePalette } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';

export default function ScanScreen() {
  const { palette } = useTheme();
  const bottomPadding = useBottomNavPadding();
  const styles = makeStyles(palette);
  const { pick, busy, error } = useIngredientPhoto();

  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={styles.screen}>
      <AppHeader />
      <ScrollView contentContainerStyle={[styles.content, { paddingBottom: bottomPadding }]}>
        <View style={styles.intro}>
          <Text accessibilityRole="header" style={styles.title}>Scan your ingredients</Text>
          <Text style={styles.description}>Take a photo or choose one from your gallery. Timpla will identify the ingredients, then show recipe ideas from your recipe collection.</Text>
        </View>

        <View style={styles.actions}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Take a photo of your ingredients"
            accessibilityHint="Opens the camera so you can frame and capture your ingredients."
            disabled={busy}
            onPress={() => router.push('/live-scan')}
            style={({ pressed }) => [styles.actionCard, pressed && styles.pressed, busy && styles.disabled]}
          >
            <View style={[styles.iconBubble, { backgroundColor: palette.accent }]}><AppIcon name="camera" size={29} color="#FFF8ED" /></View>
            <View style={styles.actionCopy}>
              <Text style={styles.actionTitle}>Take a photo</Text>
              <Text style={styles.actionDescription}>Open the camera and capture what you have.</Text>
            </View>
            <AppIcon name="chevron" size={20} color={palette.muted} />
          </Pressable>

          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Upload a photo of your ingredients"
            accessibilityHint="Opens your photo library. The selected photo will be sent for ingredient detection."
            disabled={busy}
            onPress={() => { void pick('library'); }}
            style={({ pressed }) => [styles.actionCard, pressed && styles.pressed, busy && styles.disabled]}
          >
            <View style={[styles.iconBubble, { backgroundColor: palette.secondary }]}><AppIcon name="upload" size={27} color={palette.accent} /></View>
            <View style={styles.actionCopy}>
              <Text style={styles.actionTitle}>Upload a photo</Text>
              <Text style={styles.actionDescription}>Choose an existing photo from your gallery.</Text>
            </View>
            {busy ? <ActivityIndicator color={palette.accent} /> : <AppIcon name="chevron" size={20} color={palette.muted} />}
          </Pressable>
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
