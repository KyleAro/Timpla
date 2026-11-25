import { typography } from '../theme/tokens';
import { router, useLocalSearchParams } from 'expo-router';
import { Fragment } from 'react';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import Svg, { Rect, Text as SvgText } from 'react-native-svg';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { scanDate } from './RecentsScreen';

export default function ScanDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { recentScans } = useCooking();
  const { palette } = useTheme();
  const scan = recentScans.find((item) => item.id === id);
  const back = () => router.canGoBack() ? router.back() : router.replace('/recents');
  const imageWidth = scan?.imageWidth ?? 4;
  const imageHeight = scan?.imageHeight ?? 3;
  const detections = scan?.detections ?? [];
  const hasImageDimensions = Boolean(scan?.imageWidth && scan?.imageHeight);
  const labelFontSize = imageWidth / 32;
  const labelHeight = labelFontSize * 1.5;
  const lineWidth = imageWidth / 220;
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <View style={styles.header}><Pressable accessibilityRole="button" accessibilityLabel="Back to recents" onPress={back} style={styles.back}><AppIcon name="back" size={25} /></Pressable><Text accessibilityRole="header" style={[styles.headerTitle, { color: palette.text }]}>Scan details</Text><View style={styles.back} /></View>
    <ScrollView contentContainerStyle={styles.content}>
      {!scan ? <Text style={[styles.body, { color: palette.muted }]}>Scan unavailable</Text> : <>
        <Text style={[styles.date, { color: palette.muted }]}>{scanDate(scan.createdAt)}</Text>
        <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Uploaded photo</Text>
        <View style={[styles.imageFrame, { aspectRatio: imageWidth / imageHeight, backgroundColor: palette.surface, borderColor: palette.border }]}>
          <Image source={{ uri: scan.photo }} accessibilityLabel="Original uploaded ingredient photo" resizeMode="contain" style={StyleSheet.absoluteFill} />
        </View>
        <Text accessibilityRole="header" style={[styles.section, styles.annotatedTitle, { color: palette.text }]}>Annotated image</Text>
        <View style={[styles.imageFrame, { aspectRatio: imageWidth / imageHeight, backgroundColor: palette.surface, borderColor: palette.border }]}>
          <Image source={{ uri: scan.photo }} accessibilityLabel={`Ingredient photo with ${detections.length} detection boxes`} resizeMode="contain" style={StyleSheet.absoluteFill} />
          {hasImageDimensions && detections.length > 0 && <Svg
            accessibilityLabel={`${detections.length} ingredient detection boxes`}
            width="100%"
            height="100%"
            viewBox={`0 0 ${imageWidth} ${imageHeight}`}
            preserveAspectRatio="xMidYMid meet"
            style={StyleSheet.absoluteFill}
            pointerEvents="none"
          >
            {detections.map((detection, index) => {
              const [rawX1, rawY1, rawX2, rawY2] = detection.bbox_xyxy;
              const x1 = Math.max(0, Math.min(imageWidth, rawX1));
              const y1 = Math.max(0, Math.min(imageHeight, rawY1));
              const x2 = Math.max(0, Math.min(imageWidth, rawX2));
              const y2 = Math.max(0, Math.min(imageHeight, rawY2));
              if (x2 <= x1 || y2 <= y1) return null;
              const color = detection.source_model?.toLowerCase().includes('produce') ? palette.oliveText : palette.accent;
              const label = `${detection.name} ${Math.round(detection.confidence * 100)}%`;
              const padding = labelFontSize * 0.45;
              const labelWidth = Math.min(imageWidth - x1, label.length * labelFontSize * 0.56 + padding * 2);
              const labelX = Math.max(0, Math.min(x1, imageWidth - labelWidth));
              const labelY = Math.max(0, y1 - labelHeight);
              return <Fragment key={`${detection.name}-${index}`}>
                <Rect x={x1} y={y1} width={x2 - x1} height={y2 - y1} stroke={color} strokeWidth={lineWidth} fill="none" />
                <Rect x={labelX} y={labelY} width={labelWidth} height={labelHeight} rx={labelHeight * 0.15} fill={color} />
                <SvgText x={labelX + padding} y={labelY + labelHeight * 0.72} fontSize={labelFontSize} fontWeight="600" fill="#FFFFFF">{label}</SvgText>
              </Fragment>;
            })}
          </Svg>}
        </View>
        <Text style={[styles.imageCaption, { color: palette.muted }]}>
          {detections.length ? `${detections.length} detection boxes · Green: produce · Orange: meat and other ingredients` : 'No detection boxes were saved for this scan.'}
        </Text>
        <Text accessibilityRole="header" style={[styles.section, { color: palette.text }]}>Ingredients</Text>
        {scan.ingredients.length ? <>
          <View style={[styles.ingredientRow, { borderColor: palette.border }]}><Text style={[styles.body, { color: palette.muted }]}>Ingredient</Text><Text style={[styles.body, { color: palette.muted }]}>Confidence</Text></View>
          {scan.ingredients.map((item) => <View key={item.name} style={[styles.ingredientRow, { borderColor: palette.border }]}><Text style={[styles.ingredient, { color: palette.text }]}>{item.name}</Text><Text style={[styles.confidence, { color: item.confidence === null ? palette.muted : palette.text }]}>{item.confidence === null ? 'Added manually' : `${Math.round(item.confidence * 100)}%`}</Text></View>)}
        </> : <Text style={[styles.body, { color: palette.muted }]}>No ingredients added</Text>}
        <Text style={[styles.dishLabel, { color: palette.muted }]}>Selected dish</Text>
        <Text style={[styles.dish, { color: palette.text }]}>{scan.selectedDish?.name ?? 'Not selected'}</Text>
      </>}
    </ScrollView>
  </SafeAreaView>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 }, header: { minHeight: 64, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', maxWidth: 480, alignSelf: 'center', paddingHorizontal: 12 }, back: { width: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' }, headerTitle: { fontSize: typography.title, fontWeight: '700' }, content: { width: '100%', maxWidth: 480, alignSelf: 'center', padding: 22, paddingBottom: 40 }, date: { fontSize: typography.label, marginBottom: 28 }, section: { fontSize: 23, fontWeight: '700', marginBottom: 15 }, annotatedTitle: { marginTop: 20 }, imageFrame: { width: '100%', borderWidth: 1, borderRadius: 16, overflow: 'hidden', marginBottom: 10 }, imageCaption: { fontSize: typography.label, lineHeight: 19, marginBottom: 20 }, ingredientRow: { minHeight: 54, paddingVertical: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 18, borderBottomWidth: StyleSheet.hairlineWidth }, ingredient: { fontSize: typography.body, flex: 1 }, confidence: { fontSize: typography.label, textAlign: 'right', flexShrink: 1 }, body: { fontSize: typography.body, lineHeight: 23 }, dishLabel: { fontSize: typography.body, marginTop: 32, marginBottom: 10 }, dish: { fontSize: 25, fontWeight: '700', marginBottom: 20 }, match: { padding: 20, borderRadius: 16, gap: 6 }, matchTitle: { fontSize: typography.section, fontWeight: '700' }, resultsButton: { marginTop: 28, minHeight: 54, borderWidth: 1, borderRadius: 16, alignItems: 'center', justifyContent: 'center' }, resultsText: { fontSize: typography.body, fontWeight: '600' },
});
