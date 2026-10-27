import AsyncStorage from '@react-native-async-storage/async-storage';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { cleanItems, defaultPreferences, Preferences } from '../data/account';
import { isCookingStyle } from '../data/cookingStyles';
import { loadAccount, saveAccountName, saveAccountPreferences } from '../services/account';

export function useAccountSettings() {
  const { session, preview, recovery } = useAuth();
  const userId = session?.user.id;
  const cloud = Boolean(userId && session?.user.email_confirmed_at && !preview && !recovery);
  const [preferences, setPreferences] = useState<Preferences>(defaultPreferences);
  const [displayName, setName] = useState(preview ? 'Juan Dela Cruz' : '');
  const [loaded, setLoaded] = useState(false);
  const [accountError, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const accountLoading = cloud && !loaded && !accountError;
  const mounted = useRef(true);
  const writes = useRef<Promise<unknown>>(Promise.resolve());
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);
  useEffect(() => {
    let active = true;
    if (!cloud) {
      if (preview) void AsyncStorage.getItem('timpla.preview.cooking-style').then(style => {
        if (active && isCookingStyle(style)) setPreferences(current => ({ ...current, cookingStyle: style }));
      }).catch(() => {});
      return () => { active = false; };
    }
    void AsyncStorage.getItem(`timpla.${userId}.cooking-style`).catch(() => null)
      .then(style => loadAccount(userId!, style))
      .then(account => {
        if (!active) return;
        setName(account.fullName); setPreferences(account.preferences);
      }).catch(() => { if (active) setError('Could not load your profile. Try again.'); })
      .finally(() => { if (active) setLoaded(true); });
    return () => { active = false; };
  }, [cloud, userId, preview, attempt]);

  const savePreferences = useCallback((patch: Partial<Preferences>) => {
    const task = writes.current.catch(() => {}).then(async () => {
      if (cloud && (accountLoading || accountError)) throw new Error('Load your profile before saving changes.');
      if (!cloud && !preview) throw new Error('Sign in before saving changes.');
      const result = cloud ? await saveAccountPreferences(userId!, patch) : null;
      if (preview && patch.cookingStyle) await AsyncStorage.setItem('timpla.preview.cooking-style', patch.cookingStyle);
      if (mounted.current) setPreferences(current => result ?? ({ ...current, ...patch,
        ...(patch.allergies ? { allergies: cleanItems(patch.allergies) } : {}),
        ...(patch.exclusions ? { exclusions: cleanItems(patch.exclusions) } : {}),
      }));
    });
    writes.current = task;
    return task;
  }, [cloud, preview, userId, accountLoading, accountError]);
  const saveProfile = useCallback(async (name: string) => {
    if (cloud && (accountLoading || accountError)) throw new Error('Load your profile before saving changes.');
    if (!cloud && !preview) throw new Error('Sign in before saving changes.');
    const cleaned = name.trim();
    if (!cleaned || cleaned.length > 40) throw new Error('Enter a name of 1–40 characters.');
    const value = cloud ? await saveAccountName(userId!, cleaned) : cleaned;
    if (mounted.current) setName(value);
  }, [cloud, preview, userId, accountLoading, accountError]);
  return { ...preferences, displayName, saveProfile, savePreferences, accountLoading, accountError,
    reloadAccount: () => { setLoaded(false); setError(''); setAttempt(value => value + 1); } };
}
