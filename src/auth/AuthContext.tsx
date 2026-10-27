import AsyncStorage from '@react-native-async-storage/async-storage';
import { Session } from '@supabase/supabase-js';
import * as Linking from 'expo-linking';
import { AppState, Platform } from 'react-native';
import { createContext, PropsWithChildren, useContext, useEffect, useRef, useState } from 'react';
import { authClient, supabase } from './supabase';
import { cleanEmail, readAuthCallback } from './validation';

const recoveryKey = 'timpla.auth.password-recovery';
export function authRedirectUrl() {
  return process.env.EXPO_PUBLIC_AUTH_REDIRECT_URL || Linking.createURL('auth/callback');
}
type AuthState = {
  session: Session | null;
  loading: boolean;
  recovery: boolean;
  preview: boolean;
  enterPreview: () => void;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<boolean>;
  sendReset: (email: string) => Promise<void>;
  resendConfirmation: (email: string) => Promise<void>;
  verifyCode: (email: string, token: string, kind: 'signup' | 'recovery') => Promise<void>;
  handleCallback: (url: string) => Promise<'home' | 'reset'>;
  updatePassword: (password: string) => Promise<void>;
  signOut: () => Promise<void>;
};
const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(Boolean(supabase));
  const [recovery, setRecovery] = useState(false);
  const [preview, setPreview] = useState(false);
  const recoveryRef = useRef(false);
  const callbacks = useRef(new Map<string, Promise<'home' | 'reset'>>());

  async function markRecovery(value: boolean, publish = true) {
    // Set before verifyOtp/setSession emits SIGNED_IN, so recovery never opens private screens.
    recoveryRef.current = value;
    if (publish) setRecovery(value);
    if (value) await AsyncStorage.setItem(recoveryKey, 'true');
    else await AsyncStorage.removeItem(recoveryKey);
  }

  useEffect(() => {
    if (!supabase) return;
    const client = supabase;
    let mounted = true;
    let revision = 0;
    const { data: { subscription } } = client.auth.onAuthStateChange((event, next) => {
      if (!mounted) return;
      if (event !== 'INITIAL_SESSION') revision++;
      if (event === 'PASSWORD_RECOVERY') {
        recoveryRef.current = true;
        setRecovery(true);
        void AsyncStorage.setItem(recoveryKey, 'true').catch(() => {});
      }
      if (next && event !== 'INITIAL_SESSION') setRecovery(recoveryRef.current);
      setSession(next);
    });
    const startRevision = revision;
    void Promise.all([client.auth.getSession(), AsyncStorage.getItem(recoveryKey)]).then(([result, recovering]) => {
      if (!mounted || revision !== startRevision) return;
      recoveryRef.current = Boolean(result.data.session && recovering);
      setRecovery(recoveryRef.current);
      setSession(result.error ? null : result.data.session);
    }).catch(() => { if (mounted && revision === startRevision) setSession(null); }).finally(() => { if (mounted) setLoading(false); });
    const refresh = (state: string) => {
      if (Platform.OS === 'web') return;
      if (state === 'active') client.auth.startAutoRefresh();
      else client.auth.stopAutoRefresh();
    };
    refresh(AppState.currentState);
    const appState = AppState.addEventListener('change', refresh);
    return () => { mounted = false; subscription.unsubscribe(); appState.remove(); if (Platform.OS !== 'web') client.auth.stopAutoRefresh(); };
  }, []);

  async function signIn(email: string, password: string) {
    const client = authClient();
    const { data, error } = await client.auth.signInWithPassword({ email: cleanEmail(email), password });
    if (error) throw error;
    await markRecovery(false);
    setPreview(false);
    setSession(data.session);
  }
  async function signUp(name: string, email: string, password: string) {
    const { data, error } = await authClient().auth.signUp({
      email: cleanEmail(email), password,
      options: { data: { full_name: name.trim() }, emailRedirectTo: authRedirectUrl() },
    });
    if (error) throw error;
    if (data.user?.identities?.length === 0) throw new Error('An account may already exist. Log in or reset your password.');
    return Boolean(data.session);
  }
  async function sendReset(email: string) {
    const { error } = await authClient().auth.resetPasswordForEmail(cleanEmail(email), { redirectTo: authRedirectUrl() });
    if (error) throw error;
  }
  async function resendConfirmation(email: string) {
    const { error } = await authClient().auth.resend({ type: 'signup', email: cleanEmail(email), options: { emailRedirectTo: authRedirectUrl() } });
    if (error) throw error;
  }
  async function verifyCode(email: string, token: string, kind: 'signup' | 'recovery') {
    const client = authClient();
    const previousRecovery = recoveryRef.current;
    await markRecovery(kind === 'recovery', false);
    const { data, error } = await client.auth.verifyOtp({ email: cleanEmail(email), token: token.trim(), type: kind === 'recovery' ? 'recovery' : 'email' });
    if (error) {
      await markRecovery(previousRecovery);
      throw error;
    }
    if (!data.session) { await markRecovery(previousRecovery); throw new Error('Could not verify this code. Request a new one.'); }
    setRecovery(recoveryRef.current);
    setSession(data.session);
  }
  function handleCallback(url: string): Promise<'home' | 'reset'> {
    const existing = callbacks.current.get(url);
    if (existing) return existing;
    const task = (async () => {
      const values = readAuthCallback(url);
      if (values.error) throw new Error(values.error);
      const client = authClient();
      if (!values.code && !(values.accessToken && values.refreshToken)) throw new Error('This link is incomplete. Enter the code from your email or request a new link.');
      const previousRecovery = recoveryRef.current;
      await markRecovery(values.recovery, false);
      try {
        const { data, error } = values.code
          ? await client.auth.exchangeCodeForSession(values.code)
          : await client.auth.setSession({ access_token: values.accessToken!, refresh_token: values.refreshToken! });
        if (error) throw error;
        if (!data.session) throw new Error('This link has expired. Request a new one.');
        setRecovery(recoveryRef.current);
        setSession(data.session);
      } catch (error) { await markRecovery(previousRecovery); throw error; }
      if (Platform.OS === 'web' && typeof window !== 'undefined') window.history.replaceState({}, '', '/auth/callback');
      return recoveryRef.current ? 'reset' as const : 'home' as const;
    })();
    callbacks.current.set(url, task);
    // Keep only the current in-memory callback; never persist tokens or URLs.
    if (callbacks.current.size > 1) callbacks.current = new Map([[url, task]]);
    return task;
  }
  async function updatePassword(password: string) {
    if (!recoveryRef.current || !session) throw new Error('Verify the reset code or open your reset link first.');
    const { error } = await authClient().auth.updateUser({ password });
    if (error) throw error;
    await signOut();
  }
  async function signOut() {
    if (preview) { setPreview(false); return; }
    const { error } = await authClient().auth.signOut({ scope: 'local' });
    if (error) throw error;
    setSession(null);
    callbacks.current.clear();
    await markRecovery(false);
  }
  return <AuthContext.Provider value={{ session, loading, recovery, preview, enterPreview: () => { if (__DEV__) setPreview(true); }, signIn, signUp, sendReset, resendConfirmation, verifyCode, handleCallback, updatePassword, signOut }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const state = useContext(AuthContext);
  if (!state) throw new Error('useAuth must be used inside AuthProvider');
  return state;
}
