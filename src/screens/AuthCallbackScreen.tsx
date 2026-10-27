import { useEffect, useRef, useState } from 'react';
import * as Linking from 'expo-linking';
import { router } from 'expo-router';
import { ActivityIndicator } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { authError } from '../auth/validation';
import { AuthForm, AuthLink } from '../components/AuthForm';
import { useTheme } from '../theme/ThemeContext';

export default function AuthCallbackScreen() {
  const url = Linking.useLinkingURL();
  const { loading, handleCallback } = useAuth();
  const { palette } = useTheme();
  const [error, setError] = useState('');
  const handled = useRef('');
  const callback = useRef(handleCallback);
  useEffect(() => { callback.current = handleCallback; }, [handleCallback]);
  useEffect(() => {
    if (loading || !url || handled.current === url) return;
    handled.current = url;
    let mounted = true;
    void callback.current(url).then(destination => {
      if (mounted) router.replace(destination === 'reset' ? '/reset-password' : '/home');
    }).catch(cause => { if (mounted) setError(authError(cause)); });
    return () => { mounted = false; };
  }, [url, loading]);
  return <AuthForm title={error ? 'Check your email link' : 'Verifying your email'} error={error}>
    {error ? <><AuthLink title="Request a new reset email" onPress={() => router.replace('/forgot-password')} /><AuthLink title="Back to log in" onPress={() => router.replace('/')} /></> : <ActivityIndicator size="large" color={palette.accent} />}
  </AuthForm>;
}
