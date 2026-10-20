import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, PropsWithChildren, useContext, useEffect, useRef, useState } from 'react';
import { Appearance, Platform } from 'react-native';
import { ThemePalette, themes } from './colors';

type ThemeMode = 'light' | 'dark';
type ThemeState = { mode: ThemeMode; palette: ThemePalette; setThemeMode: (mode: ThemeMode) => void };
const ThemeContext = createContext<ThemeState | null>(null);
const storageKey = 'timpla.appearance';

export function ThemeProvider({ children }: PropsWithChildren) {
  const [mode, setMode] = useState<ThemeMode>('light');
  const changedByUser = useRef(false);
  useEffect(() => {
    let mounted = true;
    AsyncStorage.getItem(storageKey)
      .then((saved) => {
        if (mounted && !changedByUser.current && (saved === 'light' || saved === 'dark')) setMode(saved);
      })
      .catch(() => {});
    return () => { mounted = false; };
  }, []);
  useEffect(() => {
    // React Native Web exposes Appearance without the native setter.
    if (Platform.OS !== 'web' && typeof Appearance.setColorScheme === 'function') {
      Appearance.setColorScheme(mode);
    }
  }, [mode]);
  function setThemeMode(nextMode: ThemeMode) {
    changedByUser.current = true;
    setMode(nextMode);
    void AsyncStorage.setItem(storageKey, nextMode).catch(() => {});
  }
  return (
    <ThemeContext.Provider value={{ mode, palette: themes[mode], setThemeMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const state = useContext(ThemeContext);
  if (!state) throw new Error('useTheme must be used inside ThemeProvider');
  return state;
}

