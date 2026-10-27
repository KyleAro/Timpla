import { useState } from 'react';
import { Redirect, router } from 'expo-router';
import { AuthButton, AuthForm, AuthInput, AuthLink } from '../components/AuthForm';
import { useAuth } from '../auth/AuthContext';
import { cleanEmail, emailError, passwordError } from '../auth/validation';
import { useAuthAction } from '../auth/useAuthAction';

export default function SignUpScreen() {
  const { session, recovery, signUp } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const { busy, error, setError, run } = useAuthAction();
  if (session && !recovery) return <Redirect href="/home" />;
  function submit() {
    const invalid = (!name.trim() ? 'Enter your name.' : '') || emailError(email) || passwordError(password) || (password !== confirmation ? 'Passwords do not match.' : '');
    if (invalid) { setError(invalid); return; }
    void run(async () => {
      const signedIn = await signUp(name, email, password);
      setPassword(''); setConfirmation('');
      if (!signedIn) router.replace({ pathname: '/verify-email', params: { email: cleanEmail(email), mode: 'signup' } });
    });
  }
  return <AuthForm title="Create your account" error={error}>
    <AuthInput accessibilityLabel="Your name" placeholder="Name" value={name} onChangeText={setName} textContentType="name" autoComplete="name" autoCapitalize="words" maxLength={40} editable={!busy} />
    <AuthInput accessibilityLabel="Email address" placeholder="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="email" textContentType="emailAddress" autoCapitalize="none" autoCorrect={false} editable={!busy} />
    <AuthInput password accessibilityLabel="Password" placeholder="Password · at least 8 characters" value={password} onChangeText={setPassword} autoComplete="new-password" textContentType="newPassword" autoCapitalize="none" autoCorrect={false} editable={!busy} />
    <AuthInput password accessibilityLabel="Confirm password" placeholder="Confirm password" value={confirmation} onChangeText={setConfirmation} autoComplete="new-password" textContentType="newPassword" autoCapitalize="none" autoCorrect={false} editable={!busy} returnKeyType="go" onSubmitEditing={submit} />
    <AuthButton title="Create account" onPress={submit} busy={busy} />
    <AuthLink title="Already have an account? Log in" onPress={() => router.replace('/')} disabled={busy} />
  </AuthForm>;
}
