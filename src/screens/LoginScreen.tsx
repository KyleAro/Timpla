import { useState } from 'react';
import { Redirect, router, useLocalSearchParams } from 'expo-router';
import { AuthButton, AuthForm, AuthInput, AuthLink } from '../components/AuthForm';
import { useAuth } from '../auth/AuthContext';
import { authError, cleanEmail, emailError } from '../auth/validation';
import { useAuthAction } from '../auth/useAuthAction';
import { defaultPreferences } from '../data/account';

export default function LoginScreen() {
  const { session, recovery, onboardingComplete, completeOnboarding, signIn, enterPreview } = useAuth();
  const { reset } = useLocalSearchParams<{ reset?: string }>();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [unconfirmed, setUnconfirmed] = useState(false);
  const { busy, error, setError, run } = useAuthAction();
  if (session && !recovery) return <Redirect href={onboardingComplete ? '/home' : '/'} />;
  if (session && recovery) return <Redirect href="/reset-password" />;
  function submit() {
    setUnconfirmed(false);
    const invalid = emailError(email) || (!password ? 'Enter your password.' : '');
    if (invalid) { setError(invalid); return; }
    void run(async () => {
      try {
        await signIn(email, password);
        if (!onboardingComplete) await completeOnboarding('', defaultPreferences, false);
        setPassword('');
      }
      catch (cause) {
        if (typeof cause === 'object' && cause && 'code' in cause && cause.code === 'email_not_confirmed') setUnconfirmed(true);
        throw new Error(authError(cause));
      }
    });
  }
  return <AuthForm title="Welcome back" error={error} notice={reset === 'done' ? 'Password updated. Log in with your new password.' : undefined}>
    <AuthInput accessibilityLabel="Email address" placeholder="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="email" textContentType="emailAddress" autoCapitalize="none" autoCorrect={false} editable={!busy} />
    <AuthInput password accessibilityLabel="Password" placeholder="Password" value={password} onChangeText={setPassword} autoComplete="current-password" textContentType="password" autoCapitalize="none" autoCorrect={false} editable={!busy} returnKeyType="go" onSubmitEditing={submit} />
    <AuthLink title="Forgot password?" onPress={() => router.push('/forgot-password')} disabled={busy} />
    {unconfirmed ? <AuthLink title="Resend confirmation email" onPress={() => router.push({ pathname: '/verify-email', params: { email: cleanEmail(email), mode: 'signup', resend: 'true' } })} disabled={busy} /> : null}
    <AuthButton title="Log in" onPress={submit} busy={busy} />
    <AuthLink title="New here? Sign up" onPress={() => router.push('/sign-up')} disabled={busy} />
    <AuthLink title="Keep browsing" onPress={() => { if (onboardingComplete) { enterPreview(); router.replace('/home'); } else router.replace('/'); }} disabled={busy} />
  </AuthForm>;
}
