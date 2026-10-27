import { useState } from 'react';
import { router } from 'expo-router';
import { useAuth } from '../auth/AuthContext';
import { useAuthAction } from '../auth/useAuthAction';
import { cleanEmail, emailError } from '../auth/validation';
import { AuthButton, AuthForm, AuthInput, AuthLink } from '../components/AuthForm';

export default function ForgotPasswordScreen() {
  const { sendReset } = useAuth();
  const [email, setEmail] = useState('');
  const { busy, error, setError, run } = useAuthAction();
  function submit() {
    if (emailError(email)) { setError(emailError(email)); return; }
    void run(async () => {
      await sendReset(email);
      router.replace({ pathname: '/verify-email', params: { email: cleanEmail(email), mode: 'recovery' } });
    });
  }
  return <AuthForm title="Forgot password?" subtitle="Enter your email to reset your password." error={error}>
    <AuthInput accessibilityLabel="Email address" placeholder="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="email" textContentType="emailAddress" autoCapitalize="none" autoCorrect={false} editable={!busy} returnKeyType="send" onSubmitEditing={submit} />
    <AuthButton title="Send reset email" onPress={submit} busy={busy} />
    <AuthLink title="Back to log in" onPress={() => router.replace('/')} disabled={busy} />
  </AuthForm>;
}
