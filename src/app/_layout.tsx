import { Stack, usePathname } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { CookingProvider } from '../state/CookingContext';
import { ThemeProvider, useTheme } from '../theme/ThemeContext';

function AppStack() {
  const { mode, palette } = useTheme();
  const pathname = usePathname();
  const cameraOpen = pathname === '/scan' || pathname === '/live-scan' || pathname === '/photo';
  return (
    <>
      <StatusBar hidden={cameraOpen} style={cameraOpen || mode === 'dark' ? 'light' : 'dark'} />
      <Stack screenOptions={{ headerShown: false, animation: 'none', gestureEnabled: false, contentStyle: { backgroundColor: palette.background } }} />
    </>
  );
}

export default function RootLayout() {
  return (
    <ThemeProvider><CookingProvider><AppStack /></CookingProvider></ThemeProvider>
  );
}

