import { Stack, usePathname } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { CookingProvider, useCooking } from '../state/CookingContext';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';
import { AuthProvider, useAuth } from '../auth/AuthContext';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { useAuthAction } from '../auth/useAuthAction';

const privateScreens = ['home', 'settings', 'scan', 'scan-details', 'saved-recipes', 'reverse-cooking', 'recipes', 'recipe', 'recents', 'profile', 'profile-details', 'photo', 'live-scan', 'ingredients', 'explore', 'cooking-preferences', 'allergies'] as const;

function AppStack() {
  const { mode, palette } = useTheme();
  const pathname = usePathname();
  const { session, loading, recovery, preview, signOut } = useAuth();
  const { accountLoading, accountError, reloadAccount } = useCooking();
  const { busy, error, run } = useAuthAction();
  const cameraOpen = pathname === '/scan' || pathname === '/live-scan' || pathname === '/photo';
  if (loading) return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: palette.background }}><ActivityIndicator color={palette.accent} size="large" accessibilityLabel="Loading account" /></View>;
  if (session?.user.email_confirmed_at && !preview && !recovery && (accountLoading || accountError)) return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 28, gap: 18, backgroundColor: palette.background }}>
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
      <Stack screenOptions={{ headerShown: false, animation: 'none', gestureEnabled: false, contentStyle: { backgroundColor: palette.background } }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="sign-up" />
        <Stack.Screen name="forgot-password" />
        <Stack.Screen name="verify-email" />
        <Stack.Screen name="reset-password" />
        <Stack.Screen name="auth/callback" />
        <Stack.Screen name="help" />
        <Stack.Protected guard={(__DEV__ && preview) || (Boolean(session?.user.email_confirmed_at) && !recovery)}>
          {privateScreens.map(name => <Stack.Screen key={name} name={name} />)}
        </Stack.Protected>
      </Stack>
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

