import { router } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useTheme } from '../theme/ThemeContext';

const pantry = ['Egg', 'Chicken breast', 'Soy sauce', 'Sayote'];

const suggestions = [
  {
    id: 'ginisang-sayote-chicken-egg',
    name: 'Ginisang Sayote with Chicken and Egg',
    uses: ['Egg', 'Chicken breast', 'Soy sauce', 'Sayote'],
    description: 'Cook the chicken and sayote together, season with soy sauce, then add egg.',
    steps: [
      'Slice the chicken and sayote. Beat the egg in a small bowl.',
      'Cook the chicken through in a pan, then add sayote and soy sauce.',
      'When the sayote is tender, add egg and cook until set.',
    ],
    left: '',
  },
  {
    id: 'tortang-sayote-chicken',
    name: 'Tortang Sayote with Chicken',
    uses: ['Egg', 'Chicken breast', 'Sayote'],
    description: 'Combine cooked chicken and shredded sayote with egg, then pan-cook.',
    steps: [
      'Shred the sayote and cut the chicken into small pieces.',
      'Cook the chicken through, then mix it with sayote and beaten egg.',
      'Cook the mixture in a pan until set and cooked through.',
    ],
    left: 'Soy sauce left for another dish',
  },
  {
    id: 'chicken-sayote-soy-sauce',
    name: 'Chicken and Sayote in Soy Sauce',
    uses: ['Chicken breast', 'Sayote', 'Soy sauce'],
    description: 'A simple pan-cooked option built around chicken, sayote, and soy sauce.',
    steps: [
      'Slice the chicken and sayote into manageable pieces.',
      'Cook the chicken through in a pan, then add sayote and soy sauce.',
      'Cook together until the sayote is tender and the chicken is fully cooked.',
    ],
    left: 'Egg left for another dish',
  },
];

export default function SuggestionsPreviewScreen() {
  const { palette } = useTheme();
  const [expanded, setExpanded] = useState<string | null>(null);
  const styles = makeStyles(palette);

  return (
    <SafeAreaView edges={['top', 'left', 'right', 'bottom']} style={styles.screen}>
      <View style={styles.header}>
        <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={() => router.back()} style={styles.back}>
          <AppIcon name="back" size={23} color={palette.text} />
        </Pressable>
        <Text accessibilityRole="header" style={styles.headerTitle}>Your ingredients</Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.overline}>SAMPLE INGREDIENTS</Text>
        <View style={styles.pantry}>
          {pantry.map(item => <View key={item} style={styles.pantryChip}><Text style={styles.pantryText}>{item}</Text></View>)}
        </View>

        <View style={styles.headingRow}>
          <Text accessibilityRole="header" style={styles.heading}>What you can make</Text>
          <View style={styles.badge}><Text style={styles.badgeText}>AI IDEAS</Text></View>
        </View>
        <Text style={styles.subheading}>Flexible suggestions using what you have</Text>

        {suggestions.map((item, index) => {
          const isOpen = expanded === item.id;
          return (
            <View key={item.id} style={styles.card}>
              <View style={styles.cardTop}>
                <View style={styles.ideaTag}><Text style={styles.ideaTagText}>TIMPLA IDEA</Text></View>
                <Text style={styles.optionNumber}>OPTION {index + 1}</Text>
              </View>
              <Text style={styles.cardTitle}>{item.name}</Text>
              <Text style={styles.usesLabel}>Uses these ingredients</Text>
              <View style={styles.usedChips}>
                {item.uses.map(ingredient => <View key={ingredient} style={styles.usedChip}><Text style={styles.usedChipText}>{ingredient}</Text></View>)}
              </View>
              <Text style={styles.description}>{item.description}</Text>
              {item.left ? <View style={styles.leftover}><AppIcon name="leaf" size={13} color={palette.accent} /><Text style={styles.leftoverText}>{item.left}</Text></View> : <View style={styles.allUsed}><AppIcon name="check" size={13} color={palette.oliveText} /><Text style={styles.allUsedText}>Uses all 4 ingredients</Text></View>}
              {isOpen ? (
                <View style={styles.steps}>
                  <Text style={styles.stepsTitle}>Simple steps</Text>
                  {item.steps.map((step, stepIndex) => <View key={step} style={styles.stepRow}><Text style={styles.stepNumber}>{stepIndex + 1}</Text><Text style={styles.stepText}>{step}</Text></View>)}
                </View>
              ) : null}
              <Pressable accessibilityRole="button" accessibilityState={{ expanded: isOpen }} onPress={() => setExpanded(isOpen ? null : item.id)} style={styles.viewButton}>
                <Text style={styles.viewButtonText}>{isOpen ? 'Hide steps' : 'View steps'}</Text>
                <AppIcon name="chevron" size={15} color={palette.accent} />
              </Pressable>
            </View>
          );
        })}

        <View style={styles.disclaimer}>
          <AppIcon name="help" size={17} color={palette.muted} />
          <Text style={styles.disclaimerText}>Design preview with sample suggestions. AI ideas are not tested recipes; check steps and cook meat thoroughly.</Text>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Your actual scanned ingredients will appear here.</Text>
        <Pressable accessibilityRole="button" onPress={() => router.replace('/scan')} style={({ pressed }) => [styles.rescan, pressed && styles.rescanPressed]}>
          <Text style={styles.rescanText}>Try a scan</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

function makeStyles(palette: ReturnType<typeof useTheme>['palette']) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: palette.background },
    header: { minHeight: 52, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 18, gap: 14 },
    back: { width: 36, height: 40, alignItems: 'flex-start', justifyContent: 'center' },
    headerTitle: { color: palette.text, fontSize: 19, fontWeight: '700', flex: 1 },
    headerSpacer: { width: 24 },
    content: { paddingHorizontal: 20, paddingTop: 15, paddingBottom: 24, gap: 0 },
    overline: { color: palette.muted, fontSize: 10, fontWeight: '800', letterSpacing: 1.1, marginBottom: 9 },
    pantry: { flexDirection: 'row', flexWrap: 'wrap', gap: 7, marginBottom: 27 },
    pantryChip: { backgroundColor: palette.chip, borderColor: palette.border, borderWidth: 1, borderRadius: 20, paddingHorizontal: 11, paddingVertical: 7 },
    pantryText: { color: palette.text, fontSize: 12, fontWeight: '600' },
    headingRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
    heading: { color: palette.text, fontSize: 22, fontWeight: '800', letterSpacing: -0.45, flexShrink: 1 },
    badge: { backgroundColor: palette.accent, borderRadius: 13, paddingHorizontal: 9, paddingVertical: 6 },
    badgeText: { color: '#FFF8ED', fontSize: 9, fontWeight: '900', letterSpacing: 0.55 },
    subheading: { color: palette.muted, fontSize: 12, marginTop: 6, marginBottom: 13 },
    card: { backgroundColor: palette.surface, borderColor: palette.border, borderWidth: 1, borderRadius: 17, padding: 14, marginBottom: 11 },
    cardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
    ideaTag: { backgroundColor: palette.secondary, borderRadius: 13, paddingHorizontal: 9, paddingVertical: 5 },
    ideaTagText: { color: palette.accent, fontSize: 9, fontWeight: '900', letterSpacing: 0.65 },
    optionNumber: { color: palette.muted, fontSize: 9, fontWeight: '700', letterSpacing: 0.6 },
    cardTitle: { color: palette.text, fontSize: 16, fontWeight: '700', lineHeight: 21, marginBottom: 9 },
    usesLabel: { color: palette.muted, fontSize: 10, fontWeight: '700', marginBottom: 6 },
    usedChips: { flexDirection: 'row', flexWrap: 'wrap', gap: 5, marginBottom: 8 },
    usedChip: { backgroundColor: palette.chip, borderRadius: 12, paddingHorizontal: 8, paddingVertical: 5 },
    usedChipText: { color: palette.text, fontSize: 10, fontWeight: '600' },
    description: { color: palette.muted, fontSize: 12, lineHeight: 17, marginBottom: 9 },
    leftover: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', gap: 5, backgroundColor: palette.secondary, borderRadius: 13, paddingHorizontal: 8, paddingVertical: 5 },
    leftoverText: { color: palette.accent, fontSize: 10, fontWeight: '600' },
    allUsed: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', gap: 5, backgroundColor: palette.olive, borderRadius: 13, paddingHorizontal: 8, paddingVertical: 5 },
    allUsedText: { color: palette.oliveText, fontSize: 10, fontWeight: '600' },
    steps: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: palette.border, marginTop: 12, paddingTop: 11, gap: 9 },
    stepsTitle: { color: palette.text, fontSize: 13, fontWeight: '700', marginBottom: 1 },
    stepRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8 },
    stepNumber: { width: 19, height: 19, borderRadius: 10, overflow: 'hidden', backgroundColor: palette.secondary, color: palette.accent, fontSize: 10, fontWeight: '800', textAlign: 'center', textAlignVertical: 'center', paddingTop: 2 },
    stepText: { color: palette.muted, flex: 1, fontSize: 11, lineHeight: 16 },
    viewButton: { flexDirection: 'row', alignSelf: 'flex-end', alignItems: 'center', gap: 2, minHeight: 37, paddingLeft: 10, marginTop: 4 },
    viewButtonText: { color: palette.accent, fontSize: 11, fontWeight: '700' },
    disclaimer: { flexDirection: 'row', gap: 8, alignItems: 'flex-start', paddingHorizontal: 2, paddingTop: 4, paddingBottom: 12 },
    disclaimerText: { color: palette.muted, flex: 1, fontSize: 10, lineHeight: 15 },
    footer: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: palette.border, backgroundColor: palette.background, paddingHorizontal: 20, paddingTop: 10, paddingBottom: 5, minHeight: 66, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
    footerText: { color: palette.muted, fontSize: 10, lineHeight: 14, flex: 1 },
    rescan: { minHeight: 42, paddingHorizontal: 18, borderRadius: 22, backgroundColor: palette.accent, alignItems: 'center', justifyContent: 'center' },
    rescanPressed: { backgroundColor: palette.accentPressed },
    rescanText: { color: '#FFF8ED', fontSize: 12, fontWeight: '700' },
  });
}
