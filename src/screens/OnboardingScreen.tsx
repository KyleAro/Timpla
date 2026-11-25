import { Redirect, router } from 'expo-router';
import { useCameraPermissions } from 'expo-camera';
import { useMediaLibraryPermissions } from 'expo-image-picker';
import { useEffect, useRef, useState } from 'react';
import { AccessibilityInfo, Animated, Easing, Keyboard, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, useWindowDimensions, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../auth/AuthContext';
import { OnboardingSplitText } from '../components/OnboardingSplitText';
import { defaultPreferences, Diet } from '../data/account';
import { useTheme } from '../theme/ThemeContext';
import { typography } from '../theme/tokens';
import { saveAccountName, saveAccountPreferences } from '../services/account';
import { useCooking } from '../state/CookingContext';
import { storyDirection } from '../utils/onboardingNavigation';

const allergiesList = ['Peanuts', 'Tree nuts', 'Dairy', 'Eggs', 'Wheat', 'Soy', 'Shellfish', 'Fish', 'Sesame'];
const diets: Diet[] = ['No preference', 'Vegetarian', 'Halal'];
const lastStep = 11;
const headings = ['Hi…', 'I’m Timpla.', 'Your cooking companion.', 'Is this your first time here?', 'What should I call you?', '', 'Cook with what you have.', 'Who’s eating?', 'How do you eat?', 'Any allergies?', 'Any dislikes?', 'You’re ready.'];

export default function OnboardingScreen({ replay = false }: { replay?: boolean }) {
  const { session, recovery, preview, onboardingComplete, completeOnboarding } = useAuth();
  const { palette } = useTheme();
  const { reloadAccount } = useCooking();
  const { width } = useWindowDimensions();
  const [step, setStep] = useState(() => !replay && session && !onboardingComplete ? 4 : 0);
  const [name, setName] = useState(() => !replay && session?.user.user_metadata?.full_name || '');
  const [people, setPeople] = useState(2);
  const [diet, setDiet] = useState<Diet>('No preference');
  const [allergies, setAllergies] = useState<string[]>([]);
  const [dislikes, setDislikes] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [reduceMotion, setReduceMotion] = useState<boolean | null>(null);
  const [progress] = useState(() => new Animated.Value(0));
  const [ready, setReady] = useState(false);
  const [cameraPermission, requestCameraPermission] = useCameraPermissions();
  const [photosPermission, requestPhotosPermission] = useMediaLibraryPermissions();
  const [permissionBusy, setPermissionBusy] = useState<'camera' | 'photos' | null>(null);
  const [permissionError, setPermissionError] = useState('');
  const transitioning = useRef(false);
  const touchStart = useRef<{ x: number; y: number } | null>(null);
  const touchBlocked = useRef(false);

  useEffect(() => {
    let active = true;
    void AccessibilityInfo.isReduceMotionEnabled().then(value => { if (active) setReduceMotion(value); }).catch(() => { if (active) setReduceMotion(false); });
    const subscription = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduceMotion);
    return () => { active = false; subscription.remove(); };
  }, []);

  useEffect(() => {
    if (reduceMotion === null) return;
    let active = true;
    transitioning.current = false;
    progress.setValue(0);
    const entrance = Animated.timing(progress, { toValue: 1, duration: reduceMotion ? 0 : 480, easing: Easing.bezier(0.4, 0, 0.2, 1), useNativeDriver: true });
    const hold = step === 0 ? 1100 : step === 1 ? 1500 : step === 5 ? 1800 : 0;
    const animation = hold ? Animated.sequence([
      entrance,
      Animated.delay(reduceMotion ? 900 : hold),
      Animated.timing(progress, { toValue: 2, duration: reduceMotion ? 0 : 360, easing: Easing.bezier(0.4, 0, 0.2, 1), useNativeDriver: true }),
    ]) : entrance;
    const frame = requestAnimationFrame(() => animation.start(({ finished }) => {
      if (active && finished && hold) { progress.setValue(0); setStep(current => current + 1); }
    }));
    const readyTimer = step === 2 ? setTimeout(() => setReady(true), reduceMotion ? 0 : 1300) : undefined;
    return () => { active = false; cancelAnimationFrame(frame); clearTimeout(readyTimer); animation.stop(); };
  }, [step, progress, reduceMotion]);

  function changeStep(target: number) {
    if (transitioning.current || busy || target < 0 || target > lastStep) return;
    Keyboard.dismiss();
    transitioning.current = true;
    Animated.timing(progress, { toValue: 2, duration: reduceMotion ? 0 : 340, easing: Easing.bezier(0.4, 0, 0.2, 1), useNativeDriver: true }).start(({ finished }) => {
      if (!finished) { transitioning.current = false; return; }
      progress.setValue(0);
      if (target === 2) setReady(false);
      setStep(target);
    });
  }

  async function finish() {
    if (busy) return;
    if (replay) { if (router.canGoBack()) router.back(); else router.replace('/settings'); return; }
    setBusy(true);
    setError('');
    try {
      const preferences = { ...defaultPreferences, people, diet, allergies,
        exclusions: dislikes.split(',').map(item => item.trim()).filter(Boolean) };
      if (session?.user.email_confirmed_at) {
        if (name.trim()) await saveAccountName(session.user.id, name.trim());
        await saveAccountPreferences(session.user.id, preferences);
      }
      await completeOnboarding(name.trim(), preferences);
      if (session?.user.email_confirmed_at) reloadAccount();
      router.replace('/home');
    } catch {
      setError('Couldn’t save your preferences. Please try again.');
      setBusy(false);
    }
  }

  function next() {
    if (step === lastStep) { void finish(); return; }
    if (step === 3 && !replay) return;
    if (step === 2 && !ready) return;
    changeStep(step + 1);
  }
  function previous() {
    if (step === 0) return;
    changeStep(step === 6 ? 4 : step === 4 && session && !replay ? 3 : step - 1);
  }
  function blockTouch() { touchBlocked.current = true; }
  function toggleAllergy(item: string) {
    setAllergies(current => current.includes(item) ? current.filter(value => value !== item) : [...current, item]);
  }
  async function askPermission(kind: 'camera' | 'photos') {
    if (permissionBusy) return;
    setPermissionBusy(kind);
    setPermissionError('');
    try {
      if (kind === 'camera') await requestCameraPermission();
      else await requestPhotosPermission();
    } catch {
      setPermissionError('Could not request access. You can try again when you scan or upload.');
    } finally {
      setPermissionBusy(null);
    }
  }
  function chip(label: string, selected: boolean, onPress: () => void) {
    return <Pressable key={label} onTouchStart={blockTouch} accessibilityRole="button" accessibilityState={{ selected }} onPress={onPress}
      style={[styles.chip, { borderColor: selected ? palette.accent : palette.border, backgroundColor: selected ? palette.olive : palette.surface }]}>
      <Text style={[styles.bodyText, { color: palette.text }]}>{label}</Text>
    </Pressable>;
  }
  function handleTouchEnd(x: number, y: number) {
    const start = touchStart.current;
    touchStart.current = null;
    const blocked = touchBlocked.current;
    touchBlocked.current = false;
    if (!start || blocked || busy || reduceMotion === null || step === 0 || step === 1 || step === 5) return;
    const direction = storyDirection(start, { x, y }, width, blocked);
    if (direction === -1) previous();
    if (direction === 1) next();
  }

  if (session && recovery) return <Redirect href="/reset-password" />;
  if (!replay && onboardingComplete && (preview || session?.user.email_confirmed_at)) return <Redirect href="/home" />;
  const heading = step === 5 ? `Hi, ${name.trim() || 'there'}.` : headings[step];
  const setupStep = step >= 4 ? step - 3 : 0;
  const canNavigate = ![0, 1, 5].includes(step);
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      {canNavigate && <View style={styles.topRow}>
        <View style={styles.progress} accessibilityLabel={step >= 4 ? `Step ${setupStep} of 8` : 'Introduction'}>
          {Array.from({ length: 8 }, (_, index) => <View key={index} style={[styles.progressSegment, { backgroundColor: step >= 4 && index < setupStep ? palette.accent : palette.border }]} />)}
        </View>
        {step === 6 && <Pressable accessibilityRole="button" accessibilityLabel="Skip permissions for now" onPress={() => changeStep(7)} style={styles.topSkip}>
          <Text style={[styles.skipText, { color: palette.accent }]}>Skip</Text>
        </Pressable>}
      </View>}
      <ScrollView keyboardShouldPersistTaps="handled" keyboardDismissMode="on-drag" contentContainerStyle={styles.scroll}
        onTouchStart={event => { touchStart.current = { x: event.nativeEvent.pageX, y: event.nativeEvent.pageY }; }}
        onTouchCancel={() => { touchStart.current = null; touchBlocked.current = false; }}
        onTouchEnd={event => handleTouchEnd(event.nativeEvent.pageX, event.nativeEvent.pageY)}>
        <Animated.View collapsable={false} style={[styles.content, {
          opacity: progress.interpolate({ inputRange: [0, 1, 2], outputRange: [0, 1, 0] }),
          transform: [{ translateY: reduceMotion ? 0 : progress.interpolate({ inputRange: [0, 1, 2], outputRange: [6, 0, -6] }) }],
        }]}>
          {reduceMotion !== null && <OnboardingSplitText key={heading} text={heading} heading style={{ ...styles.title, color: palette.text }} reduceMotion={reduceMotion} />}
          {step === 2 && ready && <OnboardingSplitText text="Ready to cook?" style={{ ...styles.subtitle, color: palette.muted }} reduceMotion={Boolean(reduceMotion)} />}
          {step === 3 && <View style={styles.choices} onTouchStart={blockTouch}>
            <Text style={[styles.bodyText, { color: palette.muted }]}>Choose how to start. You can explore without an account.</Text>
            {replay || session ? <Pressable accessibilityRole="button" onPress={() => changeStep(4)} style={[styles.choice, { backgroundColor: palette.buttonBackground }]}><Text style={styles.choicePrimary}>Continue to setup  ›</Text></Pressable> : <>
              <Pressable accessibilityRole="button" onPress={() => router.push('/sign-up')} style={[styles.choice, { backgroundColor: palette.buttonBackground }]}><Text style={styles.choicePrimary}>Yes, create an account  ›</Text></Pressable>
              <Pressable accessibilityRole="button" onPress={() => router.push('/login')} style={[styles.choice, { backgroundColor: palette.surface, borderColor: palette.border, borderWidth: 1 }]}><Text style={[styles.choiceText, { color: palette.text }]}>I have an account  ›</Text></Pressable>
              <Pressable accessibilityRole="button" onPress={() => changeStep(4)} style={styles.guest}><Text style={[styles.bodyText, { color: palette.accent }]}>Continue as guest</Text></Pressable>
            </>}
          </View>}
          {step === 4 && <View onTouchStart={blockTouch}><TextInput accessibilityLabel="Your name" placeholder="Your name" placeholderTextColor={palette.muted} value={name}
            onChangeText={setName} maxLength={40} autoComplete="given-name" autoCapitalize="words" returnKeyType="done"
            style={[styles.input, { color: palette.text, borderColor: palette.border, backgroundColor: palette.surface }]} /></View>}
          {step === 6 && <>
            <Text style={[styles.bodyText, styles.body, { color: palette.muted }]}>Scan ingredients or upload a photo. Timpla finds Filipino recipes that fit what you have.</Text>
            <View style={styles.permissionChoices} onTouchStart={blockTouch}>
              <Pressable accessibilityRole="button" accessibilityLabel={cameraPermission?.granted ? 'Camera access allowed' : 'Allow camera access'}
                accessibilityState={{ disabled: Boolean(cameraPermission?.granted || permissionBusy) }} disabled={Boolean(cameraPermission?.granted || permissionBusy)}
                onPress={() => void askPermission('camera')}
                style={[styles.permissionChoice, { backgroundColor: palette.surface, borderColor: palette.border }]}>
                <Text style={[styles.choiceText, { color: palette.text }]}>{cameraPermission?.granted ? 'Camera ready ✓' : permissionBusy === 'camera' ? 'Requesting camera…' : 'Allow camera'}</Text>
                <Text style={[styles.permissionDetail, { color: palette.muted }]}>For scanning ingredients</Text>
              </Pressable>
              <Pressable accessibilityRole="button" accessibilityLabel={photosPermission?.granted ? 'Photo access allowed' : 'Allow photo access'}
                accessibilityState={{ disabled: Boolean(photosPermission?.granted || permissionBusy) }} disabled={Boolean(photosPermission?.granted || permissionBusy)}
                onPress={() => void askPermission('photos')}
                style={[styles.permissionChoice, { backgroundColor: palette.surface, borderColor: palette.border }]}>
                <Text style={[styles.choiceText, { color: palette.text }]}>{photosPermission?.granted ? 'Photos ready ✓' : permissionBusy === 'photos' ? 'Requesting photos…' : 'Allow photos'}</Text>
                <Text style={[styles.permissionDetail, { color: palette.muted }]}>For choosing an image to upload</Text>
              </Pressable>
              {!!permissionError && <Text accessibilityRole="alert" style={[styles.permissionDetail, { color: palette.error }]}>{permissionError}</Text>}
              <Text style={[styles.permissionDetail, { color: palette.muted, textAlign: 'center' }]}>You can allow access later when you scan. Upload may work without photo access.</Text>
            </View>
          </>}
          {step === 7 && <View style={styles.servings} onTouchStart={blockTouch}>
            <Text style={[styles.bodyText, { color: palette.muted }]}>Portions per meal</Text>
            <View style={styles.counter}>
              <Pressable accessibilityRole="button" accessibilityLabel="Fewer servings" onPress={() => setPeople(value => Math.max(1, value - 1))} style={styles.stepper}><Text style={[styles.counterText, { color: palette.text }]}>−</Text></Pressable>
              <Text accessibilityLabel={`${people} servings`} style={[styles.counterText, { color: palette.text }]}>{people}</Text>
              <Pressable accessibilityRole="button" accessibilityLabel="More servings" onPress={() => setPeople(value => Math.min(20, value + 1))} style={styles.stepper}><Text style={[styles.counterText, { color: palette.text }]}>+</Text></Pressable>
            </View>
          </View>}
          {step === 8 && <><Text style={[styles.bodyText, styles.body, { color: palette.muted }]}>Choose a cooking preference.</Text><View style={styles.chips}>{diets.map(item => chip(item, diet === item, () => setDiet(item)))}</View></>}
          {step === 9 && <><Text style={[styles.bodyText, styles.body, { color: palette.muted }]}>We’ll leave these ingredients out of your recipe matches.</Text><View style={styles.chips}>{allergiesList.map(item => chip(item, allergies.includes(item), () => toggleAllergy(item)))}</View></>}
          {step === 10 && <><Text style={[styles.bodyText, styles.body, { color: palette.muted }]}>Foods you simply don’t like. Separate multiple foods with commas.</Text>
            <View onTouchStart={blockTouch}><TextInput accessibilityLabel="Foods you dislike, separated by commas" placeholder="e.g. mushrooms, okra" placeholderTextColor={palette.muted}
              value={dislikes} onChangeText={setDislikes} style={[styles.input, { color: palette.text, borderColor: palette.border, backgroundColor: palette.surface }]} /></View></>}
          {step === 11 && <View style={styles.summary}>
            <Text style={[styles.bodyText, { color: palette.muted }]}>{people} {people === 1 ? 'serving' : 'servings'} · {diet}</Text>
            <Text style={[styles.bodyText, { color: palette.muted }]}>{allergies.length ? `Avoid ${allergies.join(', ')}` : 'No allergies selected'}</Text>
            {!!dislikes.trim() && <Text style={[styles.bodyText, { color: palette.muted }]}>Skip {dislikes.trim()}</Text>}
            <Text style={[styles.bodyText, { color: palette.text, marginTop: 22 }]}>Your next meal starts with a scan.</Text>
          </View>}
        </Animated.View>
      </ScrollView>
      {canNavigate && <View style={styles.footer}>
        {!!error && <Text accessibilityRole="alert" style={[styles.bodyText, { color: palette.error }]}>{error}</Text>}
        {step !== 3 && <Text style={[styles.hint, { color: palette.muted }]}>Tap either side or swipe to move</Text>}
        <View style={styles.nav}>
          <Pressable accessibilityRole="button" accessibilityLabel="Previous step" accessibilityState={{ disabled: step === 0 }} disabled={step === 0} onPress={previous}
            style={[styles.navHalf, { borderColor: palette.border }]}><Text style={[styles.navText, { color: palette.text }]}>‹  Back</Text></Pressable>
          {step !== 3 && <Pressable accessibilityRole="button" accessibilityLabel={step === lastStep ? 'Start cooking' : 'Next step'} accessibilityState={{ disabled: busy }} disabled={busy} onPress={next}
            style={[styles.navHalf, { backgroundColor: palette.buttonBackground }]}><Text style={styles.choicePrimary}>{step === lastStep ? 'Start cooking' : 'Next  ›'}</Text></Pressable>}
        </View>
      </View>}
    </KeyboardAvoidingView>
  </SafeAreaView>;
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  topRow: { minHeight: 56, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 28, gap: 12 },
  progress: { flex: 1, flexDirection: 'row', gap: 5 },
  progressSegment: { flex: 1, height: 4, borderRadius: 4 },
  topSkip: { minWidth: 52, minHeight: 48, alignItems: 'center', justifyContent: 'center' },
  skipText: { fontSize: typography.body, fontWeight: '700' },
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 28 },
  content: { width: '100%', maxWidth: 390, alignSelf: 'center', paddingVertical: 30 },
  title: { fontSize: 34, lineHeight: 42, fontWeight: '700', letterSpacing: -0.8, textAlign: 'center' },
  subtitle: { fontSize: typography.section, lineHeight: 28, textAlign: 'center', marginTop: 20 },
  body: { marginTop: 20 },
  bodyText: { fontSize: typography.body, lineHeight: 25, textAlign: 'center' },
  input: { borderWidth: 1, borderRadius: 14, minHeight: 56, padding: 16, marginTop: 28, fontSize: typography.subtitle },
  choices: { marginTop: 32, gap: 12 },
  choice: { minHeight: 58, borderRadius: 14, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 16 },
  choicePrimary: { color: '#FFFFFF', fontSize: typography.body, fontWeight: '700', textAlign: 'center' },
  choiceText: { fontSize: typography.body, fontWeight: '700', textAlign: 'center' },
  guest: { minHeight: 52, alignItems: 'center', justifyContent: 'center' },
  permissionChoices: { marginTop: 30, gap: 12 },
  permissionChoice: { minHeight: 72, borderWidth: 1, borderRadius: 14, justifyContent: 'center', alignItems: 'center', padding: 12 },
  permissionDetail: { fontSize: typography.label, lineHeight: 20 },
  servings: { marginTop: 30, gap: 18 },
  counter: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 24 },
  counterText: { fontSize: typography.title, fontWeight: '700' },
  stepper: { minHeight: 52, minWidth: 52, alignItems: 'center', justifyContent: 'center' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 10, marginTop: 24 },
  chip: { borderWidth: 1, borderRadius: 24, paddingHorizontal: 16, paddingVertical: 12, minHeight: 48 },
  summary: { gap: 12, marginTop: 26 },
  footer: { width: '100%', maxWidth: 446, alignSelf: 'center', paddingHorizontal: 28, paddingBottom: 14 },
  hint: { fontSize: typography.caption, textAlign: 'center', marginBottom: 10 },
  nav: { flexDirection: 'row', gap: 12 },
  navHalf: { flex: 1, minHeight: 56, borderWidth: 1, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  navText: { fontSize: typography.body, fontWeight: '700' },
});
