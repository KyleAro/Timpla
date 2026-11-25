import { Stack, router, usePathname } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { CookingProvider, useCooking } from '../state/CookingContext';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { AuthProvider, useAuth } from '../auth/AuthContext';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { useAuthAction } from '../auth/useAuthAction';
import { useSwipeBack } from '../hooks/useSwipeBack';

function goBack() {
  if (router.canGoBack()) router.back();
}

const privateScreens = ['onboarding', 'home', 'settings', 'scan', 'scan-details', 'saved-recipes', 'reverse-cooking', 'recipes', 'recipe', 'recents', 'profile', 'profile-details', 'photo', 'live-scan', 'ingredients', 'explore', 'cooking-preferences', 'allergies', 'suggestions-preview', 'recommendations'] as const;

function AppStack() {
  const { mode, palette } = useTheme();
  const pathname = usePathname();
  const { session, loading, recovery, preview, onboardingComplete, signOut } = useAuth();
  const { accountLoading, accountError, reloadAccount } = useCooking();
  const { busy, error, run } = useAuthAction();
  const cameraOpen = pathname === '/live-scan' || pathname === '/photo';
  const swipeBack = useSwipeBack(!['/', '/onboarding', '/ingredients', '/recents'].includes(pathname), goBack);
  if (loading) return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: palette.background }}><ActivityIndicator color={palette.accent} size="large" accessibilityLabel="Loading account" /></View>;
  if (onboardingComplete && session?.user.email_confirmed_at && !preview && !recovery && (accountLoading || accountError)) return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 28, gap: 18, backgroundColor: palette.background }}>
    {accountLoading ? <ActivityIndicator color={palette.accent} accessibilityLabel="Loading profile" /> : <>
      <Text accessibilityRole="alert" style={{ color: palette.error, textAlign: 'center' }}>{accountError}</Text>
      <Pressable accessibilityRole="button" onPress={reloadAccount} style={{ padding: 14 }}><Text style={{ color: palette.accent }}>Retry</Text></Pressable>
      {error ? <Text accessibilityRole="alert" style={{ color: palette.error }}>{error}</Text> : null}
      <Pressable accessibilityRole="button" disabled={busy} onPress={() => { void run(signOut); }} style={{ padding: 14 }}><Text style={{ color: palette.text }}>Log out</Text></Pressable>
    </>}
  </View>;
  return (
    <>
      <StatusBar hidden={cameraOpen} style={cameraOpen || mode === 'dark' ? 'light' : 'dark'} />
      <View style={{ flex: 1 }} {...swipeBack}>
        <Stack screenOptions={{ headerShown: false, animation: 'none', gestureEnabled: false, contentStyle: { backgroundColor: palette.background } }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="reset-password" />
          <Stack.Screen name="auth/callback" />
          <Stack.Protected guard={!recovery}>
            <Stack.Screen name="login" />
            <Stack.Screen name="sign-up" />
            <Stack.Screen name="forgot-password" />
            <Stack.Screen name="verify-email" />
          </Stack.Protected>
          <Stack.Protected guard={onboardingComplete}>
            <Stack.Screen name="save-account" options={{ presentation: 'modal' }} />
            <Stack.Screen name="help" />
          </Stack.Protected>
          <Stack.Protected guard={onboardingComplete && !recovery && (preview || Boolean(session?.user.email_confirmed_at))}>
            {privateScreens.map(name => <Stack.Screen key={name} name={name} />)}
          </Stack.Protected>
        </Stack>
      </View>
    </>
  );
}

export default function RootLayout() {
  return (
    <ThemeProvider><AuthProvider><AccountApp /></AuthProvider></ThemeProvider>
  );
}

function AccountApp() {
  const { session, preview } = useAuth();
  return <CookingProvider key={preview ? 'preview' : session?.user.id ?? 'signed-out'}><AppStack /></CookingProvider>;
}

