import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient, processLock } from '@supabase/supabase-js';
import { Platform } from 'react-native';

const url = process.env.EXPO_PUBLIC_SUPABASE_URL;
const key = process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

export const supabase = url && key ? createClient(url, key, {
  auth: {
    ...(Platform.OS !== 'web' ? { storage: AsyncStorage, lock: processLock } : {}),
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: false,
    flowType: 'implicit',
  },
}) : null;

export function authClient() {
  if (!supabase) throw new Error('Account setup is missing. Add the Supabase URL and publishable key, then restart Expo.');
  return supabase;
}
